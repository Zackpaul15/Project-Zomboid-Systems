# Project Zomboid reverse-engineering notes

Target: `<game install>` (Build 42 era: entity components, imgui-java, basements).

## Survey (2026-10-24) — [observed] unless tagged

- Engine is Java: `projectzomboid.jar` (65.7 MB, sha256 `e1a69eb7...a33`, 23,829 classes, 24,697 files).
  Main class `zombie.gameStates.MainScreenState` (jar manifest and `ProjectZomboid64.json`). Multi-Release jar.
- Game code is in `zombie/*` (~5.5k classes); the rest is bundled libraries (Guava, BouncyCastle, JNA, Jackson,
  LWJGL, Javacord, Trove, OSHI, Prometheus, ZXing, Kotlin, Vavr).
- Largest game packages by class count: core 733, iso 628, network 601, scripting 385, characters 321,
  entity 300, util 201, audio 164, randomizedWorld 157, worldMap 146, vehicles 145, pathfind 123, ai 119.
- Native side (Windows DLLs): `PZBullet64`, `PZPathFind64`, `PZPopMan64`, `PZClipper64`,
  `RakNet64`, `ZNetJNI64`/`ZNetNoSteam64`, `Lighting64`, `ProjectZomboid64.exe` (launcher only).
- Content: Lua in `media/lua`, scripts in `media/scripts`, anim/models/maps under `media/`.

## Java and native boundary

- The jar's classes are class-file major 69 (Java 25).
- Java coverage: zombie.ai (99 files), zombie.pathfind (90), zombie.popman (22).
- Native libraries are loaded by name (`PZPathFind64`, `PZPopMan64`) via `System.loadLibrary`.

## Notes index

- [notes/population.md](notes/population.md) - virtual/real zombie handover, native popman JNI, config keys.
- [notes/pathfinding.md](notes/pathfinding.md) - Java<->native pathfinder interface, `findPath` buffer layout,
  native internals.
- [notes/zombie-ai.md](notes/zombie-ai.md) - group manager, idle/lunge states, constants.
- [notes/functions-popman.md](notes/functions-popman.md) - `PZPopMan64.dll` function map: proposed names, JNI exports, layout.
- [notes/functions-pathfind.md](notes/functions-pathfind.md) - `PZPathFind64.dll` function map: proposed names by subsystem.
- [modding/README.md](modding/README.md) - entry point to the Lua-modding reference (Lua API, script formats, vanilla
  Lua library, workflow, tables); [modding/cookbook/](modding/cookbook/README.md) is the practical starting point
  (recipes are untested).
- Open questions are listed at the end of each note (native search function, density curve, remaining states).
