# PZPopMan64 native export inventory

Survey date: 2026-10-25. Game build: Project Zomboid Build 42; `projectzomboid.jar` SHA256 prefix `e1a69eb7` [observed in R0].
Target: `F:\SteamLibrary\steamapps\common\ProjectZomboid\PZPopMan64.dll`, 1,303,040 bytes [observed].
DLL SHA256: `5b2e3ef5d383c5e5e6fecf49afd514b196617925c1a0e3623bf0e7917a010ec6` [observed].

## Boundary

**[observed]** This x86-64 Windows DLL supplies export-name matches for all 59 declarations attributed to it in
[R0](native-boundary.md). The population manager's loader provides R0's direct attribution for its own methods;
the other classes retain R0's original observed/inferred confidence values.
**[inferred]** Names suggest population, collision-grid/navigation-task and debug/renderer bridges, rather than a
population-only library. Names alone do not establish implementation behaviour.

## Export totals and join

- **[observed]** The PE export directory contains 59 address-table slots and 59 named exports: 59 literal
  `Java_*` JNI names, 0 non-`Java_*` names, 0 C++-decorated names, 0 forwarded exports,
  0 unnamed live slots and 0 zero-target slots. All 59 target addresses match Ghidra-recognized functions.
- **[observed]** All 59 R0 declarations resolve to distinct exported symbols. Unresolved declarations: **none**.
  Exports without an R0 declaration: **0**. CSV totals equal both `NumberOfFunctions=59` and `NumberOfNames=59`.
  The export directory byte length is 3,924, not a count of symbols.
- **[observed]** Expected names escape literal underscores as `_1`, replace class dots with underscores, and join
  `Java_<class>_<method>`. Five `MapCollisionData.n_setGameState` overloads require the long form:
  append `__` and the mangled argument descriptor, escaping `;` as `_2`, `[` as `_3` and `/` as `_`.
  For example, `n_setGameState` with descriptor `(Ljava/lang/String;D)V` matches
  `Java_zombie_MapCollisionData_n_1setGameState__Ljava_lang_String_2D`.
  The CSV intentionally repeats `class.method` for those five rows; their exact export names distinguish them.
- **[observed]** CSV confidence is copied unchanged from R0: 28 direct, 17 observed and 14 inferred.
  Export presence provides new name evidence for the inferred assignments without changing the R0 input.

| R0 class [observed] | Declarations / resolved [observed] | Copied confidence [observed] |
|---|---:|---|
| zombie.popman.ZombiePopulationManager | 28 / 28 | direct |
| zombie.MapCollisionData | 17 / 17 | observed |
| zombie.popman.MPDebugInfo | 8 / 8 | inferred |
| zombie.popman.ZombiePopulationRenderer | 5 / 5 | inferred |
| zombie.popman.DebugCommands | 1 / 1 | inferred |
| **Total** | **59 / 59** | |

**[observed]** Reconciliation hook 1: **PZPopMan64.dll really hosts all 17 MapCollisionData entries**.
Examples are `Java_zombie_MapCollisionData_n_1init` at `0x180023dc0`,
`Java_zombie_MapCollisionData_n_1pathTask` at `0x1800242d0`, and the five long-form
`n_1setGameState__*` entries at `0x1800244a0/0x180024720/0x1800249a0/0x180024c50/0x180025110`.
The evidence is the export table, not an inference from the DLL filename.

**[observed]** Reconciliation hook 2: the older [population notes](population.md) explicitly say
“PZPopMan64.dll also hosts zombie.MapCollisionData natives”; this inventory confirms that attribution.
The DLL SHA256 in [functions-popman.md](functions-popman.md) matches exactly.
Its grouped MapCollisionData range `0x180023b00–0x180025580`, debug entry `0x180022cb0`,
population-manager addresses and renderer range `0x18002acd0–0x18002b030` agree with the current exports.
**[observed]** No conflicting DLL attribution or disproved exported entry was found in those two bounded surface tables.
Neither older table claims an exhaustive export total, so its abbreviated listing is not a competing count of 59.

**[observed]** The older function map labels entries as “Java native” and shortens, for example,
`MPDebugInfo.getLoadedAreasData`; its actual native/export spellings are `MPDebugInfo.n_getLoadedAreasData` /
`Java_zombie_popman_MPDebugInfo_n_1getLoadedAreasData` at `0x1800255a0`.
Likewise, the grouped `MapCollisionData` names omit `n_`, and literal `n_config*` is a family abbreviation,
not an export named with an asterisk. This CSV's exact PE spellings are authoritative for symbol lookup.
**[observed]** The function map's “4286 internal procedures” is an analysis-procedure count, not a PE-export count;
the proposed internal names such as `ReadCellFile` do not occur among these 59 named exports.

**[observed]** The old documents do disagree on coverage wording: the function map says
“all 790 were decompiled and triaged”, while population.md marks `n_updateThread` “[not decompiled]”.
**[unknown]** This inventory cannot adjudicate historical decompilation coverage or the older behaviour claims;
neither coverage statement is evidence against the observed `n_1updateThread` export at `0x1800290f0`.
No function bodies were opened in R7.

## Resolved JNI exports by feature area

**[inferred]** Classification uses names only. MapCollisionData takes the collision/nav category; renderer and MP/debug
classes take their corresponding categories. Manager radar methods join debug queries. Manager add/aggro/getAdd/register/release,
outfit/spawn-origin, horde and real-zombie-update names form add/spawn/registration; its other methods form state/config.
**[observed]** Each matched export is counted once; counts sum to 59.

| Feature area [inferred] | Exports [observed] |
|---|---:|
| Population-manager state/configuration and lifecycle | 15 |
| Add/spawn and registration | 10 |
| Collision-grid and navigation-task methods | 17 |
| Debug/repopulation-info and radar queries/commands | 12 |
| Renderer and wall-follower debug controls | 5 |
| **Total** | **59** |

## What a modder can act on

**[observed]** The installed DLL contains concrete function exports for the Java declarations `n_configFloat`,
`n_spawnHorde`, `n_registerZombie`, `n_pathTask`, `n_getRepopEventData` and `n_setDebugOption`,
among the 59 matched entries. R0 records `lua_exposed=no` for all 59.
**[inferred]** These are entry points for a later bounded implementation trace; the filename does not justify excluding
MapCollisionData from that work. **[unknown]** This inventory does not establish Lua/mod reachability, valid arguments,
safe lifecycle or an operation's actual gameplay effect.

## Verification and regeneration

- **[observed]** One PZPopMan64.dll session completed Ghidra 12.1.4 default auto-analysis. The complete export directory
  was read through REA `read_bytes` at `0x180125e80` (image base `0x180000000`, RVA `0x125e80`, 3,924 bytes).
  Evidence: `ev_14165348ca28560701f613ca9449515098bc345b294677649e31b6ba8e12ac4a`.
- **[observed]** The independent fallback used a separate PowerShell PE parser over the source DLL: DOS/PE headers,
  section-based RVA-to-file translation, export name pointers, ordinal indices and target RVAs.
  Directory file offset: `0x125280`. It independently enumerated all 59 names.
  Comparing sets gave **0 Ghidra-only and 0 source-only names**; every ordinal and target RVA also agreed.
  The Ghidra directory bytes additionally matched the source-directory read.
- **[observed]** Requested-reader limitation: `pe_exports.py` was not found in recursive searches of
  `C:\Users\zackp\.agents\skills` and `C:\Users\zackp\.codex\skills`; no `windows-binary-re` directory was found
  at those skill roots. Shell `python` discovery returned no executable; the attempted Python313 `-I --version`
  executable was not found, and the tested pz-work venv path did not exist.
  **[unknown]** The specifically requested Python-reader comparison remains **UNVERIFIED**; the brief-authorized
  hand-verification fallback was used rather than claiming that script ran.
- **[observed]** Ghidra's procedure-name inventory independently recognized all 59 exact names at their exported addresses.
  Evidence: `ev_1f0027b0f19e46f97d9543ff1d37d1b2de4629ec874b945708ba8a70181e2ae8`.
  Three randomly selected names were also re-read through `list_names`:
  `Java_zombie_popman_ZombiePopulationManager_n_1stop` (`0x1800289d0`),
  `Java_zombie_popman_MPDebugInfo_n_1hasData` (`0x180025ec0`), and
  `Java_zombie_popman_ZombiePopulationRenderer_n_1setWallFollowerStart` (`0x18002afe0`); all matched.
- **[observed]** CSV file-generation iteration count: **2**. First generation used Ghidra's enumeration; the CSV
  was deleted and regenerated using the independent PowerShell enumeration. First SHA256:
  `f5ae3018d26ba9812d0a386395f0a4a38cbd758cd6763cf04f9cdfc50e9b2f7a`.
  Second SHA256: `f5ae3018d26ba9812d0a386395f0a4a38cbd758cd6763cf04f9cdfc50e9b2f7a`.
  Outputs are byte-identical, sorted in ordinal string order, with the exact six requested columns and LF endings.
- **[observed]** Manual-edit disclosure: all four R7 repository edits were assembled through the hand-verification fallback:
  the CSV from the in-memory join, this original notes document, one appended HANDOFF line and one README index row.
  No persistent Python generator was created under the four-path ownership constraint.
- **[observed]** Explicit retained bundle `r7-popman-evidence.json` and snapshot `r7-popman-snapshot.json` were saved
  under `C:\Users\zackp\Documents\Code stuff\tools\pz-work\codex-scratch\`; `close_binary` completed.

## Limits

- **[observed]** Only PZPopMan64.dll was selected as an analysis target. This pass reads exported names/function addresses,
  without decompiling any function body or executing the target. No game code, bodies, disassembly or bytes entered the repo.
- **[unknown]** Behaviour, argument meaning, units, valid ranges, side effects, nested/indirect calls, runtime registration,
  actual invocation and script-value effects were not determined. The older behavioural notes were not revalidated.
- **[unknown]** `pe_exports.py` itself could not be run; a coordinator rerun is needed to close that specific tool-method gap.
  The independently implemented PowerShell name-set comparison did pass.
- **[observed]** An actual `%TEMP%\rea-ghidra-f1ab7b91ca375631454038812e563f9e` directory was visible during this
  session, timestamped at the session's analysis start (2026-10-25 13:33:42 local).
  Attempts to enumerate its contents/read `ghidra.log` were denied.
  **[inferred]** It is the matching REA ephemeral root; **[unknown]** exact project/log contents and per-target attribution
  could not be independently verified because of access denial. Internal scratch-only placement is **UNVERIFIED**;
  the visible Temp location is outside the requested scratch root. Explicit retained artifacts use scratch.
