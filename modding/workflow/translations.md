# Translation layout

Survey date: 2026-10-24. Build: jar sha256 prefix `e1a69eb7`.
Source: installed `media/lua/shared/Translate`; JSON loader corroborated in the
read-only `Translator` source. Claims are **[observed]** unless tagged
**[inferred]** or **[unknown]**. No game translation text is reproduced.

## Files and key shapes [observed]

**[observed]** This install has **1,248 JSON files and two TXT files** under **29 first-level
language directories**. English has 43 inventoried files. The two TXT files are
`TH/credits.txt` and `TH/language.txt`, not a parallel collection of old-style UI
translation tables. [translation-layout.csv](../data/translation-layout.csv)
records language, relative file path, format and entry count. It contains counts and filenames,
without translation keys/values or per-item name lists.

Files such as `EN/UI.json`, `EN/ContextMenu.json`, `EN/Tooltip.json`,
`EN/Sandbox.json` and `EN/ItemName.json` are JSON objects. UI/context/sandbox
families use prefixes such as `UI_`, `ContextMenu_` and `Sandbox_`. Item-name keys
instead use full identifiers shaped `<module>.<item>`; the item-resource table records
4,900 matching item identifiers without exporting their names or translated text.
Do not mechanically add `ItemName_` to those JSON keys.

**[observed, loader confirmation]** The loader opens
`media/lua/shared/Translate/<language>/<category>.json` beneath each resource
root. It parses a JSON object into the category map. **[unknown]** This survey
does not establish all duplicate-key precedence, mod override order or fallback
rules for every category; filenames alone cannot settle those rules.

## Add an original label [inferred]

For the walkthrough mod, create
`42/media/lua/shared/Translate/EN/UI.json` with an original mapping:

```json
{
    "UI_GuideHello_Action": "Guide action"
}
```

Use `getText("UI_GuideHello_Action")` from the appropriate Lua UI code. The
installed UI uses `getText` with this family of keys. Use valid JSON, retain the
exact spelling of identifiers and keep the mod's keys distinctive. Other languages
use matching category filenames beneath their language directories.

**[observed]** Translation values can contain `%1`-style substitutions; English
sandbox/UI files contain these markers. **[inferred]** Preserve the substitution
markers expected by the caller when translating a label. **[unknown]** This page
does not test an invented label in-game or promise a fallback result for a missing
key. See [sandbox-vars.md](sandbox-vars.md) for custom-option label stems.
