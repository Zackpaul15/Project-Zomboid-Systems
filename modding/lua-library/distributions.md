# Distributions and vanilla event usage (Project Zomboid, Build 42)

Survey date: 2026-10-24. Build identifier: jar sha256 prefix `e1a69eb7`.
Sources: installed Lua files; event comparison uses Claude's `data/events.csv`.
Claims are **[observed]** unless tagged **[inferred]** or **[unknown]**. No loot
contents, clothing lists, per-room values or copied game tables are included.

## Generated tables [observed]

Run `python -I modding/tools/survey_lua.py events` to regenerate:

- [vanilla-event-subscriptions.csv](../data/vanilla-event-subscriptions.csv): `event, file, side`, one row per literal `Events.<Name>.Add(` occurrence, including repeated subscriptions in one file.
- [vanilla-lua-event-triggers.csv](../data/vanilla-lua-event-triggers.csv): literal `triggerEvent` calls, with event name, file and side.
- [vanilla-event-comparison.csv](../data/vanilla-event-comparison.csv): subscription totals, Java catalogue registration/static-trigger evidence and Lua literal-trigger counts.
- [distribution-fields.csv](../data/distribution-fields.csv): assignment counts for selected schema-field names in seven distribution/clothing files.

The event scan covers all 1,395 vanilla Lua files in client/server/shared.
It masks comments and strings when finding subscriptions and checks literal
trigger-call locations against masked code. Whitespace between call tokens is
accepted. **[unknown]** Dynamic event indexing, aliases and computed event names
are outside this literal-pattern survey. The field table counts assignments
textually, not resolved or merged records; it is not a loot-probability calculator.

## Room and procedural loot [observed]

`server/Items/Distributions.lua` initializes `Distributions`, creates a local
room/container table, inserts it at the front of that list and assigns the
compatibility alias `SuburbsDistributions` to that room table. A leading space
on its root declaration means the X6 column-zero candidate heuristic misses
`Distributions`; the root and the compatibility alias both exist in this file.

The shape is a room key mapping to container keys. A container can hold
`procedural = true` and a `procList` array. Each procedure entry names a
distribution through `name` and carries `min`/`max`, with optional `weightChance`
and tile constraints such as `forceForTiles`. Some containers instead have direct
`rolls` and `items` fields, plus optional `junk` definitions.

`server/Items/ProceduralDistributions.lua` defines
`ProceduralDistributions.list`. Its named distributions hold `rolls` and an
`items` array; entries alternate an item identifier and a numeric weight.
Optional `junk` tables have their own rolls/items shape.
**[unknown]** Weights are not established here as percentages or independent
probabilities, and this survey does not calculate final spawn odds.

`server/Items/SuburbsDistributions.lua` supplies merge/manipulation functions,
including `MergeDistributionRecursive`, `RemoveItemFromDistribution`,
`ReplaceItemInDistribution` and `ClearAllDistributionItems`. It subscribes to
`OnPreDistributionMerge`, `OnDistributionMerge` and `OnPostDistributionMerge`.
The merge callback uses the first `Distributions` entry as the base and merges
the remaining entries. Recursive merging appends `items` array entries, adds
missing keys and leaves existing scalar values unchanged.

**[inferred]** To add room/container loot through that merge path, require the
relevant vanilla distribution modules, construct an original addon table with
the same shapes, and append it after the base entry before the distribution
merge phase. Define a new procedure under `ProceduralDistributions.list` before
referencing its name from a `procList`. If extending an existing `items` array,
append both the item identifier and its weight; an unmatched entry breaks the
alternating shape. Do not assume that setting an existing scalar in an addon
table overrides the base during this merge.
**[unknown]** This guidance is static source analysis, not an in-game compatibility
test across multiple loot mods or already-generated containers.

## Vehicle and clothing tables [observed]

`server/Vehicles/VehicleDistributions.lua` initializes `VehicleDistributions`,
defines named container loot tables and inserts a local vehicle mapping into
the list. Its container definitions also use `rolls`, alternating `items`
entries and `junk`. Junk can reference another table such as `ClutterTables`,
rather than appearing as an inline table. Vehicle variants can alias the same
mapping table. **[inferred]** Mutating an aliased table may affect more than one
vehicle name; inspect the mapping before changing it.

`shared/Definitions/ClothingSelectionDefinitions.lua` uses profession/default
keys, sex-specific groups and body-location entries. Body-location entries hold
an `items` array and can have `chance`. These item arrays contain identifiers
without the alternating numeric weights used by loot arrays.
`TraitClothingSelectionDefinitions.lua` is the separate trait-related source.
`DefaultClothing.lua` groups clothing XML identifiers under fields such as
`hue`, `texture` and `tint`; its source explicitly distinguishes them from item
type identifiers. **[inferred]** Extend each table using its own shape rather than
reusing a weighted-loot insertion pattern for clothing selection.
**[unknown]** Clothing-selection chance semantics, outfit XML generation and
the precise application timing are outside this survey.

## Events vanilla subscribes to [observed]

There are **412 literal subscription occurrences**, for **180 event names** in
**177 files**: 290 client, 63 server and 59 shared occurrences. There are **96
registered catalogue events with no literal vanilla subscription**. Examples
include `LoadChunk`, `OnAIStateChange`, `OnAddBuilding`, `OnAmbientSound`,
`OnChangeWeather` and `OnCharacterDeath`; the complete list is obtained by
filtering comparison rows with `registered = Y` and zero subscription occurrences.
No vanilla listener does not imply that an event is never fired or unsuitable
for a mod.

Eight subscribed names have no static Java trigger site in the catalogue:
`OnChallengeQuery`, `OnFillInventoryObjectContextMenu`, `OnFillWorldObjectContextMenu`, `OnOverrideSearchManager`, `OnSwitchVehicleSeat`, `OnVehicleHorn`, `onEnableSearchMode`, `onUpdateIcon`.

Of these, `OnSwitchVehicleSeat`, `OnVehicleHorn` and `onEnableSearchMode` are not
rows in Claude's Java event catalogue. This Lua scan finds literal triggers for
`OnSwitchVehicleSeat` and `onEnableSearchMode`; it finds none for `OnVehicleHorn`.
The world/inventory context-menu events are also fired from Lua, as described in
[events.md](../lua-api/events.md). **[unknown]** Missing static trigger evidence
does not exclude dynamic dispatch, another subsystem or a mod firing the name.
Registration, a subscription and a trigger are three separate facts.

## Validation

**[observed]** Three seeded source checks: the three distribution-merge
subscriptions, clothing selection's `chance`/`items` shape and insertion of the
base room table at the front of `Distributions`. A raw subscription scan finds
432 occurrences; all 20 excluded matches were inspected and are line comments.
All four CSVs regenerate byte-for-byte. Checks are recorded in `HANDOFF.md`.
**[unknown]** No loot generation or event callbacks were executed in-game.
