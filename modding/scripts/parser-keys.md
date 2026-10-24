# Script parser keys: how the Java side reads `media/scripts` (Build 42)

Survey date: 2026-10-24. Game: Project Zomboid Build 42 (Java 25 class files; jar sha256 prefix e1a69eb7).
Source: Vineflower decompile of `zombie/**`. Names, shapes and counts only; no game code or script text is copied.
Claims are tagged **[observed]** (read in the decompile), **[inferred]** (deduced from it) or **[unknown]**.

Companion table: [`../data/script-keys.csv`](../data/script-keys.csv), made by
[`../tools/extract_script_keys.py`](../tools/extract_script_keys.py). It lists every key, nested block, line-grammar
word and enum flag a parser compares against, with the Java class, reader method and decompile line. Per-folder
content of the vanilla files is the other agent's area (`overview.md`, `items.md`, `crafting.md`, ...); this page is
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
the extractor found; `xui` counts are registered variables.

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
other places and is the other agent's survey.

## 5. `craftRecipe` micro-grammar

`craftRecipe <name> { ... }` is a normal block, except its `inputs` and `outputs` blocks hold **lines** that a custom
parser (`InputScript.Load`, `OutputScript.Load`) tokenizes on whitespace. Words are in the CSV with `kind = token`;
enum constants with `kind = flag` (69 input flags, 12 output flags).

- First word is the resource type: `item`, `fluid` or `energy` (an internal-only `uses` form exists for `+` lines)
  [observed]. Anything else throws "unknown type in craftrecipe".
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
  item, and not apply on tick [observed in `OnPostWorldDictionaryInit`].
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
has its own parser class under `scripting/entity/components/**` [observed]. Components the extractor found with
their own key sets (CSV block `entity > component <Name>`): ContextMenuConfig, CraftBench, CraftLogic, DryingLogic,
FluidContainer, FurnaceLogic, MashingLogic, Resources, SpriteConfig, SpriteOverlayConfig, UiConfig,
WallCoveringConfig, plus a development `TestComponent` [observed]. Components registered in `ComponentType` that are
absent from that list have no key comparisons the extractor recognized (they may read keys another way)
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

## 9. Not ScriptManager scripts

A few formats reuse `ScriptParser` but load through their own classes: custom perks, custom sandbox options, the
active-mods list, sprite models, tile seams, seating, tile depth assignments, tile geometry, and fonts. The CSV
labels them `(file) ...` [observed].

## 10. Extractor limits

- The extractor reads string comparisons against the key variable (`param`, `key`, `k`) and block `type`. Keys
  matched through `switch` over a variable, helper methods or lookup tables are not seen **[unknown]** how many.
- Value types are guessed from the code that follows each comparison (`value_type`) and are **[inferred]**.
- Placeholder literals used in dead or sample branches (`something`, `xxx`, `someType`, ...) are dropped.

## Verification log (re-checked against the decompile, 2026-10-24)

1. Non-`.txt` files warn and are skipped; `.tmx` sets a map path (`ScriptManager.LoadFile`).
2. `unknown script object` is a warning from `ScriptModule` (not an exception).
3. `fluidMapper`/`energyMapper` throw "Not yet implemented"; `itemMapper` and `overlayMapper` are parsed
   (`CraftRecipe` block loop). This corrected an earlier draft of this page that listed all four as working.
