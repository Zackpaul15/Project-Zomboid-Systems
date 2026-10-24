# Prompt for Codex (paste as the first message, or let it read `AGENTS.md`, which points here)

Start Codex with the repo root as its working directory:
`C:\Users\zackp\Documents\Code stuff\Reverse Engineer\ProjectZomboid`. Everything below the line is the prompt.

---

You are **Codex**, working next to **Claude** on a docs-only reference for **Lua modding of Project Zomboid
(Build 42)**. The repo is `Zackpaul15/Project-Zomboid-Systems`, checked out in your working directory. Claude
decompiles the Java side and documents the Lua binding, events and script parsers. **You document the game's data
files and its vanilla Lua library**, working only from the game's `media\` folder. We both commit to `main`, split by
folder ownership, so we never edit the same file.

Read these first, in order: `AGENTS.md`, `modding/SCOPE.md`, `README.md` (style of the existing notes), then skim
`modding/lua-api/events.md` and `modding/lua-api/how-binding-works.md` (Claude's finished docs) to match their
tone, tags and table style.

## Inputs (read-only)

- Game: `F:\SteamLibrary\steamapps\common\ProjectZomboid`
  - Scripts: `media\scripts\**` (text blocks: items, recipes, vehicles, sounds, fluids, entities, ...)
  - Lua: `media\lua\{client,server,shared}`; samples: `media\luaexamples`, `Workshop\ModTemplate`,
    `mods\examplemod`; engine Lua helpers such as `stdlib.lua`
- Claude's decompile of the Java (for confirming how a script key is parsed; optional):
  `C:\Users\zackp\Documents\Code stuff\tools\pz-work\src\` (see `STATUS.txt` beside it). Treat it as read-only.
- Claude's tables you can cross-check against: `modding/data/events.csv` (every event Java fires),
  `modding/data/lua-globals.csv` (Lua global functions), `modding/data/exposed-classes.csv`,
  `modding/data/exposed-methods.csv` (Java API visible to Lua).

## Hard rules

1. **Docs only.** Never copy game Lua, script text, Java, textures, sounds or other assets into the repo. Allowed:
   identifiers (property names, block types, class/function/event names), counts, value *shapes*
   (`int`, `list of Type;Type`, `bool`), short descriptions in your own words, and at most one-line identifier lists.
   No per-item value dumps and no verbatim script blocks.
2. **Tag claims**: **[observed]** (you read it in game files), **[inferred]**, **[unknown]**. Put the survey date and
   game build at the top of every doc. Get the build from the install (`version.txt`, `media\...`, or the jar manifest);
   if you cannot find it, record "jar sha256 prefix e1a69eb7".
3. **Tables come from scripts.** Python 3, run as `python -I`, saved in `modding/tools/`, reading the game folder and
   writing CSV into `modding/data/`. Commit the script with its output. Re-running must reproduce the file.
4. **Scratch outside the repo**: `C:\Users\zackp\Documents\Code stuff\tools\pz-work\codex-scratch\`. Never commit
   scratch, caches or logs.
5. **Verify**: before you mark a doc done, pick 3 random claims in it and re-check each against the game files.
   Note the check in your HANDOFF line.
6. Searching the whole `media\` tree with a naive recursive grep can take minutes. Prefer `rg`, or script it.

## Folders you own (do not edit anything else)

`modding/lua-library/`, `modding/workflow/`, and these files under `modding/scripts/`: `overview.md`, `items.md`,
`crafting.md`, `vehicles.md`, `sounds.md`, `fluids.md`, `entities.md`. Data files `modding/data/<your names>` and
scripts `modding/tools/<your names>`. Claude owns `modding/lua-api/`, `modding/scripts/parser-keys.md`,
`notes/`, and the root `README.md`/`SCOPE.md`. If you need a change in a file you do not own, add a line to
`modding/HANDOFF.md`; do not edit it.

## Work packages (do in this order; X5-X8 are independent of each other)

For every WP: write the doc(s), generate the table(s) with a script, check 3 claims, commit, and add a HANDOFF line.

**X1 — script block survey** → `modding/scripts/overview.md`
Classify every `.txt` under `media\scripts` by the block type(s) it contains (`item`, `recipe`, `craftRecipe`,
`vehicle`, `sound`, `fluid`, `entity`, `evolvedrecipe`, `fixing`, `model`, `animation`, `mannequin`, `module`, ...).
Give: block type, file count, block count, example file *names* (not contents), nesting (blocks inside blocks),
module naming (`module Base { ... }` and how other modules are referenced), comment/syntax rules you can confirm.
Done when every script file is classified. Data: `modding/data/script-blocks.csv`
(`block_type, files, blocks, folder_hint, nested_in`).

**X2 — items** → `modding/scripts/items.md`, `modding/data/item-properties.csv`
Observed property names across all `item` blocks. CSV: `property, count, types_seen_on, value_shape, example_shape`
(`value_shape` is a shape such as `int|float|bool|string|list;|ref-to-item|tag-list`, `example_shape` is a *pattern*
like `0.5` or `Base.Axe;Base.Hammer`, never a unique per-item value). In the doc: which properties are common to all
items, which belong to one `Type` (Weapon, Food, Clothing, Container, Literature, Drainable, Moveable, Radio,
Normal, ...), tags (`Tags`), and how `DisplayName`/icons/models/sounds link to other scripts and translations.

**X3 — crafting** → `modding/scripts/crafting.md`, `modding/data/recipe-keys.csv`
Document `craftRecipe` (inputs, outputs, tools, skills, time, categories, `timedAction`, `tags`), legacy `recipe`,
`evolvedrecipe`, `fixing`, plus the tag system. CSV: `block_type, key, count, value_shape, notes`. For each syntax
variant give an *invented* example in the right shape (do not paste a vanilla block). Cross-check keys against
Claude's `scripts/parser-keys.md` when it exists; list differences in HANDOFF as `[review]`.

**X4 — vehicles, sounds, fluids, entities** → `modding/scripts/vehicles.md`, `sounds.md`, `fluids.md`,
`entities.md` (+ `_xuiSkin`/component blocks), data CSVs named `vehicle-keys.csv`, `sound-keys.csv`,
`fluid-keys.csv`, `entity-keys.csv` with the same columns as X2/X3. Include characters/outfits/zone scripts only
if they exist as script blocks.

**X5 — UI layer** → `modding/lua-library/ui.md`
`media\lua\client\ISUI`, `OptionScreens`, XUI skin scripts. Give the widget class inheritance list (parent → child
table), how a panel is created and added (`new`, `initialise`, `instantiate`, `addToUIManager`), and entry points
for ISContextMenu and the radial menu. Include a minimal "add a context menu entry" recipe written in your own
words with an invented snippet of at most ~10 lines. Link to `modding/lua-api/events.md` for the context-menu events.

**X6 — vanilla Lua library map** → `modding/lua-library/overview.md`, `timed-actions.md`, `index.csv`
Per folder (`client`, `server`, `shared`): module inventory, key global tables, the `ISBaseTimedAction` family and
how a timed action is queued, and a "where does X happen" index (building, crafting, fishing, farming, vehicles,
...). `index.csv`: `side, path, main_globals, one_line_role`, **one row per .lua file**.

**X7 — distributions and event usage** → `modding/lua-library/distributions.md`,
`modding/data/vanilla-event-subscriptions.csv`
Loot and spawn tables (`Distributions`, `ProceduralDistributions`, `SuburbsDistributions`, vehicle and clothing
distributions): table shapes and how mods extend them (shapes only, no table dumps). CSV: `event, file, side`
for **every** `Events.<Name>.Add(` in vanilla Lua (`side` = client/server/shared from the folder). Then compare
against `modding/data/events.csv` and put a short "events nobody subscribes to / subscribed names that Java never
fires" list in the doc.

**X8 — mod workflow** → `modding/workflow/*.md` (suggested: `mod-layout.md`, `mod-info.md`, `load-order.md`,
`workshop-upload.md`, `sandbox-vars.md`, `translations.md`, `debug-mode.md`, `b41-vs-b42.md`)
Mod folder layout for B42 (including the versioned subfolders if present), every `mod.info` key observed, how and
in what order `media\lua` files load, walkthrough of `ModTemplate` and `examplemod` (describe, do not copy),
Workshop upload files, sandbox-vars, translation file layout, debug mode flags, and B41→B42 differences visible in
the files. Done when a new modder can create and load a hello-world mod from the docs alone.

## Progress, git and review

- After each WP append one line to `modding/HANDOFF.md`:
  `[done] X2 modding/scripts/items.md, modding/data/item-properties.csv; checked: <3 claims>`
  Problems or questions: `[question] <path>: ...`. Findings about Claude's files: `[review] <path>: ...`.
  Claude replies there; a `[review]` becomes `[resolved]` when its owner fixes it.
- Git: work on `main`. Before committing run `git status`; other changes belong to Claude, leave them. Stage
  explicit paths only: `git add <paths>` (never `git add -A` or `git commit -a`). Commit one WP at a time with
  `git commit -m "X2: item property survey" -- <your paths>` so nothing Claude staged rides along. Add a trailer
  naming yourself (for example `Co-Authored-By: Codex <noreply@openai.com>`). **Never push.** If a commit fails
  on `index.lock`, wait a few seconds and retry; Claude may be committing.
- Do not rewrite or delete Claude's commits; no force operations.
- Ask the user only when blocked on something the files cannot answer. Otherwise decide, record the assumption in
  your doc as **[inferred]**, and move on.

## Definition of done for the whole task

All of X1–X8 committed on `main`, each doc has date/build/tags and a 3-claim check recorded, every CSV is
reproducible by its script, and `modding/HANDOFF.md` lists a `[done]` line per package. Start now with X1.
