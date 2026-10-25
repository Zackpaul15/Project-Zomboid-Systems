# Debugging a Lua mod

Survey date: 2026-10-24. Build: jar sha256 prefix `e1a69eb7`.
Sources: installed launch scripts, Lua debug UI and read-only
`MainScreenState` flag parsing. Claims are **[observed]** unless tagged
**[inferred]** or **[unknown]**. No launch settings were changed or game run made.

## Launch flags [observed]

**[observed]** [debug-launch-flags.csv](../data/debug-launch-flags.csv) inventories literal
flag occurrences in the main-screen parser and installed BAT files. Occurrence counts are source
references, not counts of enabled settings.

- `-debug` enables the engine debug flag.
- `-imgui` enables ImGui and debug; `-imguidebugviewports` also enables viewports.
- `-debuglog=<categories>` selects log categories; the installed
  `ProjectZomboidOpenGLDebug64.bat` uses the Shader category.
- `-debugtranslation` enables translation diagnostics.
- `-debugcfg=<path>` and `-debugLogFile=<path>` are recognized diagnostic inputs;
  **[unknown]** their complete file-format and redirection contracts are not
  documented here.
- `-cachedir=<path>` changes the cache location and therefore affects where to
  look for local mods and diagnostics.

**[inferred]** Add only the flags needed for a particular investigation to the
launch configuration you actually use. The filename “OpenGLDebug” is not evidence
that its BAT file passes `-debug`; it passes `-debuglog=Shader`. This distinction
is visible in the installed launch file.

## Lua tools and a first diagnosis [observed / inferred]

**[observed]** `client/DebugUIs/DebugMenu/ISDebugMenu.lua` gates its UI with
`getCore():getDebug()` or its own force-enable setting and names panels for
items, fluids, entities, scripts and craft recipes. The vanilla library also has
specialized debug windows indexed under `client/DebugUIs`.

**[inferred]** Start with the hello-world print in [mod-layout.md](mod-layout.md)
and inspect that launch's Lua/console output. A missing mod in the selector points
first to discovery/layout/metadata; a visible mod with no print points to active
selection, the Lua side/path or an earlier load error. A menu callback that logs
but produces no state change is a different problem: inspect its arguments,
validity and the action/network path. Use the relevant debug panel to inspect
the parsed script rather than assuming a file's presence proves it loaded.

**[observed, engine reference]** Syntax/compile failures and runtime failures
are handled differently by Lua loading; runtime code can leave partial effects.
See [load-order.md](load-order.md) and the lifecycle reference.
**[unknown]** This static survey does not establish a universal debug-menu hotkey,
the exact log filename for every launch, or safe hot-reload behavior for every
class. No runtime test is claimed.
