# Lua events (Project Zomboid, Build 42)

Survey date: 2026-10-24. Source: decompile of `zombie/**` (`zombie.Lua.LuaEventManager`, `zombie.Lua.Event`,
`zombie.Lua.LuaManager`) and a scan of the vanilla `media/lua` tree. Names and shapes only. Tags: **[observed]**,
**[inferred]**, **[unknown]**.

Full table: [`../data/events.csv`](../data/events.csv) (275 rows; regenerate with
`modding/tools/extract_events.py`). Columns: `event`, `registered`, `reg_index`, `methods`, `arg_counts`,
`trigger_classes`, `sample_args`, `lua_trigger_files`.

## Mechanism [observed]

- A mod subscribes with `Events.<Name>.Add(fn)` and unsubscribes with `Events.<Name>.Remove(fn)`. `Events` is a global
  table with one entry per event; each entry has `Add` and `Remove` Java functions. Callbacks are kept in order of
  subscription and run in that order.
- `LuaEventManager.AddEvents()` registers **262 event names** at startup (each as `AddEvent("<Name>")`), creating the
  `Events.<Name>` entries. Duplicate registrations collapse.
- Java fires an event with `LuaEventManager.triggerEvent("<Name>", arg1, ...)`. There are overloads for 0 to 8
  arguments (the Lua global `triggerEvent` has its own overloads), and `triggerEventGarbage` / `triggerEventUnique` variants that
  differ in how argument boxing and queuing are handled. Arguments are passed to every callback unchanged.
- Each callback runs through a protected call: an error in one Lua callback is logged and does not stop the other
  callbacks. [observed that calls are protected; exact logging not read]
- Events fired from a non-main thread are queued and run later on the main thread (`RunQueuedEvents`). [observed]
- Lua can fire any event, registered or not, with the global `triggerEvent(name, ...)` (`LuaManager.GlobalObject`).
  Vanilla Lua uses this for its own events (for example the context-menu events below).
- An event name that is triggered or subscribed to but was never registered is **created on demand**; the
  subscription still works once something fires that name. [inferred from the add-on-miss path]

## Counts [observed, this build]

| Measure | Count |
|---|---|
| Names registered in `AddEvents()` | 262 |
| Registered and fired from Java at least once | 211 |
| Registered, never fired from Java | 51 |
| of those, fired from vanilla Lua through `triggerEvent` (comments excluded) | 16 |
| of those, with **no** live trigger in Java or vanilla Lua | 35 |
| Fired from Java but not registered | 13 |
| Argument count per Java-fired event: 0 / 1 / 2 / 3 / 4 or more / mixed between sites | 48 / 76 / 46 / 31 / 20 / 3 (max 7) |

Notes on the findings:

- The 35 events with no live trigger anywhere are vestigial or reserved: `OnDusk`, `OnDawn`, `OnChangeWeather`
  (their only `triggerEvent` calls in `server/Seasons/season.lua` sit inside `--[[ ]]` block comments), `OnPreGameStart`, `OnRenderUpdate`,
  `OnNPCSurvivorUpdate`, `OnAddBuilding`, `OnMakeItem`, `OnLoginState`, `OnLoginStateSuccess`,
  `OnCharacterCreateStats`, `OnDoTileBuilding`, `OnNewSurvivorGroup`, `OnPlayerSetSafehouse`, the `OnPost*Draw`
  family (`OnPostFloorSquareDraw`, `OnPostTilesSquareDraw`, `OnPostTileDraw`, `OnPostWallSquareDraw`,
  `OnPostCharactersSquareDraw`), `OnMapLoadCreateIsoObject`, `OnCharacterMeet`, `OnAIStateExecute`,
  `OnAIStateEnter`, `OnAIStateExit`, `OnIsoThumpableLoad`, `OnIsoThumpableSave`, `OnRainStart`, `OnWorldMessage`,
  `OnRadioInteraction`, `SyncFactionServer`, `OnBeingHitByZombie`, `OnServerStatisticReceived`,
  `OnMovingObjectCrop`, `OnOverrideSearchManager`, `OnServerCustomizationDataReceived`. Subscribing to them
  is harmless but the callback never runs in the base game. [observed that no static trigger exists; a mod or a
  path that builds the name at runtime could still fire one, and `LuaManager` does fire by dynamic name]
- Registered events fired only from Lua include `OnFillInventoryObjectContextMenu`, `OnFillWorldObjectContextMenu`,
  `OnPreFillInventoryObjectContextMenu`, `OnPreFillWorldObjectContextMenu`, `OnRefreshInventoryWindowContainers`,
  `OnSpawnRegionsLoaded`, `OnChallengeQuery` and the foraging/skill/item
  definition hooks (`preAddForageDefs`, `onAddForageDefs`, `preAddSkillDefs`, `preAddZoneDefs`, `preAddCatDefs`,
  `preAddItemDefs`, `onFillSearchIconContextMenu`, `onUpdateIcon`). The arguments are whatever the Lua caller passes.
- Triggered but unregistered (13): `OnExitVehicle`, `OnUseVehicle`, `OnForagePool`, `OnForageRequestZone`,
  `OnForageSpot`, `OnSteamFriendStatusChanged`, `OnSteamWorkshopItemCreated`, `OnSteamWorkshopItemNotCreated`,
  `OnSteamWorkshopItemNotUpdated`, `OnSteamWorkshopItemUpdated`, `GrappleGrabCollisionCheck`, `GrapplerLetGo`,
  `OnDesignationZoneUpdatedNetwork`. Because unknown names are auto-created, these work; they are simply not in
  the registration list.

Correction (C1-FIX1): an earlier revision counted commented-out Lua `triggerEvent` calls (the two Lua-related rows above
were 19 / 32, now 16 / 35; three comment-only events had been misfiled as Lua-fired). The extractor now strips `--` line comments and
`--[[ ]]` / `--[==[ ]==]` block comments before matching. Known limit [unknown]: comment forms built by string
concatenation or generated code, and `triggerEvent` text inside `[[ ]]` long strings, are not handled. The J1
key-coverage `defect` count dropping to 0 after this lands is expected, not a regression.

## Choosing an event (common ones) [observed]

Arguments below are the Java call-site expressions; the names are the game's local variable names and are a hint
for what each value is, not a documented contract.

| Event | Fired from (class) | Arguments |
|---|---|---|
| `OnGameBoot` | `GameWindow`, `Core` | none |
| `OnMainMenuEnter` | `MainScreenState`, `Core` | none |
| `OnGameTimeLoaded` | `GameLoadingState`, `GameServer` | none |
| `OnInitWorld`, `OnLoadMapZones`, `OnPreDistributionMerge`, `OnDistributionMerge`, `OnPostDistributionMerge` | `IsoWorld` | none |
| `OnInitGlobalModData` | `GlobalModData` | `isNewGame` (boolean) |
| `OnSGlobalObjectSystemInit`, `OnCGlobalObjectSystemInit` | `SGlobalObjects`, `CGlobalObjects` | none |
| `OnGameStart`, `OnLoad` | `IngameState` | none |
| `OnNewGame` | `IsoWorld`, `LuaManager` | `playerObj`, `square` |
| `OnCreatePlayer` | `GameLoadingState`, others | `playerIndex`, `player` |
| `OnCreateLivingCharacter` | `IsoPlayer`, `IsoSurvivor` | `character`, `descriptor` |
| `OnTick` | `IngameState` | tick counter (number) |
| `OnPlayerUpdate`, `OnPlayerMove` | `IsoPlayer` | `player` |
| `OnZombieUpdate` | `IsoZombie` | `zombie` |
| `OnZombieDead`, `OnCharacterDeath`, `OnPlayerDeath` | `IsoGameCharacter`, `IsoZombie`, `IsoPlayer` | `character` |
| `EveryOneMinute`, `EveryTenMinutes`, `EveryHours`, `EveryDays` | `GameTime` | none |
| `OnWeaponSwing` | `SwipeStatePlayer` | `player`, `weapon` |
| `OnPlayerAttackFinished` | `SwipeStatePlayer` | `owner`, `weapon` |
| `OnWeaponHitCharacter` | `IsoGameCharacter` | `wielder`, `target`, `weapon`, `damage` |
| `OnHitZombie` | `IsoZombie` | `zombie`, `wielder`, `bodyPart`, `weapon` |
| `OnEquipPrimary` | `IsoGameCharacter` | `character`, `item` |
| `OnClothingUpdated` | `IsoGameCharacter` and others | `character` |
| `LoadGridsquare` | `IsoChunk` | `square` |
| `OnObjectAdded` | `AddItemToMapPacket` and others | `object` |
| `OnKeyPressed`, `OnCustomUIKey` | `GameKeyboard`, `UIManager` | key code |
| `OnPreUIDraw`, `OnPostUIDraw`, `OnRenderTick`, `OnCreateUI` | `UIManager`, `GameWindow` | none |
| `OnClientCommand` | `GameServer`, `LuaManager`, SP path | `module`, `command`, `player`, `args` (table) |
| `OnServerCommand` | `GameClient`, SP path | `module`, `command`, `args` (table) |
| `OnConnected`, `OnDisconnect`, `OnServerStarted`, `OnSteamGameJoin` | network classes | none |
| `OnReceiveGlobalModData` | `GlobalModDataPacket` | `tag`, `data` |
| `OnAIStateChange` | `StateMachine` | `owner`, `current`, `previous` |
| `OnEnterVehicle` | `IsoCell`, `BaseVehicle` | `character` |
| `OnResetLua` | `Core` | `reason` |

For the full set with sample argument expressions and trigger classes, filter `../data/events.csv`.

## Gaps [unknown]

- Whether each event fires on the client, the server, or both in multiplayer: the trigger class hints at it (for
  example `GameServer` vs `GameClient`) but a per-event side assignment is not established. See the multiplayer
  doc when it exists.
- The exact semantics of `triggerEventGarbage` / `triggerEventUnique` (which events use them is in the CSV's
  `methods` column; four rows do).
- Event ordering at game start across client and server Lua loads.
