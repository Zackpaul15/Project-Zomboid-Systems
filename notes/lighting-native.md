# Lighting64 native export inventory

Survey date: 2026-10-25. Game build: Project Zomboid Build 42, `projectzomboid.jar` sha256 prefix `e1a69eb7` [observed].
Target: `<game install>\Lighting64.dll`, 609,280 bytes [observed].
DLL SHA256: `1866188d8e253de521ba208f06f1db9b9019f333162ff3c31dd83506fafee773` [observed].

## Boundary

**[observed]** This x86-64 Windows shared library exports the Java lighting entry points catalogued in
[native boundary survey](native-boundary.md). The native boundary survey attributes 50 declarations in `zombie.iso.LightingJNI` to `Lighting64.dll`,
all with `dll_confidence=direct`, based on the Java loader boundary. Every declaration now has an export-name match.
**[inferred]** The names identify a bridge for lighting, visibility and streamed world updates; names alone do not establish behaviour.

## Export totals and join

- **[observed]** The PE export directory has 50 address-table slots and 50 named exports, with no unnamed live slots,
  zero targets or forwarded exports. All 50 target addresses correspond to recognized functions.
- **[observed]** All 50 names start with `Java_`; other forms: **0**. The CSV follows
  [Bullet export inventory](bullet-native.md): literal `Java_` prefix means `is_jni=yes`; `kind=function` requires a recognized function
  at the exported address.
- **[observed]** The native boundary survey assigns exactly 50 declarations to this DLL, all in `zombie.iso.LightingJNI`.
  All 50 resolve to distinct exported names; unresolved declarations: **none**.
  Exports without a native boundary survey declaration: **0**; unmatched `Java_*` exports: **0**.
- **[observed]** The CSV copies the native boundary survey's confidence values: 50 `direct`. No `[none]` or `[n/a]` rows are needed.
- **[observed]** Expected names were formed by escaping literal underscores as `_1` in class and method identifiers,
  replacing class-name dots with underscores, and joining `Java_<class>_<method>`.
  `zombie.iso.LightingJNI.getCouldSee` matches `Java_zombie_iso_LightingJNI_getCouldSee`.
  None of these 50 declarations shares a class/method name with an overload, so no descriptor suffix was needed.
  All export names match declarations in the native boundary survey.
- **[observed]** The CSV row total of 50 agrees with both PE count fields (`NumberOfFunctions=50`,
  `NumberOfNames=50`). The export data-directory byte length is **2,684**, not a symbol count.

## Resolved JNI exports by feature area

**[inferred]** Areas classify names, not verified behaviour. Each matched export is counted once: light-source
add/remove/set methods and `updateTorch`; chunk-prefixed methods plus `getChunkDirty`; square-prefixed methods
plus `getSquareDirty` and `getSquareLighting`; remaining getters; `playerSet`, scrolling and teleport;
then remaining update/bridge methods. **[observed]** Counts total 50.

| Feature area [inferred] | Exports [observed] |
|---|---:|
| Light sources, room lights and torches | 10 |
| Chunk updates and dirty query | 6 |
| Square updates and lighting queries | 11 |
| Visibility, room and light queries | 9 |
| Player state, scrolling and teleport | 6 |
| State updates, synchronization and bridge | 8 |
| **Total** | **50** |

## What a modder can act on

**[observed]** Java declarations including `addLight`, `addRoomLight`, `updateTorch`, `getSquareLighting`,
`getCanSee`, `squareSetLightTransmission`, `configure` and `teleport` have concrete exported function
entry points in this installed DLL. **[inferred]** The named entries are potential Java/native integration points.
**[unknown]** This inventory does not establish usable mod routes or safe parameter changes; export presence
alone does not establish the operation suggested by a method name.

## Confidence and limits

- **[observed]** The PE export directory has image base `0x180000000`, RVA `0x8d4d0` and length 2,684 bytes.
- **[observed]** Its file offset is `0x8bad0`; the file and loaded directory agree on all 50 exact names, ordinals and target RVAs.
- **[observed]** All 50 export names correspond to recognized functions at their export-table addresses.
- **[observed]** `Java_zombie_iso_LightingJNI_chunkEndUpdate` is at `0x1800133c0`.
- **[observed]** `Java_zombie_iso_LightingJNI_chunkBeginUpdate` is at `0x1800131f0`.
- **[observed]** `Java_zombie_iso_LightingJNI_getCouldSee` is at `0x180013c50`.
- **[observed]** The CSV has six columns, exact names in ordinal string order, the native boundary survey's confidence
  values, and notes identifying matched JNI exports.
- **[unknown]** The agreement between file and loaded directories is not independent of their shared directory interpretation.
- **[unknown]** This inventory establishes exported names and function addresses, without establishing function-body
  behaviour, argument meanings, units, valid ranges, side effects or script-value effects.
- **[unknown]** Nested calls, indirect calls, runtime registration and actual invocation remain unproven.
  Export presence does not prove a useful implementation or a reachable mod API.
