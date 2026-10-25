# A first B42 Lua mod

Survey date: 2026-10-24. Build: jar sha256 prefix `e1a69eb7` (read-only Core
source corroborates 42.21). Sources: installed samples and Lua menu code;
version/discovery details corroborated in `ChooseGameInfo`/`ZomboidFileSystem`.
Claims use **[observed]**, **[inferred]** and **[unknown]**. Examples are invented.

## Folder structure and discovery

**[observed, loader confirmation]** Local mods are discovered under the game's
cache-directory `mods` folder. Discovery checks for `mod.info` in `common` or the
selected version subfolder; it does not use the root-level metadata layout shown
by the installed legacy samples. A major-version directory such as `42` is
recognized, as are major/minor names. The loader selects the highest eligible
version at least 42.0 and no greater than the running game. `common` is a separate
shared overlay. With no matching folder found, its default version name is `42.0`.

**[inferred]** For a small new mod, put metadata and all content in `42`, and
reserve `common` for content intentionally shared across version variants.
This invented working layout avoids relying on the flat legacy samples:

```text
<cache>/mods/GuideHello/
    common/
    42/
        mod.info
        media/
            lua/
                client/
                    GuideHello.lua
```

**[observed]** `Workshop/ModTemplate` contains two example map folders, a flat
`mod.info`, poster and Workshop wrapper. `mods/examplemod` contains a flat
`mod.info`, a tuning Lua file, a music helper, music files and a UI image.
`media/luaexamples` contains old UI/action demonstrations. **[observed]** None of these sample
trees has a `42` or `common` directory. Their complete filename inventory is
[mod-sample-files.csv](../data/mod-sample-files.csv). Describe their roles when learning
the structure; do not copy their assets or assume their APIs are current.

## Create and load hello world

**[inferred, source-based walkthrough]** These steps are intended for a fresh
local test. They reflect loader and menu control flow; in-game execution remains unverified.

1. Find the cache folder used by this launch. On a default Windows setup it is
   normally `<user profile>\Zomboid`; `-cachedir=` can change it. Create the
   `GuideHello` tree above under that folder's `mods` directory. Ensure the actual
   filenames are `mod.info` and `GuideHello.lua`, without an extra `.txt` suffix.
2. Create `42/mod.info` with these invented lines:

   ```text
   name=Guide Hello
   id=GuideHello
   description=A small local Lua loading test.
   ```

3. Create `42/media/lua/client/GuideHello.lua` containing this original line:

   ```lua
   print("GuideHello loaded")
   ```

4. Launch the game, open its Mods selector, locate **Guide Hello**, enable it and
   accept/apply the selection. The Lua environment can reload when the selection
   changes. For a new-game test, check the New Game mod selection as well; the
   menu has separate paths for new games and existing saves.
5. Confirm that the launch's Lua output contains `GuideHello loaded`. If the mod
   is absent from the selector, check the selected version folder, metadata path
   and `id`. If listed but silent, check the selected game/save's active mod set,
   `client` path and Lua error output. See [debug-mode.md](debug-mode.md).
6. For a visible interactive follow-up, use the small invented world-context-menu
   subscriber in [ui.md](../lua-library/ui.md#context-menus). Keep a unique Lua
   filename so the mod does not unintentionally shadow a vanilla file.

**[observed]** MainScreen/NewGame/LoadGame UI code opens the mod selector in
different modes. **[unknown]** This static walkthrough does not guarantee UI
wording, a particular machine's cache path or successful runtime execution.
