# Lighting64 native export inventory

Survey date: 2026-10-25. Game build: Project Zomboid Build 42, `projectzomboid.jar` sha256 prefix `e1a69eb7` [observed in R0].
Target: `F:\SteamLibrary\steamapps\common\ProjectZomboid\Lighting64.dll`, 609,280 bytes [observed].
DLL SHA256: `1866188d8e253de521ba208f06f1db9b9019f333162ff3c31dd83506fafee773` [observed].

## Boundary

**[observed]** This x86-64 Windows shared library exports the Java lighting entry points catalogued in
[R0](native-boundary.md). R0 attributes 50 declarations in `zombie.iso.LightingJNI` to `Lighting64.dll`,
all with `dll_confidence=direct`, based on the Java loader boundary. Every declaration now has an export-name match.
**[inferred]** The names identify a bridge for lighting, visibility and streamed world updates; names alone do not establish behaviour.

## Export totals and join

- **[observed]** The PE export directory has 50 address-table slots and 50 named exports, with no unnamed live slots,
  zero targets or forwarded exports. All 50 target addresses correspond to Ghidra-recognized functions.
- **[observed]** All 50 names start with `Java_`; other forms: **0**. The CSV follows
  [R1](bullet-native.md): literal `Java_` prefix means `is_jni=yes`; `kind=function` requires a recognized function
  at the exported address.
- **[observed]** R0 assigns exactly 50 declarations to this DLL, all in `zombie.iso.LightingJNI`.
  All 50 resolve to distinct exported names; unresolved declarations: **none**.
  Exports without an R0 declaration: **0**; unmatched `Java_*` exports: **0**.
- **[observed]** The CSV copies R0's confidence values: 50 `direct`. No `[none]` or `[n/a]` rows are needed.
- **[observed]** Expected names were formed by escaping literal underscores as `_1` in class and method identifiers,
  replacing class-name dots with underscores, and joining `Java_<class>_<method>`.
  `zombie.iso.LightingJNI.getCouldSee` matches `Java_zombie_iso_LightingJNI_getCouldSee`.
  None of these 50 declarations shares a class/method name with an overload, so no descriptor suffix was needed.
  All names were joined against the R0 declarations, rather than inferred from a Ghidra name search alone.
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
entry points in this installed DLL. **[inferred]** These names are starting points for a later implementation trace.
**[unknown]** This inventory does not establish usable mod routes or safe parameter changes; export presence
alone does not establish the operation suggested by a method name.

## Verification and regeneration

- **[observed]** One DLL session and one Ghidra 12.1.4 default auto-analysis pass completed. Export data was read through
  REA's Ghidra `read_bytes` at image base `0x180000000`: directory RVA `0x8d4d0`, length 2,684 bytes.
  The read was complete. Directory Evidence: `ev_68fdc583f0f6598241681f16554112c1c3c822d80543d1b8568a644cd133f35c`.
- **[observed]** An independent PowerShell source-file read located the export directory at file offset `0x8bad0`
  by parsing the PE section headers. Source bytes and Ghidra's initialized directory bytes matched completely.
  Separately enumerating each directory produced the same 50 exact names, ordinals and target RVAs.
  The independent route shares the small in-memory directory decoder, but not Ghidra's loader or memory read.
- **[observed]** Ghidra's procedure search independently recognized all 50 export names at their export-table addresses.
  Evidence: `ev_918d802cdc799e8947140be82dba8c5cb78ef448d16a2277e99de2923b6cc0a7`.
- **[observed]** Three randomly selected names were rechecked against the source-file table and separately through
  Ghidra `list_names`: `Java_zombie_iso_LightingJNI_chunkEndUpdate` (`0x1800133c0`),
  `Java_zombie_iso_LightingJNI_chunkBeginUpdate` (`0x1800131f0`) and
  `Java_zombie_iso_LightingJNI_getCouldSee` (`0x180013c50`). All matched exactly as imported function symbols.
- **[observed]** CSV generation iteration count: **2**. The first used the Ghidra directory enumeration; after
  deleting the CSV, the second used the independently read source-file enumeration. Both files had SHA256
  `bc941d091c411a76a53cac8ae3901d84b7067027c224748714cea2075af89c3b`.
  Regeneration sorts exact names in ordinal string order, joins expected JNI names to R0, copies R0 confidence,
  and writes the requested six columns with LF line endings. Fixed notes identify matched JNI exports.
  No generator script was added outside this task's two owned repository paths.
- **[observed]** Retained Evidence and snapshot were saved under
  `C:\Users\zackp\Documents\Code stuff\tools\pz-work\codex-scratch\` as `r4-lighting-evidence.json` and
  `r4-lighting-snapshot.json`; `close_binary` completed.
  **[unknown]** REA's internal ephemeral project/log location was not exposed or selectable through these calls;
  placement of those internal intermediates under the requested scratch root is **UNVERIFIED**.

## Limits

- **[observed]** This pass inventories exported names and their function addresses; it does not decompile function bodies
  or execute the DLL. Only `Lighting64.dll` was opened.
- **[unknown]** Behaviour, argument meaning, units, valid ranges, side effects, and the effect of changing a script value
  are not established by this pass; those require implementation evidence.
- **[unknown]** Nested calls, indirect calls, runtime registration, and whether a matched entry point is ever invoked
  are unproven. Export presence does not prove a useful implementation or a reachable mod API.
