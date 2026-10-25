# Script parser keys: how the Java side reads `media/scripts` (Build 42)

Survey date: 2026-10-24. Game: Project Zomboid Build 42 (Java 25 class files; jar sha256 prefix e1a69eb7).
Source: Java declarations and control flow in `zombie/**`. Names, shapes and counts only; no game code or script text is copied.
Claims are tagged **[observed]** (supported by Java control flow), **[inferred]** (deduced from that evidence) or **[unknown]**.

Companion table: [`../data/script-keys.csv`](../data/script-keys.csv). It lists every key, nested block, line-grammar
word and enum flag a parser compares against, with the Java class, reader method and documented Java line. Per-folder
content of the vanilla files is documented in `overview.md`, `items.md`, `crafting.md` and related pages; this page is
the engine-side contract those pages should be consistent with.

## 1. Loading pipeline

1. **File selection** [observed]. `ScriptManager.LoadFile` only reads files ending in `.txt`; a `.tmx` file only
   records a map path. Any other extension logs a warning "file is not a .txt (script) file" and is skipped. Mods are read after the base game, in load order (see the
   workflow docs for order).
2. **Comment stripping** [observed]. `ScriptParser.stripComments` removes `/* ... */` comments and handles nesting.
   There is no line-comment syntax in this stage [inferred: no `//` handling was found in it].
3. **Top-level tokens** [observed]. Only tokens that begin with the word `module` are accepted: `module <Name> { ... }`.
   A module with the same name as an earlier one is reused (so many files and mods can add to `Base`).
4. **Module body** [observed]. `ScriptModule.Load` splits the body into top-level blocks by brace depth
   (`ScriptParser.parseTokens`). The block type is the first whitespace-delimited word of each token.
5. **Dispatch** [observed]. `imports { A, B }` adds module imports (importing itself is an error). Any other block
   type goes to the first `ScriptBucket` whose `ScriptType` tag equals that word. An unmatched type logs a warning
   "unknown script object" and is skipped; it is not fatal.
6. **Two-phase construction** [observed]. The bucket creates the instance and registers its name at once
   (`InitLoadPP`), and keeps the body text. After every file is read, `LoadScripts` calls `script.Load(name, body)` for
   each stored body. The same name declared twice therefore gets **both bodies applied in order** to one object
   [observed: duplicate bodies are appended], which is how a later file overrides or extends a block.
7. **Skips** [observed]. A script is skipped when it is marked obsolete, when it sets `enabled = false`, or when it sets
   `debugOnly = true` and the game is not in debug mode.
8. **Name lookup** [observed]. A name containing `.` is resolved through the manager as `Module.Name`; a bare name is
   looked up in the current module, then in its `imports`.
9. **Reload flags** [observed]. Each bucket carries flags (ResetExisting, RemoveLoadError, SeekImports,
   NewInstanceOnReload, ResetOnceOnReload, AllowNewScriptDiscoveryOnReload) that control debug script reloading; their
   per-type values are in `ScriptType`/`ScriptBucket`. Template buckets (`template vehicle <name> { }`,
   `template entity <name> { }`) share the same mechanism.

## 2. Block syntax

- A block is `type name { ... }` (some types have no name or a different second word; see sections 4 and 5).
  Values are `key = value,` entries separated by commas; `ScriptParser.readBlock` splits the header on whitespace
  and each entry on the **first** `=` only [observed].
- Nested blocks use the same shape. The block header is `type id` and `readBlock` exposes them as `child.type` and
  `child.id` [observed].
- Item parsing splits entries with `split("=")`, so text after a **second** `=` in one value is dropped [observed in
  `Item.DoParam`; other blocks that use `getKey/getValue` keep it] [inferred consequence: do not put `=` in an item
  value].
- Key matching is mostly case-insensitive (`equalsIgnoreCase`); the `case_sensitive` column in the CSV records the
  exceptions per key [observed].
- Every block accepts the two common keys `enabled` and `debugOnly` [observed; `BaseScriptObject`].

## 3. What happens to an unknown key

| Block | Behaviour | Tag |
|---|---|---|
| `item` | Checked against the attribute registry first, then ~389 explicit keys; anything else is stored as free-form mod data on the item (not an error) | [observed] |
| `recipe` (legacy) | In Build 42 the legacy `recipe` parser only handles source lines and an `Override` key; other keys are not read | [observed] |
| `entity` | A child block that is not `component` logs an error "Unknown block ... in entity script"; loading continues | [observed] |
| `craftRecipe` | Unknown child block: error log, thrown only in debug mode; unknown key/line word inside `inputs`/`outputs`: exception | [observed] |
| most others | The key is ignored or logged; check `reader` + `java_line` in the CSV for the specific class | [inferred] |
| top-level type | Warning "unknown script object"; block skipped | [observed] |

Whether a logged key problem is visible without debug mode is **[unknown]**.

## 4. Top-level block types

The ScriptType tags the loader accepts (full key lists in the CSV, column `block`). Counts are keys + nested blocks
present in the catalogue; `xui` counts are registered variables.

| Block (tag) | Parser class | Notes |
|---|---|---|
| `item` | `Item` | 389 keys, one nested `component <Type>` block; also the attribute registry (17 names) |
| `recipe` | `Recipe` | Legacy; sources + `Override` only [observed] |
| `craftRecipe` | `CraftRecipe` | 30 keys, nested `inputs`/`outputs` and four mapper blocks (section 5) |
| `entity`, `template entity` | `GameEntityScript` | `entitytemplate` key, `component <ComponentType>` blocks (section 6) |
| `evolvedrecipe` | `EvolvedRecipe` | 12 keys |
| `uniquerecipe` | `UniqueRecipe` | 5 keys |
| `fixing` | `Fixing` | 4 keys (`Require`, `Fixer`, `GlobalItem`, `ConditionModifier`) |
| `model` | `ModelScript` | 14 keys, nested `attachment` |
| `animationsMesh` | `AnimationsMesh` | 5 keys |
| `animation` | `RuntimeAnimationScript` | nested `CopyFrame` / `CopyFrames` |
| `mannequin` | `MannequinScript` | 7 keys |
| `sound`, `soundTimeline` | `GameSoundScript`, `SoundTimelineScript` | sound: 14 keys + nested `clip` |
| `vehicle`, `template vehicle` | `VehicleScript` | 155 keys, 21 nested block types (section 7) |
| `vehicleEngineRPM` | `VehicleEngineRPM` | 3 keys |
| `fluid`, `energy` | `FluidDefinitionScript`, `EnergyDefinitionScript` | fluid 23 keys + 5 nested blocks; energy 8 keys |
| `itemFilter`, `fluidFilter`, `stringList` | filter / list scripts | list-style blocks |
| `physicsShape`, `physicsHitReaction`, `ragdoll` | physics scripts | ragdoll has 31 keys |
| `timedAction` | `TimedActionScript` | 15 keys |
| `clock`, `spriteModel` | `ClockScript`, `SpriteModel` | clock: 8 keys, nested `hand` |
| `character_trait_definition`, `character_profession_definition` | definition scripts | 11 and 8 keys |
| `itemConfig` | `ItemConfig` | `include`, nested `variables`/`includes`, root buckets such as `container`, `room`, `tile`, `vehicle`, `zone` |
| `xuiConfig`, `xuiLayout`, `xuiStyle`, `xuiDefaultStyle`, `xuiGlobalColors`, `xuiSkin` | `Xui*Script` | 198 registered xui variables (section 8) |

Exact tag spellings and the buckets that own them are in `ScriptType.java` [observed]. A tag that does not appear in
vanilla `media/scripts` files in this install can still be valid; this install's `media/scripts` holds only some
sub-folders (entities, generated, ragdolls, xui) [observed], so vanilla coverage of the other types comes from
other locations described by the vanilla script inventory.

## 5. `craftRecipe` micro-grammar

`craftRecipe <name> { ... }` is a normal block, except its `inputs` and `outputs` blocks hold **lines** that a custom
parser (`InputScript.Load`, `OutputScript.Load`) tokenizes on whitespace. Words are in the CSV with `kind = token`;
enum constants with `kind = flag` (69 input flags, 12 output flags).

- First word is the resource type: `item`, `fluid` or `energy` [observed]. Anything else throws "unknown type in
  craftrecipe". Attached `-` input lines (below) also accept `uses` as the first word, meaning an item.
- Second word is the amount: a number, or `variable[min:max]` [observed, outputs]; negative values are clamped to 0.
- Third word is the resource: item list (inputs) or `mapper:<name>` (outputs, resolved against the recipe's mapper
  blocks; a missing mapper is an error), a fluid name, or an energy name.
- Remaining words are options, matched by prefix: `mode:<value>`, `chance:<0..1>` (outputs, clamped),
  `shapedIndex:<int>`, `apply:onTick` (outputs: energy only, it throws for item and fluid outputs), `flags[A;B;...]`,
  `tags[...]`, `categories[...]`, `mappers[...]`, `overlayMapper...` [observed]. An unknown word throws
  "unknown recipe param".
- `mode:` values depend on the resource type [observed]. Items: use, keep, destroy, prop1, prop2, useprop1, useprop2,
  keepprop1, keepprop2; fluids: exact, primary, anything, plus mixture on inputs; energy: keep on inputs. Output `mode:` accepts only the fluid values and ignores it for items. Values for a
  resource type that does not support them throw (some only when the game is in debug mode).
- A `+` output line attaches an "item create" to the previous output line; the previous line must have amount 1, be an
  item, and not apply on tick [observed in `OnPostWorldDictionaryInit`]. On the attached line the item type's third
  word should be `Uses` (a mismatch throws only in debug mode), no mapper lookup happens, and `apply:` throws
  [observed, `OutputScript.Load` internal path]. A `-` line in `outputs` throws.

Input-side attachments [observed, `CraftRecipe.LoadIO`, `InputScript.Load`]. Inside an `inputs` block a line that
starts with `-` or `+` is not a new input; it attaches to the **previous** input line:

- `-<line>` sets that input's "consume from" line. The rest of the line uses the normal input grammar, parsed in
  internal mode (the resource may be `item`, `fluid`, `energy` or `uses`; the attached line starts out as
  accept-any-item, and an explicit list adds to that). The attached line is not added to the recipe's inputs; it is kept as a child of the previous input.
- `+<line>` on an input sets that input's "create to" line, parsed with the output grammar's internal path (see the
  `+` output bullet above for what that changes).
- Load errors (thrown, so the script fails): no previous input line; the previous input already has a `-` (or a `+`)
  attachment.
- Checks that run after the world dictionary is built: one input cannot carry a `-` and a `+` of the same resource
  type; a line followed by `-` or `+` must be an item input with amount 1, not variable, and not apply on tick; its
  item mode becomes Keep (a `-` keeps Destroy if it was already set).
- When the previous input accepts any item and the attached `-`/`+` line is a fluid or energy, the candidate items are
  limited to items with a fluid container (fluid) or drainable items (energy) [observed].
- In this install `media/scripts` holds **55** `-fluid` lines in 13 files and **no** `+`
  lines [observed by a text count]. The attached `-` lines carry the same words as ordinary lines (amount, list,
  `mode:`, `categories[...]`), so no new key is needed in the CSV.
- `flags[...]` entries must be valid constants of `InputFlag` / `OutputFlag`; an unknown constant throws from
  `valueOf` [observed].

Mapper blocks [observed, `CraftRecipe`]:

- `itemMapper <name> { ... }` is an output mapper that `mapper:<name>` output lines refer to. Entries are
  `<key> = A;B;C` (the value is a `;`-separated list of item names; a `kind$` prefix before an item is stripped, and
  `fluid$` / `energy$` prefixes throw "Not yet implemented") plus one `default = <item>` entry. A mapper with no
  entries is an error.
- `overlayMapper { ... }` maps overlay styles: `default = <style>` plus `<A;B;C> = <style>` pairs (the key is a
  `;`-separated list). An empty overlay mapper is an error.
- `fluidMapper` and `energyMapper` blocks throw "Not yet implemented" in this build.
- Any other child block logs an error "Unknown block ... in craft recipe", and throws only in debug mode.

## 6. `entity` and components

`entity <name> { ... }` accepts `entitytemplate <name>` (copy another entity's components) and
`component <ComponentType> { ... }` blocks. `ComponentType` names the registered components, and each component
has its own parser class under `scripting/entity/components/**` [observed]. Components with documented
key sets (CSV block `entity > component <Name>`): ContextMenuConfig, CraftBench, CraftLogic, DryingLogic,
FluidContainer, FurnaceLogic, MashingLogic, Resources, SpriteConfig, SpriteOverlayConfig, UiConfig,
WallCoveringConfig, plus a development `TestComponent` [observed]. Components registered in `ComponentType` that are
absent from that list have no established key comparisons in the catalogue (they may read keys another way)
**[unknown]**.

## 7. `vehicle`

`vehicle <name> { ... }` holds 155 keys over its top level and nested blocks: model, skin, anim, attachment, area,
part (with nested table/lua/container/window/door/model/anim/sound blocks), passenger (position, switchSeat), wheel,
physics (shape ids `box`, `sphere`, `mesh`), lightbar, sound, crawlThroughWheel [observed]. A `template vehicle <name>`
can be copied into another vehicle by block kind (area, part, ...); the copy source is the second word of the block
header [observed]. See the CSV `reader` column for which key belongs to which nested block.

## 8. XUI scripts

XUI element variables are not compared with strings; they are registered one by one with typed `Xui*` helper
objects in `XuiScript`. The CSV `xui-var` rows list the 198 names with their type in `value_type` (boolean 46, color 39, float 37, texture 23, unit 21, translatestring 10, string 7,
fonttype 5, plus vector, spacing, integer, stringlist, textalign, vectorposalign) [observed]. Layout/style scripts share that set; `xuiSkin` adds its own 15 keys and
nested `colors`, `components`, `entity`, `imports` [observed].

### `xuiConfig` versus the parser variables

These are two separate registries, so a difference between them is expected rather than an error [observed]:

- **Parser variables (the 198).** Each `XuiScript` instance registers its own typed variables in its constructor
  (`addVar`). These are the keys a layout, style or default-style script can set on one element. The CSV `xui-var`
  rows come from here (195 from `XuiScript`, 3 from `XuiTableScript`).
- **Config variables (the 229).** An `xuiConfig <name> { ... }` block lists names under typed sub-blocks (`String`,
  `StringList`, `TranslateString`, `Double`, `Boolean`, `FontType`, `Color`, `Texture`). `XuiManager.ParseScripts` hands
  every config to `XuiLuaStyle.ReadConfigs`, which adds each name to a static registry of Lua-style variables
  (cleared on reset). A name listed under two types, in one block or across configs, throws.
- **What the registry gates.** `XuiSkin` loads each skin style into an `XuiLuaStyle` through `loadVar(key, value)`. A
  key that is neither already on that style nor in the registry throws "not registered or key typo". So `xuiConfig`
  is the allow-list for the keys a skin may set on a Lua UI class, and the types there are coarser (a `Double` covers
  what the parser splits into float, integer, unit and others).
- **Reading the overlap.** Of the 229 config names, 177 also exist as parser variables (a skin overriding a layout
  property) and 52 are config-only: mostly `style*` selectors, `enable*`/`do*`/`hide*` switches and colours that Lua
  UI classes read from their style [inferred from the names; which Lua code reads each one is **[unknown]**]. The 21
  parser-only names are layout-only (`xuiKey`, `xuiStyle`, `xuiLuaClass`, `xuiCellStyle`, `xuiColumnStyle`,
  `xuiRowStyle`, `xuiCustomDebug`, the `icon_*`/`image_*` position and size names, `vector`, `vectorPosAlign`,
  `textAlign`, `borderLocked`); they are not in the registry, so a skin style line using one would fail the
  registry check above [observed from the registry code, names from `xui-config-coverage.csv`].
- **Not resolved.** Whether the config-only names are all still read by some Lua file was not checked
  **[unknown]**; the difference between the two lists alone does not show a stale entry.

## 9. Not ScriptManager scripts

A few formats reuse `ScriptParser` but load through their own classes: custom perks, custom sandbox options, the
active-mods list, sprite models, tile seams, seating, tile depth assignments, tile geometry, and fonts. The CSV
labels them `(file) ...` [observed].

## 10. Catalogue limits

- The catalogue covers string comparisons against the key variable (`param`, `key`, `k`) and block `type`.
  Keys resolved through `switch` over a variable, helper methods or lookup tables have no established coverage;
  their number is **[unknown]**.
- Value types are guessed from the code that follows each comparison (`value_type`) and are **[inferred]**.
- Placeholder literals used in dead or sample branches (`something`, `xxx`, `someType`, ...) are dropped.

## Confidence and limits (2026-10-24)

1. Non-`.txt` files warn and are skipped; `.tmx` sets a map path (`ScriptManager.LoadFile`).
2. `unknown script object` is a warning from `ScriptModule` (not an exception).
3. `fluidMapper`/`energyMapper` throw "Not yet implemented"; `itemMapper` and `overlayMapper` are parsed
   (`CraftRecipe` block loop). This corrected an earlier draft of this page that listed all four as working.
4. `inputs` lines starting `-`/`+` attach to the previous input (`CraftRecipe.LoadIO`); duplicate attachment and a
   missing previous input throw. The earlier note that `uses` belongs to `+` lines was wrong: `uses` is a first word on
   attached `-` input lines, and attached `+` output lines expect `Uses` as the third word.
5. `xuiConfig` names are registered into `XuiLuaStyle`'s static registry and gate skin keys; the 198 parser variables
   are registered per `XuiScript` instance. The two lists are different registries (`XuiLuaStyle.ReadConfigs`,
   `XuiSkin` `loadVar`).

## 11. Java-side interpretation of the unresolved key/event comparisons

Survey date: 2026-10-24. Build 42, jar sha256 prefix e1a69eb7.
This section retains the historical comparison described in [key-coverage.md](key-coverage.md),
before its corrected results. Names, shapes and counts only. Counts are historical CSV records of
[`../data/key-coverage.csv`](../data/key-coverage.csv), grouped by its `name`/`evidence` columns, not distinct keys.

### 11.1 Crosswalk gaps: Java readers that exist but are not in the ten-entry `CONTEXTS`

[observed] Java `unknown` rows grouped by `source_class`/`reader`:

| Java reader (`script-keys.csv`) | Unknown rows | Data path it would correspond to | Tag |
|---|---:|---|---|
| `VehicleScript` `Load` plus 13 sub-readers (`LoadPart`, `LoadModel`, `LoadSkin`, `LoadAnim`, `LoadWheel`, `LoadPassenger`, `LoadContainer`, `LoadPhysicsShape`, ...) | 179 | `vehicle`, `template vehicle` and nested `part`, `part/model`, `part/anim`, `part/container`, `passenger`, `wheel`, `skin`, ... in `vehicle-keys.csv` | reader set [observed]; path mapping [inferred] |
| `XuiScript` (empty reader) | 195 of the 198 `xui-var` rows | `xuiConfig/<type>` (`Boolean`, `Double`, `Color`, `Texture`, ...). The data side is a config registry, not a block of assignments | [inferred] |
| `XuiSkinScript` `Load`/`LoadComponentBlock`/`LoadEntityBlock` | 19 | `xuiSkin/<Panel>`, `xuiSkin/entity/components/<C>`, `xuiSkin/colors` | [inferred] |
| `FluidContainerScript` `load`, `loadBlockFluids`, `readFluidAsBlock` | 24 | `item/component:FluidContainer[/Fluids]` and `entity/component:FluidContainer[/Fluids\|whitelist]` | [inferred] |
| `FluidDefinitionScript` `Load`/`LoadProperties`/`LoadPoison` | 28 | `fluid`, `fluid/Properties`, `fluid/Poison` | [inferred] |
| `SpriteConfigScript`, `ContextMenuConfigScript`, `CraftLogicScript` and other component loaders | about 30 | `entity/component:SpriteConfig/...`, `.../ContextMenuConfig/contextEntry`, `.../DryingCraftLogic` | [inferred] |
| `GameEntityScript` `Load`/`LoadComponentBlock` | 3 | `entity`, `template entity` | [inferred] |
| `VehicleEngineRPM` `Load`/`LoadData` | 3 | `vehicleEngineRPM`, `vehicleEngineRPM/data` | [inferred] |

Two structural facts matter more than the individual rows:

- **`item / entity attributes` is a Java context the crosswalk never maps** [observed]. The 17 `kind=attribute` rows
  (`Attribute` `static init`, e.g. `script-keys.csv#record=771` HeadCondition, `#772` HeadConditionMax, `#773` OriginX,
  `#777` Sharpness) cannot match because the historical crosswalk requires `kind == "key"` and has no `CONTEXTS` entry for that
  block, although `Item.DoParam` consults the attribute registry first (section 3). The data side therefore reports
  `HeadCondition` (57 items), `Sharpness` (112) and `OriginX/Y/Z` (2 each) as `scope_or_grammar_unresolved` with exactly
  the right candidate record. [inferred] An `item` <- `item / entity attributes` equivalence is a context equivalence
  that exists but was never declared; it accounts for 8 `item` data rows. 11 further attribute rows are
  `no_observation` (registered, unused in the surveyed scripts).
- **The `kind == "key"` filter excludes every other kind by design** [observed]: `flag` 81, `token` 39, `block` 108,
  `block-id` 3, `xui-var` 198. These are line-grammar words, enum flags and nested block names, not assignments, so a
  key-to-key compare cannot resolve them. [inferred] They are the genuinely *grammar* part of
  `scope_or_grammar_unresolved`.

### 11.2 Scope vs unmapped, per bucket

| Bucket (rows) | Dominant Java-side cause | Scope or unmapped |
|---|---|---|
| `scope_or_grammar_unresolved`, Java 422 | `VehicleScript` sub-readers, `XuiScript` variables, fluid/component readers, attributes | **Unmapped** for vehicle, fluid, component, attribute (a data path exists). **Grammar** for xui-var, flag, token, block |
| `scope_or_grammar_unresolved`, data 1,010 | `xuiSkin` 523, `xuiConfig` 177, `vehicle` 108, `template vehicle` 105, `entity` 53, `fluid` 19, `item` 18 | Same split. `xuiSkin`/`xuiConfig` are read through registries (the registry distinction in Confidence and limits), so they are a **different registry**, not an unmapped block |
| `no_observation_in_input_catalogues`, Java 472 | Parser keys no surveyed script uses. In-crosswalk readers: 33 `Item.DoParam` and 15 `CraftRecipe` (`Animation`, `OnStart`, `OnFailed`, `OnUpdate`, `OnAddToMenu`, `consumeOnFinish`, `energyMapper`, `fluidMapper`, `itemMapper`, `inputs`, `outputs`, ...) | **Genuine scope**: the parser accepts keys vanilla does not use. `InputFlag`/`OutputFlag` enums (81 rows) are flags, not keys |
| `no_parser_match_in_input_catalogue`, data 385 | `xuiSkin` 103 keys + 60 markers, `xuiConfig` 52, `entity` 14 + 25 markers, `template vehicle` 25 + 22 markers, `vehicle` 12 + 19 markers | Mostly **structural markers** (167 positive-count) and registry-backed keys with no `key = value` compare |
| item keys with no parser candidate (`IsWaterSource`, `RainFactor`) | No `"IsWaterSource"` literal exists in `zombie/**`; `"RainFactor"` is compared only in `FluidContainerScript.load` | [inferred] Top-level use on an item is not read by `Item.DoParam` and falls to free-form mod data (section 3); the `item/component:FluidContainer` form is the parsed one. **Genuine** data/parser divergence worth a runtime check |

[observed] Events: of 87 `unknown`, 86 are Java rows and 1 is Lua (`OnVehicleHorn`, subscribed in
`server/Vehicles/Vehicles.lua`, no `events.csv` row). Of the Java rows, 50 are registered with a literal Java trigger
site but no Lua listener (legitimate scope: engine-only events), 31 are registered with neither, 3 (`OnChangeWeather`,
`OnDawn`, `OnDusk`) are registered with `lua_trigger_files=1` yet have no row in the Lua trigger table (the comment-only trigger discrepancy), and 2 are
unregistered Java triggers (dynamic-name callers, see the event reference). [unknown] Whether `OnVehicleHorn` is raised
from a name built at run time.

### 11.3 Evidence that would resolve the largest buckets

1. **Vehicle (about 290 rows incl. markers): a declared sub-reader crosswalk.** [inferred] The data block paths map
   onto the `VehicleScript.Load*` reader names (`LoadPart` -> `vehicle/part`, `LoadModel` -> `vehicle/part/model` or
   `vehicle/model` by call site, ...). The unresolved relation is between each reader and its calling context; `template vehicle` reuses the same readers [inferred].
2. **Attributes (17 + 8 rows): one declared equivalence** `item` <- `item / entity attributes`, `kind=attribute`.
3. **Component/fluid/entity (about 125 rows): reader-to-component mapping**, plus identity of `item/component:X` and
   `entity/component:X`. Both tables already name the component types.
4. **xui (about 1,000 rows): not resolvable by this comparison.** Config and skin names are registry entries compared by
   variable (the registry distinction in Confidence and limits); the right resolution is a registry-to-registry compare, which needs the Lua-side
   style/skin definitions as the data source.
5. **`no_observation` (472):** only a broader data corpus (mods, other builds) could change it. Correctly *unknown*
   rather than defective; not resolvable from vanilla alone.
6. **Dynamic-name events:** their actual runtime names are unestablished by static evidence. [unknown]

### 11.4 Supporting Java and script findings

1. `animalTrailerSize` is read in `VehicleScript.Load` with `equalsIgnoreCase` at the documented Java line 222, matching
   `script-keys.csv#record=913` (`java_line=222`, `case_sensitive=no`).
2. `HeadCondition` is registered in `Attribute`'s static initialiser at the documented Java line 24 (`#771`, `java_line=24`).
3. `RainFactor` is compared in `FluidContainerScript.load` at line 167, and vanilla
   `media/scripts/generated/items/drainable.txt` uses `RainFactor` and `IsWaterSource` as top-level item keys.
