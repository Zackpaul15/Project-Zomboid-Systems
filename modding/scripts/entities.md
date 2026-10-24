# Entities, components and XUI (Project Zomboid, Build 42)

Survey date: 2026-10-24. Build identifier: jar sha256 prefix `e1a69eb7`.
Source: installed `media/scripts/**/*.txt`; XUI name comparison uses Claude's
`data/script-keys.csv`. Claims are **[observed]** unless marked **[inferred]**
or **[unknown]**. No entity definitions, sprite rows or UI assets are reproduced.

## Coverage and reproduction [observed]

The survey finds **219 module-level `entity` blocks in 194 files**, **254
`xuiSkin` blocks in 246 files**, and **one `xuiConfig` block in one file**.
There are no `template entity`, `xuiLayout`, `xuiStyle`, `xuiDefaultStyle` or
`xuiGlobalColors` blocks in this tree. Those are source-coverage statements, not
claims about parser support. Example files are
`generated/entities/admin/entity_piano.txt`,
`entities/admin/entity_piano_xuiSkin.txt`, `xui/defaultskin/xs_ISPanel.txt`
and `xui/xui_config.txt`.

Run `python -I modding/tools/survey_components.py` to generate:

- [entity-keys.csv](../data/entity-keys.csv): `block_type, key, count, value_shape, notes`.
- [component-blocks.csv](../data/component-blocks.csv): family totals, file counts and example filenames.
- [xui-config-coverage.csv](../data/xui-config-coverage.csv): config variable identifiers compared to Claude's extracted `xui-var` names.

Context paths keep component type names, for example
`entity/component:FluidContainer`, but omit concrete entity, style and sprite
instance names. `<block>` counts blocks and `<entry>` counts bare entries; neither
is a literal property. For `xuiConfig`, bare identifiers are exported individually
as declared variable names under their typed group. Assignment counts retain
repeated keys such as sprite `row`, without exporting the referenced tile names.

## Component composition [observed]

All surveyed entities consist of component children; none has a direct assignment.
There are **726 component blocks**, distributed as follows:

| Component type | Blocks | Observed role/fields |
|---|---:|---|
| `UiConfig` | 215 | `uiEnabled`, `xuiSkin`, `entityStyle` |
| `SpriteConfig` | 210 | Sprite faces/layers plus construction and behavior fields |
| `CraftRecipe` | 202 | Crafting fields and `inputs` child |
| `CraftBench` | 35 | `Recipes` associations |
| `ContextMenuConfig` | 14 | `contextEntry` children |
| `FluidContainer` | 11 | Capacity, initial fill, rain and locking fields |
| `CraftBenchSounds` | 9 | Sound identifiers for workbench actions |
| `SpriteOverlayConfig` | 8 | Style/progress/face/layer structure |
| `WallCoveringConfig` | 8 | `sign`, `type` |
| `Resources` | 7 | Resource groups and optional whitelist structure |
| `DryingCraftLogic` | 7 | `Recipes`, `StartMode`, `actionAnim`, `inputGroup`, `outputGroup` |

The role summaries describe source organization; **[unknown]** they do not
establish construction order, update scheduling or multiplayer ownership.
See [parser-keys.md](parser-keys.md#6-entity-and-components) for parser context.

## Construction recipes and workstation data [observed]

`component CraftRecipe` is a component header with a capitalized type name, not
another occurrence of the module-level lowercase `craftRecipe` block counted in
[crafting.md](crafting.md). Its 202 instances have 202 `inputs` blocks containing
675 bare input entries; no `outputs` child occurs in this component subset.
Observed direct keys are `time`, `timedAction`, `category`, `Tooltip`, `Tags`,
`SkillRequired`, `xpAward`, `NeedToBeLearn` and `OnAddToMenu`. `time` occurs in all
202; unlike the module-level recipes, `Tags` is not universal here.
**[inferred]** Keep entity construction inputs separate from standalone crafting
results when reading or counting the data. **[unknown]** Do not infer the entity
creation path or callback contract solely from those matching field names.

`CraftBench` and `DryingCraftLogic` refer to recipe associations through `Recipes`.
`CraftBenchSounds` has `AddFuel`, `AddInput`, `LightFire`, `RemoveInput`,
`Running` and `StartCraft`. **[unknown]** These keys alone do not establish a
complete workbench registration or crafting lifecycle.

## Sprites, menus and fluid storage [observed]

`SpriteConfig` uses `face` children with `layer` children and repeated `row`
assignments. Its observed keys include `LogicClass`, `OnCreate`, `OnIsValid`,
`TimedActionOnIsValid`, `health`, `bonusHealth`, `skillBaseHealth`,
`canBePadlocked`, `needWindowFrame`, `needToBeAgainstWall`, `previousStage`
and light-source fields. **[inferred]** The nested face/layer/row structure
describes sprite arrangements; this reference deliberately omits those arrays.

`ContextMenuConfig/contextEntry` has `menu`, `icon`, `customFunction`,
`customSubmenu`, `extraParam` and `time`. These are separate script components
from the Lua `ISContextMenu` widget itself. **[unknown]** The data survey does not
establish parameter types or callback arguments for every context entry.

Entity `FluidContainer` properties include `Capacity`, `ContainerName`,
`FillsWithCleanWater`, `HiddenAmount`, `InputLocked`, `InitialPercentMin`,
`InitialPercentMax` and `RainFactor`; some have nested `Fluids` blocks.
Compare [fluids.md](fluids.md) and the item component table in [items.md](items.md).
**[unknown]** A shared component name does not imply that all observed keys occur
on every kind of owner or that a missing field has a particular default.

## XUI skins and variable declarations [observed]

`_xuiSkin` occurs as a filename suffix; the script block type is **`xuiSkin`**.
Skin children include widget-class headers such as `ISPanel`, `ISButton`,
`ISItemSlot` and `ISTableLayout`, plus `entity`, `colors` and `imports` blocks.
For example, `ISPanel` has boolean anchoring/background fields and color
identifiers. `entity` skin children have fields including `DisplayName`,
`Description`, `BuildDescription`, `Icon` and `LuaWindowClass`; some have nested
`components`. `colors` maps symbolic color keys to values; `imports` contains
bare skin identifiers.

`UiConfig` components use `xuiSkin` and `entityStyle` identifiers.
**[inferred]** These link entity data to skin/style definitions, which in turn
name Lua widget/window classes. **[unknown]** This source survey does not prove
style-resolution order or override precedence. Skin attributes do not replace
the widget's Lua implementation.

The `xuiConfig` file groups **229 declared variable identifiers** into eight typed
blocks: `String`, `StringList`, `TranslateString`, `Double`, `Boolean`,
`FontType`, `Color` and `Texture`. These are declarations of property names, not
229 skin instances or values. The source comments distinguish ordinary strings
from translated strings.

Compared with Claude's 198 extracted `xui-var` names, **177 names overlap**,
**52 occur only in config**, and **21 only in the parser catalogue**.
`xui-config-coverage.csv` lists the individual identifier differences, using exact
spelling. **[unknown]** This discrepancy alone cannot distinguish stale config,
dynamic extension, inherited registration or extractor coverage. A handoff review
asks Claude to reconcile the two sources; neither list is labeled invalid here.

## Other character-related script blocks [observed]

The tree also has **97 `character_trait_definition` blocks** in
`generated/characters/character_traits.txt` and **25
`character_profession_definition` blocks** in
`generated/characters/character_professions.txt`. Their observed keys are included
in the entity-family CSV, under their actual block types. Trait fields include
`CharacterTrait`, `Cost`, `UIName`, `UIDescription`, `IsProfessionTrait`,
`DisabledInMultiplayer`, `MutuallyExclusiveTraits`, `XPBoosts`, `GrantedRecipes`
and `GrantedTraits`. Profession fields include `CharacterProfession`, `Cost`,
`UIName`, `UIDescription`, `IconPathName`, `XPBoosts`, `GrantedRecipes` and
`GrantedTraits`.

No module-level outfit or zone script type occurs in the X1 inventory.
**[unknown]** This is not a survey of outfit XML, map zones or Lua distributions
outside `media/scripts`, and does not imply those systems are absent.

## Limits and checks

**[inferred]** All shapes are lexical and inherit the X1 structural reader's
limitations. No parser defaults, numeric units or lifecycle behavior are inferred
from absent keys. Concrete values, sprite rows and per-entity mappings stay in
the installed game rather than the repository.

**[observed]** Three source checks selected with seed `20261024`: 202 entity
`CraftRecipe` components, 229 XUI config variable identifiers and 219 entity
blocks. An independent module-depth scan confirms family block/file counts;
all six X4 CSVs reproduce byte-for-byte. Checks are recorded in `HANDOFF.md`.
