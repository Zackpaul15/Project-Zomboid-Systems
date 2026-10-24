# Crafting formats (Project Zomboid, Build 42)

Survey date: 2026-10-24. Build identifier: jar sha256 prefix `e1a69eb7`.
Sources: installed `media/scripts/**/*.txt`; cross-check against
[Claude's parser reference](parser-keys.md) and `data/script-keys.csv`.
Optional parser confirmations use the read-only `Recipe` and `CraftRecipe`
decompiles. Claims are **[observed]** unless marked **[inferred]** or **[unknown]**.
All examples below are invented shapes, not copied vanilla definitions.

## Inventory and tables [observed]

| Block type | Blocks | Immediate parent | Example source filename |
|---|---:|---|---|
| `craftRecipe` | 969 | `module` | `generated/recipes/recipes_carpentry.txt` |
| `recipe` | 0 | Not observed | None |
| `evolvedrecipe` | 63 | `module` | `generated/evolvedrecipes.txt` |
| `fixing` | 29 | `module` | `generated/fixing.txt` |

Every observed craft recipe has `time`, `Tags` and an `inputs` block. There are
958 `outputs` blocks, 225 `itemMapper` blocks and three `overlayMapper` blocks.
These are textual occurrences, before overrides, filtering or runtime merging.
No recipe in this survey is nested inside an entity component.

Run `python -I modding/tools/survey_crafting.py` from the repository root:

- [recipe-keys.csv](../data/recipe-keys.csv): `block_type, key, count, value_shape, notes`.
- [recipe-grammar-identifiers.csv](../data/recipe-grammar-identifiers.csv): mode and flag identifiers, with occurrence counts by input/output context.
- [recipe-parser-coverage.csv](../data/recipe-parser-coverage.csv): every observed direct key checked against Claude's parser-key catalogue, ignoring case.

Paths such as `craftRecipe/inputs` distinguish nested grammar. `<block>` counts
whole definitions; `<child:...>` counts child blocks; `<line:...>` counts entries.
Mapper keys are reduced to `<mapping-key>` except for the grammar key `default`.
No concrete mapper associations, recipe names or source values are exported.
Shapes are lexical: `namespaced-id` here can describe a skill-and-level pair,
not necessarily a registry identifier. Semicolons inside a value are not commas
between script entries. The generator fails on unclassified resource lines or
option tokens rather than silently dropping them.

## `craftRecipe`: the outer definition [observed]

Observed direct keys fall into these groups; counts and spellings are in the CSV:

- Work and presentation: `time`, `timedAction`, `category`, `Icon`, `Tooltip`, `recipeGroup`, `overlayStyle`.
- Skills and learning: `SkillRequired`, `xpAward`, `NeedToBeLearn`, `AutoLearnAll`, `AutoLearnAny`, `ResearchAny`, `ResearchSkillLevel`.
- Routing and behavior: `Tags`, `MetaRecipe`, `AllowBatchCraft`, `OnCreate`, `OnTest`.

`time` is written as an integer in all 969 definitions. **[unknown]** The data
survey does not establish its conversion to wall-clock seconds. `timedAction`
occurs 889 times; values name action definitions. `SkillRequired`, `xpAward` and
the auto-learning fields use `Name:number` entries, with semicolons between
multiple entries. `OnCreate` and `OnTest` use dotted callback names.
**[unknown]** Their callback argument contracts are not determined by this survey.

An invented module-level shape follows. The item references, tag and action name
are placeholders that need corresponding definitions before this can be a mod:

```text
module Guide
{
    craftRecipe AssembleMarker
    {
        time = 45,
        timedAction = GuideAssembly,
        category = GuideCrafts,
        Tags = GuideWorkbench,
        inputs
        {
            item 2 [Guide.Slat] mode:destroy,
            item 1 [Guide.Mallet] mode:keep flags[Prop1],
        }
        outputs
        {
            item 1 Guide.Marker,
        }
    }
}
```

**[inferred]** The useful distinction is between an input that is consumed and
one retained as a tool. Tool-like inputs in the files combine `mode:keep` with
selectors and optional flags such as `Prop1`, `Prop2`, `MayDegradeLight` and
`IsNotDull`. Retention does not imply that durability cannot change.
**[unknown]** A flag's name alone is not a complete account of its effects.

## Inputs, outputs and selectors [observed]

There are 3,410 input entries: 3,355 begin with `item` and 55 with `-fluid`.
All 988 output entries begin with `item`. Amounts use integers, decimals on input
fluid lines, or `variable[min:max]`. There are more output entries than output
blocks because a block can emit multiple results.

The following invented lines illustrate the observed syntax variants. They are
individual comma-terminated entries to put inside the appropriate child block:

| Context | Invented shape | What the source establishes |
|---|---|---|
| Input alternatives | `item 2 [Guide.Slat;Guide.Strip] mode:destroy,` | Brackets and semicolons group candidate identifiers |
| Input item tags | `item 1 tags[guide:cuttingtool] mode:keep,` | `tags[...]` can occupy the selector position |
| Input categories | `item 1 categories[GuideCategory] mode:keep,` | `categories[...]` is another selector form |
| Variable input | `item variable[1:8] [Guide.Offcut] flags[ItemCount] mode:destroy,` | Amounts can use bracketed ranges |
| Container input | `item 1 [*],` | A wildcard item selector occurs before fluid attachment lines |
| Attached fluid input | `-fluid 0.3 [GuideSolvent] mode:mixture,` | The minus-prefixed line follows an item input |
| Ordinary output | `item 1 Guide.Marker,` | Output identifiers need not use an input-style bracket list |
| Variable output | `item variable[1:8] Guide.Token,` | Variable quantities occur on outputs too |
| Mapped output | `item 1 mapper:guideShapes,` | The output selects a named mapper |

**[observed, parser confirmation]** `CraftRecipe.LoadIO` strips the leading `-`
and attaches the resulting input as `consumeFromItemScript` to the previous
ordinary item input. A missing previous input or duplicate attachment is an
error. A minus line is not a standalone fluid requirement. **[inferred]** Treat
the preceding item and its fluid attachment as one container/resource relationship.

Input option tokens observed here are `mode:`, `flags[]`, `tags[]`,
`categories[]`, `mappers[]` and the bare marker `overlayMapper`. The mode values
are `keep`, `destroy` and, for attached fluid lines, `mixture`.
Output options in these files consist of `flags[]`. The grammar-identifiers CSV
records the observed flag spellings individually. Input flags and output flags
belong to different sets; do not transfer a flag between them solely because its
name looks appropriate.

**[observed, Claude's parser reference]** The engine also recognizes resource and
option forms not exercised by this tree, including energy lines and additional
fluid modes. `chance:`, `shapedIndex:`, `apply:` and plus-prefixed lines are not
observed in this survey. Absence from this CSV is not a claim that the parser
rejects them; use [parser-keys.md](parser-keys.md#5-craftrecipe-micro-grammar) for
the larger grammar and its restrictions.

## Mapper blocks [observed]

Inputs with `mappers[...]` occur alongside named `itemMapper` children and output
selectors of the form `mapper:<name>`. Mapper assignments use item identifiers
as keys and single identifiers or semicolon lists as values; a `default` key is
also observed. Not every item-mapper block contains `default`.
An invented structural example is:

```text
itemMapper guideShapes
{
    Guide.Marker = Guide.Slat;Guide.Strip,
    default = Guide.Marker,
}
```

The three `overlayMapper` blocks have `default` entries and item-keyed mappings
to string identifiers. Their recipes also use the input marker `overlayMapper`
and outer `overlayStyle`. An invented child-block shape is
`overlayMapper { default = GuidePlain, Guide.Slat = GuideStriped, }`.
**[unknown]** The data alone does not establish all mapper selection or overlay
precedence rules. **[observed, Claude's parser reference]** `fluidMapper` and
`energyMapper` throw “Not yet implemented” in this build; they are not working
alternatives to the observed item mapper.

## Recipe tags versus item tags [observed]

Outer `Tags` uses plain string identifiers or semicolon lists; all 969 craft
recipes have it. Input `tags[...]` instead uses namespaced item-tag identifiers,
the same lexical family as item `Tags` in [items.md](items.md#tags-and-references).
`category` is another field, not an alias for either tag collection.
**[inferred]** Keep recipe routing labels, input item tags and presentation
categories separate when designing definitions. **[unknown]** This survey does
not prove that adding an arbitrary outer tag creates a workstation or UI route.

## Legacy `recipe` [observed / unknown]

**[observed]** No `recipe` blocks occur under this install's `media/scripts`.
The CSV therefore has an explicit zero block row rather than invented key counts.
**[observed, parser confirmation]** The current `Recipe.Load` handles source
entries and recognizes `Override:`; it reports other colon-key entries as errors.
`DoSource` understands a count after `=`, `keep`/`destroy` prefixes, alternatives
separated by `/`, and use quantities after `;`.

An invented source-grammar illustration, not a complete working recipe, is:

```text
recipe GuideLegacyShape
{
    Guide.Slat/Guide.Strip=2,
    keep Guide.Mallet,
    destroy Guide.Wrapper,
    Guide.Paste;0.2,
}
```

**[unknown]** There is no vanilla example here demonstrating a usable legacy
result path. Do not assume older `Result:`/`Time:` tutorials work in this build;
use `craftRecipe` as the observed current definition format.

## `evolvedrecipe` [observed]

All 63 blocks have `BaseItem`, `ResultItem`, `MaxItems`, `Name` and `Template`.
Optional observed keys are `Cookable`, `CanAddSpicesEmpty`,
`AddIngredientIfCooked`, `MinimumWater` and `AddIngredientSound`.
Item properties such as `EvolvedRecipe` provide the other side of these
associations, using recipe labels and numeric annotations.
**[inferred]** This is the ingredient-combination family, rather than another
spelling of `craftRecipe` inputs and outputs. An invented definition shape:

```text
evolvedrecipe GuideMeal
{
    BaseItem = Guide.Bowl,
    ResultItem = Guide.PreparedMeal,
    MaxItems = 4,
    Name = Prepare Guide Meal,
    Template = GuideMeal,
    Cookable = true,
    MinimumWater = 0.4,
}
```

An invented item-property association is `EvolvedRecipe = GuideMeal:6,`.
**[unknown]** The survey does not establish units or consumption behavior from
that numeric annotation alone, or whether the invented template would resolve.

## `fixing` [observed]

The 29 repair definitions have 29 `Require` assignments and 45 `Fixer`
assignments. `ConditionModifier` occurs nine times and `GlobalItem` eight times.
`Require` can contain a qualified identifier or semicolon list. `Fixer` entries
combine an item identifier, a semicolon, and skill requirements written with `=`;
some item segments also carry a count after `=`. An invented shape is:

```text
fixing GuideRepair
{
    Require = Guide.Marker,
    Fixer = Guide.RepairKit=2; Woodwork=1,
    ConditionModifier = 0.7,
    GlobalItem = Guide.Adhesive=1,
}
```

**[unknown]** The observed shapes do not establish the condition-restoration
formula or failure odds. Repeated `Fixer` assignments remain separate occurrences
in the CSV; they are not collapsed into one property per block.

## Cross-check and validation

**[observed]** Every observed direct key for craft recipes, evolved recipes and
fixing blocks appears in Claude's parser-key CSV when compared without case.
The extractor advertises additional accepted keys and grammar, so source coverage
is a subset rather than a replacement for the engine reference. A handoff review
flags the missing minus-input discussion in the parser prose; its owner should
make that update.

**[inferred]** Reproduction inherits the structural reader's delimiter limits;
it does not execute recipes, resolve callbacks or validate invented examples in
the game. The examples demonstrate grammar only and need registered resources.

**[observed]** Three source claims selected with seed `20261024` are checked
independently against installed text before commit; the exact selected claims
and results are recorded in `HANDOFF.md`. Generated CSVs are rerun and compared
byte-for-byte before marking X3 complete.
