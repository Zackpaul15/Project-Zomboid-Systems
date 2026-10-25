# Key coverage: Java, vanilla Lua and script data (Build 42)

Survey date: 2026-10-24. Build/fingerprint: Project Zomboid Build 42;
jar sha256 prefix `e1a69eb7` (inherited from the source surveys).
[observed] Historical pre-correction input revision: `67f662930a7f93bdfd7173a05daf58542aaaec4a`.
Historical pre-correction output SHA-256: `4ede143ae002cb0a6b3a21dd1655b63e357b4e8363c9ea1793728a65e6aaefd2`.
The build fingerprint is inherited from the source surveys, not independently
verified by this catalogue comparison.

## Inputs [observed]

The generator compares these committed catalogues, without accessing the game install:

- Events: [events.csv](../data/events.csv),
  [vanilla-event-subscriptions.csv](../data/vanilla-event-subscriptions.csv) and
  [vanilla-lua-event-triggers.csv](../data/vanilla-lua-event-triggers.csv).
- Java parser identifiers: [script-keys.csv](../data/script-keys.csv).
- Observed script identifiers: [item-properties.csv](../data/item-properties.csv),
  [item-component-properties.csv](../data/item-component-properties.csv),
  [recipe-keys.csv](../data/recipe-keys.csv), [vehicle-keys.csv](../data/vehicle-keys.csv),
  [sound-keys.csv](../data/sound-keys.csv), [fluid-keys.csv](../data/fluid-keys.csv) and
  [entity-keys.csv](../data/entity-keys.csv).

## Method [observed: generator and CSV inspection]

Run `python -I modding/tools/survey_key_coverage.py` from the repository root.
The standard-library generator is [survey_key_coverage.py](../tools/survey_key_coverage.py).
Its sole output is [key-coverage.csv](../data/key-coverage.csv).
Git must be available: the generator resolves HEAD once and reads all eleven inputs
with `git show <revision>:modding/data/<filename>`. Uncommitted CSV edits are excluded.
Each evidence cell records that revision, the SHA-256 of its source CSV bytes and
the source record number (header is record 1; this is not a physical line number
when a CSV field contains newlines). Missing inputs, changed schemas and malformed
rows fail before the output is written. The recorded revision is the **parent
HEAD at generation time**, before Hermes proxy-commits generated evidence. Re-running
at a new HEAD changes evidence bytes even with identical input CSV bytes because
`input_revision` is embedded in every row.

There is one output row per input record, including repeated Lua trigger sites,
Java grammar/block entries, structural survey markers and zero-count markers.
Rows use a total lexical sort, UTF-8 without BOM and LF line endings. Evidence is
JSON with sorted keys. There are no timestamps or machine-dependent input paths.
Two runs against the same resolved revision must produce byte-identical output.
[unknown] Post-correction distribution, hash and repeatability await Hermes's two
runs. J1A-FIX1 did not run the generator or recompute classifications. Historical
counts and fingerprints below describe the pre-correction artifact only.

Identifier spelling and **case sensitivity** are preserved. Event joins are exact
and case-sensitive. Script keys match case-insensitively only when the Java record
explicitly says `case_sensitive=no`, and only for ASCII identifiers; differently
spelled matches are `explained`, with the parser flag retained in evidence.
Other spellings are not normalized into matches.

**Nested parser context** is retained in the name and evidence: Java block, kind,
class and reader method; data block paths including component types and nested
children. The generator has a deliberately limited assignment-reader crosswalk:
item/DoParam; recipe, evolvedrecipe, fixing, craftRecipe and energy/Load;
sound/Load and sound/clip/LoadClip; and the two character-definition readers.
The crosswalk includes the class as well as the method. Attribute registry rows
(`kind=attribute`, `Attribute.static init`) also map to `item`,
`item/component:Attributes` and `entity/component:Attributes`.
[observed] `Item.DoParam(String,String)` checks `Attribute.TypeFromName` before
explicit keys (Item.java:1937); `AttributesScript.parseKeyValue` consults the same
registry (AttributesScript.java:91). These justify the attribute equivalence,
even where the current data surveys contain no Attributes component occurrence.
[inferred] These are the
paths used for mechanical assignment comparison. Other readers, template aliases,
common-key registries, XUI registries and line grammar are
retained without asserting an equivalent data path. Same-family name candidates
are evidence for review, not matches. In particular, a component key cannot match
a direct item key just because its spelling agrees. Structural markers are never
matched to assignments. Unresolved comparisons remain explicitly `unknown`.

**Java-vs-Lua event provenance** remains separate. `side=java` rows originate only
in events.csv; their evidence retains registration, Java methods/classes and the
catalogue's Lua-trigger count. That count is not used to infer a Java trigger.
`side=lua` rows retain whether they are subscriptions or literal triggers, their
file and client/server/shared folder. Event overlap means catalogue-name overlap,
even if Java only registers the name. A Lua-only literal trigger is `explained`
by its Lua provenance; a subscription alone does not prove that a trigger exists.

[unknown] **Absence from one static catalogue does not establish invalidity.**
Dynamic names, extractor limitations and unobserved content can leave gaps.
C1 already records a dynamic-name Java caller; see the
[Java event reference](../lua-api/events.md). This generator cannot enumerate
runtime names. An unmatched key or subscription alone is not classified as defective.

## Output columns [observed: generator design]

| Column | Meaning |
|---|---|
| `domain` | `events` or `script_keys`. |
| `side` | Provenance of this input record: `java`, `lua` or `data`. |
| `name` | Exact event name; for script identifiers, a JSON object retaining key, kind and context. Java names additionally retain class and reader. |
| `present_java` | `1` for an established catalogue occurrence/match, `0` for no candidate in these inputs, `unknown` when candidates lack a proven context equivalence. |
| `present_lua` | Event-name presence across the two Lua input tables (`1`/`0`); `n/a` for script keys. Subscriptions and triggers are distinguished in evidence. |
| `present_data` | Script assignment/marker occurrence or proven counterpart (`1`/`0`/`unknown`); `n/a` for events. A source count of zero is `0`, not an occurrence. |
| `classification` | Exactly `matched`, `explained`, `defect` or `unknown`, as defined below. |
| `evidence` | JSON containing input revision, source record and full source fields, source SHA-256, reason, and related/matched/candidate record references. |

`matched` means exact spelling and established catalogue context overlap.
`explained` covers explicit case-insensitive parser overlap, Lua-only literal
trigger provenance, and structural or zero-count survey markers. `unknown` retains
one-sided or ambiguous comparisons. `defect` is emitted mechanically for an
`events.csv` record with positive `lua_trigger_files` and no corresponding record
in `vanilla-lua-event-triggers.csv`. Evidence names the contradiction, finding,
owners and review destination. This is a catalogue defect, not a runtime verdict.
Every mismatch is explained, defect-routed or explicitly unknown.
[observed: classification policy]

Unresolved Java grammar kinds (`flag`, `token`, `block`, `block-id`, `xui-var`)
use `grammar_kind_not_assignment`. Assignment/attribute readers lacking a proven
crosswalk use `reader_context_unmapped`; mapped readers with only out-of-context
candidates use `candidate_context_unresolved`. Data rows with only grammar
candidates use `grammar_candidate_not_assignment`; data with unmapped assignment
reader candidates use `reader_context_unmapped`. Rows with no candidates retain
the relevant `no_observation_in_input_catalogues` or
`no_parser_match_in_input_catalogue` reason. These split the old
`scope_or_grammar_unresolved` bucket into actionable work. [observed: generator]

## Historical pre-correction results [observed]

Counts below are CSV records, **not distinct names, runtime occurrences or
percentages of valid mod keys**. A counterpart can contribute a row on each side;
repeated Lua sites and structural survey markers remain separate records.

| Domain | matched | explained | unknown | defect | Total |
|---|---:|---:|---:|---:|---:|
| events | 669 | 8 | 87 | 0 | 764 |
| script_keys | 661 | 184 | 2,289 | 0 | 3,134 |
| Overall | 1,330 | 192 | 2,376 | 0 | 3,898 |

[observed: pre-correction artifact] All 3,898 evidence cells are populated, parse as JSON and identify the
input revision above. There are no illegal classification values. The eleven
source fingerprints recorded in evidence agree with the supplied run evidence
(SHA-256 prefixes, first 16 characters):

| Input | Fingerprint |
|---|---|
| events.csv | `b3f4e5160a05ad5f` |
| vanilla-event-subscriptions.csv | `2397626b11d083e6` |
| vanilla-lua-event-triggers.csv | `d135b2b986ffaee2` |
| script-keys.csv | `f440a840c8fdecaa` |
| item-properties.csv | `798d93663ae5466b` |
| item-component-properties.csv | `b4fe8052e2a7e776` |
| recipe-keys.csv | `b2ea752fe405e2a8` |
| vehicle-keys.csv | `be0c3fe8696b1d35` |
| sound-keys.csv | `956229809314d799` |
| fluid-keys.csv | `794f4b770d3f2c6b` |
| entity-keys.csv | `43202bd9b74686ef` |

### Expected correction effects [inferred]

The new distribution is pending Hermes; no replacement counts are asserted here.
Row totals should stay unchanged because every input record is still emitted once.
Attribute mappings should move established overlaps from `unknown` to `matched`
(or `explained` for case-insensitive overlap). The 167 previously unknown positive
survey markers should become `explained` with
`structural_survey_marker_not_applicable`, without increasing `matched`.
The trigger-count contradictions below should become `defect`. Reason splitting
changes the unknown breakdown without itself changing classifications. The old
zero-defect count was structurally guaranteed; the new detector measures only the
specified cross-table contradiction, not the overall defect rate.

### Named catalogue finding J1B-6

[observed: input CSV inspection at J1A-FIX1 base HEAD]
`OnChangeWeather`, `OnDawn` and `OnDusk` each have `lua_trigger_files=1` in
`events.csv` and no row in `vanilla-lua-event-triggers.csv`. This contradicts the
catalogues' trigger coverage and must be reconciled by Claude (events table) and
Codex (Lua trigger table). The generator emits
`lua_trigger_count_without_trigger_record` and routes evidence here. Which
extractor needs correction remains [unknown]; this does not claim broken events.

### Defect candidate checks [observed unless marked otherwise]

- **J1B-1(a): holds.** The three names above meet the mechanical contradiction.
  Detection uses input values, not a hard-coded event-name list.
- **J1B-1(b): absence holds; defect unproven.** `OnVehicleHorn` is subscribed in
  `server/Vehicles/Vehicles.lua` and absent from `events.csv`. The game file also
  registers it literally via `LuaEventManager.AddEvent` (line 1538), before the
  subscription (line 1540). The CSVs cannot rule out dynamic-name triggers; C1
  documents that such Java calls exist. It stays `unknown`, with that limitation
  explicit in evidence. Missing a static catalogue row alone is insufficient.
- **J1B-1(c): no established counterpart.** Positive data occurrences differing
  only in case from `case_sensitive=yes` Java keys were inspected across all
  seven data tables. The apparent pairs belong to different contexts, such as
  `VehicleScript.LoadContainer/capacity` versus item `Capacity`, or evolvedrecipe
  `Template` versus vehicle `template`. None establishes a scoped contradiction;
  no case-sensitive defect is emitted.

### Accepted limitations from this correction

- **J1B-3 deferred.** Vehicle, fluid and further component reader mappings need
  validated Java call-site provenance per entry. That is a new work item; spelling
  alone cannot justify them. Unmapped readers remain explicit in evidence.
- **J1B-5 deferred.** Prefix rows are `kind=token` and never enter assignment-key
  comparison. Treating them as exact strings for discovery has no behavioural
  effect on established matches; grammar reasons now identify their scope.

[unknown] Catalogue overlaps do not establish runtime values, argument contracts
or behaviour. Remaining mappings, grammar/registry/template provenance and dynamic
event names require further source-supported analysis.

[observed] Three randomly selected Lua-source claims (seed `20261024`) were
checked against the installed game files: `OnSteamGameJoin` subscription in
`client/OptionScreens/MainScreen.lua`, `OnInitWorld` subscription in
`client/OptionScreens/LastStandPlayerSelect.lua`, and `EveryDays` subscription in
`server/Traps/STrapSystem.lua`. These three checks were repeated for J1A-FIX1 against the installed files; they spot-check provenance, not all classifications.

## Java-side interpretation — pending Claude-owned material [unknown]

Java-side mismatch interpretation belongs to Claude's later task. Pending its
specific destination, use the existing [parser reference](parser-keys.md) and
[event reference](../lua-api/events.md) as entry points. This skeleton does not
attribute causes or propose Java-side fixes for unresolved comparisons.
