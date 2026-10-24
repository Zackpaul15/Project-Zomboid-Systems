# Lua and mod load order

Survey date: 2026-10-24. Build: jar sha256 prefix `e1a69eb7`.
Sources: installed Lua `require`/event usage; engine order is cross-referenced to
Claude's [lifecycle.md](../lua-api/lifecycle.md). Claims are **[observed]** unless
tagged **[inferred]** or **[unknown]**. No source bodies are copied.

## Startup and folder order

**[observed, engine reference]** Ordinary client startup loads shared Lua and
then client Lua before `OnGameBoot`. Server-tree Lua is visited when a world
loads, including on multiplayer clients. A dedicated server hashes client Lua
for checksums but does not execute that folder. Thus the folder label by itself
is not a complete statement of execution authority.

Within one side, vanilla file paths are sorted case-insensitively. Active mods'
file lists follow in mod order. For each mod, common content is searched before
the selected version content, and its file list is sorted. This is a path sort,
not a dependency sort. A relative Lua name runs at most once per environment;
a cached return value is used when it is requested again.

**[inferred, engine reference]** A mod at the same relative Lua path as another
resource can shadow it through the active-file map; later-mod precedence was
not fully established in the lifecycle analysis. **[inferred]** Give addon files
unique relative paths and use `require` for the modules they need, rather than
depending on an alphabetically earlier filename or copying a vanilla file.

## Dependencies, hooks and reloads

**[observed]** Vanilla UI modules require dependencies by slash-separated module
name without the `.lua` suffix; `ISPanel` requires `ISUI/ISUIElement`.
`ISBaseTimedAction` requires `ISBaseObject`. The mod metadata parser recognizes
`require`, `loadModAfter` and `loadModBefore`; see [mod-info.md](mod-info.md).
**[unknown]** The sample mods do not exercise these metadata keys or establish
the behavior of contradictory ordering hints and dependency cycles.

**[inferred]** Use a mod-level dependency for another required mod, a Lua
`require` for a particular module, and an event callback for work that requires a
later lifecycle phase. These solve different ordering problems. A shared file
cannot assume that a client-side global already exists at shared-load time.

**[observed, engine reference]** Mod changes and return-to-menu paths can reset
the Lua environment. Top-level code and `Events.X.Add` subscriptions run again
in the new environment. Recursive `require` requests are detected; a top-level
runtime error can leave partial effects even though subsequent files continue.
**[inferred]** Keep initialization repeatable and use the normal reload path
when testing edits. **[unknown]** File-watcher presence alone does not establish
that every edit is safely hot-reloadable.

## Distribution and action timing

**[observed]** The distribution helpers subscribe to pre/merge/post-distribution
events, while the UI menu modules subscribe to rendering/input/world hooks.
See [distributions.md](../lua-library/distributions.md) and the generated
[vanilla-event-subscriptions.csv](../data/vanilla-event-subscriptions.csv).
**[inferred]** Choose a hook from its arguments and source phase, not just its
name. In particular, client menu readiness does not imply that a world or
server-owned object is ready for mutation.

**[observed]** Three installed-Lua source checks per page are recorded in
`HANDOFF.md`. Engine order claims retain the confidence and limits of Claude's
reference rather than being presented as results of a runtime test here.
