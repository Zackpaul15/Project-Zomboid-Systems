# Key coverage: Java, vanilla Lua and script data (Build 42)

Survey date: 2026-10-24. Build/fingerprint: Project Zomboid Build 42;
jar sha256 prefix `e1a69eb7` (inherited from the source surveys).
[observed] Input revision: `67f662930a7f93bdfd7173a05daf58542aaaec4a`.
Output SHA-256: `4ede143ae002cb0a6b3a21dd1655b63e357b4e8363c9ea1793728a65e6aaefd2`.
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
rows fail before the output is written. Hermes reports two successful runs at
the revision above with identical output bytes; this phase independently reads
the resulting CSV and checks its hash, counts and evidence metadata. The output
is currently untracked, so it is inspected from disk, not claimed as committed.

There is one output row per input record, including repeated Lua trigger sites,
Java grammar/block entries, structural survey markers and zero-count markers.
Rows use a total lexical sort, UTF-8 without BOM and LF line endings. Evidence is
JSON with sorted keys. There are no timestamps or machine-dependent input paths.
Two runs against the same resolved revision must produce byte-identical output;
the supplied Hermes run evidence reports that check passed.

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
The crosswalk includes the class as well as the method. [inferred] These are the
paths used for mechanical assignment comparison. Other readers, template aliases,
shared attribute/common-key registries, XUI registries and line grammar are
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
runtime names and does not conclude that an unmatched key or event is defective.

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
trigger provenance, or a zero-count survey marker. `unknown` records every
remaining one-sided or ambiguous comparison. `defect` is reserved for a confirmed,
routed defect with an owner and destination recorded in evidence; this generator
makes no automatic defect assignments. These classes describe coverage evidence,
not a runtime validity verdict. Every mismatch must be explained, defect-routed,
or explicitly unknown; none is silently dropped. [observed: classification policy]

## Classified results [observed]

Counts below are CSV records, **not distinct names, runtime occurrences or
percentages of valid mod keys**. A counterpart can contribute a row on each side;
repeated Lua sites and structural survey markers remain separate records.

| Domain | matched | explained | unknown | defect | Total |
|---|---:|---:|---:|---:|---:|
| events | 669 | 8 | 87 | 0 | 764 |
| script_keys | 661 | 184 | 2,289 | 0 | 3,134 |
| Overall | 1,330 | 192 | 2,376 | 0 | 3,898 |

[observed] All 3,898 evidence cells are populated, parse as JSON and identify the
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

### What the unresolved majority means

[observed] **The static catalogues as compared by this generator cannot resolve
2,376 of 3,898 rows (60.95%, approximately 61%).** The reason breakdown is:

| Unknown reason | Java rows | Lua rows | Data rows | Total |
|---|---:|---:|---:|---:|
| `one_sided_static_catalogue` (events) | 86 | 1 | 0 | 87 |
| `scope_or_grammar_unresolved` (script keys) | 422 | 0 | 1,010 | 1,432 |
| `no_observation_in_input_catalogues` (script keys) | 472 | 0 | 0 | 472 |
| `no_parser_match_in_input_catalogue` (script keys) | 0 | 0 | 385 | 385 |

[inferred] This is honest under-resolution **only when read as a coverage
limitation**. The bucket retains real catalogue mismatches and can conceal real
defects among them; it does not establish their causes or harmlessness. The ten-entry
`CONTEXTS` crosswalk is too small to resolve the full comparison: for example,
data `vehicle/animalTrailerSize` has Java candidate `script-keys.csv#record=913`
(`VehicleScript.Load`), but vehicle readers have no crosswalk entry. That is an
unresolved mapping, not proof of an invalid key. Expanding the crosswalk requires
validated context equivalences, not matching spellings alone.

[observed] There is also avoidable classification coarseness: **167 unknown data
rows are positive-count `survey-marker` records**, including `craftRecipe/<block>`
and `craftRecipe/<child:inputs>`. Their source notes already identify structural
counts rather than assignment keys. [inferred] Those rows warrant a future
`explained` reason such as "structural survey marker; assignment comparison not
applicable", without inflating `matched`. The current generator explains six
zero-count markers but has no equivalent rule for positive structural markers.
This phase preserves the supplied CSV and reports its classifications unchanged.

[observed] Of the 192 explained rows, 178 are case-insensitive parser overlaps,
eight have literal Lua-trigger provenance, and six are zero-count survey markers.
The 1,330 matched rows establish catalogue overlap under the rules above; event
overlap can include registration without a Java trigger. [unknown] Neither group
establishes correct runtime values, argument contracts or behavior.

[observed] **Zero defects is an artefact of the classification scope, not a
finding that there are no defects.** No generator branch emits `defect`; the
reserved class would require separate confirmation and routing evidence. The
present output cannot measure a defect rate. [unknown] Whether any unresolved
assignment or subscription is actually broken remains open.

[inferred] Resolving the remainder requires reader-to-nested-data-path mappings
with source locations, grammar/registry and template provenance, and comparison
against the same pinned build. Some rows may then become explained because they
are structural or outside the opposing survey's scope. Others need targeted
parser/runtime checks or dynamic event-name tracing. A confirmed defect needs a
reproducible failure or source-supported contradiction plus an owner and review
destination. **Absence from one static catalogue does not establish invalidity**,
especially for dynamic names. Java-side conclusions are deferred to the
[pending Claude-owned section](#java-side-interpretation--pending-claude-owned-material-unknown).

[observed] Three randomly selected Lua-source claims (seed `20261024`) were
checked against the installed game files: `OnSteamGameJoin` subscription in
`client/OptionScreens/MainScreen.lua`, `OnInitWorld` subscription in
`client/OptionScreens/LastStandPlayerSelect.lua`, and `EveryDays` subscription in
`server/Traps/STrapSystem.lua`. These spot-check provenance, not all classifications.

## Java-side interpretation — pending Claude-owned material [unknown]

Java-side mismatch interpretation belongs to Claude's later task. Pending its
specific destination, use the existing [parser reference](parser-keys.md) and
[event reference](../lua-api/events.md) as entry points. This skeleton does not
attribute causes or propose Java-side fixes for unresolved comparisons.
