# Fluid and energy definitions (Project Zomboid, Build 42)

Survey date: 2026-10-24. Build identifier: jar sha256 prefix `e1a69eb7`.
Source: installed `media/scripts/**/*.txt`. Claims are **[observed]** unless
marked **[inferred]** or **[unknown]**. Only identifiers, counts and shapes are
recorded; no per-fluid nutritional, color or poison values are reproduced.

## Coverage [observed]

There are **61 `fluid` blocks in three files** and **seven `energy` blocks in one
file**. The fluid files are `generated/fluids.txt`, `generated/fluids_Alcoholic.txt`
and `generated/fluids_Beverages.txt`; energy definitions are in
`generated/energies.txt`. All these blocks are module-level definitions.

[fluid-keys.csv](../data/fluid-keys.csv) and the shared
[component-blocks.csv](../data/component-blocks.csv) describe fluid/energy definitions. Columns are
`block_type, key, count, value_shape, notes`. Context paths retain case:
`fluid/Categories` and `fluid/BlendWhiteList/categories` are different contexts.
`<block>` counts structural blocks and `<entry>` counts bare comma-delimited
entries. Source values and fluid-instance names are omitted.

## Fluid structure [observed]

Every fluid definition has `ColorReference`, `DisplayName` and a `Categories`
child. The color and display-name fields are strings. `DisplayName` values use
translation-key-shaped identifiers; they are not readable name text in the
definition itself. There are 100 bare category entries across the 61 category
blocks. Category identifiers include `Beverage`, `Water` and `Hazardous`.

| Child context | Blocks | Observed fields/entry shape |
|---|---:|---|
| `Categories` | 61 | Bare category identifiers |
| `Properties` | 51 | Numeric nutritional and character-effect fields |
| `BlendWhiteList` | 56 | `whitelist` boolean and nested lowercase `categories` |
| `BlendWhiteList/categories` | 56 | Bare category identifiers; some blocks empty |
| `Poison` | 10 | `maxEffect` identifier; `minAmount`, `diluteRatio` decimals |

`Properties` contains keys including `Calories`, `Carbohydrates`, `Lipids`,
`Proteins`, `HungerChange`, `ThirstChange`, `StressChange` and `UnhappyChange`.
Other observed spellings include `alcohol`, `enduranceChange`, `fatigueChange`,
`fluReduction`, `foodSicknessChange` and `painReduction`. Most are written as
decimals; `foodSicknessChange` is written as an integer in this tree.
**[unknown]** A numeric shape does not determine its unit, scaling, sign semantics
or dose calculation.

All 56 `BlendWhiteList` blocks have `whitelist` and a lowercase `categories`
child. Those category children contain 52 bare entries in total, so an empty
category list is an observed form. **[unknown]** Do not infer from an empty list
alone whether mixing is allowed or denied; runtime whitelist behavior belongs
to the parser and fluid system.

## Containers and crafting links [observed / inferred]

**[observed]** Fluid storage is a separate component context. Items can carry
`component FluidContainer` with `Capacity`, `ContainerName`, initial-percentage
fields and nested `Fluids` assignments; see
[items.md](items.md#components-inside-items). Entity components use the same
component name with a different observed key subset; see [entities.md](entities.md).
Definitions of fluids, definitions of their containers, and crafting consumption
lines are separate parts of the data.

**[observed]** [crafting.md](crafting.md#inputs-outputs-and-selectors) describes
minus-prefixed fluid inputs attached to an item input. **[inferred]** Follow the
container/resource relationship rather than treating an item identifier and a
fluid identifier as interchangeable. **[unknown]** This survey does not derive
transfer units, mixture matching or consumption rates from names alone.

## Energy definitions [observed]

Each of the seven `energy` definitions has `DisplayName`, `Color`, `iconTexture`,
`horizontalBarTexture` and `verticalBarTexture`. `Color` uses colon-separated
numeric components; the three texture properties contain resource paths.
The shared lexical classifier records those multi-colon values as `string`,
which is a fallback category, not a claim that they lack color structure.
**[unknown]** These seven definitions do not demonstrate energy consumption in
the module-level vanilla craft recipes in the crafting inventory. The Java grammar accepts
more resource forms than this subset of source files exercises.

**[inferred]** Tables share the script inventory's structural limitations and describe
textual occurrences before overrides. Consult [parser-keys.md](parser-keys.md)
for accepted fields and conversions, rather than using absent source keys as
evidence of rejection or defaults.

**[observed]** There are 61 `Categories` blocks, 56 `BlendWhiteList` blocks and 61 fluid definitions.
