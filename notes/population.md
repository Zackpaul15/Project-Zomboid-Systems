# Zombie population (zombie.popman + PZPopMan64.dll)

Confidence tags: **[observed]** directly supported by Java/native structure or data flow, **[inferred]** deduced from
structure or names, **[unknown]** unresolved. Scope: `zombie.popman` (22 classes) and
`PZPopMan64.dll` (sha256 `5b2e3ef5...0ec6`, x86-64, PDB name `PZPopMan64.pdb` referenced
but not loaded). No game code is copied here; names and shapes only.

Function-level names and address ranges: [functions-popman.md](functions-popman.md).

## Architecture

- **[observed]** `ZombiePopulationManager` (Java) is a thin driver over the native DLL. Zombies out of the
  player's loaded area are *virtual* (native-side records); zombies near players are real `IsoZombie` objects.
- **[observed]** Handover Java -> native happens when a chunk unloads (`removeChunkFromWorld`): each live,
  non-reanimated-player zombie is passed to `n_addZombie` (x, y, z, direction ordinal byte, persistent outfit id,
  packed state flags, path target x/y, persistentId) and removed from the world. Dead zombies are just `die()`d.
- **[observed]** A zombie that is on z=0, outdoors, and in `WalkTowardState` or `PathFindState` is virtualized
  *with* its path target (it keeps walking toward it); all others get `Integer.MIN_VALUE` targets (stationary).
- **[observed]** Native -> Java: the native side produces "add zombie" records read through
  `getAddZombieCount` / `getAddZombieData` (direct ByteBuffer). Per-record layout for `updateMain` consumers:
  x, y, z (floats), dir (byte), descriptorID, state, pathTargetX, pathTargetY, persistentId (ints).
- **[observed]** `n_updateMain(multiplier float, worldAgeHours double)` runs each tick; the native side keeps a
  "time changed" bit when either value differs from last call (`+0x3c |= changed`). Then it drains a ring of
  work objects (pool capped at ~50 retained, 0x110-byte objects) and publishes them to a result vector.
  [inferred] this is the producer/consumer transfer to the worker thread that runs `n_updateThread`.
- **[observed]** `n_updateRealZombies` / `packRealZombies` send Java's real zombies to native as parallel arrays
  (2 ints per zombie: persistentId + state; 3 floats: position). Zombies with `persistentId == 0` are counted as
  unregistered; reanimated players and dead zombies are skipped.

## Native JNI surface (all in `PZPopMan64.dll`)

| JNI | Address | Notes |
|---|---|---|
| `n_addZombie` | 0x180026d70 | register a virtual zombie [observed signature] |
| `n_loadedAreas` | 0x180027f20 | up to 64 rects (x,y,w,h), clamped 1..128 (Java side) |
| `n_spawnHorde` | 0x1800288f0 | **[observed]** appends a 0x1c-byte record (7 x 32-bit: spawnX, spawnY, spawnW, spawnH, targetX, targetY, count) to a growable queue at manager+0xc8..0xd0; processed later on the worker thread |
| `n_updateMain` | 0x1800289e0 | see above |
| `n_updateRealZombies` | 0x180028d30 | |
| `n_updateThread` | 0x1800290f0 | worker-thread step [behaviour unresolved] |
| `n_worldSound` | 0x1800291d0 | **[observed]** allocates a 0x28-byte sound event (x, y, radius, volume) and appends it to a pending-sounds vector at manager+0xd8..0xe0 |
| `n_config*`, `n_init`, `n_setOutfitNames`, `n_setSpawnOrigins`, `n_loadChunk`, `n_save`, `n_saveCell`, `n_registerZombie`, `n_releaseZombie`, `n_aggroTarget`, `n_shouldWait`, `n_readyToPause`, `n_stop`, radar/`hasDataForThread` | | behaviour unresolved |

- **[observed]** The DLL keeps a global manager pointer via a pointer table (`PTR_DAT_18012f058 + 0x90`); every
  JNI entry dereferences it with no null check in the ones read (spawnHorde, worldSound, updateMain).
  [inferred] calling them before `n_init` would crash the process rather than throw.
- **[observed]** `PZPopMan64.dll` also hosts `zombie.MapCollisionData` natives (`init`, `pathTask`,
  `chunkUpdateTask`, `squareUpdateTask`, `initMetaCell/Chunk/Grid`, `setGameState`, `save`, ...), a wall-following
  path engine used for virtual zombies (`mcd::IPathResult`). Renderer/debug natives:
  `ZombiePopulationRenderer`, `MPDebugInfo`, `DebugCommands.n_debugCommand`.

## Sound -> zombies (Java side)

- **[observed]** `addWorldSound` is ignored on clients, ignored for radius < 50, for zombie-sourced sounds, and for
  sounds without `stressZombies`.
- **[observed]** Radius is multiplied by `WorldSoundManager.getHearingMultiplier(lore.hearing)`; hearing values 4
  and 5 are remapped to 2 first. Result is `ceil(radius * mult)`, then `n_worldSound(x, y, radius, volume)`.

## Configuration keys pushed to native (`onConfigReloaded`)

All **[observed]** both as Java call sites and as strings in the DLL (`0x1800f9c08..0x1800f9d18`):

| Key | Type | Java source |
|---|---|---|
| `PopulationMultiplier` | float | `zombieConfig.populationMultiplier` |
| `PopulationStartMultiplier` | float | `zombieConfig.populationStartMultiplier` |
| `PopulationPeakMultiplier` | float | `zombieConfig.populationPeakMultiplier` |
| `PopulationPeakDay` | int | `zombieConfig.populationPeakDay` |
| `RespawnHours` | float | `zombieConfig.respawnHours` |
| `RespawnUnseenHours` | float | `zombieConfig.respawnUnseenHours` |
| `RespawnMultiplier` | float | `zombieConfig.respawnMultiplier` |
| `RedistributeHours` | float | `zombieConfig.redistributeHours` |
| `FollowSoundDistance` | int | `zombieConfig.followSoundDistance` |
| `MinZombiesPerChunk` / `MaxZombiesPerChunk` | float | `setZombiesMin/MaxPerChunk` (map/Lua driven) |
| `UniformZombiesPerChunk` | float | hard-coded `0.2` in Java |

Native class names recovered from RTTI [observed]: `popman::RepopulateTask` (with `FloodFill`, `FloodFill<8>`
variants), `popman::FloodFillOneChunk`, `popman::VirtualZombiePool`, `popman::ZombiePool`,
`popman::DebugCmd` (`SpawnTimeToZero`, `ClearZombies`, `SpawnNow`), `ObjectPool<Zombie*>`,
`ObjectPool<VirtualZombie*>`.
[inferred] Repopulation is a flood fill over chunks that decides where new zombies may spawn, run as a
background task; the debug commands force the respawn timer / clear / spawn immediately.

## Unknowns / next steps

- **[unknown]** How the native density curve combines Start/Peak multiplier and PeakDay (needs `n_updateThread`
  and the identified `RepopulateTask` behaviour).
- **[unknown]** Exact meaning of `FollowSoundDistance` and `RedistributeHours` in the native code.
- **[unknown]** Native save format (`n_save`, `n_saveCell`) and the persistentId allocation scheme.
