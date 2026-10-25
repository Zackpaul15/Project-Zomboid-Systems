# Recipe: add a context-menu entry

Survey date: 2026-10-24. Game build: Build 42 (jar sha256 prefix e1a69eb7; read-only Core source corroborates 42.21).
Tags: **[observed]** / **[inferred]** / **[unknown]**; every snippet is **[inferred]** (invented, not game code).

> **NOT RUNTIME-VERIFIED — no in-game smoke test was run.** Status: **untested**. Index: [README.md](README.md).

## Goal

Add one entry to the world right-click menu that prints a line when chosen.

## Prerequisites

Build 42; the skeleton from [README.md](README.md#common-setup-all-recipes); the mod enabled and a game (new or
loaded) started with it active. This is client-side UI code, so it goes in the client Lua folder
([load-order.md](../workflow/load-order.md)).

## Files

```text
GuideCookbook/42/media/lua/client/GuideCookbookMenu.lua
GuideCookbook/42/media/lua/shared/Translate/EN/ContextMenu.json   (optional, for a translated label)
```

**media/lua/client/GuideCookbookMenu.lua** [inferred snippet, same shape as the invented sample in [ui.md](../lua-library/ui.md#context-menus)]:

```lua
local function addGuideEntry(playerNum, context, worldobjects, test)
    if test then return end
    context:addOption("Guide entry", worldobjects, function()
        print("GuideCookbook: menu entry chosen")
    end)
end

Events.OnFillWorldObjectContextMenu.Add(addGuideEntry)
```

What each piece is:

- `OnFillWorldObjectContextMenu` is a registered event fired from Lua with `player`, `context`, `worldobjects`, `test`
  ([ui.md](../lua-library/ui.md#context-menus), [events.md](../lua-api/events.md), row in [events.csv](../data/events.csv)). [observed]
  The first argument is named `player` in the reference but the snippet treats it as a player index; **[unknown]**
  which of an index or an object it is, so the snippet does not use it.
- `ISContextMenu` method `addOption` (name, target, onSelect, ...) adds an option and returns the option object; use the supplied
  `context`, do not replace the menu ([ui.md](../lua-library/ui.md#context-menus)). [observed] The class derives from `ISPanel`
  ([ui-inheritance.csv](../data/ui-inheritance.csv)). [observed]
- The `test` pass is skipped so the callback is not queued twice. The reference says the event is "gated by the vanilla
  menu-building path"; the exact meaning of `test` is **[unknown]**, and skipping it is a convention in the reference's
  own example, not a verified rule. [inferred]
- Label text: a literal is used for simplicity. To translate, add a key to the ContextMenu translation JSON and call
  `getText` ([translations.md](../workflow/translations.md)); the key name is yours to invent. [inferred]
- The menu action only runs on the client. Anything that changes server-owned state needs a command, see
  [client-server-command.md](client-server-command.md). [observed in [multiplayer.md](../lua-api/multiplayer.md)]
- For inventory items there is a separate pair of events, `OnFillInventoryObjectContextMenu` and its pre-fill sibling;
  their argument lists are not interchangeable with the world one ([ui.md](../lua-library/ui.md#context-menus)). [observed]

## Expected in-game result [inferred]

Right-click in the world: a "Guide entry" line appears in the menu; choosing it writes
"GuideCookbook: menu entry chosen" to the Lua/console output ([debug-mode.md](../workflow/debug-mode.md)). Whether the
entry appears for every cursor position is **[unknown]**; the reference says the event is not guaranteed for every
position.

## See also

[ui.md](../lua-library/ui.md) · [events.md](../lua-api/events.md) · [hook-an-event.md](hook-an-event.md)
