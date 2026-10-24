# Sound scripts (Project Zomboid, Build 42)

Survey date: 2026-10-24. Build identifier: jar sha256 prefix `e1a69eb7`.
Source: installed `media/scripts/**/*.txt`. Claims are **[observed]** unless
marked **[inferred]** or **[unknown]**. No audio or source definitions are copied.

## Coverage and reproduction [observed]

There are **3,038 module-level `sound` definitions in 147 files** and **five
`soundTimeline` definitions in two files**. Every sound definition has a
`category` assignment and one `clip` child in the surveyed text. These counts
are before runtime merging, not counts of unique playable audio resources.
Example files are `generated/sounds/animals/sounds_animal_babyrabbit.txt` and
`generated/sounds/objects/sounds_object_fridge_soundTimeline.txt`.

Run `python -I modding/tools/survey_components.py` to regenerate
[sound-keys.csv](../data/sound-keys.csv) and the shared
[component-blocks.csv](../data/component-blocks.csv). The key table has
`block_type, key, count, value_shape, notes`; paths distinguish `sound/clip`
from the definition's own keys. `<block>` is a count row, not a literal key.
Only module-level sounds are selected, so vehicle-part `sound` children do not
inflate the global sound total.

## Keys and resource links [observed]

| Context | Observed keys | Observed lexical shapes |
|---|---|---|
| `sound` | `category`, `master` | String identifiers |
| `sound` | `loop` | Boolean |
| `sound` | `maxInstancesPerEmitter` | Integer |
| `sound/clip` | `event`, `file` | Strings/paths |
| `sound/clip` | `distanceMax` | Integer |
| `sound/clip` | `volume` | Decimal |
| `soundTimeline` | `idle`, `ElectricityOn` | Integer |

`master` occurs 50 times, `loop` 32 times and `maxInstancesPerEmitter` 22 times.
Of the 3,038 clips, **3,037 have `event`**, **one has `file`**, 280 have
`distanceMax` and one has `volume`. The event identifiers and direct file paths
are deliberately not exported. **[inferred]** The distinction is between a named
audio event and a direct file resource; the predominance of `event` means a sound
definition usually does not point at an obvious standalone audio filename.
**[unknown]** This survey does not inspect sound banks or prove that every event
and path resolves successfully.

**[observed]** Item properties such as `SwingSound` and `CookingSound` match
global sound-block names; [items.md](items.md#names-icons-models-and-sounds)
records aggregate matches. Vehicle scripts have their own nested sound contexts.
**[inferred]** Follow the named definition to its `clip` rather than treating an
item's sound property as a direct audio file path.

## Timelines and boundaries [observed / unknown]

The five sound timelines contain four `idle` assignments and one `ElectricityOn`
assignment. These are marker-shaped integer entries in separate definitions.
**[unknown]** The source shapes alone do not establish timing units, scheduling
rules or which playback path consumes a marker.

The engine-side list in [parser-keys.md](parser-keys.md) is broader than this
observed-key table. **[unknown]** An absent `loop`, `volume` or distance key does
not establish a default. **[inferred]** Counts and lexical shapes cannot establish
audio mixing, attenuation or concurrency behavior; verify those in the consuming
engine code or in-game before relying on them.

**[observed]** Three source checks selected with seed `20261024`: 3,038 clip
children, one clip `file` assignment and 3,038 sound blocks. An independent
module-depth scan confirms family block/file counts; all six X4 CSVs reproduce
byte-for-byte. Checks are recorded in `HANDOFF.md`.
