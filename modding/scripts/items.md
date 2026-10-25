# Item properties (Project Zomboid, Build 42)

Survey date: 2026-10-24. Build identifier: jar sha256 prefix `e1a69eb7`.
Sources: installed `media/scripts/**/*.txt`, English item-name translations,
and clothing XML filenames. Claims are **[observed]** unless marked
**[inferred]** or **[unknown]**. No game definitions or per-item values are reproduced.

## Coverage [observed]

There are **5,105 item blocks**, all immediately inside modules, with **363 distinct
direct property names** and **15 ItemType identifiers**. Counts describe source
occurrences before runtime merging, not the final item registry. All direct entries
in these item blocks are assignments; nested components are counted separately.

The item tables use the script inventory's structural definitions:

- [item-properties.csv](../data/item-properties.csv): `property, count, types_seen_on, value_shape, example_shape`.
- [item-component-properties.csv](../data/item-component-properties.csv): the same fields with a `block_path` prefix.
- [item-types.csv](../data/item-types.csv): item-block totals and the number of properties exclusive to each observed type.
- [item-resource-links.csv](../data/item-resource-links.csv): aggregate identifier matches to model/sound blocks, clothing XML filenames and English translation keys.

`count` is assignment occurrences, including repeated assignments within one block.
For example, `SoundMap` repeats within 15 items and `ModelWeaponPart` within 12.
`types_seen_on` is a semicolon-separated set of the enclosing items' `ItemType`
values. Property spelling and case are preserved, including names such as
`Researchablerecipes`, `Eattime` and `hidden`.

**[inferred]** Shapes are lexical descriptions, not Java parameter types.
`qualified-id` means two word tokens separated by a dot; it can describe an item
reference or a Lua callback. `namespaced-id` describes colon-separated identifiers.
`list;` means semicolon-separated entries; `tag-list` identifies that shape for
`Tags`. Numeric values distinguish integer and decimal spellings. `string` is the
fallback, including multiword values. Patterns in `example_shape` are fixed
placeholders, never sampled item values. See
[parser-keys.md](parser-keys.md) for accepted keys, conversions and defaults;
an unobserved key may still be supported by the engine.

## Common properties and item families [observed]

Only **DisplayCategory** and **ItemType** are present on every surveyed item.
`Icon` occurs 4,683 times and `Weight` 4,525 times. Both appear in every type family,
but neither appears on every item. Absence here does not establish a runtime default.
The direct property `Type` does not occur; this install uses namespaced `ItemType`
values instead. `DisplayName` does not occur either.

The table's totals come from `item-types.csv`; representative keys come from
`item-properties.csv`. “Exclusive” means seen only on that family in these files;
it does not mean other types reject the key.

| ItemType | Item blocks | Representative properties exclusive to this family |
|---|---:|---|
| `base:alarmclock` | 2 | None |
| `base:alarmclockclothing` | 16 | None |
| `base:animal` | 1 | None |
| `base:clothing` | 1,395 | `BiteDefense`, `ScratchDefense`, `WaterResistance` |
| `base:container` | 308 | `Capacity`, `WeightReduction`, `AcceptItemFunction` |
| `base:drainable` | 150 | `ReplaceOnDeplete`, `UseWhileUnequipped`, `IsWaterSource` |
| `base:food` | 722 | `DaysFresh`, `MinutesToCook`, `ReplaceOnCooked` |
| `base:key` | 6 | `Padlock`, `DigitalPadlock` |
| `base:literature` | 561 | `NumberOfPages`, `SkillTrained`, `LearnedRecipes` |
| `base:map` | 15 | `Map` |
| `base:moveable` | 393 | None |
| `base:normal` | 1,099 | `CanBandage`, `brakeForce`, `wheelFriction` |
| `base:radio` | 17 | `TwoWay`, `TransmitRange`, `UsesBattery` |
| `base:weapon` | 409 | `MaxDamage`, `SwingSound`, `CriticalChance` |
| `base:weaponpart` | 11 | `MountOn`, `PartType`, `WeightModifier` |

Shared keys cross boundaries that the names might suggest. `HungerChange` appears
on food and drainable items. `UseDelta` appears on drainable, food, radio and
weaponpart items. `Insulation` appears on clothing and normal items.
`CanBeEquipped` appears on containers and radios. Use the CSV to check the observed
scope of a key rather than assuming that one filename or familiar item category
defines all its uses.

## Tags and references [observed]

`Tags` occurs on 3,527 items. Each entry has the form `<namespace>:<tag>`;
multiple entries are separated by semicolons. Every observed tag entry has that
namespaced lexical shape. Tags are distinct from the single `ItemType` identifier,
from `DisplayCategory`, and from dotted `<module>.<item>` references.

Replacement and recipe-related keys include `ReplaceOnUse`, `ReplaceOnDeplete`,
`ReplaceOnCooked`, `EvolvedRecipe`, `LearnedRecipes` and `Researchablerecipes`.
Their shapes differ: a replacement can use a dotted identifier, while a recipe
association can carry a semicolon list with additional colon-delimited data.
**[unknown]** The lexical survey alone does not establish lookup fallback,
callback timing, or the meaning of every list position. Do not treat every colon
as a tag delimiter or every dotted value as an item reference.

## Names, icons, models and sounds

- **[observed]** `media/lua/shared/Translate/EN/ItemName.json` is a JSON object
  mapping full item identifiers, shaped `<module>.<item>`, to readable names.
  Its keys match 4,900 of the surveyed item-block identifiers. No direct
  `DisplayName` assignment occurs in this script tree. **[unknown]** Missing English
  keys alone do not establish the displayed fallback or whether an item is usable.
- **[observed]** `Icon` uses string identifiers. Loose PNG filenames with an
  `Item_` prefix exist under `media/textures`; texture packs also exist under
  `media/texturepacks`. **[inferred]** Treat `Icon` as a texture lookup identifier,
  rather than assuming every icon is a loose image you can find by filename.
  **[unknown]** This survey does not resolve texture-pack contents or fallback icons.
- **[observed]** Every `StaticModel` assignment (1,559) and `WorldStaticModel`
  assignment (3,844) matches the name of a `model` block in the script tree.
  **[inferred]** These are references into model definitions rather than mesh paths.
  A successful name match does not verify that a referenced mesh or texture loads.
- **[observed]** Every `ClothingItem` assignment (1,580) matches a filename stem
  under `media/clothing/clothingItems/*.xml`. This property occurs on clothing,
  containers, radios and alarmclockclothing items, not just the clothing family.
- **[observed]** Every `SwingSound` assignment (408) and `CookingSound` assignment
  (203) matches a named `sound` block. Other sound-related keys include
  `BreakSound`, `OpenSound`, `CloseSound`, `PutInSound` and `CustomEatSound`.
  `SoundMap` uses whitespace-separated entries and can repeat within an item.
  **[unknown]** The aggregate matching check covers the two named sound properties,
  not every sound-related key or playback condition.

## Components inside items [observed]

Items can contain `component <ComponentType>` blocks. This survey finds 133
`FluidContainer`, five `Durability` and one `ContextMenuConfig` component blocks.
The companion CSV has **14 scoped property names**. Fluid-container properties
include `ContainerName`, `Capacity`, `RainFactor`, `TransferRate` and
`CustomDrinkSound`; nested `Fluids` blocks contain repeated `fluid` assignments.
Durability components use `Material` and `MaxHitPoints`. The context-menu component
has a `contextEntry` child with `menu` and `customFunction` keys.

Direct item `Capacity` occurs only on `base:container`; component `Capacity` occurs
on clothing, container, normal and weapon items. They are separate rows in separate
tables because they occupy different parser contexts. Component names and child
paths are retained; enclosing item identifiers and all source values are omitted.

## Limits and source checks

**[inferred]** Coverage follows the script inventory's brace/comma and block-comment
boundaries. Arbitrary quoted delimiters, Java reference validity and overrides remain outside its scope. Repeated keys are retained rather than collapsed;
the observed type for an item is its final textual `ItemType` assignment, falling
back to `Type` only if absent. All current items have `ItemType`.

**[observed]** No item uses `DisplayName`; `BiteDefense` is restricted to clothing items;
direct `Capacity` is restricted to container items. These direct-key findings exclude nested component bodies.
