# Java <-> native (JNI) boundary map

Survey date: 2026-10-25. Game build: Project Zomboid Build 42, `projectzomboid.jar` sha256 prefix `e1a69eb7`.
Scope: Java declarations and JVM descriptors under `zombie/**`, installed DLL names, and
[exposed classes](../modding/data/exposed-classes.csv). The [boundary table](../modding/data/native-boundary.csv)
records how Java reaches natives; native implementation behaviour remains unestablished.

## What the boundary is

- **[observed]** 392 `native` method declarations exist under `zombie/**`, in 26 top-level classes (none nested).
  This total includes wrapped declarations and equals the CSV row count.
- **[observed]** One more package outside `zombie/**` has natives: `fmod.javafmodJNI` (445 declarations, FMOD audio).
  It is out of scope for the CSV, which covers `zombie/**` only.
- **[observed]** No `native` declaration is a nested class member; all sit at class-member level of a top-level class.

## How a Java `native` becomes a DLL symbol

- **[inferred]** (JNI specification; DLL-specific behaviour unproven) `System.loadLibrary("X")` loads `X.dll` from the
  library path; the JVM then resolves each `native` method lazily on first call by looking up an export named
  `Java_<mangled fqcn>_<mangled method>`, with `.` -> `_`, `_` -> `_1`. Overloaded natives get a second form with
  `__<mangled arg descriptor>` appended. The `jni_signature` column is the JVM descriptor that fixes that overload.
- **[observed]** All natives here are plain `native` members; none is registered through a `RegisterNatives` table
  visible from Java. **[unknown]** whether a DLL registers some itself (needs the DLL).
- **[observed]** Many natives take `ByteBuffer` and primitive handles (`int`) rather than objects.
  **[inferred]** The DLL side keeps its own state keyed by integer ids (see `notes/population.md` for the PopMan case).

## loadLibrary -> DLL mapping

**[observed]** Names below are library names selected by the Java loaders. Loaders with a `zomboid.debuglibs.*`
check append a debug suffix `d` when the corresponding runtime property is `1`.
**[unknown]** Runtime property values are unknown; installed filenames do not establish those values.
**[inferred]** A load request identifies a candidate library, not proof that it implements a particular native.

| Java loader (class) | Library name | Present as DLL in install? |
|---|---|---|
| `zombie.core.znet.SteamUtils` | `steam_api64` | yes `steam_api64.dll` (Valve's SDK, no PZ natives) |
| `zombie.core.znet.SteamUtils` | `RakNet64` | yes `RakNet64.dll` |
| `zombie.core.znet.SteamUtils` | `ZNetJNI64` (steam) / `ZNetNoSteam64` (no steam) | yes, both |
| `zombie.network.FakeClientManager` | `RakNet64`, `ZNetNoSteam64` | yes |
| `zombie.popman.ZombiePopulationManager` | `PZPopMan64` | yes |
| `zombie.pathfind.nativeCode.PathfindNative` | `PZPathFind64` | yes |
| `zombie.core.physics.Bullet` | `PZBullet64`; `PZBulletNoOpenGL64` only for a Unix server | `PZBullet64.dll` yes; Unix-only alternative is n/a on Windows [observed] |
| `zombie.iso.LightingJNI`, `zombie.GameWindow` | `Lighting64` | yes |
| `zombie.vehicles.Clipper` | `PZClipper64` | yes |
| `zombie.core.textures.VideoTexture` | `bink2w64`, `bink64` (Windows); `Bink2x64` (Linux) | yes both Windows; `Bink2x64` n/a on Windows |
| `zombie.core.skinnedmodel.model.jassimp.JAssImpImporter` | `jassimp64` | yes `jassimp64.dll` (no `zombie/**` natives) |
| `fmod.javafmodJNI` | `fmod`, `fmodstudio`, `fmodintegration64` | yes, all three |
| `zombie.jsig`, `zombie.pzexe` | `pzexe_jni64` | **no**: `[unknown]`, not installed (launcher-side helper) |

- **[observed]** Linux/macOS branches load un-suffixed or `64` names with no `.dll`; they are irrelevant to this install.
- **[observed]** Install DLLs never loaded by any `loadLibrary` in the available Java declarations: `imgui-java64.dll`, `jnidispatch.dll`
  (likely loaded by their Java libraries' own extractors, **[unknown]**).
- **[unknown]** Which of the two ZNet DLLs holds a given `RakNetPeerInterface` / `RakVoice` / Steam* symbol (both are
  loaded in different modes). The CSV records `ZNetJNI64.dll|ZNetNoSteam64.dll` for all of them. `RakNet64.dll` is
  loaded first, but **[inferred]** it is the underlying RakNet library, not the JNI shim.
- **[inferred]** PhysicsDebugRenderer, ClipperOffset, ZombiePopulationRenderer/MPDebugInfo/DebugCommands,
  PathfindNativeRenderer have no loader of their own; they are mapped to the DLL of their sibling class in the same
  package. `MapCollisionData -> PZPopMan64.dll` is **[observed]** in `notes/population.md` /
  `notes/functions-popman.md` (exports in the PopMan DLL), the others are by package proximity only.
- **[unknown]** The Bink pair: natives of `VideoTexture` map to `bink64.dll|bink2w64.dll`; no PZ-specific wrapper DLL
  is installed, so the symbols may live in either (RAD ships these as the codec libraries).

## Per-DLL native counts (matches the CSV `dll` column exactly)

**[observed]** Counts below describe the CSV's candidate assignments; DLL ownership confidence is recorded separately.

| `dll` value | natives | classes |
|---|---:|---|
| `ZNetJNI64.dll\|ZNetNoSteam64.dll` | 140 | `RakNetPeerInterface` 30, `RakVoice` 22, `SteamWorkshop` 23, `SteamGameServer` 19, `SteamFriends` 14, `ServerBrowser` 11, `PortMapper` 10, `SteamUtils` 7, `ZNet` 2, `SteamUser` 1, `SteamRemotePlay` 1 |
| `PZBullet64.dll` | 98 | `Bullet` 93, `PhysicsDebugRenderer` 5 |
| `PZPopMan64.dll` | 59 | `ZombiePopulationManager` 28, `MapCollisionData` 17, `MPDebugInfo` 8, `ZombiePopulationRenderer` 5, `DebugCommands` 1 |
| `Lighting64.dll` | 50 | `LightingJNI` 50 |
| `PZClipper64.dll` | 19 | `Clipper` 13, `ClipperOffset` 6 |
| `PZPathFind64.dll` | 13 | `PathfindNative` 11, `PathfindNativeRenderer` 2 |
| `bink64.dll\|bink2w64.dll` | 11 | `VideoTexture` 11 |
| `[unknown]` | 2 | `pzexe.findJNI`, `jsig` (1 each; `pzexe_jni64` not installed) |
| **total** | **392** | |

## `dll_confidence` column

- **[observed]** `direct`: 197 rows whose class has its own library-loading code and whose candidate is not a pair.
  This records a load request, not verified symbol ownership. The two `jsig`/`pzexe` rows are `direct` even though
  their `dll` remains `[unknown]`: both request `pzexe_jni64`, which is absent from this Windows install.
- **[observed]** `observed`: 17 `MapCollisionData` rows, backed by the existing export evidence in
  `notes/population.md` and `notes/functions-popman.md`.
- **[inferred]** `inferred`: 27 rows assigned by sibling/package proximity: PhysicsDebugRenderer (5), ClipperOffset (6),
  ZombiePopulationRenderer (5), MPDebugInfo (8), DebugCommands (1), PathfindNativeRenderer (2).
- **[unknown]** `unknown`: 151 rows with unresolved ownership within a pair: networking (140) and VideoTexture/Bink (11).
- **[observed]** Own-class loading evidence covers 215 rows, overlapping the paired candidates for SteamUtils (7)
  and VideoTexture (11). Pair ambiguity takes precedence, so the four exclusive counts are 197 + 17 + 27 + 151 = 392.

## Lua reachability

- **[observed]** `lua_exposed = yes` rows: 0. A native is only `yes` if its class is in
  `modding/data/exposed-classes.csv` *and* the native itself is public. Two native-bearing classes are exposed
  (`ZombiePopulationRenderer`, `VideoTexture`), but every one of their natives is `private`, so these natives are not directly bound.
  **[observed]** Their public wrapper methods are what Lua sees.
- **[inferred]** `no` means "no direct path"; a Lua-callable Java wrapper can still reach a private native
  indirectly. Follow `java_caller` to find the wrapper.
- **[inferred]** Other classes with natives carry no `@UsedFromLua`; only exposure-list membership is established.
  Exposure through a base class or a global function would not be caught (**[unknown]**, none found).

## `java_caller` column

- **[inferred]** Heuristic text match, not a call graph. Static public natives: the other class with the most
  `Class.method(` hits. Otherwise the declaring class if it calls the method itself (typical private `n_*` wrapper
  pattern), otherwise a same-package or other class that mentions both the class name and `.method(`.
- **[observed]** 355 of 392 rows have a caller; 37 are `[unknown]` (no textual call found; they may be unused in this
  build, called via reflection, or called with an alias the heuristic misses). Concentrated in `Bullet` (16),
  `LightingJNI` (6), `RakVoice` (5), `RakNetPeerInterface` (3), `SteamFriends` (3).

## Using the CSV

- **[inferred]** To form an expected JNI export, escape literal underscores as `_1` in the class and method names,
  then replace class-name dots with `_`: `Java_<mangled class>_<mangled method>`. For overloaded natives append
  `__<mangled argument descriptor>` (excluding the return descriptor). For example, `zombie.MapCollisionData.n_init`
  gives `Java_zombie_MapCollisionData_n_1init`. This predicts a symbol name; its presence in a DLL remains unverified.
- The `dll` and `java_caller` columns associate candidate libraries with Java callers.
  Rows are sorted by class, method and signature.

## Confidence and limits

- **[observed]** The CSV contains 392 rows for the 392 native declarations under `zombie/**`.
- **[observed]** All 392 `jni_signature` values match the installed jar's JVM descriptors; native counts agree
  between the jar and Java declarations for every class.
- **[observed]** The confidence column preserves all six original CSV columns, including all 392 signatures.
- **[unknown]** Independent reproducibility of the updated confidence column remains UNVERIFIED.
