# Project Zomboid Lua modding reference (Build 42)

Docs-only reference generated from the game install and a decompile of its Java. No game code or assets are
included; only names, shapes, counts and original explanations. Claims are tagged **[observed]**, **[inferred]** or
**[unknown]**. Survey date: 2026-10-24. Game build: Build 42 (jar sha256 prefix `e1a69eb7`; no version file was
found, see [`SCOPE.md`](SCOPE.md)). How the work is split: [`SCOPE.md`](SCOPE.md). Progress log: [`HANDOFF.md`](HANDOFF.md).

## Lua API (from the Java side)

| Doc | Contents | Table |
|---|---|---|
| [`lua-api/how-binding-works.md`](lua-api/how-binding-works.md) | How Java classes, statics, constructors, overloads and global functions reach Lua | [`data/lua-globals.csv`](data/lua-globals.csv) (759 globals) |
| [`lua-api/events.md`](lua-api/events.md) | The event system, 262 registered events, orphan and unregistered findings | [`data/events.csv`](data/events.csv) |
| [`lua-api/lifecycle.md`](lua-api/lifecycle.md) | Boot, load-game, reload, multiplayer-client and dedicated-server order: when each Lua folder loads and each lifecycle event fires | (uses [`data/events.csv`](data/events.csv)) |
| [`lua-api/sandbox-options.md`](lua-api/sandbox-options.md) | The sandbox option system: types, defaults vs the Apocalypse preset, `SandboxVars` vs the Java copy, persistence, network, mod `sandbox-options.txt` | [`data/sandbox-options.csv`](data/sandbox-options.csv) (269 options) |
| [`lua-api/multiplayer.md`](lua-api/multiplayer.md) | Networking for Lua: the client/server command round trip, `args` encoding, global ModData, object/square/item ModData transmit, the global-object channel, single-player behaviour | (uses [`data/lua-globals.csv`](data/lua-globals.csv) and [`data/events.csv`](data/events.csv)) |
| [`lua-api/classes/`](lua-api/classes/README.md) | One page per commonly used exposed class (60) | [`data/exposed-classes.csv`](data/exposed-classes.csv) (999 classes), [`data/exposed-methods.csv`](data/exposed-methods.csv) |

## Script formats (from the Java side)

| Doc | Contents | Table |
|---|---|---|
| [`scripts/parser-keys.md`](scripts/parser-keys.md) | How `media/scripts` is loaded, block syntax, unknown-key behaviour, `craftRecipe` line grammar, entity/vehicle/XUI structure | [`data/script-keys.csv`](data/script-keys.csv) (every key, nested block, line word and flag the parsers compare) |

## Vanilla data, Lua library and mod workflow

| Group | Start here | Contents |
|---|---|---|
| Script data (what vanilla scripts contain) | [`scripts/overview.md`](scripts/overview.md) | Block-type map of `media/scripts`, then per-topic pages: [`items.md`](scripts/items.md), [`crafting.md`](scripts/crafting.md), [`entities.md`](scripts/entities.md), [`fluids.md`](scripts/fluids.md), [`sounds.md`](scripts/sounds.md), [`vehicles.md`](scripts/vehicles.md) and [`key-coverage.md`](scripts/key-coverage.md) (script keys compared across the Java parsers, vanilla Lua and vanilla script data) |
| Vanilla Lua library map | [`lua-library/overview.md`](lua-library/overview.md) | Inventory of the vanilla `media/lua` folders; [`timed-actions.md`](lua-library/timed-actions.md), [`ui.md`](lua-library/ui.md), [`distributions.md`](lua-library/distributions.md); file index [`index.csv`](lua-library/index.csv) |
| Mod workflow | [`workflow/mod-layout.md`](workflow/mod-layout.md) | Folder layout, [`mod-info.md`](workflow/mod-info.md), [`load-order.md`](workflow/load-order.md), [`translations.md`](workflow/translations.md), [`sandbox-vars.md`](workflow/sandbox-vars.md), [`debug-mode.md`](workflow/debug-mode.md), [`workshop-upload.md`](workflow/workshop-upload.md), [`b41-vs-b42.md`](workflow/b41-vs-b42.md) |
| Generated tables | [`data/`](data/) | CSV tables written by the scripts in `tools/` (see "Regenerating tables"); each doc above links the tables it uses |
| Cookbook | [`cookbook/README.md`](cookbook/README.md) | Six short recipes (item, craftRecipe, context-menu entry, event hook, sandbox option, client-to-server command). **Untested: none of the recipes was run in the game; they are not runtime-verified.** The practical starting point for a first mod |

## The native layer (Java -> JNI -> engine DLLs)

Much modder-facing behaviour stops at the Java boundary and continues in C++ DLLs reached through JNI `native`
methods. These docs map that layer: which `native` declarations exist, which DLL owns each one, what their
arguments do, and whether a mod can actually reach them from Lua. The DLL passes used Ghidra; per the repo rules
only names, offsets, counts and one-line summaries are recorded here, never bodies or disassembly.

| Doc | Contents | Table |
|---|---|---|
| [`../notes/native-boundary.md`](../notes/native-boundary.md) | The JNI boundary itself: every `native` declaration, per-DLL attribution and how confident that attribution is. Start here | [`data/native-boundary.csv`](data/native-boundary.csv) (392 natives) |
| [`../notes/native-reachability.md`](../notes/native-reachability.md) | Can a mod reach this native, and through what path? Includes the end-to-end `Lua/Java entry -> native -> effect` chains for the traced vehicle and ballistics natives | [`data/native-reachability.csv`](data/native-reachability.csv) |
| [`../notes/bullet-native.md`](../notes/bullet-native.md) | `PZBullet64.dll` export inventory: 103 exports, 98 of them resolving to declarations | [`data/bullet-exports.csv`](data/bullet-exports.csv) |
| [`../notes/bullet-vehicle.md`](../notes/bullet-vehicle.md) | Vehicle-control natives (`controlVehicle`, `setTireInflation`, `applyImpulse`, ...): what each argument changes | [`data/bullet-vehicle-io.csv`](data/bullet-vehicle-io.csv) |
| [`../notes/bullet-ballistics.md`](../notes/bullet-ballistics.md) | Ballistics and aiming natives (`updateBallistics*`, `setBallistics*`, targets): what each argument changes | [`data/bullet-ballistics-io.csv`](data/bullet-ballistics-io.csv) |
| [`../notes/lighting-native.md`](../notes/lighting-native.md) | `Lighting64.dll` export inventory: 50 exports, every one resolving to a `LightingJNI` declaration | [`data/lighting-exports.csv`](data/lighting-exports.csv) |
| [`../notes/popman-native.md`](../notes/popman-native.md) | **[observed]** `PZPopMan64.dll` export inventory: 59 exports resolving all 59 R0 declarations, including 17 `MapCollisionData` natives; earlier population notes reconciled | [`data/popman-exports.csv`](data/popman-exports.csv) |
| [`../notes/lighting.md`](../notes/lighting.md) | Lighting behaviour: light placement, colour/active state and the darkness multipliers — what each argument changes | [`data/lighting-io.csv`](data/lighting-io.csv) |
| [`../notes/bullet-ragdoll.md`](../notes/bullet-ragdoll.md) | Ragdoll configuration: creation/mass/transform natives and how ragdolls are defined in scripts — what each argument changes | [`data/bullet-ragdoll-io.csv`](data/bullet-ragdoll-io.csv) |

Earlier engine notes cover the other DLLs: [`../notes/population.md`](../notes/population.md) and
[`../notes/functions-popman.md`](../notes/functions-popman.md) for `PZPopMan64.dll`,
[`../notes/pathfinding.md`](../notes/pathfinding.md) and [`../notes/functions-pathfind.md`](../notes/functions-pathfind.md)
for `PZPathFind64.dll`, plus [`../notes/zombie-ai.md`](../notes/zombie-ai.md) for the Java-side zombie AI.
`PZClipper64.dll` and the networking DLLs, plus `Lighting64.dll`'s remaining square/visibility natives and
`PZBullet64.dll`'s remaining natives, are catalogued in the boundary map but not yet described in detail.

## Working on this repo (two agents)

[`tools/collab.py`](tools/collab.py) reads `SCOPE.md` and `HANDOFF.md` and runs the checks both agents agreed on. It
never pushes and never stages anything you did not name.

- `python -I modding/tools/collab.py status`: packages done, open `[review]` lines, uncommitted files by owner.
- `python -I modding/tools/collab.py next --agent codex`: a ready-to-paste prompt for that agent's next job.
- `python -I modding/tools/collab.py gates [--agent A] [--all]`: owner, date/build header, links, CSV shape,
  long code fences, local paths.
- `python -I modding/tools/collab.py commit --agent A --wp ID --message TEXT PATH... [--yes]`: gates, then commit
  exactly those paths (dry run without `--yes`).

## Regenerating tables

Python 3, run as `python -I`, from `modding/tools/`:

- `extract_events.py <decompiled src> ../data/events.csv <game media/lua>`
- `extract_exposed.py <decompiled src> ../data`
- `gen_class_docs.py ../data ../lua-api/classes`
- `extract_script_keys.py <decompiled src> ../data/script-keys.csv`
- `extract_sandbox_options.py <decompiled src> <game media/lua> ../data/sandbox-options.csv`
- `native_boundary.py <decompiled src root> <projectzomboid.jar> <javap.exe> ../data/native-boundary.csv`

`native_boundary.py` is the only generator for the native layer. The other native tables
(`bullet-exports.csv`, `bullet-vehicle-io.csv`, `bullet-ballistics-io.csv`, `native-reachability.csv`) were built by
the analysis passes themselves and are not script-regenerated; their method, checks and confidence rules are
recorded in the matching doc under `../notes/`.

The decompile is made outside the repo (Vineflower; see `SCOPE.md`, "Shared workspace").
