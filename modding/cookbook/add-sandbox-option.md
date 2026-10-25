# Recipe: add a sandbox option

Survey date: 2026-10-24. Game build: Build 42 (jar sha256 prefix e1a69eb7; read-only Core source corroborates 42.21).
Tags: **[observed]** / **[inferred]** / **[unknown]**; every snippet is **[inferred]** (invented, not game code).

> **NOT RUNTIME-VERIFIED — no in-game smoke test was run.** Status: **untested**. Index: [README.md](README.md).

## Goal

Register a mod-owned boolean sandbox option on its own settings page, label it, and read it from Lua.

## Prerequisites

Build 42; the skeleton from [README.md](README.md#common-setup-all-recipes); the mod enabled before the sandbox
screen is opened for a new game. No custom-option sample ships with the game, so every shape below comes from the
parser description in [sandbox-options.md](../lua-api/sandbox-options.md), not from an example file. [observed]

## Files

```text
GuideCookbook/42/media/sandbox-options.txt
GuideCookbook/42/media/lua/shared/Translate/EN/Sandbox.json
GuideCookbook/42/media/lua/client/GuideCookbookSandbox.lua
```

1. **Option definition** `media/sandbox-options.txt` [inferred snippet]. For each active mod one file is read:
   the version-folder file if present, otherwise the common one; they are **not merged**. A top-level `VERSION = 1` is
   required, otherwise that mod's options are not added. Every child block must be of type `option`; the block id is
   the option name and a dot in it creates a nested table ([sandbox-options.md](../lua-api/sandbox-options.md#adding-options-from-a-mod-mediasandbox-optionstxt)). [observed]

   ```text
   VERSION = 1,
   option GuideCookbook.Enabled
   {
       type = boolean,
       default = true,
       page = GuideCookbook,
       translation = GuideCookbook_Enabled,
   }
   ```

   - `type` and `default` are required for every option; `min`/`max` for integer and double; `numValues` for enum
     ([sandbox-options.md](../lua-api/sandbox-options.md)). [observed]
   - Without `page` the option is not placed on any settings page, logs "WARN:MISSING in SettingsTable", and still exists
     with its default. [observed]
   - The same shape appears in [sandbox-vars.md](../workflow/sandbox-vars.md#registering-a-mod-option-observed--inferred). [observed]

2. **Labels** **media/lua/shared/Translate/EN/Sandbox.json** [inferred snippet]. The page title key is
   `Sandbox_<page>` and the option label is `Sandbox_<translation stem>` ([sandbox-options.md](../lua-api/sandbox-options.md), [translations.md](../workflow/translations.md)):

   ```json
   {
       "Sandbox_GuideCookbook": "Guide Cookbook",
       "Sandbox_GuideCookbook_Enabled": "Enable the guide feature"
   }
   ```

3. **Reading it** **media/lua/client/GuideCookbookSandbox.lua** [inferred snippet]:

   ```lua
   Events.OnGameStart.Add(function()
       local opts = SandboxVars.GuideCookbook
       if opts and opts.Enabled then
           print("GuideCookbook: option is on")
       else
           print("GuideCookbook: option is off or missing")
       end
   end)
   ```

   - Read as `SandboxVars.<Table>.<Short>` for a dotted name ([sandbox-options.md](../lua-api/sandbox-options.md#naming-and-tables-observed)). [observed]
   - `SandboxVars` is the Lua copy; writing to it does **not** change the Java option, so treat it as read-only for
     mods and use the option object's setter for engine-visible changes ([sandbox-options.md](../lua-api/sandbox-options.md#lua-and-java-copies-observed)). [observed]
   - Reading at `OnGameStart` is a choice for a late, post-load phase ([hook-an-event.md](hook-an-event.md)). When a
     multiplayer client's `SandboxVars` first reflects the server values is **[unknown]**
     ([sandbox-options.md](../lua-api/sandbox-options.md#open-items), [lifecycle.md](../lua-api/lifecycle.md)).
   - Custom options are cleared and rebuilt from the files on Lua reset and return to menu, so do not cache them in
     your own global across a reset. [observed; advice inferred]

## Expected in-game result [inferred]

Start a **new** game or open the server/admin sandbox settings: a "Guide Cookbook" page with an "Enable the guide
feature" checkbox defaulting to on. After the world loads the Lua output shows "GuideCookbook: option is on" (or
"off" if you cleared it). **[unknown]** Whether an existing save picks up a newly added option: a save stores its own
option list and an unknown or new name handling is documented only for the unknown-name direction
([sandbox-options.md](../lua-api/sandbox-options.md#persistence-files-and-network)). Test with a new game first.

## See also

[sandbox-options.md](../lua-api/sandbox-options.md) · [sandbox-options.csv](../data/sandbox-options.csv) ·
[sandbox-vars.md](../workflow/sandbox-vars.md) · [translations.md](../workflow/translations.md)
