# `mod.info` metadata

Survey date: 2026-10-24. Build: jar sha256 prefix `e1a69eb7`.
Sources: installed `mods/examplemod/mod.info` and
`Workshop/ModTemplate/Contents/mods/ModTemplate/mod.info`; optional read-only
`ChooseGameInfo.readModInfoAux` confirms parser keys. Claims are **[observed]**
unless tagged **[inferred]** or **[unknown]**. No sample values are copied.

## Observed keys and parser coverage [observed]

**[observed]** The two installed sample files contain five distinct keys: `name`, `id`,
`description`, `poster` and `url`. The parser confirmation adds twelve recognized
keys not exercised by those samples. All seventeen are in
[mod-info-keys.csv](../data/mod-info-keys.csv), with sample-file/occurrence counts,
lexical shapes and parser presence. `not-sampled` is not a claim that a key is unsupported.

| Keys | Purpose/shape | Evidence |
|---|---|---|
| `name`, `id` | Display label and mod identifier strings | Samples and parser |
| `description` | Descriptive text; parser concatenates repeated entries | Samples and parser |
| `poster` | Image filename relative to selected version/common directory | Samples and parser |
| `url` | Homepage string | One sample and parser |
| `author`, `category`, `modversion` | Descriptive metadata strings | Parser only |
| `icon` | Image filename, version then common lookup | Parser only |
| `require`, `incompatible` | Comma-separated mod-ID lists | Parser only |
| `loadModAfter`, `loadModBefore` | Comma-separated ordering-ID lists | Parser only |
| `pack` | Texture-pack basename; optional pack modifiers | Parser only |
| `tiledef` | File stem followed by an integer file number | Parser only |
| `versionMin`, `versionMax` | Game version strings parsed as major.minor | Parser only |

**[observed, parser confirmation]** The loader reads version-folder `mod.info`
first, falling back to `common/mod.info` if it is absent. It does not combine
both metadata files. Poster/icon resource lookup also tries the version path
before common. `tiledef` requires a number in 100..8189. `pack` supports a `type=ui`
modifier and special handling for the `.floor` suffix.
**[unknown]** A recognized key is not proof that every value or combination is
valid; this page does not provide a complete asset-pack authoring guide.

## Choosing identifiers and versions

**[inferred]** Use a stable, distinctive `id`; dependencies refer to mod IDs,
not folder labels, display names or Steam Workshop numbers. Keep metadata
in the same selected version layout as your test content unless you deliberately
share it through `common`. See [mod-layout.md](mod-layout.md) for an original
minimal example and [load-order.md](load-order.md) for ordering limits.

**[observed]** `version` appears in the supplied **workshop.txt**, not either
sample `mod.info`, and is not one of the extracted mod-info parser keys.
`modversion`, game compatibility bounds and version-folder selection are separate
concepts. **[unknown]** Do not infer a game-build restriction merely from a
mod author's release-version label.
