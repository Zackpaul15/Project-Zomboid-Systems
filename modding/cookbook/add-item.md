# Recipe: add an item

Survey date: 2026-10-24. Game build: Build 42 (jar sha256 prefix e1a69eb7; read-only Core source corroborates 42.21).
Tags: **[observed]** / **[inferred]** / **[unknown]**; every snippet is **[inferred]** (invented, not game code).

> **NOT RUNTIME-VERIFIED — no in-game smoke test was run.** Status: **untested**. Index: [README.md](README.md).

## Goal

Define two new items, Slat and Marker, in a mod-owned script module, with display names. They are reused by
[add-craft-recipe.md](add-craft-recipe.md).

## Prerequisites

Build 42, the empty-mod skeleton (folder, mod.info) from [README.md](README.md#common-setup-all-recipes), and the mod
enabled ([load-order.md](../workflow/load-order.md)).

## Files

```text
GuideCookbook/42/mod.info                                         (from README)
GuideCookbook/42/media/scripts/GuideItems.txt
GuideCookbook/42/media/lua/shared/Translate/EN/ItemName.json
```

1. **Script file** **media/scripts/GuideItems.txt** [inferred snippet]. Only files ending in .txt are read; the top level
   accepts only `module <Name> { ... }`, and a module name already in use is reused ([parser-keys.md](../scripts/parser-keys.md#1-loading-pipeline)).
   The folder name media/scripts is where the vanilla script files live ([overview.md](../scripts/overview.md));
   that a mod file may use any .txt name there is **[inferred]**.

   ```text
   module Guide
   {
       item Slat
       {
           ItemType = base:normal,
           DisplayCategory = GuideCategory,
           Weight = 0.5,
       }
       item Marker
       {
           ItemType = base:normal,
           DisplayCategory = GuideCategory,
           Weight = 0.2,
       }
   }
   ```

   - Block shape `item <Name> { key = value, }`, comma-terminated entries: [parser-keys.md](../scripts/parser-keys.md#2-block-syntax). [observed]
   - `ItemType` and `DisplayCategory` are the only two properties present on every surveyed item; `base:normal` is one
     of 15 observed ItemType values; `Weight` appears on 4,525 of 5,105 items ([items.md](../scripts/items.md),
     [item-properties.csv](../data/item-properties.csv), [item-types.csv](../data/item-types.csv)). [observed]
   - Do not put a second `=` inside a value: text after it is dropped ([parser-keys.md](../scripts/parser-keys.md#2-block-syntax)). [observed]
   - **[unknown]** Which `DisplayCategory` values are valid or whether an arbitrary string is accepted; the survey only
     records the value shape. **[unknown]** Which icon is used when `Icon` is omitted (`Icon` is on 4,683 of 5,105
     items, not all); an Icon needs a texture you supply and is left out of this minimal recipe.
   - Unknown keys are stored as free-form mod data rather than raising an error, so a misspelled key fails silently ([parser-keys.md](../scripts/parser-keys.md#3-what-happens-to-an-unknown-key)). [observed]

2. **Display names** **media/lua/shared/Translate/EN/ItemName.json** [inferred snippet]. English item names are a JSON
   object keyed by the full identifier shaped `<module>.<item>` ([items.md](../scripts/items.md#names-icons-models-and-sounds),
   [translations.md](../workflow/translations.md)); do not add an ItemName_ prefix.

   ```json
   {
       "Guide.Slat": "Guide Slat",
       "Guide.Marker": "Guide Marker"
   }
   ```

   **[unknown]** What is shown when a key is missing (not established by the survey).

## Expected in-game result [inferred]

With the mod enabled and no script errors in the Lua/console output, the full types Guide.Slat and Guide.Marker exist
and display the names above. **[unknown]** How you obtain one in-game: this repo has no tested spawn procedure. Look at
debug options in [debug-mode.md](../workflow/debug-mode.md), or add the item to loot with
[distributions.md](../lua-library/distributions.md). A check from the Lua console, if your build exposes it:
(class `ScriptManager`, method `getItem`; exposed method getItem on ScriptManager, [exposed-methods.csv](../data/exposed-methods.csv)):

```lua
ScriptManager.instance:getItem("Guide.Slat")
```

should return a non-nil item. [inferred; not run]

## If it does not appear

Check file names (.txt, no hidden extension), that mod.info is under the 42 folder, that the mod is enabled for the
current save, and the launch log ([mod-layout.md](../workflow/mod-layout.md)).

## See also

[items.md](../scripts/items.md) · [parser-keys.md](../scripts/parser-keys.md) · [translations.md](../workflow/translations.md) · next: [add-craft-recipe.md](add-craft-recipe.md)
