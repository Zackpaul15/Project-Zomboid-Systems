# Brief for Codex: Project Zomboid modding reference

Read `modding/SCOPE.md` first, then follow the full task prompt in `modding/CODEX_PROMPT.md` (work packages,
table column specs, git protocol). Summary: you own work packages **X1-X8** and the folders `modding/lua-library/`,
`modding/workflow/`, and the `scripts/` files named in those packages. Claude owns **C0-C6** (Java decompile,
events, Lua-exposed classes, script parsers). Do not edit paths you do not own; use `modding/HANDOFF.md`.

## Inputs

- Game install (read-only): `F:\SteamLibrary\steamapps\common\ProjectZomboid`
  - Lua: `media\lua\{client,server,shared}`; scripts: `media\scripts\**`; mod samples: `media\luaexamples`,
    `Workshop\ModTemplate`, `mods\examplemod`; `stdlib.lua`.
- Optional: Claude's decompile of `zombie/**` at `C:\Users\zackp\Documents\Code stuff\tools\pz-work\src\` once
  `STATUS.txt` says it is done. Use it only to confirm how a script key is parsed.
- Existing notes for style: `README.md`, `notes\*.md`.

## Rules

- Original notes and tables only. Never copy game Lua/script/Java bodies or assets into this repo. Names, shapes,
  counts and one-line summaries only.
- Tag claims **[observed]** / **[inferred]** / **[unknown]**. Put the survey date and game build at the top of
  every doc.
- Tables are produced by scripts under `modding/tools/` (Python, run as `python -I`) and written to
  `modding/data/`. Commit the script with the table.
- Scratch files go in `C:\Users\zackp\Documents\Code stuff\tools\pz-work\codex-scratch\`, never in the repo.
- Verify 3 random claims in each doc against the game files before calling it done.
- Git: you and Claude both work on `main`; stage only explicit paths in your own folders (`git add <path>`, never
  `git add -A`), check `git status` first and leave the other agent's modified files alone; never push.

## Suggested start

X1 (block-type survey of `media\scripts`), then X2-X4 in order; X5-X8 can run in any order afterwards.
Report progress by appending a line per finished WP to `modding/HANDOFF.md`:
`[done] X2 modding/scripts/items.md, modding/data/item-properties.csv`.

## Workshop doctrine (when a run is orchestrated by Hermes)

This repo is one **project** in the Hermes agent workshop. The binding doctrine lives outside the repo:

    C:\Users\zackp\hermes\doctrine\README.md      authority table + index
    C:\Users\zackp\hermes\doctrine\SITUATIONS.md  playbooks: what to do in specific situations
    C:\Users\zackp\hermes\doctrine\PROTOCOLS.md   packet / evidence / review / commit
    C:\Users\zackp\hermes\doctrine\GOVERNANCE.md  Tier 1 hard stops

If a packet and the doctrine disagree, **the doctrine wins and the packet is a bug.** The supervisor injects
that doctrine into every dispatched packet; this pointer exists so a CLI started by hand in this repo also
sees it.

Non-negotiables, in addition to the rules above: never call `kanban_complete` / `kanban_block` yourself (the
supervisor owns lifecycle); prove a claim or mark it **UNVERIFIED**; absence of evidence is not evidence of
absence — say *what* is unverified rather than asserting *that* something is wrong; stay strictly inside the
paths your packet declares; never edit governance files.

