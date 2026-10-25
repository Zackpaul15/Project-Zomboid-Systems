# Key coverage: Java, vanilla Lua and script data (Build 42)

Survey date: 2026-10-24. Build/fingerprint: Project Zomboid Build 42;
jar sha256 prefix `e1a69eb7` (inherited from the source surveys).
[observed] This catalogue contains the corrected comparison results.
Output SHA-256: `e20bf21e17545d6e7caae01cc7b71e377f324e04dd98c9944d8845c4c64ea951`.
The build fingerprint is inherited from the source surveys, not independently
verified by this catalogue comparison.

## Inputs [observed]

The comparison covers these catalogues; it does not establish additional game-install behaviour:

- Events: [events.csv](../data/events.csv),
  [vanilla-event-subscriptions.csv](../data/vanilla-event-subscriptions.csv) and
  [vanilla-lua-event-triggers.csv](../data/vanilla-lua-event-triggers.csv).
- Java parser identifiers: [script-keys.csv](../data/script-keys.csv).
- Observed script identifiers: [item-properties.csv](../data/item-properties.csv),
  [item-component-properties.csv](../data/item-component-properties.csv),
  [recipe-keys.csv](../data/recipe-keys.csv), [vehicle-keys.csv](../data/vehicle-keys.csv),
  [sound-keys.csv](../data/sound-keys.csv), [fluid-keys.csv](../data/fluid-keys.csv) and
  [entity-keys.csv](../data/entity-keys.csv).

## Comparison scope and evidence [observed]

[key-coverage.csv](../data/key-coverage.csv) contains one output row per input record from eleven source catalogues,
including repeated Lua trigger sites, Java grammar/block entries, structural survey markers and zero-count markers.
Each evidence cell identifies the input revision, source CSV SHA-256 and source record number.
The header is record 1; a record number is not a physical line number when a CSV field contains newlines.
The `input_revision` field distinguishes catalogue revisions even when their source CSV contents are identical.
Missing inputs, changed schemas and malformed rows are outside the catalogue's valid input contract.

Rows use a total lexical sort, UTF-8 without BOM and LF line endings. Evidence is JSON with sorted keys,
without timestamps or machine-dependent input paths.
[observed] The catalogue was reproduced twice at the same input revision with identical contents.
The counts and fingerprints below describe the corrected result.

Identifier spelling and **case sensitivity** are preserved. Event joins are exact
and case-sensitive. Script keys match case-insensitively only when the Java record
explicitly says `case_sensitive=no`, and only for ASCII identifiers; differently
spelled matches are `explained`, with the parser flag retained in evidence.
Other spellings are not normalized into matches.

**Nested parser context** is retained in the name and evidence: Java block, kind,
class and reader method; data block paths including component types and nested
children. The assignment-reader crosswalk is limited to:
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
Dynamic names, catalogue limitations and unobserved content can leave gaps.
The [Java event reference](../lua-api/events.md) records a dynamic-name Java caller.
Runtime names are outside this catalogue's scope. An unmatched key or subscription alone is not classified as defective.

## Output columns [observed]

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
in `vanilla-lua-event-triggers.csv`. Evidence identifies the contradiction and related catalogue records. This is a catalogue defect, not a runtime verdict.
Every mismatch is explained, classified as a catalogue defect or explicitly unknown.
[observed: classification policy]

Unresolved Java grammar kinds (`flag`, `token`, `block`, `block-id`, `xui-var`)
use `grammar_kind_not_assignment`. Assignment/attribute readers lacking a proven
crosswalk use `reader_context_unmapped`; mapped readers with only out-of-context
candidates use `candidate_context_unresolved`. Data rows with only grammar
candidates use `grammar_candidate_not_assignment`; data with unmapped assignment
reader candidates use `reader_context_unmapped`. Rows with no candidates retain
the relevant `no_observation_in_input_catalogues` or
`no_parser_match_in_input_catalogue` reason. These distinguish the causes previously grouped under
`scope_or_grammar_unresolved`. [observed]

## Corrected results [observed]

Counts below are CSV records, **not distinct names, runtime occurrences or
percentages of valid mod keys**. A counterpart can contribute a row on each side;
repeated Lua sites and structural survey markers remain separate records.

| Domain | matched | explained | unknown | defect | Total |
|---|---:|---:|---:|---:|---:|
| events | 669 | 8 | 87 | 0 | 764 |
| script_keys | 671 | 353 | 2,110 | 0 | 3,134 |
| Overall | 1,340 | 361 | 2,197 | 0 | 3,898 |

[observed] All 3,898 evidence cells are populated, contain valid JSON and identify the same input revision.
There are no illegal classification values. The eleven source fingerprints recorded in evidence are
(SHA-256 prefixes, first 16 characters):

| Input | Fingerprint |
|---|---|
| events.csv | `f8aff47e0fc37f4c` |
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

### Correction effects and zero-defect interpretation [observed]

Relative to the earlier comparison, exactly three rows moved from
`defect` to `unknown`: unknown increased from 2,194 to 2,197 and defects fell from
3 to 0. They did not become `matched`. Matched remains 1,340, explained remains
361, and the total remains 3,898; this correction does not inflate matched coverage.

**A defect count of 0 is now the expected state, not a regression.** The
three earlier defect rows were real cross-table contradictions correctly detected
by the check. Their cause was fixed, and the check was not weakened. A future
cross-table contradiction would still legitimately trigger a defect: specifically,
an `events.csv` row with positive `lua_trigger_files` but no corresponding literal
trigger record in `vanilla-lua-event-triggers.csv`. Zero defects therefore records
the absence of this contradiction in the corrected inputs, rather than merely an
artefact of scope; it does not establish the absence of all possible defects.

### Commented Lua trigger correction

[observed]
`OnChangeWeather`, `OnDawn` and `OnDusk` previously each had `lua_trigger_files=1`
in `events.csv` and no row in `vanilla-lua-event-triggers.csv`. The root cause was
the inclusion of `triggerEvent` calls inside Lua `--[[ ]]` block comments in `season.lua`.
The corrected `events.csv` excludes those commented calls; those three counts changed from 1 to 0.
The contradictory positive claims are gone, so the rows now remain `unknown`
without a literal trigger counterpart. The earlier
`lua_trigger_count_without_trigger_record` flags correctly identified catalogue
defects; their resolution does not establish runtime event behaviour.

### Catalogue discrepancies [observed unless marked otherwise]

- **Comment-only trigger counts: detected, then resolved.** The three names above met the mechanical
  contradiction in the earlier catalogue; the corrected input no longer meets it.
  Detection still uses input values, not a hard-coded event-name list.
- **Missing Java event entry: absence holds; defect unproven.** `OnVehicleHorn` is subscribed in
  `server/Vehicles/Vehicles.lua` and absent from `events.csv`. The game file also
  registers it literally via `LuaEventManager.AddEvent` (line 1538), before the
  subscription (line 1540). The CSVs cannot rule out dynamic-name triggers; the Java event reference
  documents that such Java calls exist. It stays `unknown`, with that limitation
  explicit in evidence. Missing a static catalogue row alone is insufficient.
- **Case-sensitive keys: no established counterpart.** Positive data occurrences differing
  only in case from `case_sensitive=yes` Java keys were inspected across all
  seven data tables. The apparent pairs belong to different contexts, such as
  `VehicleScript.LoadContainer/capacity` versus item `Capacity`, or evolvedrecipe
  `Template` versus vehicle `template`. None establishes a scoped contradiction;
  no case-sensitive defect is emitted.

### Accepted limitations from this correction

- **Unresolved reader mappings.** Vehicle, fluid and further component reader mappings need
  established Java call-site provenance per entry; spelling
  alone cannot justify them. Unmapped readers remain explicit in evidence.
- **Token grammar remains separate.** Prefix rows are `kind=token` and never enter assignment-key
  comparison. Treating them as exact strings for discovery has no behavioural
  effect on established matches; grammar reasons now identify their scope.

[unknown] Catalogue overlaps do not establish runtime values, argument contracts
or behaviour. Remaining mappings, grammar/registry/template provenance and dynamic
event names require further source-supported analysis.

[observed] Lua subscriptions include `OnSteamGameJoin` in `client/OptionScreens/MainScreen.lua`,
`OnInitWorld` in `client/OptionScreens/LastStandPlayerSelect.lua`, and `EveryDays` in
`server/Traps/STrapSystem.lua`. These examples establish source provenance, not all catalogue classifications.

## Java-side interpretation [unknown]

Causes and Java-side fixes for unresolved comparisons remain unestablished here.
The [parser reference](parser-keys.md) and [event reference](../lua-api/events.md)
describe the relevant Java-side contracts and limitations.
