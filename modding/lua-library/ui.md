# Lua UI layer (Project Zomboid, Build 42)

Survey date: 2026-10-24. Build identifier: jar sha256 prefix `e1a69eb7`.
Sources: installed `media/lua/client/ISUI`, `client/OptionScreens` and the XUI
scripts described in [entities.md](../scripts/entities.md). Claims are
**[observed]** unless tagged **[inferred]** or **[unknown]**.

## Class map [observed]

The selected folders have **265 ISUI Lua files**, **51 OptionScreens Lua files**
and **356 textual derive declarations**. One file can define multiple classes.
The complete parent → child table, with the defining filename, is
[ui-inheritance.csv](../data/ui-inheritance.csv); folder totals are in
[ui-folder-counts.csv](../data/ui-folder-counts.csv).

Selected rows from that declaration table:

| Parent | Child |
|---|---|
| `ISBaseObject` | `ISUIElement` |
| `ISUIElement` | `ISPanel` |
| `ISUIElement` | `ISPanelJoypad` |
| `ISPanel` | `ISButton` |
| `ISPanel` | `ISCollapsableWindow` |
| `ISPanel` | `ISContextMenu` |
| `ISPanelJoypad` | `ISRadialMenu` |
| `ISPanelJoypad` | `MainScreen` |

**[inferred]** The CSV is a declaration map, not a complete runtime type graph.
It covers assignments of the form `Child = Parent:derive(...)` outside comments
and strings, and omits computed factories, local
aliases and classes outside these two folders. Some helper classes are not
widgets even though they live beside UI code. The parent may be defined outside
the selected folder, as with `ISBaseObject` in shared Lua.

## Creating and showing a panel [observed]

`ISPanel:new(x, y, width, height)` creates the Lua object. Call `initialise()`
once to establish the element's child collections and ID. `instantiate()` creates
the Java-backed element, transfers geometry/anchoring settings and calls
`createChildren()`. Subclasses can override instantiation; the radial menu creates
a Java `RadialMenu`, rather than the base Java `UIElement`.

`addToUIManager()` checks for the Java object and calls `instantiate()` if needed,
then registers it with `UIManager.AddUI`. Thus an explicit `instantiate()` can be
useful when configuring the Java object first, but is not mandatory before adding
the element to the UI manager. `removeFromUIManager()` removes its Java element.
Child widgets use the parent's `addChild` path instead of each becoming an
independent top-level UI-manager entry.

**[inferred]** For a simple panel, require its class, construct it, initialise it,
configure it and add it to the UI manager. Put subclass child creation in the
appropriate lifecycle method. **[unknown]** A widget's constructor arguments,
focus needs and layout behavior must be checked on that widget; the base panel
sequence is not a guarantee for every specialized UI class.

## Context menus [observed]

`ISContextMenu:addOption(name, target, onSelect, ...)` adds an option and returns
its option object. `addSubMenu(option, menu)` attaches a submenu, and
`getNew(parentContext)` is the submenu allocation entry point. In an event callback,
use the supplied context object rather than replacing the entire menu.

`ISWorldObjectContextMenu` fires `OnPreFillWorldObjectContextMenu` and
`OnFillWorldObjectContextMenu` with `player`, `context`, `worldobjects`, `test`.
The final event is gated by the vanilla menu-building path; it is not a guaranteed
callback for every possible cursor position. Inventory menus have their own pre-fill
and fill events. See [events.md](../lua-api/events.md) for the separate argument
lists; the inventory and world-object signatures are not interchangeable.

**[inferred]** To add a harmless client-side menu action, place a Lua file in the
mod's client tree, subscribe once, skip the world-menu test pass, and add an option
to the provided context. This invented example only prints when selected:

```lua
local function addGuideOption(playerNum, context, objects, test)
    if test then return end
    local function report() print("Guide action selected") end
    context:addOption("Guide action", nil, report)
end
Events.OnFillWorldObjectContextMenu.Add(addGuideOption)
```

**[unknown]** This illustrative snippet has not been executed in-game. Actions
that alter world state need their own validity checks and multiplayer handling;
the UI event itself does not establish authority to change server state.

## Radial menus and XUI [observed]

`ISRadialMenu:new(x, y, innerRadius, outerRadius, playerNum)` constructs the radial
widget. `clear()` resets its slices; `addSlice(text, texture, command, ...)` stores
the display data and callback arguments. `undisplay()` is the hide/removal path.
Vanilla controller helpers such as `ISLightSourceRadialMenu` obtain the player's
menu through `getPlayerRadialMenu(playerNum)` and populate it. Look there, or in
`ISFirearmRadialMenu` and `ISEmoteRadialMenu`, for domain-specific entry points.
**[unknown]** This survey does not establish a universal radial-menu event hook.

XUI skin scripts supply widget/style attributes and entity-window links; their
block and variable inventories are in [entities.md](../scripts/entities.md).
**[inferred]** A skin supplements the Lua widget class; it does not contain that
class's event handlers or replace its lifecycle.

**[observed]** The class and folder tables describe declarations and file counts in ISUI and OptionScreens.
