# Project Zomboid reverse-engineering notes

Target: `F:\SteamLibrary\steamapps\common\ProjectZomboid` (Build 42 era: entity components, imgui-java, basements).

## Survey (2026-10-24) — [observed] unless tagged

- Engine is Java: `projectzomboid.jar` (65.7 MB, sha256 `e1a69eb7...a33`, 23,829 classes, 24,697 files).
  Main class `zombie.gameStates.MainScreenState` (jar manifest and `ProjectZomboid64.json`). Multi-Release jar.
- Game code is in `zombie/*` (~5.5k classes); the rest is bundled libraries (Guava, BouncyCastle, JNA, Jackson,
  LWJGL, Javacord, Trove, OSHI, Prometheus, ZXing, Kotlin, Vavr).
- Largest game packages by class count: core 733, iso 628, network 601, scripting 385, characters 321,
  entity 300, util 201, audio 164, randomizedWorld 157, worldMap 146, vehicles 145, pathfind 123, ai 119.
- Native side (Windows DLLs, Ghidra-analysable): `PZBullet64`, `PZPathFind64`, `PZPopMan64`, `PZClipper64`,
  `RakNet64`, `ZNetJNI64`/`ZNetNoSteam64`, `Lighting64`, `ProjectZomboid64.exe` (launcher only).
- Content: Lua in `media/lua`, scripts in `media/scripts`, anim/models/maps under `media/`.

## REA notes

- REA opens the jar as an archive (`open_binary`, `inspect_artifact`) but cannot decompile Java bytecode with the
  providers configured here (Ghidra only; JEB/IDA/Kuna not set up). `extract_artifact` timed out on this jar.
- Workaround used: unzip into a scratch folder outside the project; JDK 21 (`tools\jdk`) gives `javap`.
- Per project rules, game files/extracted classes are NOT copied into this folder.

## Decompilers (set up 2026-10-24)

- Installed in `C:\Users\zackp\Documents\Code stuff\tools\decompilers\`: `vineflower-1.12.0.jar` (primary) and
  `cfr-0.152.jar` (second opinion; 2021 release). Run with `tools\jdk` (JDK 21).
- The jar's classes are class-file major 69 (Java 25); both decompilers read them under JDK 21.
- Example: `java -jar vineflower-1.12.0.jar <extracted>\zombie\ai <out_dir>` (output kept outside the project).
- Decompiled so far (Vineflower, no failure markers): zombie.ai (99 files), zombie.pathfind (90), zombie.popman (22).
- Native libs are loaded by name (`PZPathFind64`, `PZPopMan64`) via `System.loadLibrary`.
- REA sessions for `PZPathFind64.dll` and `PZPopMan64.dll` (Ghidra) were used and then closed; re-open with
  `open_binary` when continuing.

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
- [modding/SCOPE.md](modding/SCOPE.md) - Lua-modding reference repo: scope, work packages and the Claude/Codex split
  ([AGENTS.md](AGENTS.md) is the Codex brief).
- Open questions are listed at the end of each note (native search function, density curve, remaining states).
