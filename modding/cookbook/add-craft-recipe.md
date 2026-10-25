# Recipe: add a craftRecipe

Survey date: 2026-10-24. Game build: Build 42 (jar sha256 prefix e1a69eb7; read-only Core source corroborates 42.21).
Tags: **[observed]** / **[inferred]** / **[unknown]**; every snippet is **[inferred]** (invented, not game code).

> **NOT RUNTIME-VERIFIED — no in-game smoke test was run.** Status: **untested**. Index: [README.md](README.md).

## Goal

Add a craftRecipe that consumes two Guide.Slat and produces one Guide.Marker. Needs the items from
[add-item.md](add-item.md).

## Prerequisites

Build 42; the skeleton from [README.md](README.md#common-setup-all-recipes); the two items from
[add-item.md](add-item.md) (a recipe naming an undefined item is a mistake: [crafting.md](../scripts/crafting.md));
the mod enabled.

## Files

```text
GuideCookbook/42/media/scripts/GuideRecipes.txt
```

Legacy `recipe` blocks do not occur in the Build 42 tree; the current form is `craftRecipe` ([crafting.md](../scripts/crafting.md)). [observed]

**media/scripts/GuideRecipes.txt** [inferred snippet, shaped after the invented example in [crafting.md](../scripts/crafting.md)]:

```text
module Guide
{
    craftRecipe AssembleMarker
    {
        time = 45,
        Tags = GuideWorkbench,
        category = GuideCrafts,
        inputs
        {
            item 2 [Guide.Slat] mode:destroy,
        }
        outputs
        {
            item 1 Guide.Marker,
        }
    }
}
```

What each piece is, from the reference:

- Every observed craftRecipe has `time`, `Tags` and an `inputs` block; `time` is an integer ([crafting.md](../scripts/crafting.md),
  [recipe-keys.csv](../data/recipe-keys.csv)). [observed]
- Input line shape: first word is the resource type (`item`, `fluid` or `energy`), then an amount, then a bracketed
  candidate list, then options such as mode:destroy (consumed) or mode:keep (kept as a tool). Output lines are
  `item <amount> <FullType>` ([crafting.md](../scripts/crafting.md#inputs-outputs-and-selectors-observed),
  [parser-keys.md](../scripts/parser-keys.md#5-craftrecipe-micro-grammar)). [observed]
- Entries are comma-terminated; an unknown line word inside `inputs` or `outputs` throws ([parser-keys.md](../scripts/parser-keys.md#3-what-happens-to-an-unknown-key)). [observed]
- `timedAction` is omitted: 889 of 969 recipes use it, so it is optional in the data, but
  **[unknown]** which action the game uses when it is absent.
- **Routing and category: the reference does not establish a working configuration.** The values `GuideWorkbench` and
  `GuideCrafts` in the snippet are invented placeholders, not known-good routing. [inferred] The survey records only
  that `Tags` is a plain string or semicolon list present on all 969 recipes, that `category` is a separate field, and
  that adding an arbitrary outer tag is not proven to create a workstation or UI route
  ([crafting.md](../scripts/crafting.md#recipe-tags-versus-item-tags-observed)). [observed]
  **[unknown]** Which `Tags` / `category` values place a recipe in a given crafting menu, and which menu (or how) a
  recipe with these placeholders becomes reachable in-game. To get a reachable recipe, study the `Tags` and `category`
  of a vanilla recipe file listed in [crafting.md](../scripts/crafting.md) and reuse values it already uses; this
  cookbook has not verified any such value. [inferred]
- **[unknown]** The text label shown for the recipe name; no translation key for recipe names is documented here.

## Expected in-game result [inferred]

If the routing places it in a crafting menu you can open, a recipe appears needing two Guide Slat and yielding one Guide
Marker; running it consumes the slats. With the placeholder routing above, whether it appears at all is **[unknown]**.
If it does not appear, the cause is **[unknown]**; inspect script errors and verify routing and item references
([debug-mode.md](../workflow/debug-mode.md)). Loading order of script files is in
[parser-keys.md](../scripts/parser-keys.md#1-loading-pipeline) (a second body for the same name is applied after the first).

## See also

[crafting.md](../scripts/crafting.md) · [entities.md](../scripts/entities.md) (the component CraftRecipe form) ·
[parser-keys.md](../scripts/parser-keys.md) · previous: [add-item.md](add-item.md)
