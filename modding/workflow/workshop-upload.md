# Workshop staging files

Survey date: 2026-10-24. Build: jar sha256 prefix `e1a69eb7`.
Sources: installed `Workshop/ModTemplate` and
`client/OptionScreens/WorkshopSubmitScreen.lua`. Claims are **[observed]** unless
tagged **[inferred]** or **[unknown]**. No upload was performed.

## Wrapper versus mod content [observed]

The supplied wrapper has `workshop.txt`, `preview.png` and
`Contents/mods/ModTemplate/`. The mod folder contains its own `mod.info`,
`poster.png` and two map directories with `map.info`, `spawnpoints.lua` and
thumbnail files. The wrapper preview and mod poster are distinct resources.
See [mod-sample-files.csv](../data/mod-sample-files.csv) for the complete
filename inventory; it contains no assets or file bodies.

[workshop-metadata-keys.csv](../data/workshop-metadata-keys.csv) lists every
observed key and shape in the supplied `workshop.txt`. Generate it with
`python -I modding/tools/survey_workflow.py`.

| Observed key | Shape/purpose |
|---|---|
| `version` | Integer wrapper-format field |
| `title` | Workshop title string |
| `description` | Repeated text lines, including an empty line |
| `tags` | Empty in the sample |
| `visibility` | Visibility identifier |

**[unknown]** An empty sample `tags` field does not establish list syntax or
every accepted tag. These five fields are an observed sample inventory, not
every field the upload engine may accept or add after publishing.

## Staging and submission [observed / inferred]

**[observed]** `WorkshopSubmitScreen` shows the staging root as the game's user
document/cache area plus `Workshop`. It enumerates staged items with
`getSteamWorkshopStagedItems()` and calls `validateContents()` before moving on.
The UI offers title, description, tags, preview and visibility controls, including
public, friends-only, private and unlisted choices.

**[inferred]** Assemble your own staging wrapper in that user `Workshop` area.
Keep an original preview image at the wrapper level and place the tested,
versioned mod beneath `Contents/mods/<folder>/`, following
[mod-layout.md](mod-layout.md). Review metadata and visibility in the Workshop
submission screen, resolve its validation errors, then use its final submission
control when you intend to publish. Do not treat the installation's flat template
as proof of the current B42 mod discovery layout.

**[unknown]** The Lua UI alone does not establish preview dimension/size limits,
all accepted content constraints, Steam ownership requirements or current service
policy. This reference does not invent limits or claim an upload was tested.
The game UI's own validation is the concrete check available in these files.

**[observed]** Three source checks and byte-for-byte regeneration of the wrapper
metadata/file inventories are recorded in `HANDOFF.md`.
