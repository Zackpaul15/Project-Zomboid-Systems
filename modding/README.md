# Project Zomboid Lua modding reference (Build 42)

Docs-only reference generated from the game install and a decompile of its Java. No game code or assets are
included; only names, shapes, counts and original explanations. Claims are tagged **[observed]**, **[inferred]** or
**[unknown]**. How the work is split: [`SCOPE.md`](SCOPE.md). Progress log: [`HANDOFF.md`](HANDOFF.md).
Prompt for the second agent: [`CODEX_PROMPT.md`](CODEX_PROMPT.md).

## Lua API (from the Java side)

| Doc | Contents | Table |
|---|---|---|
| [`lua-api/how-binding-works.md`](lua-api/how-binding-works.md) | How Java classes, statics, constructors, overloads and global functions reach Lua | [`data/lua-globals.csv`](data/lua-globals.csv) (759 globals) |
| [`lua-api/events.md`](lua-api/events.md) | The event system, 262 registered events, orphan and unregistered findings | [`data/events.csv`](data/events.csv) |
| [`lua-api/classes/`](lua-api/classes/README.md) | One page per commonly used exposed class (60) | [`data/exposed-classes.csv`](data/exposed-classes.csv) (999 classes), [`data/exposed-methods.csv`](data/exposed-methods.csv) |

## Script formats (from the Java side)

| Doc | Contents | Table |
|---|---|---|
| [`scripts/parser-keys.md`](scripts/parser-keys.md) | How `media/scripts` is loaded, block syntax, unknown-key behaviour, `craftRecipe` line grammar, entity/vehicle/XUI structure | [`data/script-keys.csv`](data/script-keys.csv) (every key, nested block, line word and flag the parsers compare) |

The data-file side (what vanilla scripts contain: `overview.md` and later pages in `scripts/`) is written by the
other agent.

## Planned (in progress by the other agent or later)

Vanilla Lua library map (`lua-library/`), mod workflow (`workflow/`), lifecycle and multiplayer docs, and a
cookbook. See `SCOPE.md` for the packages.

## Regenerating tables

Python 3, run as `python -I`, from `modding/tools/`:

- `extract_events.py <decompiled src> ../data/events.csv <game media/lua>`
- `extract_exposed.py <decompiled src> ../data`
- `gen_class_docs.py ../data ../lua-api/classes`
- `extract_script_keys.py <decompiled src> ../data/script-keys.csv`

The decompile is made outside the repo (Vineflower; see `SCOPE.md`, "Shared workspace").
