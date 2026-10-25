# Startup, load and reload lifecycle (Project Zomboid, Build 42)

Survey date: 2026-10-24. Source: Java declarations and control flow in `zombie/**` (`GameWindow`, `core.Core`, `Lua.LuaManager`,
`gameStates.*`, `iso.IsoWorld`, `network.GameServer`, `network.packets.*`, `SandboxOptions`). Order claims describe
control flow inside the named methods; runtime ordering is unverified. Tags: **[observed]**, **[inferred]**,
**[unknown]**. Event names, arguments and registration are in [`events.md`](events.md) and
[`../data/events.csv`](../data/events.csv). Sandbox values: [`sandbox-options.md`](sandbox-options.md).

## Short version

1. Boot loads **shared** then **client** Lua, then fires `OnLoadSoundBanks`, later `OnGameBoot`, then the menu fires
   `OnMainMenuEnter`.
2. The **server** Lua folder is loaded only when a world starts to load (`GameLoadingState`), not at boot.
3. `IsoWorld.init` fires the world events in a fixed order (table below); `OnGameTimeLoaded` comes after it returns,
   then `OnCreatePlayer`, then `OnGameStart` and `OnLoad`.
4. Leaving the game, or changing mods, **wipes the Lua state and reloads everything**, so `OnGameBoot` fires again.
   Mod top-level code and `Events.X.Add` calls run again each time; do not keep state in Java-side singletons you
   expect to survive.

## Lua file load order [observed]

`LuaManager.LoadDirBase(sub)` is the only place mod and vanilla Lua files are run (apart from `require` and
`dofile`-style calls made by Lua itself).

- For one folder name (`shared`, `client` or `server`) it collects `.lua` files from the game's `media/lua/<sub>/`
  tree. Paths are stored lower-cased and relative to their root.
- It then collects the same folder from every active mod, in `ZomboidFileSystem.getModIDs()` order. For each mod the
  **common** directory is searched first and then the **version** directory; that mod's list is sorted
  case-insensitively.
- The game list is sorted case-insensitively, the mod lists are appended after it (not merged into it). Every vanilla
  file therefore runs before any mod file of the same folder, and mods run in mod order.
- A relative path is run once. The absolute file comes from `ZomboidFileSystem.getAbsolutePath(rel)`, a lookup in a
  map keyed by the lower-cased relative path, so a mod file with exactly the same relative path as a vanilla file is
  expected to **replace** that vanilla file (run at the vanilla file's position). [inferred: the map's filling order was
  not read; later mods winning is the likely rule]
- Because everything is sorted by path, ordering inside a folder is alphabetical, not by dependency. Use `require`
  for load-order dependencies. [inferred from the sort; `require` itself not traced here]
- A file is run at most once per Lua environment. `LuaManager.RunLua` keeps a set of loaded names; asking again
  returns the first run's return value (this is what `require` relies on). A file that is already being loaded and is
  requested again produces a "recursive require()" warning and returns nothing. [observed]
- A failing file does **not** stop the folder. [observed in `RunLuaInternal`]
  - Missing file: the error is logged and the file is skipped.
  - Syntax or compile error: logged as "Error found in LUA file"; the file is skipped and is not marked loaded.
  - Runtime error in top-level code: logged with the Lua stack trace; the part that ran stays in effect, the file is
    marked loaded, and its return value is nil.
  - Every run clears the Lua function and table lookup caches and marks several data definitions (craft recipes,
    attached-weapon, default-clothing, hair-outfit, underwear and zombie-zone definitions) as needing a refresh.

| Entry point | Folders run | Notes |
|---|---|---|
| `LoadDirBase()` (no argument) | `shared`, then `client` | boot (`GameWindow`), reload (`Core.ResetLua`), return to menu (`IngameState.exit`); starts by resetting the net checksum |
| `LoadDirBase("server")` | `server` | called in `GameLoadingState.enter` for every world load, including multiplayer clients |
| dedicated server startup | `shared`, `client` (checksum only), `server` | the `client` folder is **not run** on a dedicated server, only hashed |

## Net checksum [observed]

On a client or dedicated server, each Lua file visited by `LoadDirBase` is added to a checksum (`NetChecksum`), except
a file whose name contains `SandboxVars.lua`. `LuaManager.finishChecksum` stores the digest (`GameServer.checksum` or
`GameClient.checksum`) and stops further additions. [observed] The comparison between client and server happens in
the connection code, which was not traced; the usual consequence is that mods must match between client and server.
[inferred]

## Timeline: single player [observed order]

Times are the order of the calls, not wall-clock.

| # | Where | What happens | Events fired |
|---|---|---|---|
| 1 | `GameWindow.init` | Translations, fonts; `LuaManager.init` (builds the Lua environment); `GameWindow.initShared` (creates the custom-sandbox and custom-perk registries and reads mod `sandbox-options.txt` files) | none |
| 2 | `GameWindow.init` | `LoadDirBase()`: all `shared` then all `client` Lua, then `ZomboidGlobals.Load` | `OnLoadSoundBanks` |
| 3 | `GameWindow.enter` (runs after `init`; after model, depth-texture and voice set-up) | | `OnGameBoot` |
| 4 | `MainScreenState.enter` | main menu appears | `OnMainMenuEnter` |
| 5 | user picks New Game or Continue | menu Lua (`MainScreen.lua`, `SandboxOptions.lua`, `ServerSettingsScreen.lua`) builds the save and sets sandbox values | UI events only |
| 6 | `GameLoadingState.enter` | `LoadDirBase("server")`, `finishChecksum`, `ScriptManager.LoadedAfterLua`; creates the new `GameTime`, `ClimateManager`, `IsoWorld` instances | `OnPreMapLoad` (fired before `IsoWorld.init` is called) |
| 7 | `IsoWorld.init` | see the next table | many |
| 8 | back in `GameLoadingState` | `SGlobalObjects.initSystems`, `CGlobalObjects.initSystems`, tutorial set-up | `OnGameTimeLoaded` |
| 9 | `GameLoadingState.exit` | `UIManager.init` | `OnCreatePlayer` (args: player index `0`, the player object) |
| 10 | `IngameState.enter` | music state, first climate update | `OnGameStart`, then `OnLoad` |
| 11 | game loop | per-tick and render events (`OnTick`, `OnRenderTick`, ...) | see `events.md` |

Rows 8 and 9 were ordered from the positions of the event calls inside `GameLoadingState`; other work between them was
not catalogued.

### Inside `IsoWorld.init` [observed order]

| Step | Call | Event fired | Notes |
|---|---|---|---|
| 1 | world and save-file set-up, `createWorld` for a new save, object-ID and area managers loaded | | |
| 2 | loot-distribution merge hooks | `OnPreDistributionMerge`, `OnDistributionMerge`, `OnPostDistributionMerge` | all three fire back to back, before the Java side parses the distributions |
| 3 | | `OnInitWorld` | |
| 4 | `SandboxOptions.instance.load()` | | **only when this is not a multiplayer client** |
| 5 | `ItemPickerJava.Parse`, `InitSandboxLootSettings` | | loot tables are parsed after sandbox values are known |
| 6 | tile definition files read (property strings, then definitions) | `OnLoadedTileDefinitions` (arg: the sprite manager) | |
| 7 | weather mask, regions, `GameTime.init` + `load`, fog | | `handleOldZombiesFile2` runs just before `GameTime` |
| 8 | `ZomboidRadio.Init` | `OnLoadRadioScripts` (args: radio script manager, new-save flag) | |
| 9 | `GlobalModData.init` | `OnInitGlobalModData` (arg: new-game flag) | |
| 10 | `WorldDictionary.init`, `ScriptManager.PostWorldDictionaryInit` | | item and entity IDs become stable here |
| 11 | `ClimateManager.init` | | |
| 12 | map zones | `OnLoadMapZones`, `OnLoadedMapZones` | |
| 13 | collision data, cell and chunk loading (cell loader fires `OnPostMapLoad` per loaded cell) | `OnPostMapLoad` (args: cell, world x, world y) | repeated while chunks load |
| 14 | new save only: player placement, poisonous berry and mushroom picks (not on a client) | `OnNewGame` (args: player, square) | fired once per newly created player |
| (any) | erosion season set-up (`ErosionMain`) | `OnInitSeasons` (arg: season object) | position inside the sequence not traced |

**Consequences for a mod [inferred from the order above]:**

- `Events.OnGameBoot` handlers run before any world exists: `getWorld()`, the player, `ModData` and `SandboxVars`
  values of a specific save are not yet meaningful. `SandboxVars` then holds the **preset defaults**
  (`Apocalypse`), plus any custom options.
- `OnInitWorld` fires before `SandboxOptions.instance.load()` on a non-client. A single-player continue of a
  *Sandbox*-mode save has already read the save's options earlier (`MainScreen.lua` calls
  `loadCurrentGameBinFile` on the Continue path), so the value is normally right; do not rely on it for other
  routes. [observed that the call exists; "normally right" is inferred]
- `OnGameTimeLoaded`, `OnCreatePlayer` and later events see the loaded sandbox values.
- `OnNewGame` runs only for a new character in a new world; it does not run on Continue. [observed condition
  structure; the exact predicate was not read]
- `OnPostMapLoad` fires many times; keep the handler cheap.
- `OnLoad` and `OnGameStart` are fired back to back from `IngameState.enter`, each with no arguments; there is no
  separate signal for "first frame".

## Timeline: multiplayer client [observed call sites, order partly inferred]

Boot is the same as single player. The differences:

- `GameLoadingState.enter` calls `LoadDirBase("server")` as well, so a client runs the game's and mods' `server`
  folder too. [observed] Code in `media/lua/server` is therefore not server-only; guard with `isServer()`,
  `isClient()` as the vanilla scripts do.
- The client connects before the world loads: `GameClient.instance.init()` runs inside `GameLoadingState.enter`.
  `OnConnected` fires from `ConnectToServerState.receiveWorldDictionary`, when the world dictionary arrives from the
  server. [observed]
- `IsoWorld.init` **skips** `SandboxOptions.instance.load()`. Sandbox values come from the server
  (`GameClient.receiveSandboxOptions` loads, applies and calls `toLua`). [observed] When exactly that packet arrives
  relative to the events above is **[unknown]**.
- `OnGameTimeLoaded` has two call sites that a client can reach: the connection packet that carries the server's
  `GameTime` (`ConnectedPacket`) and `GameLoadingState` after `IsoWorld.init`. A handler may therefore run twice on a
  client. [inferred from both call sites; not confirmed at runtime]
- `OnNewGame` is guarded by "not a client" only for the berry and mushroom set-up; the event itself is called for a
  client's new player as well. [observed]

## Timeline: dedicated server [observed order]

`GameServer.doMinimumInit` then `startServer`:

1. `CustomSandboxOptions` init (reads mod `sandbox-options.txt`), `ModRegistries.init`, `ScriptManager.Load`, clothing
   and model set-up.
2. Lua: `initChecksum`; `LoadDirBase("shared")`; `LoadDirBase("client", true)` (**checksum only**); `LoadDirBase("server")`;
   `finishChecksum`; `ScriptManager.LoadedAfterLua`.
3. Sandbox: if `<cacheDir>/Server/<serverName>_SandboxVars.lua` exists it is loaded (the server **exits** on a load
   error); then `handleOldServerZombiesFile`, `saveServerLuaFile` (writes the file back, creating it on first run) and
   `toLua`. If the file is missing, the same last three steps still run.
4. `OnGameBoot` fires after the sandbox file handling, after the word filter loads, so `SandboxVars` is already filled
   from the server file when server `OnGameBoot` handlers run. [observed order]
5. World creation runs `IsoWorld.init` (same table as above) and then `OnGameTimeLoaded` fires from `GameServer`.
6. `startServer` fires `OnServerStarted` once networking is up.
7. `OnServerStartSaving` fires when the server receives the start-pause packet used for saves
   (`StartPausePacket`). `OnSave` / `OnPostSave` fire from the shared save code. [observed sites]

`OnMainMenuEnter`, `OnCreatePlayer`, `OnGameStart` and `OnLoad` are fired only by client-side state classes
(`MainScreenState`, `GameLoadingState`, `IngameState`), so a dedicated server does not fire them. [inferred from the
firing classes]

## Saving [observed]

`GameWindow.save(boolean)` is the save routine. It does nothing when saving is disabled, when there is no current
cell, or in the LastStand and Tutorial game modes. It has two branches, and each fires `OnSave` once:

- Normal branch: writes `map_ver.bin`, then `map_sand.bin` (via `SandboxOptions.save`), the world-gen parameters,
  the instance and meta trackers and the statistics, and **then** fires `OnSave`. A sandbox value a mod changes inside
  an `OnSave` handler is therefore not in that save's `map_sand.bin`. [observed order]
- Client-save branch (a multiplayer client with the client-save flag set): saves the world map items and the visited
  map data, then fires `OnSave`; the files above are not written here. [observed]

`OnPostSave` is fired by the callers (`GameWindow` and `IngameState`) after `save` returns, only if the current cell
exists. [observed]

## Reload paths: why `OnGameBoot` fires again [observed]

| Path | Trigger | What is reset | Events after reload |
|---|---|---|---|
| `Core.ResetLua(activeMods, reason)` | mod list changed in the menu; `Core.DelayResetLua` queues it and `MainScreenState` runs it on its next tick | body locations, container overlays, fences, tile overlays, Lua hooks, perks, custom and built-in sandbox options, world map, animal and migration definitions are reset; `LuaManager.init` creates a **new** Lua environment; the file system and mod list are re-read (`loadMods`); translations, custom perks and custom sandbox options are re-initialised; scripts are reloaded (`ScriptManager.Load`); models, hair, outfits and similar tables are rebuilt; `LoadDirBase()` reloads `shared` and `client` | `OnGameBoot`, `OnMainMenuEnter`, `OnResetLua(reason)` |
| `IngameState.exit` (back to the main menu) | leaving a game | the same kind of reset as above (scripts, clothing and hair tables, sounds, perks, hooks, overlays, both sandbox classes), the file system is reset and `loadMods("default")` re-reads the mod list for the mod set named `default` (also the name the one-argument `ResetLua(boolean, ...)` overload uses; that this equals the player's menu selection is [inferred]), translations and scripts are reloaded, custom sandbox options are re-initialised, then `LuaManager.init` and `LoadDirBase()` | `OnGameBoot` only (`OnMainMenuEnter` comes from `MainScreenState.enter` afterwards) |

After a reload the Lua globals, every `Events.X.Add` registration and every table a mod built are gone and rebuilt by
the files running again. `SandboxOptions.Reset` removes custom sandbox options and `CustomSandboxOptions.Reset` clears
their list; both are rebuilt by the init pair, so each reload re-reads every mod's `sandbox-options.txt`.

Failure handling: in `ResetLua` a thrown error while reloading prints a "Reloading Lua - ERRORS!" loading text and
pauses about two seconds before continuing. [observed]

## Open items

- **[unknown]** Which events can fire on which side. The firing class is known (table above); the Lua-visible
  `isClient()`/`isServer()` answer per event was not enumerated.
- **[unknown]** What `triggerEventGarbage` and `triggerEventUnique` change at run time (covered in `events.md`).
- **[unknown]** Conversion rules for arguments between Java and Lua values (boxing of numbers, strings).
- **[unknown]** The position of `OnInitSeasons` inside `IsoWorld.init` and whether the client or the server fires it.
- **[unknown]** The moment the client receives the server's sandbox options relative to the events in the multiplayer
  section.
