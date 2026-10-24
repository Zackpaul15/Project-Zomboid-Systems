# Sandbox variables and custom options

Survey date: 2026-10-24. Build: jar sha256 prefix `e1a69eb7`.
Sources: installed `media/lua/shared/Sandbox` and Claude's
[sandbox-options.md](../lua-api/sandbox-options.md). Claims are **[observed]**
unless tagged **[inferred]** or **[unknown]**. Examples are invented.

## Vanilla initialization [observed]

`shared/Sandbox/SandboxVars.lua` assigns `SandboxVars` from the Apocalypse preset
and calls `getSandboxOptions():initSandboxVars()`. Other files in this folder are
presets that return tables, rather than all assigning the global themselves.
The folder contains `Apocalypse`, `Extinction`, `Outbreak`, `Rising`,
`SixMonthsLater` and the `SandboxVars` initializer. The presets use nested tables
such as `ZombieLore`, `ZombieConfig`, `MultiplierConfig`, `Map` and `Basement`.

**[observed, engine reference]** The Java sandbox options and Lua `SandboxVars`
are separate copies. Assigning a Lua field does not automatically synchronize
the Java option or connected peers. Claude's reference covers synchronization,
defaults, persistence and all 269 built-in options. Use its generated
[sandbox-options.csv](../data/sandbox-options.csv) rather than treating a single
preset as the complete engine defaults.

## Registering a mod option [observed / inferred]

**[observed, engine reference]** Custom definitions use
`media/sandbox-options.txt`, with a required top-level `VERSION = 1` and `option`
blocks. The version-folder file takes precedence over common; the two files are
not merged. Types are `boolean`, `integer`, `double`, `enum` and `string`.
Numeric types need bounds, enums need `numValues`, and all types need `default`.
`page` places an option in the settings UI; `translation` supplies its label stem.
No custom-option sample file is shipped in the installed sample trees.

**[inferred]** This original shape would define a mod-owned toggle when saved as
`42/media/sandbox-options.txt` in the walkthrough mod:

```text
VERSION = 1,
option GuideHello.Enabled
{
    type = boolean,
    default = true,
    page = GuideHello,
    translation = GuideHello_Enabled,
}
```

Add original labels to `42/media/lua/shared/Translate/EN/Sandbox.json`, using
`Sandbox_GuideHello` for the page and `Sandbox_GuideHello_Enabled` for the option.
After initialization the dotted option name corresponds to
`SandboxVars.GuideHello.Enabled`. **[unknown]** This invented example was not
loaded in-game; it illustrates the parser contract confirmed in Claude's page.

**[inferred]** Read world settings after their initialization phase, preserve
existing `SandboxVars` rather than replacing the whole table, and use the relevant
engine/network mechanism for runtime changes. See
[load-order.md](load-order.md) and [multiplayer.md](../lua-api/multiplayer.md).
**[unknown]** A Lua mutation alone does not prove persistence or replication.

**[observed]** Three installed-source checks per page are recorded in
`HANDOFF.md`; sandbox registration details retain their engine-reference tags.
