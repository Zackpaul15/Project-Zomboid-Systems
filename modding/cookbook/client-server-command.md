# Recipe: send a client to server command

Survey date: 2026-10-24. Game build: Build 42 (jar sha256 prefix e1a69eb7; read-only Core source corroborates 42.21).
Tags: **[observed]** / **[inferred]** / **[unknown]**; every snippet is **[inferred]** (invented, not game code).

> **NOT RUNTIME-VERIFIED — no in-game smoke test was run.** Status: **untested**. Index: [README.md](README.md).

## Goal

From a client, send a small request to the server and handle it there, with an optional answer back.

## Prerequisites

Build 42; the skeleton from [README.md](README.md#common-setup-all-recipes); the mod enabled on **both** the client
and the server. Testing needs a multiplayer session (host or dedicated). Single player behaves differently, see
below. Background: [multiplayer.md](../lua-api/multiplayer.md).

## Files

```text
GuideCookbook/42/media/lua/client/GuideCookbookClient.lua
GuideCookbook/42/media/lua/server/GuideCookbookServer.lua
```

1. **Client** **media/lua/client/GuideCookbookClient.lua** [inferred snippet, shaped after the invented exchange in [multiplayer.md](../lua-api/multiplayer.md#11-a-minimal-exchange-invented-not-run-in-game)]:

   ```lua
   local function ask(player)
       sendClientCommand(player, "GuideCookbook", "ping", { n = 1 })
   end

   Events.OnServerCommand.Add(function(module, command, args)
       if module ~= "GuideCookbook" or command ~= "pong" or not args then return end
       print("GuideCookbook answer", args.n)
   end)

   -- trigger [inferred]: runs once each time the game starts, then sends the request
   Events.OnGameStart.Add(function()
       ask(getPlayer())
   end)
   ```

   `OnGameStart` is listed in [events.csv](../data/events.csv) and fires when the in-game state starts; the callback
   therefore runs once the player has loaded in. [inferred] An alternative trigger is a menu entry, see
   [context-menu-entry.md](context-menu-entry.md).

2. **Server** **media/lua/server/GuideCookbookServer.lua** [inferred snippet]:

   ```lua
   Events.OnClientCommand.Add(function(module, command, player, args)
       if module ~= "GuideCookbook" or command ~= "ping" or not args then return end
       local n = tonumber(args.n) or 0
       sendServerCommand(player, "GuideCookbook", "pong", { n = n + 1 })
   end)
   ```

What each piece is:

- The command channel is one packet type used in both directions. Client to server fires `OnClientCommand(module,
  command, player, args)` on the server; server to client fires `OnServerCommand(module, command, args)`
  ([multiplayer.md](../lua-api/multiplayer.md#1-the-four-paths-at-a-glance), rows in [events.csv](../data/events.csv)). [observed]
  The first two arguments are strings you choose; filter on your own module name first. [observed]
- There is no acknowledgement and no return value; a "response" is a second command you send yourself. [observed]
- `args` keeps only string or number keys and string, number, boolean, table, item, direction and dead-body values; other
  values (a player or square nested in the table) are silently dropped. Send ids or coordinates instead. [observed]
- Validate on the server: the player is the connection's own character but all content is client supplied. [observed]
- **Side checks.** `sendServerCommand` is a no-op on clients and in single player; `sendClientCommand` has two forms
  ([multiplayer.md](../lua-api/multiplayer.md) §2.2): the three-argument `(module, command, args)` form throws on a
  server, while the four-argument `(player, module, command, args)` form, used in the snippet above, sends from an
  in-game multiplayer client when the player is local; on a server it fires `OnClientCommand` locally without sending a
  packet. Code in the server Lua folder also runs on multiplayer clients, so guard with `isServer()` / `isClient()`
  ([lifecycle.md](../lua-api/lifecycle.md), [multiplayer.md](../lua-api/multiplayer.md)). [observed] The snippets above
  do not add guards; add them before shipping. [inferred]
- **Single player.** The client call loops back and `OnClientCommand` fires, but `sendServerCommand` does nothing, so
  the answer never arrives; a mod that must work there calls its client logic directly
  ([multiplayer.md](../lua-api/multiplayer.md)). [observed]
- `sendClientCommandV` and `sendServerCommandV` are variadic key/value forms ([multiplayer.md](../lua-api/multiplayer.md);
  global functions listed in [lua-globals.csv](../data/lua-globals.csv)). [observed]
- The server option `ClientCommandFilter` only changes what is logged, not what is delivered. [observed]

## Expected in-game result [inferred]

In a multiplayer session with the mod on both sides, calling `ask` on a client prints "GuideCookbook answer 2" in that
client's Lua output. In single player nothing is printed on the client (the server handler runs, the reply is dropped).
**[unknown]** What happens if the client sends before it is fully in game ([multiplayer.md](../lua-api/multiplayer.md#open-items)).

## See also

[multiplayer.md](../lua-api/multiplayer.md) · [events.md](../lua-api/events.md) · [lifecycle.md](../lua-api/lifecycle.md) ·
[context-menu-entry.md](context-menu-entry.md) (a way to trigger `ask`)
