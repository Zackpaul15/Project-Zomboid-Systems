# PZPopMan64.dll function map

Companion to [population.md](population.md). Names below are **proposed** (the DLL ships without a loaded PDB, so
only JNI exports and CRT symbols carry real names). Tags: **[observed]** read in decompiled output, **[inferred]**
deduced from structure, strings or callers, **[unknown]** not read. No game code is reproduced here.

- Binary: `PZPopMan64.dll`, sha256 `5b2e3ef5d383c5e5e6fecf49afd514b196617925c1a0e3623bf0e7917a010ec6`, x86-64, MSVC (VS2019 STL).
- 4286 internal procedures. **790** sit in the game-code range `0x180001000`-`0x18002b030`; all 790 were decompiled and
  triaged. Everything from `0x18002b080` up is CRT / STL / regex / locale and is only grouped (last section).
- Ghidra renames made through REA are ephemeral, so this file is the durable record. Re-apply with
  `set_addresses_names` if a fresh session is opened.
- Coverage: the entries below are the functions whose role I could establish. The remaining game-range functions are
  STL template instantiations (vector / deque / hash map / pool helpers) and small accessors; they are grouped by
  range in "Address-range map".

## Address-range map (game range)

| Range | Contents | Tag |
|---|---|---|
| `0x180001000`-`0x180004414` | static initialisers, global ctors (MT19937 seeded at `0x180002b80`) | [observed] |
| `0x180004414`-`0x180008880` | STL container / allocator instantiations | [inferred] |
| `0x180008000`-`0x18001dxxx` | population logic: cell files, chunk data, repopulation, flood fill, virtual zombies | [observed] |
| `0x18001e000`-`0x180022fff` | save/load of virtual-zombie and id files, population thread loop | [observed] |
| `0x180022cb0`-`0x18002b030` | JNI exports and debug renderer | [observed] |

## Core functions

| Address | Proposed name | Purpose | Tag |
|---|---|---|---|
| `0x180002b80` | `SeedMT19937` | seeds the Mersenne-Twister used for spawn rolls (constant `0x9908b0df` nearby) | [observed] |
| `0x1800096a0` | `ReadCellFile` | reads `zpop_<y>_<x>.bin`, file versions 1..7 | [observed] |
| `0x18000a430` | `WriteCellFile` | writes the same file (current version) | [observed] |
| `0x18000f5b0` | `ReadChunkData` | reads map-collision `chunkdata_*` file | [observed] |
| `0x180010840` | `WriteChunkData` | writes it | [observed] |
| `0x18001ddc0` | `CreateWorldSoundEvent` | builds the 0x28-byte sound event used by `worldSound` | [observed] |
| `0x18001d5e0` | `MergeWorkObjectIntoManager` | merges a handed-over 0x110-byte work object into manager state | [observed] |
| `0x18001dfc0` | `LoadVirtualZombiesFile` | loader for `zpop_virtual.bin` | [observed] |
| `0x18001e780` | `LoadZombieIdsFile` | loader for `zpop_ids.bin` | [observed] |
| `0x18001e9e0` | `ApplyConfigMapToManager` | applies the config key/value map (`PopulationMultiplier` etc.) to manager fields | [observed] |
| `0x18001f180` | `PopThread_PeriodicTask` | task run every 300000 ms on the population thread | [observed] (what it computes: [inferred] redistribute / respawn bookkeeping) |
| `0x18001faa0` | `SaveVirtualZombiesFile` | writer for `zpop_virtual.bin` | [observed] |
| `0x180020080` | `SaveZombieIdsFile` | writer for `zpop_ids.bin` (`.tmp` then rename) | [observed] |
| `0x1800203a0` | `PopThread_ProcessSpawnHordeRecord` | consumes one 28-byte spawnHorde record | [inferred] |
| `0x18001c260` | `PopThread_ReprocessWorldSound` | re-processes a sound event (every 5000 ms) | [inferred] |
| `0x1800218e0` | `PopThread_UpdateCycle` | thread-side update: pop ring, merge, config, hordes, per-cell update, ageing (>2000 ms idle cells), sounds (>1000 ms expiry), real-zombie positioning, snapshots | [observed] |
| `0x1800228d0` | `BuildZombieIdsFilename` | builds the `zpop_ids.bin` path | [observed] |
| `0x180023930` | `PopLog` | logger (level, std::string) | [observed] |

## JNI exports

All [observed] (named by the DLL's export table).

| Address | Java native |
|---|---|
| `0x180022cb0` | `DebugCommands.n_debugCommand` |
| `0x180023b00`-`0x180025580` | `MapCollisionData` natives: `chunkUpdateTask`, `hasDataForThread`, `init`, `initMetaCell/Chunk/Grid`, `pathTask`, `save`, `setGameState` (D/F/I/String/Z), `shouldWait`, `squareUpdateTask`, `stop`, `update` |
| `0x1800255a0` / `0x1800258e0` / `0x180025c50` | `MPDebugInfo.getLoadedAreasData` / `getLoadedCellsData` / `getRepopEventData` |
| `0x180026d70` | `ZombiePopulationManager.n_addZombie` |
| `0x180026e60` | `n_aggroTarget` |
| `0x180026f10` / `0x180027040` / `0x180027290` | `n_config` / `n_configFloat` / `n_configInt` |
| `0x180027420` / `0x180027430` | `n_getAddZombieCount` / `n_getAddZombieData` |
| `0x180027aa0` | `n_getRadarZombieData` |
| `0x180027c40` / `0x180027e10` | `n_hasDataForThread` / `n_hasRadarData` |
| `0x180027e20` | `n_init` |
| `0x180027e70` / `0x180027f20` | `n_loadChunk` / `n_loadedAreas` |
| `0x180028170` | `n_readyToPause` |
| `0x180028190` / `0x180028280` | `n_registerZombie` / `n_releaseZombie` |
| `0x180028320` | `n_requestRadarData` |
| `0x180028340` / `0x180028350` | `n_save` / `n_saveCell` |
| `0x180028370` / `0x180028760` | `n_setOutfitNames` / `n_setSpawnOrigins` |
| `0x1800288e0` / `0x1800288f0` | `n_shouldWait` / `n_spawnHorde` |
| `0x1800289d0` / `0x1800289e0` | `n_stop` / `n_updateMain` |
| `0x180028d30` / `0x1800290f0` | `n_updateRealZombies` / `n_updateThread` |
| `0x1800291d0` | `n_worldSound` |
| `0x18002acd0`-`0x18002b030` | `ZombiePopulationRenderer` natives (`setDebugOption` at `0x18002ad50`) |

## Manager object layout (partial)

Object at `*(PTR_DAT_18012f058) + 0x90`. [observed] unless noted.

| Offset | Field |
|---|---|
| `+0x30` | world age (double) |
| `+0x38` | time multiplier (float) |
| `+0x3c` | "time changed" flag |
| `+0x42` / `+0x44` | pause byte / next 5-minute tick (int64) [inferred meaning] |
| `+0x48` | spawn-group list |
| `+0x60` | registered-zombie hash map |
| `+0xc8/0xcc/0xd0` | spawnHorde queue (28-byte records) |
| `+0xd8/0xdc/0xe0` | pending worldSound events |
| `+0x140` | object pool |

## Boilerplate (not documented per function)

| Range | Contents |
|---|---|
| `0x18002b080` upward | CRT startup, UCRT, MSVC STL (string, vector, deque, unordered_map, ios/iostream, locale, regex), exception types |
| RTTI classes present [observed] | `popman::DebugCmd`, `popman::RepopulateTask` (+`FloodFill`), `popman::FloodFillOneChunk`, `popman::VirtualZombiePool`, `popman::ZombiePool`, `ObjectPool<>`, `mcd::IPathResult` |
