# PZPopMan64 native export inventory

Survey date: 2026-10-25. Game build: Project Zomboid Build 42; `projectzomboid.jar` SHA256 prefix `e1a69eb7` [observed].
Target: `<game install>\PZPopMan64.dll`, 1,303,040 bytes [observed].
DLL SHA256: `5b2e3ef5d383c5e5e6fecf49afd514b196617925c1a0e3623bf0e7917a010ec6` [observed].

## Boundary

**[observed]** This x86-64 Windows DLL supplies export-name matches for all 59 declarations attributed to it in
[native boundary survey](native-boundary.md). The population manager's loader provides the native boundary survey's direct attribution for its own methods;
the other classes retain the native boundary survey's original observed/inferred confidence values.
**[inferred]** Names suggest population, collision-grid/navigation-task and debug/renderer bridges, rather than a
population-only library. Names alone do not establish implementation behaviour.

## Export totals and join

- **[observed]** The PE export directory contains 59 address-table slots and 59 named exports: 59 literal
  `Java_*` JNI names, 0 non-`Java_*` names, 0 C++-decorated names, 0 forwarded exports,
  0 unnamed live slots and 0 zero-target slots. All 59 target addresses match recognized functions.
- **[observed]** All 59 native boundary survey declarations resolve to distinct exported symbols. Unresolved declarations: **none**.
  Exports without a native boundary survey declaration: **0**. CSV totals equal both `NumberOfFunctions=59` and `NumberOfNames=59`.
  The export directory byte length is 3,924, not a count of symbols.
- **[observed]** Expected names escape literal underscores as `_1`, replace class dots with underscores, and join
  `Java_<class>_<method>`. Five `MapCollisionData.n_setGameState` overloads require the long form:
  append `__` and the mangled argument descriptor, escaping `;` as `_2`, `[` as `_3` and `/` as `_`.
  For example, `n_setGameState` with descriptor `(Ljava/lang/String;D)V` matches
  `Java_zombie_MapCollisionData_n_1setGameState__Ljava_lang_String_2D`.
  The CSV intentionally repeats `class.method` for those five rows; their exact export names distinguish them.
- **[observed]** CSV confidence is copied unchanged from the native boundary survey: 28 direct, 17 observed and 14 inferred.
  Export presence provides new name evidence for the inferred assignments without changing the native boundary survey input.

| native boundary survey class [observed] | Declarations / resolved [observed] | Copied confidence [observed] |
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
**[observed]** The function map's “4286 internal procedures” is an internal-procedure count, not a PE-export count;
the proposed internal names such as `ReadCellFile` do not occur among these 59 named exports.

**[observed]** Historical coverage statements conflict: the function map reports coverage of all 790 game-range
procedures, while the population notes leave `n_updateThread` behaviour unknown.
**[unknown]** This inventory cannot resolve historical coverage or the older behaviour claims;
neither statement contradicts the observed `n_1updateThread` export at `0x1800290f0`.

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
among the 59 matched entries. The native boundary survey records `lua_exposed=no` for all 59.
**[inferred]** These named entries suggest integration points spanning population and MapCollisionData;
the filename does not imply a population-only interface. **[unknown]** This inventory does not establish Lua/mod reachability, valid arguments,
safe lifecycle or an operation's actual gameplay effect.

## Confidence and limits

- **[observed]** The PE export directory is at `0x180125e80`, with image base `0x180000000`, RVA `0x125e80` and length 3,924 bytes.
- **[observed]** Its file offset is `0x125280`.
- **[observed]** The file and loaded directory agree on all 59 names, ordinals and target RVAs.
- **[observed]** All 59 exact export names correspond to recognized functions at their exported addresses.
- **[observed]** `Java_zombie_popman_ZombiePopulationManager_n_1stop` is at `0x1800289d0`.
- **[observed]** `Java_zombie_popman_MPDebugInfo_n_1hasData` is at `0x180025ec0`.
- **[observed]** `Java_zombie_popman_ZombiePopulationRenderer_n_1setWallFollowerStart` is at `0x18002afe0`.
- **[observed]** The CSV has six columns and exact names sorted in ordinal string order.
- **[observed]** The inventory concerns exported names and function addresses in `PZPopMan64.dll`.
- **[unknown]** An additional independent export-reader comparison remains UNVERIFIED.
- **[unknown]** Function-body behaviour, argument meanings, units, valid ranges and side effects are unestablished by this inventory.
- **[unknown]** Nested/indirect calls, runtime registration, actual invocation and script-value effects remain unproven.
- **[unknown]** Older behavioural claims remain unvalidated by this inventory.
- **[inferred]** Name-based feature areas describe likely roles; **[unknown]** they do not establish implementation behaviour.
