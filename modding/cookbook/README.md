# Modding cookbook (Build 42)

Survey date: 2026-10-24. Game build: Build 42 (jar sha256 prefix e1a69eb7; read-only Core source corroborates 42.21).
Sources: this repo's own reference pages only, linked per step. Tags: **[observed]** = found in the repo reference
data, **[inferred]** = reasoned from it (every code snippet in this cookbook is **[inferred]**: invented here, not
copied from the game), **[unknown]** = not established.

> **NOT RUNTIME-VERIFIED — no in-game smoke test was run.** Status of every recipe: **untested**. Everything here is
> assembled from static reference material; reproducing a documented shape is not observed behaviour.

Six short recipes. Each lists the exact file path of every file starting from an empty mod folder, the prerequisites,
the expected in-game result (and how sure we are of it), and links to the reference page behind each piece.

| Recipe | One line | Status |
|---|---|---|
| [Add an item](add-item.md) | Declare two new script items and give them display names | untested |
| [Add a craftRecipe](add-craft-recipe.md) | Combine the two items with a craftRecipe block | untested |
| [Add a context-menu entry](context-menu-entry.md) | Add a client-side option to the world context menu | untested |
| [Hook an event](hook-an-event.md) | Subscribe a function to a game event and choose one from the events table | untested |
| [Add a sandbox option](add-sandbox-option.md) | Register a mod-owned boolean option and read it from Lua | untested |
| [Send a client to server command](client-server-command.md) | Ask the server to act, using sendClientCommand and OnClientCommand | untested |

## Common setup (all recipes)

**Prerequisites.**

- A Build 42 install. The layout follows [mod-layout.md](../workflow/mod-layout.md); the flat legacy sample layout is
  not used here ([b41-vs-b42.md](../workflow/b41-vs-b42.md)). [observed in those pages; not executed]
- The mod must be **enabled** in the Mods selector, and for a new game also in the New Game mod selection. Ordering
  background: [load-order.md](../workflow/load-order.md). Launch flags and where to read Lua output:
  [debug-mode.md](../workflow/debug-mode.md).

**Empty-mod skeleton** [inferred]. Create this folder under the mods directory of the game's cache folder (normally
<user profile>\Zomboid\mods on Windows; -cachedir= can change it). All names are invented for this cookbook.

```text
GuideCookbook/
    42/
        mod.info
        media/
            (each recipe adds files here)
```

The mod.info file uses the three sampled keys name, id and description ([mod-info.md](../workflow/mod-info.md)):

```text
name=Guide Cookbook
id=GuideCookbook
description=Cookbook test mod, untested.
```

All six recipes can live in this one mod; their files do not collide. File names are invented and unique on purpose so
they do not shadow vanilla files ([load-order.md](../workflow/load-order.md)).

## Reference map

| Topic | Pages |
|---|---|
| Script block syntax and keys | [overview.md](../scripts/overview.md), [parser-keys.md](../scripts/parser-keys.md) |
| Items | [items.md](../scripts/items.md) |
| craftRecipe | [crafting.md](../scripts/crafting.md) |
| Lua UI and context menus | [ui.md](../lua-library/ui.md) |
| Events | [events.md](../lua-api/events.md), [events.csv](../data/events.csv) |
| Sandbox | [sandbox-options.md](../lua-api/sandbox-options.md), [sandbox-vars.md](../workflow/sandbox-vars.md) |
| Client/server commands | [multiplayer.md](../lua-api/multiplayer.md) |
| Translations | [translations.md](../workflow/translations.md) |

## Lua syntax check

**[unknown]** Lua syntax validity is unverified for every snippet; validate it before relying on an example.
