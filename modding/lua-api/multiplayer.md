# Multiplayer for Lua: commands and ModData (Project Zomboid, Build 42)

Survey date: 2026-10-24. Source: Java declarations and control flow in `zombie/**` (`Lua.LuaManager`, `network.GameServer`, `network.GameClient`,
`network.TableNetworkUtils`, `network.PacketTypes`, `network.packets.*`, `spnetwork.*`, `world.moddata.*`,
`globalObjects.*`, `core.raknet.UdpConnection`) plus the shipped Lua under `media/lua`. Everything here comes from
reading code, not from running a server. Tags: **[observed]**, **[inferred]**, **[unknown]**. Event names and
arguments are in [`events.md`](events.md) and [`../data/events.csv`](../data/events.csv). When each Lua folder loads
and when the lifecycle events fire is in [`lifecycle.md`](lifecycle.md). The global functions are rows in
[`../data/lua-globals.csv`](../data/lua-globals.csv). No game code or Lua bodies are copied; the one code sample
in section 11 is invented.

## Short version

1. There are four separate paths from Lua to the network: the **command channel**, **global ModData**,
   **per-object ModData** (objects, squares, items), and the **global-object channel**.
   Each has its own packet type and its own receive event or callback. [observed]
2. The command channel is one packet type, `ClientCommand`, used in both directions. Client to server fires
   `OnClientCommand(module, command, player, args)` on the server. Server to client fires
   `OnServerCommand(module, command, args)` on the client. There is no acknowledgement and no return value.
   A "response" is a second command that you send yourself. [observed]
3. `args` travels as a Kahlua table through `TableNetworkUtils`. Only string and number keys survive, and only
   string, number, boolean, table, inventory item, direction and dead-body values survive. Everything else is
   dropped from the wire without an error, and only a top-level drop is logged. [observed]
4. In **single player** the client call loops back into the in-process server and `OnClientCommand` fires.
   The server-side `sendServerCommand` global does nothing, so single-player code cannot answer with it. [observed]
5. Global ModData tables are saved with the world, but receiving one over the network does not store it.
   `OnReceiveGlobalModData` hands you the table; keeping it is up to your handler. [observed]
6. The server's `ClientCommandFilter` option changes what is **logged**, not what is delivered. The only
   delivery gate in Java is for `vehicle.remove`. [observed]

## 1. The four paths at a glance

| Path | Lua entry points | Direction | Receiver in Lua | Format |
|---|---|---|---|---|
| Command channel | `sendClientCommand`, `sendServerCommand`, `sendClientCommandV`, `sendServerCommandV` | both | `OnClientCommand` (server), `OnServerCommand` (client) | `TableNetworkUtils` |
| Global ModData | `ModData.transmit`, `ModData.request` (and `add`, `get`, `getOrCreate`, ...) | both | `OnReceiveGlobalModData` (client or server) | `KahluaTable.save` |
| Object / square / item ModData | `IsoObject:transmitModData`, `IsoGridSquare:transmitModdata`, `syncItemModData`, `getServerModData` | both (item sync: server to client) | `onLoadModDataFromServer` (squares), `SendCustomModData` (server), `OnWaterAmountChange` (objects, only when the fluid amount changed) | `KahluaTable.save` |
| Global-object channel | `SGlobalObjectSystem:sendCommand`, `CGlobalObjectSystem:sendCommand` | both | functions stored on the system table | `TableNetworkUtils` |

Packet registration is in `PacketTypes.PacketType`: `ClientCommand`, `GlobalObjects`, `GlobalModData`,
`GlobalModDataRequest`, `ReceiveModData`, `ObjectModData`, `SyncItemModData`, `GetModData`. [observed] Every one of
them is declared with `requiredCapability = LoginOnServer`, so the server only accepts them from a logged-in
connection. [observed] The handling-type bitmask on a packet is None 0, Server 1, Client 2, ClientLoading 4,
All 7; the ModData packets below use 1, 2 or 3. [observed]

## 2. The command channel, end to end

### 2.1 Request and response

```
CLIENT                                         SERVER
sendClientCommand(player, "mod", "ask", t)
  -> GameClient.sendClientCommand
     packet ClientCommand
     [player index][module][command][hasArgs][args]
                         ------------------>   GameServer.receiveClientCommand
                                                 resolve the player from connection + index
                                                 log line (ClientCommandFilter decides)
                                                 vehicle.remove gate (section 2.4)
                                                 LuaEventManager "OnClientCommand"
                                                   (module, command, player, args)
                                               your handler runs, then calls:
                                               sendServerCommand(player, "mod", "answer", t2)
                         <------------------     GameServer.sendServerCommand
                                                 packet ClientCommand
                                                 [module][command][hasArgs][args]
GameClient.receiveClientCommand
  LuaEventManager "OnServerCommand"
  (module, command, args)
```

The request and the answer are independent packets. The sender gets nothing back unless the server code sends a
command, and the server has no way to tell a client "your command was ignored". [observed]

### 2.2 The Lua globals and where they work

| Global | Overloads in Java | Client (MP, in game) | Server | Single player |
|---|---|---|---|---|
| `sendClientCommand` | `(module, command, args)` | sends with player index -1 | **throws** `IllegalStateException` | loops back, player index -1 |
| | `(player, module, command, args)` | sends only if `player:isLocalPlayer()` | fires `OnClientCommand` locally with that player, no packet | loops back, only if `player:isLocalPlayer()` |
| `sendServerCommand` | `(module, command, args)` | no-op | sends to every connection | no-op |
| | `(player, module, command, args)` | no-op | sends to that player's connection only | no-op |
| `sendClientCommandV` | `(player, module, command, ...)` | sends | no-op | **no-op** (guarded by `GameClient.client`) |
| `sendServerCommandV` | `(module, command, ...)` | no-op | sends to every connection | no-op |

All rows [observed] in `LuaManager` (lines 7431 to 7487) and the called classes. Details:

- "Client (MP, in game)" means `GameClient.client && GameClient.ingame`. A client that is connected but not yet in
  game falls through to `SinglePlayerClient.sendClientCommand`; what that does in a multiplayer client is
  **[unknown]** (the loopback connection may not exist there).
- With player index -1 the server uses the **first** player slot it finds on that connection
  (`getAnyPlayerFromConnection`). Split-screen clients should pass the player explicitly. [observed]
- If the server cannot resolve a player, it logs "receiveClientCommand: player is null" and drops the command
  without firing `OnClientCommand`. [observed]
- The 4-argument `sendServerCommand` looks the player up in the server's player-to-address map. If the player
  has no connection it silently sends nothing. [observed]
- A server-side `sendClientCommand(player, ...)` is a way to run your own `OnClientCommand` handlers from server
  code. It skips the packet, the log line and the vehicle gate. [observed]
- There is no Lua global for "send to everyone near a point". The Java method
  `GameServer.sendServerCommandToRelevant(x, y, ...)` exists (used by one recipe callback) but is not a global and
  `GameServer` is not an exposed class. [observed]

### 2.3 Wire layout

Both directions use the same packet type. Fields are written in this order. [observed]

| Direction | Fields |
|---|---|
| client to server | byte player index (or -1), UTF module, UTF command, boolean hasArgs, then (if hasArgs) the table |
| server to client | UTF module, UTF command, boolean hasArgs, then (if hasArgs) the table |

`hasArgs` is false when `args` is nil **or an empty table**. On receipt a false `hasArgs` gives your handler a
**nil** `args`, not an empty table, so always guard with `args and args.x`. [observed]

### 2.4 What the server does before your handler runs

1. Reads the fields and loads the table. If loading throws, it logs the exception and drops the command. [observed]
2. Resolves the player (section 2.2). [observed]
3. Looks up a `ClientCommandFilter` entry for the module and, unless it says "suppress", writes one line to the
   `cmd` log: connection id, username, `module.command`, and the player's tile. [observed]
4. If the command is exactly `vehicle.remove`, it is delivered only when at least one of these holds: the server is
   in debug mode, the connection's role has the `GeneralCheats` capability, or the player's network character AI
   says dismantling is allowed. Otherwise it is silently dropped. [observed]
5. Fires `OnClientCommand(module, command, player, args)`. [observed]

No other command is gated in Java. Authorisation, rate limiting and argument validation are the mod's job, and
everything in `args` is client-controlled. [observed, inferred for the advice]

### 2.5 `ClientCommandFilter` (log only)

The server option `ClientCommandFilter` is a semicolon-separated list of `+module.command` or `-module.command`
entries. `command` may be `*`. A `-` entry means "do not log", a `+` entry means "log". The default is
`-vehicle.*;+vehicle.damageWindow;+vehicle.fixPart;+vehicle.installPart;+vehicle.uninstallPart`. [observed]

- Entries are chained per module with the **later** entry first, so a later entry beats an earlier one. The
  default therefore logs the four named vehicle commands and suppresses the rest of the `vehicle` module. [observed]
- A module with no entry is always logged. [observed]
- Entries without exactly one dot, or that do not start with `+` or `-`, are ignored. [observed]
- The filter never stops `OnClientCommand` from firing. Do not use it as a block list. [observed]

### 2.6 Client side

`GameClient.receiveClientCommand` reads module, command and the optional table, then fires
`OnServerCommand(module, command, tbl)`. There is no filter, no player argument, and no gate. A table that fails to
load is logged and the command is dropped. [observed]

### 2.7 Single player

`SinglePlayerClient.sendClientCommand` writes the same packet layout into an in-process connection and ends it
immediately. `SinglePlayerServer` reads it, resolves the player the same way, and fires `OnClientCommand`. [observed]
There is no `ClientCommandFilter` check and no `vehicle.remove` gate on that path. [observed]

The return path is missing: the Lua `sendServerCommand` only acts when `GameServer.server` is true, and
`SinglePlayerServer.sendServerCommand` has no callers in the decompile. [observed] So in single player an
`OnClientCommand` handler cannot reach `OnServerCommand` through the globals. `SinglePlayerClient` does have a
receive path that fires `OnServerCommand`, so an answer would work if something sent one, but nothing in the
decompile does. [observed]

Because the vanilla server Lua loads in single player too (see [`lifecycle.md`](lifecycle.md)), code that needs to
run in single player, on a host and on a dedicated server should either call its server logic directly in single
player or branch on `isClient()`, `isServer()` and `GameClient.client`. [inferred]

## 3. How `args` is encoded

`TableNetworkUtils` writes an int count and then, per entry, a type byte and value for the key and again for the
value. [observed]

| Type byte | Lua type | Key allowed | Value allowed | Wire value |
|---|---|---|---|---|
| 0 | string | yes | yes | UTF string |
| 1 | number (Double) | yes | yes | 8-byte double |
| 2 | table | no | yes | the same layout, recursively |
| 3 | boolean | no | yes | one boolean |
| 4 | `InventoryItem` | no | yes | the item saved with its size |
| 5 | `IsoDirections` | no | yes | enum |
| 6 | `IsoDeadBody` | no | yes | the body's object id |
| -1 | anything else | no | no | not written |

Consequences, all [observed]:

- **Dropped entries.** An entry whose key is not a string or number, or whose value is a function, userdata other
  than the three item/direction/body types, or a Java object such as an `IsoPlayer`, `IsoGridSquare`, `ArrayList`,
  is skipped, and the count written is the number of entries that survive.
- **Only the top level is logged.** Before saving, the sender checks each top-level entry with `canSave` and
  prints "can't save key,value=..." to the debug log. Entries inside nested tables are dropped with no message.
- **Numbers are doubles.** There is no integer type. Integers round-trip as doubles, which is the same as Lua.
- **Identity is lost.** An inventory item is written out in full and rebuilt on the receiving side as a **new**
  item (loaded with save version 249). A dead body is sent as an object id and looked up on the receiver; the
  result is nil if the receiver has no such body loaded.
- **Cycles are not detected.** `TableNetworkUtils` has no cycle guard, so a table that contains itself would recurse
  until it fails. [inferred from the absence of a check]
- **Loading wipes.** `load` empties the destination table before filling it, so each command gets a fresh table.
- Array-style tables survive because number keys are allowed; they come back with double keys.

### 3.1 The V variants

`sendClientCommandV(player, module, command, k1, v1, k2, v2, ...)` and `sendServerCommandV(module, command, k1, v1, ...)`
build a table from alternating keys and values and then call the normal sender. [observed]

- Zero extra arguments sends a command with no table.
- An odd number of extra arguments logs "called with wrong number of arguments" (or "invalid number") and sends
  nothing.
- Java `Float`, `Integer` and `Short` values are converted to doubles; other values are stored as given. From Lua
  all numbers already arrive as doubles, so this matters only for Java callers.
- The client variant has no player-less form and does nothing outside a multiplayer client (section 2.2).

## 4. Targeting and reach

| Need | What exists | Notes |
|---|---|---|
| One player, from the server | `sendServerCommand(player, ...)` | Silent if the player has no connection. |
| Everyone, from the server | `sendServerCommand(module, ...)` or `sendServerCommandV` | Loops over **all** connections, with no "fully connected" or distance check on this path. [observed] |
| Everyone near a point | not available from Lua | Java only (section 2.2). Use `OnServerCommand` with a position in `args` and filter on the client. [inferred] |
| One client, from another client | not available | Route through the server: client to server, then `sendServerCommand(otherPlayer, ...)`. The vanilla `LuaNet` module does this (section 7). |
| "Near" semantics where the Java side uses them | `UdpConnection.isRelevantTo(x, y)` | True when the point is inside the square of tiles around any of the connection's four player slots (chunk-map width times 8 tiles), or within `relevantRange * 8` tiles of a stored relevant position on each axis. Used by the ModData packets below. [observed] |

## 5. Global ModData

`ModData` is the Lua-facing facade over `GlobalModData`, a map from a string tag to a Kahlua table. See also the
class page [`classes/ModData.md`](classes/ModData.md). [observed]

### 5.1 API

| Lua call | Behaviour |
|---|---|
| `ModData.getTableNames()` | Returns the tag list. The list object is **shared and reused** by every call, so copy it if you keep it. |
| `ModData.exists(tag)` | Boolean. |
| `ModData.get(tag)` | The table, or nil. |
| `ModData.getOrCreate(tag)` | The table; creates an empty one when missing. |
| `ModData.create()` | Creates a table under a random UUID tag and returns the tag string. |
| `ModData.create(tag)` | Creates and returns an empty table, or logs and returns **nil** when the tag already exists. |
| `ModData.add(tag, table)` | Stores (or replaces) the table under the tag. This is how you keep a received table. |
| `ModData.remove(tag)` | Removes and returns the table (nil when absent). |
| `ModData.transmit(tag)` | Sends the table (section 5.3). Logs "cannot transmit moddata not found" for an unknown tag. |
| `ModData.request(tag)` | Asks the server for a table. Does nothing but log when not called on a multiplayer client. |

### 5.2 Persistence

- Tables are saved to `global_mod_data.bin` in the save folder: an int version (249), an int table count, and per
  table a size, the tag and the table. The file is written to a temporary name and copied over the final name.
  It is skipped when `Core.isNoSave()` is true. `GameWindow.save` calls the save; see
  [`lifecycle.md`](lifecycle.md), "Saving". [observed]
- `GlobalModData.init()` runs inside `IsoWorld.init`: it clears the map, loads the file and fires
  `OnInitGlobalModData(isNewGame)`. That event is the supported place to call `ModData.getOrCreate` for your own
  tags. The vanilla foraging and vehicle-spawn scripts do exactly that. [observed]
- Whether multiplayer **clients** run the same `IsoWorld.init` step is not separately shown here; the vanilla
  foraging code registers an `OnInitGlobalModData` handler in both a client file and a server file, which suggests
  it fires on both. [inferred]
- The tables use `KahluaTable.save`, not `TableNetworkUtils`, so persistence and transmit accept a wider set of
  value types than the command channel. The exact set is **[unknown]** here.

### 5.3 Transmit and request

| Caller | `ModData.transmit(tag)` does | Receiver event |
|---|---|---|
| multiplayer client | writes one `GlobalModData` packet to the server | `OnReceiveGlobalModData(tag, table)` fires **on the server** |
| dedicated server | writes the packet to **every** connection | `OnReceiveGlobalModData(tag, table)` fires on every client |
| single player | nothing | none |

| Caller | `ModData.request(tag)` does | Result |
|---|---|---|
| multiplayer client | writes a `GlobalModDataRequest` packet | server answers **only the requester** with one `GlobalModData` packet: tag, a boolean "exists", and the table when it exists |
| anything else | logs "can only request from Client" | nothing |

Receipt, all [observed]:

- `OnReceiveGlobalModData(tag, table)` fires with the decoded table. When the server has no such tag, the client
  receives `(tag, false)` instead of a table.
- The receiver does **not** store the table and the server does **not** forward a client's transmit to other
  clients. A handler that wants the data must call `ModData.add(tag, table)` itself, and a mod that wants clients to
  see each other's data must re-send from the server.
- Nothing in the shipped Lua listens for `OnReceiveGlobalModData` or calls `ModData.request`. The only shipped
  `ModData.transmit` call is in the foraging server script. [observed in `media/lua` counts, 2026-10-24]
- Both packets carry no per-recipient checks beyond login. A `transmit` from a client therefore reaches the server's
  handlers whatever the table holds; validate it. [inferred]

## 6. Per-object ModData: objects, squares, items

Every `IsoObject`, `IsoGridSquare` and `InventoryItem` has its own ModData table (see
[`classes/IsoObject.md`](classes/IsoObject.md), [`classes/IsoGridSquare.md`](classes/IsoGridSquare.md),
[`classes/InventoryItem.md`](classes/InventoryItem.md)). Changing the table does not send anything. You have to
call a transmit method. [observed]

| Source | Call | Client does | Server does | Receiver event |
|---|---|---|---|---|
| world object | `obj:transmitModData()` | sends `ObjectModData` to the server, then flags the object for a hot save | sends `ObjectModData` to every relevant connection (not when the server is in soft reset or fast-forward), then flags for hot save | none generic; `OnWaterAmountChange(obj, oldAmount)` when the object's fluid amount differs after load |
| square | `sq:transmitModdata()` (note the lower-case `d`) | sends `ReceiveModData` to the server | runs `GameServer.loadModData(sq)` then sends to every **relevant** connection | `onLoadModDataFromServer(sq)` |
| item | `syncItemModData(player, item)` | **no-op** | sends `SyncItemModData` to connections relevant to the player's tile | none |
| anything | `getServerModData()` | sends an empty `GetModData` packet | on receipt fires `SendCustomModData` with no arguments | `SendCustomModData` (server) |

Notes, all [observed]:

- `transmitModData` does nothing if the object has no square.
- When a **client** sends an object or square, the server loads it into its own copy and **forwards it to the other
  relevant clients**, skipping the sender. For squares the server also fires `onLoadModDataFromServer(sq)` on its
  own side before forwarding.
- An object packet whose ModData is empty **wipes** the receiver's table; a non-empty one loads into it.
- If a client receives square data for a square that is not loaded yet, the packet is queued
  (`delayPacket`) and replayed later; if the square is out of bounds it is dropped.
- `GameServer.loadModData(sq)` has a vanilla-farming side effect: when the square's ModData has an `id` key and
  `remove` is absent or "false", it copies a fixed list of `planting:<id>:...` keys into the **game time** ModData
  table. Do not reuse a square ModData key named `id` unless you intend that. The same copy runs when the server
  receives a client's `ReceiveModData`.
- Items are found on the client by container plus item id; if no such item is found the packet is ignored.
- `SendCustomModData` is the hook a server mod uses to answer `getServerModData()`; it has no arguments and no
  requester, so a handler cannot tell who asked. No shipped Lua uses either `SendCustomModData` or
  `onLoadModDataFromServer`.
- The object ModData packet has special cases after loading: for an animal on a hook it notifies the hook, and for a
  dead body it invalidates the corpse (and reads an `animalRotStage` key when the body is an animal).

## 7. The global-object channel

The global-object systems (`SGlobalObjectSystem`, `CGlobalObjectSystem`, see
[`how-binding-works.md`](how-binding-works.md) for the exposed classes) use their own packet, `GlobalObjects`, with
a one-byte sub-type, **not** `ClientCommand`. They do not fire `OnClientCommand` or `OnServerCommand`. [observed]

| Sub-type | Direction | Contents |
|---|---|---|
| 1 server command | server to client | UTF system name, UTF command, hasArgs, table |
| 2 client command | client to server | **player index byte first**, then system name, command, hasArgs, table |
| 3 new object | server to client | system name, x, y, z, then the object's synced keys |
| 4 remove object | server to client | system name, x, y, z |
| 5 update object | server to client | system name, x, y, z, then the object's synced keys |

- **Lua entry points.** On the server `SGlobalObjectSystem:sendCommand(command, args)`; on the client
  `CGlobalObjectSystem:sendCommand(command, player, args)`. [observed]
- **Dispatch.** The receiver looks the system up by name and calls a function stored **in that system's own Lua
  table**. On the server that is `OnClientCommand`. On the client it is `OnServerCommand`, `newLuaObjectAt`,
  `removeLuaObjectAt` and `OnLuaObjectUpdated`. The system table is passed as the first argument. If the system is
  unknown, or `OnClientCommand`, `OnServerCommand` or `newLuaObjectAt` is missing, the Java side throws
  `IllegalStateException`, so register these functions before any traffic. The server system also looks up
  `OnChunkLoaded`, `getInitialStateForClient`, `OnIsoObjectChangedItself` and `OnModDataChangeItself` the same way
  (not traced further here). [observed]
- **Reach.** The server's send loops over all connections with no distance test, unlike the ModData packets. [observed]
- **Synced keys.** Object new/update packets carry only the keys registered in the system's `objectSyncKeys`
  set (written with `TableNetworkUtils.saveSome`); other keys on the object never reach the client. [observed]
- **Single player.** Both directions have loopback code paths: `SinglePlayerServer` and `SinglePlayerClient` each
  have a `GlobalObjects` case, and the server's send loops over the loopback connections. [observed]

## 8. Vanilla dispatch patterns (names only)

- **One handler per side, a table of commands.** The shipped server file `server/ClientCommands.lua` keeps a
  `Commands[module][command]` table and registers a single `OnClientCommand` handler that looks up and calls
  `Commands[module][command](player, args)`. The client file `client/ServerCommands.lua` does the same for
  `OnServerCommand` with `(args)`. The server file starts with an `isClient()` early return. [observed]
- **Lots of callers.** In the shipped `media/lua` (2026-10-24): `sendClientCommand` appears in 43 files (116
  lines), `sendServerCommand` in 22 files (30 lines), `OnClientCommand` in 11 files and `OnServerCommand` in 5 files
  (plain text matches; the event comparison's active-subscription counts are 7 and 3, see
  [`../data/vanilla-event-comparison.csv`](../data/vanilla-event-comparison.csv)). `transmitModData` appears in 23
  files, `syncItemModData` in 1. That comparison also lists `OnReceiveGlobalModData`, `SendCustomModData` and
  `onLoadModDataFromServer` with no vanilla subscription. [observed]
- **`LuaNet`.** `shared/Util/LuaNet.lua` is a small wrapper that routes through the command channel: it uses
  one fixed module name, uses the wrapper's own name as the command, and puts `{command, recipient, source, payload}`
  in `args`. On the server a package with a `recipient` is forwarded to that named player; otherwise it is passed to
  a registered handler. This is the vanilla way to do client to client messaging (section 4). [observed]
- **Extra handler parameters.** At least one vanilla handler (`forageServer.OnClientCommand`) declares a fifth
  parameter, `_clientID`. The Java side passes four values, so that parameter is nil. [observed]
- **An unexplained call.** `server/Foraging/forageServer.lua` calls a four-argument `sendServerCommand` with a
  string first, which matches no Java overload (the four-argument form takes a player first). What the game does
  with that call is **[unknown]**; do not copy it.

## 9. Pitfalls

1. **Args can be nil.** Empty or missing `args` arrives as nil, not `{}`.
2. **Silent type loss.** Passing a Java object (player, square, list) inside `args` drops it with no error when it is
   nested. Send ids or coordinates and look the object up on the receiver.
3. **A table is not a reference.** Each command rebuilds the table on the receiving side; items and bodies are
   copies or lookups.
4. **No reply.** If you need a result, send a second command and correlate with an id you put in `args`.
5. **Do not trust `player` or `args` on the server.** The player is the connection's own character, but all content
   is client-supplied and the only Java-side gate is `vehicle.remove`.
6. **`sendServerCommand` is a no-op on clients and single player; `sendClientCommand` throws on a server.** Write
   the side check first (`isClient()`, `isServer()`).
7. **Transmitting is explicit.** Editing a ModData table never syncs it. Call the matching transmit method, and
   remember that the global ModData receiver does not store what it receives.
8. **`ClientCommandFilter` is not a firewall.** It only trims the log.
9. **Global ModData `transmit` from the server goes to everyone, with no distance filter.** Object and square
   transmits are limited to relevant connections.

## 10. Choosing a path

| You want to | Use |
|---|---|
| ask the server to do something for a player | `sendClientCommand` to your module, handle in `OnClientCommand` |
| tell one player something | `sendServerCommand(player, ...)` |
| tell everyone | `sendServerCommand(module, ...)`, or global ModData `transmit` when it is state rather than an event |
| keep world-wide state across saves and sync it | global ModData (`getOrCreate` in `OnInitGlobalModData`, `transmit` after changes, `add` in `OnReceiveGlobalModData`) |
| sync a field on a placed object or square | edit its ModData, then `transmitModData` / `transmitModdata` |
| sync a field on an inventory item | edit its ModData, then `syncItemModData(player, item)` on the server |
| a per-player message through a shared module | the vanilla `LuaNet` pattern |

## 11. A minimal exchange (invented, not run in game)

The sample uses invented names and shows only the shape of a request and an answer. Put the first half in a
`client/` file and the second in a `server/` file.

```lua
-- client: ask, then listen for the answer
local function ask(player)
    sendClientCommand(player, "MyMod", "ping", { n = 1 })
end

Events.OnServerCommand.Add(function(module, command, args)
    if module ~= "MyMod" or command ~= "pong" or not args then return end
    print("answer", args.n)
end)

-- server: validate, answer the player who asked
Events.OnClientCommand.Add(function(module, command, player, args)
    if module ~= "MyMod" or command ~= "ping" or not args then return end
    local n = tonumber(args.n) or 0
    sendServerCommand(player, "MyMod", "pong", { n = n + 1 })
end)
```

In single player the `pong` never reaches the client (section 2.7); a mod that must work there has to call the
client logic directly.

## Open items

- **[unknown]** The exact set of value types `KahluaTable.save` accepts for ModData packets and the save file. It lives
  in the Kahlua library, which is not part of the game's `zombie/**` tree surveyed here.
- **[unknown]** The behaviour of `sendClientCommand` on a multiplayer client that is connected but not yet "in game"
  (section 2.2).
- **[unknown]** What the game does with the four-argument call in `forageServer.lua` (section 8).
- **[unknown]** How a Lua value is converted to each Java overload's parameter types when a global is called with
  mismatched or extra arguments. This is the carry-over from [`how-binding-works.md`](how-binding-works.md).
- **[unknown]** Whether multiplayer clients fire `OnInitGlobalModData` at the same point in the load as the server
  (section 5.2); the call site sits in `IsoWorld.init`, whose client behaviour is only partly traced in
  [`lifecycle.md`](lifecycle.md).
- **[unknown]** Delivery guarantees. Packets are declared with a priority and reliability value, but the mapping of
  those numbers to network behaviour was not decoded, so ordering between a command and a ModData packet is not
  claimed.
