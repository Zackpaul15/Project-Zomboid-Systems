# Handoff log (Claude <-> Codex)

Append-only. One line per event. Prefixes: `[done]`, `[question]`, `[review]`, `[resolved]`, `[note]`.
Claude owns C0-C6; Codex owns X1-X8 (see `SCOPE.md`).

[done] C0 decompile of zombie/**, astar, fmod, N3D into the shared workspace (see pz-work\STATUS.txt)
[done] C1 modding/lua-api/events.md, modding/data/events.csv, modding/tools/extract_events.py
[done] C2 modding/lua-api/how-binding-works.md, modding/data/lua-globals.csv, modding/tools/extract_exposed.py
[done] C3 modding/data/exposed-classes.csv, modding/data/exposed-methods.csv, modding/lua-api/classes/ (60 pages), modding/tools/gen_class_docs.py
[note] Claude: decompile also includes the bundled Kahlua in pz-work\src\se (read-only for Codex).
[note] Claude next: C4 script parsers (scripts/parser-keys.md, data/script-keys.csv), then C5, C6.
[done] X1 modding/scripts/overview.md, modding/data/script-blocks.csv, modding/data/script-files.csv, modding/tools/survey_scripts.py; checked (randomized order): food ItemType; craftRecipe inputs nesting; ISPanel skin nesting; independent item-header count 5105; all 1004 files classified.
[done] C4 modding/scripts/parser-keys.md, modding/data/script-keys.csv, modding/tools/extract_script_keys.py; checked: non-.txt warn+skip, unknown script object is a warning, fluidMapper/energyMapper throw "Not yet implemented". Note for X3/X4: media\scripts in this install holds only entities/generated/ragdolls/xui sub-folders.
