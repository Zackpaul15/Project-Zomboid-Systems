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

## Planned (in progress by the other agent or later)

Script formats (`scripts/`), vanilla Lua library map (`lua-library/`), mod workflow (`workflow/`), script parser
keys, lifecycle and multiplayer docs, and a cookbook. See `SCOPE.md` for the packages.

## Regenerating tables

Python 3, run as `python -I`, from `modding/tools/`:

- `extract_events.py <decompiled src> ../data/events.csv <game media/lua>`
- `extract_exposed.py <decompiled src> ../data`
- `gen_class_docs.py ../data ../lua-api/classes`

The decompile is made outside the repo (Vineflower; see `SCOPE.md`, "Shared workspace").
