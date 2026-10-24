# Modding reference repo: scope and work split

Goal: a shareable, docs-only reference for **Lua modding** of Project Zomboid (Build 42): items, recipes, UI, events,
and the Java API exposed to Lua. Original notes and tables generated from the game; **no game code, no game assets,
no verbatim script bodies**. Identifiers (class, method, event, field, item-type names) and shapes are fine.

Two agents work in parallel: **Claude** (Java decompile + Lua binding) and **Codex** (data-file and Lua-library
survey). Split along *input type* so neither needs the other's tooling output, and by *output folder* so we never edit
the same file.

## Shared ground rules

- Tags on every non-trivial claim: **[observed]** (read in game files/decompile), **[inferred]**, **[unknown]**.
- Write the game build + date the survey was taken at the top of each doc (read `version.txt`/jar manifest; if absent,
  record the jar sha256 prefix `e1a69eb7`).
- Decompile output, extracted jars and scratch data live **outside the repo**:
  `C:\Users\zackp\Documents\Code stuff\tools\pz-work\` (see "Shared workspace"). Never copy it into the repo.
- Do not paste game Lua/script/Java bodies. Summarise behaviour in your own words; quote at most a signature or a
  one-line identifier list.
- Generated tables go in `modding\data\` as CSV or JSON **with the script that produced them** in `modding\tools\`.
  Scripts run as `python -I` and read the game from `F:\SteamLibrary\steamapps\common\ProjectZomboid`.
- One owner per path (table below). Need a change in someone else's file? Leave a note in `modding\HANDOFF.md`
  instead of editing it.
- No `git commit` of the other agent's paths; commit only your own folders (see "Git").

## Shared workspace (set up once, by Claude)

`C:\Users\zackp\Documents\Code stuff\tools\pz-work\`

| Path | Contents |
|---|---|
| `jar\` | `projectzomboid.jar` unzipped (class files) |
| `src\` | Vineflower 1.12.0 output of all `zombie/**` (game packages only, no bundled libs) |
| `STATUS.txt` | what is done, failed classes, command used |

Tools: `...\tools\decompilers\vineflower-1.12.0.jar`, JDK 21 `java.exe` under `...\tools\jdk\jdk-21.0.12.1+1\bin\`.
Codex only *reads* `src\` when a script format needs confirming; its main inputs are the game's `media\` files.

## Folder ownership

| Folder | Owner | What goes there |
|---|---|---|
| `modding\lua-api\` | Claude | events, Java classes exposed to Lua, global Lua functions |
| `modding\scripts\` | split by file (see WPs) | format reference per script block type |
| `modding\lua-library\` | Codex | map of vanilla `media\lua` (client/server/shared) |
| `modding\workflow\` | Codex | mod folder layout, `mod.info`, load order, Workshop, B41->B42 differences |
| `modding\data\`, `modding\tools\` | whoever wrote the script | CSV/JSON + generator |
| `modding\README.md`, `SCOPE.md`, `HANDOFF.md` | Claude (index), both (HANDOFF) | |
| `notes\`, root `README.md` | Claude | existing native-code notes |

## Work packages

Sizes: S under 1 h, M 1-3 h, L over 3 h of agent time. Order inside an owner is the suggested order.

### Claude (needs the decompiled jar)

| ID | Package | Output | Done when |
|---|---|---|---|
| C0 | Full Vineflower decompile of `zombie/**` into the shared workspace (L, mostly waiting) | `pz-work\src`, `STATUS.txt` | failures listed; class count matches the jar survey |
| C1 | Lua event system: `LuaEventManager`, `Events`, every `triggerEvent` name and its argument list | `lua-api\events.md`, `data\events.csv` (name, args, trigger site class, client/server) | every event string literal in `zombie/**` is in the CSV |
| C2 | Exposure mechanism: `LuaManager`, `Exposer` / `LuaManager$Exposer`, how a Java class becomes callable, `@UsedFromLua`-style markers, global functions | `lua-api\how-binding-works.md`, `data\lua-globals.csv` | can explain how to find the Lua name of any Java method |
| C3 | Exposed class catalogue: every class registered with the exposer, public methods (name, params, return) | `data\exposed-classes.csv`, one `lua-api\classes\<Class>.md` for the ~40 most used (IsoPlayer, IsoGameCharacter, InventoryItem, IsoObject, IsoGridSquare, IsoCell, BaseVehicle, ...) | CSV covers 100% of registered classes; the ~40 docs list fields/groups of methods with one-line purpose each |
| C4 | Script parsers: `ScriptManager`, `ScriptModule`, `*Script` classes. Which block names exist, which keys each reads, value types, defaults, required keys | `scripts\parser-keys.md`, `data\script-keys.csv` (block, key, type, default, source class) | one row per key the parser reads; unknown keys behaviour recorded |
| C5 | Game-flow hooks for modders: client/server startup order, which Java calls fire which events, timed-action/ISUI Java side, `GameTime`, `ZomboidGlobals`, sandbox option registration | `lua-api\lifecycle.md`, `lua-api\sandbox-options.md` | an ordered startup timeline with the events fired |
| C6 | Networking for Lua: `sendClientCommand`/`sendServerCommand`, `onClientCommand`, ModData transmit | `lua-api\multiplayer.md` | request/response path documented client-to-server and back |

### Codex (needs only the game's `media\` folder and normal file reading)

| ID | Package | Output | Done when |
|---|---|---|---|
| X1 | Survey `media\scripts\**`: list every block type (`item`, `recipe`, `craftRecipe`, `vehicle`, `sound`, `fluid`, `entity`, `evolvedrecipe`, `fixing`, `model`, `animation`, `mannequin`, ...) with file locations and counts | `scripts\overview.md` | every `.txt` under scripts is classified |
| X2 | Item format: observed property names across all `item` blocks, value shapes, which properties vary by `Type` (Weapon, Food, Clothing, Container, Literature, ...) | `scripts\items.md`, `data\item-properties.csv` (property, types seen on, example value shape, count) | CSV built by a script over all item files |
| X3 | Recipe/crafting formats: `craftRecipe` (inputs/outputs/tools/skills), legacy `recipe`, `evolvedrecipe`, `fixing`; tag system | `scripts\crafting.md`, `data\recipe-keys.csv` | each syntax variant has a described example shape |
| X4 | Vehicles, sounds, fluids, entities (+ components, `_xuiSkin`), characters/outfits/zones if present | `scripts\vehicles.md`, `scripts\sounds.md`, `scripts\fluids.md`, `scripts\entities.md` | same standard as X2 |
| X5 | UI layer: `media\lua\client\ISUI`, `OptionScreens`, XUI skin scripts; widget class tree, how panels are created and added, ISContextMenu/Radial menu entry points | `lua-library\ui.md` | class inheritance list + a minimal "add a context menu entry" recipe |
| X6 | Vanilla Lua library map: per folder (`client`, `server`, `shared`) module inventory, key global tables, timed actions (`ISBaseTimedAction` family), Bite-size "where does X happen" index | `lua-library\overview.md`, `lua-library\timed-actions.md`, `lua-library\index.csv` (file, main globals/classes defined) | every file is in the index |
| X7 | Distribution/spawn tables (`ProceduralDistributions`, `Distributions`, loot, `SuburbsDistributions`), `Events.*` usage patterns in vanilla code (which events vanilla subscribes to) | `lua-library\distributions.md`, `data\vanilla-event-subscriptions.csv` (event, file) | every `Events.X.Add` in vanilla Lua is in the CSV |
| X8 | Workflow docs: mod folder layout, `mod.info` keys, `media\lua` load order, `ModTemplate` and `examplemod` walkthrough, Workshop upload files, sandbox-vars, translations, debug mode, B41->B42 changes visible in the files | `workflow\*.md` | a new modder can create and load a hello-world mod from the docs |

X5-X8 are independent; X1-X4 share the "block survey" and should go first.

### Joint (after both finish)

| ID | Package | Notes |
|---|---|---|
| J1 | Cross-check: events used by vanilla Lua (X7 CSV) vs events found in Java (C1 CSV); items/recipes keys read by the Java parser (C4) vs seen in data (X2/X3) | produce `scripts\key-coverage.md`; mismatches are valuable findings |
| J2 | "Cookbook": 5-8 short recipes (add an item, add a craftRecipe, add a context menu entry, hook an event, add sandbox option, send client->server command) cross-linked to the reference pages | Claude writes, Codex reviews |
| J3 | Top-level `modding\README.md` index, `.gitignore`, `git init`, review pass | Claude |

## Dependencies

```
C0 -> C1..C6        (all Claude work needs the decompile)
X1 -> X2, X3, X4
C4 <-> X2/X3        (only J1 needs both)
everything -> J1 -> J2 -> J3
```

Codex can start X1-X8 today with no dependency on Claude. Claude starts with C0.

## Git

- Repo root: `ProjectZomboid\` (so the existing `notes\` ride along; native notes stay).
- **Decided:** both agents work directly on `main`, separated by folder ownership only (no per-agent branches).
  Each agent stages explicit paths from its own folders (`git add <path>`, never `git add -A`), commits one WP at a
  time, and runs `git pull`-style conflict checks by looking at `git status` first; if the other agent's files show
  as modified, leave them alone. Nobody pushes without the user asking.
- `.gitignore`: `_*`, `*.class`, `*.jar`, `*.dll`, scratch dirs. Commit trailer for Claude commits:
  `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

## Review

- Each agent reviews the other's output on the shared WPs (J1, J2). Findings go in `HANDOFF.md` as
  `[review] <path>: <issue>`; the owner resolves and marks `[resolved]`.
- Spot-check rule: for each doc, verify 3 random claims against the game files before marking it done.

## Open decisions for the user

1. ~~Branches per agent?~~ Decided: both on `main`, folder ownership only.
2. Should identifier lists (all item type names, all vanilla item IDs) be included, or only property/format shapes?
   Plan assumes shapes plus identifiers needed for the API, and no per-item value dumps.
3. Target build: this install only, or also document B41 vs B42 differences where visible?
