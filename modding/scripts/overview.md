# Script-file map (Project Zomboid, Build 42)

Survey date: 2026-10-24. Build identifier: jar sha256 prefix `e1a69eb7` (no version file found; the jar manifest gives no game version). Sources: installed `media/scripts/**/*.txt`. Claims are **[observed]** unless marked **[inferred]** or **[unknown]**.

## Coverage [observed]

The survey covers all **1,004 `.txt` files**, **35,731 structural blocks** and **134 distinct block-header types**. Every file contains at least one block; none is unclassified. These are textual occurrences, including templates and repeated definitions, not counts of runtime objects after merging.

- [script-blocks.csv](../data/script-blocks.csv): block header, distinct files, occurrences, folders and immediate parent header types.
- [script-files.csv](../data/script-files.csv): one row per file, block count, types and classification. `root_values` exposes text outside blocks rather than silently dropping it.
- Generator: `python -I modding/tools/survey_scripts.py X1` (optional `--game PATH`). Sorting and LF CSV output are deterministic.

## Main families [observed]

`generated/items/*.txt` contains item definitions grouped by item type. There are **5,105 item blocks**. `generated/recipes/` and generated entity subfolders contain **969 module-level craftRecipe blocks**; no additional craftRecipe blocks are nested in components in this survey. Legacy `recipe` blocks do not occur in this tree. `evolvedrecipe` and `fixing` remain present.

Vehicles include `vehicle`, `template`, `vehicleEngineRPM` and nested parts, passengers, areas, models and physics. Audio has `sound`, `soundTimeline` and nested clips. Fluids have `fluid` with category, properties, blending and poison subblocks. Entities compose components; the craftRecipe definitions in generated entity subfolders are module-level blocks. XUI has `xuiSkin` and `xuiConfig`; widget class names are themselves nested headers. A numeric header under a vehicle loot `items` block is a structural header, not a ScriptModule registration.

Other module children include `animation`, `animationsMesh`, `model`, `mannequin`, `timedAction`, `energy`, `clock`, `physicsShape`, `physicsHitReaction`, `ragdoll`, `character_trait_definition` and `character_profession_definition`. The complete inventory, including every nested header, is in the CSV. There is no module-level outfit or zone block in this survey; Lua/XML definitions outside this tree are outside X1's coverage.

Example file names: `generated/items/food.txt`, `generated/recipes/recipes_carpentry.txt`, `generated/fluids.txt`, `generated/evolvedrecipes.txt`, `generated/fixing.txt`, `xui/xui_config.txt`, `xui/defaultskin/xs_ISPanel.txt`. These are locations, not copies of definitions.

## Names, nesting and punctuation [observed]

Files use `module Base` followed by a brace-delimited body. Module bodies contain named definitions; definitions can contain further blocks. The same module appears in many files. Item references use qualified identifiers such as `Base.<ItemId>`. Registry identifiers also use colon syntax, for example `base:<tag>` and `base:<item-type>`; those namespaces are distinct from dotted script references. **[unknown]** The data alone does not establish module import precedence or fallback rules for an unqualified reference.

Headers precede `{`; `}` ends the block. Values generally end with commas and use `key = value`. Some subblocks instead contain bare comma-separated entries (fluid categories, crafting input/output lines). Semicolons separate lists inside a value; brackets are used by crafting selectors. Whitespace, indentation and newlines separate readable tokens but are not a substitute for a comma in the survey parser. `/* ... */` comments occur, including explanatory comments in `xui/xui_config.txt`. **[unknown]** Do not infer support for Lua `--` or C++ `//` comments from these files.

## Limits and validation

**[inferred]** This generator describes source structure, not parser acceptance, defaults or runtime merge behavior. It removes nested block comments and walks braces/commas; it retains a final unterminated value for coverage. It fails on unmatched braces or comments. It does not implement quoted delimiter escaping, conditional loading, or game-specific validation. Successful structural parsing of every current file establishes survey coverage, not general compatibility with arbitrary mod syntax.

**[observed]** Three source checks: item headers and `ItemType` in `generated/items/food.txt`; `inputs`/`outputs` nested in `craftRecipe` in `generated/recipes/recipes_carpentry.txt`; `ISPanel` nested in `xuiSkin` in `xui/defaultskin/xs_ISPanel.txt`. Independent full-tree header counts are also used to check the principal totals before commit.
