# Recipe: hook an event

Survey date: 2026-10-24. Game build: Build 42 (jar sha256 prefix e1a69eb7; read-only Core source corroborates 42.21).
Tags: **[observed]** / **[inferred]** / **[unknown]**; every snippet is **[inferred]** (invented, not game code).

> **NOT RUNTIME-VERIFIED — no in-game smoke test was run.** Status: **untested**. Index: [README.md](README.md).

## Goal

Run your own function once when a game starts and once per in-game hour.

## Prerequisites

Build 42; the skeleton from [README.md](README.md#common-setup-all-recipes); the mod enabled. A client-folder Lua
file is used; folder and load-order background is in [load-order.md](../workflow/load-order.md) and
[lifecycle.md](../lua-api/lifecycle.md).

## Files

```text
GuideCookbook/42/media/lua/client/GuideCookbookEvents.lua
```

**media/lua/client/GuideCookbookEvents.lua** [inferred snippet]:

```lua
local function onStart()
    print("GuideCookbook: OnGameStart fired")
end

local function onHour()
    print("GuideCookbook: EveryHours fired")
end

Events.OnGameStart.Add(onStart)
Events.EveryHours.Add(onHour)
```

How it works:

- Subscribe with `Events.<Name>.Add(fn)`, unsubscribe with `Events.<Name>.Remove(fn)`; callbacks run in subscription
  order and each runs in a protected call, so an error in one does not stop the others ([events.md](../lua-api/events.md#mechanism-observed)). [observed]
- Choose the event name from [events.csv](../data/events.csv): the `event` column is the name, `sample_args` and
  `arg_counts` show what the callback receives. In this table `OnGameStart` has 0 arguments and `EveryHours` has 0
  arguments, both fired by the game's own classes (`IngameState` and `GameTime`). [observed]
  For a per-frame hook the table lists `OnTick` (one argument, a tick counter) and for the local player
  `OnPlayerUpdate` (one argument, the player). [observed]
- `OnGameStart` and `OnLoad` are fired back to back from the in-game state with no arguments
  ([lifecycle.md](../lua-api/lifecycle.md)). [observed]
- Mod changes and return-to-menu can reset the Lua environment, and the top-level `Events.X.Add` then runs again; keep
  startup code repeatable ([load-order.md](../workflow/load-order.md)). [observed in that page]
- Events a mod subscribes to that the game never registered are created on demand, and may simply never fire
  ([events.md](../lua-api/events.md#mechanism-observed)). A misspelled name therefore fails silently. [inferred]
- For what vanilla itself subscribes to, see [vanilla-event-subscriptions.csv](../data/vanilla-event-subscriptions.csv).
- Lua can fire any event name with the global `triggerEvent(name, ...)` ([events.md](../lua-api/events.md#mechanism-observed)). [observed]

## Expected in-game result [inferred]

After the world loads, the console/Lua output ([debug-mode.md](../workflow/debug-mode.md)) shows
"GuideCookbook: OnGameStart fired" once, then "GuideCookbook: EveryHours fired" each in-game hour (the real-time
length of an in-game hour depends on the day length sandbox option and is **[unknown]** here).

## See also

[events.md](../lua-api/events.md) · [events.csv](../data/events.csv) · [lifecycle.md](../lua-api/lifecycle.md) ·
[context-menu-entry.md](context-menu-entry.md)
