# Moodles

Survey date: 2026-10-24, Build 42. Reference: `../../data/exposed-methods.csv`. Names and signatures only.

- Java class: `zombie.characters.Moodles.Moodles` (class)
- Extends: `-`; implements: `-`
- Summary [inferred from member names]: Moodle (status icon) levels for a character.
- Lua access: static members at the class table (`zombie.characters.Moodles.Moodles` or the short name when unique), instance members through `obj:method(...)`. Members inherited from the superclass chain are available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).
- Declared public members: 8 instance, 0 static, 3 static fields, 1 constructors.

## Constructors (`Moodles.new`)

- `new(IsoGameCharacter parent)`

## Static fields (snapshot values)

- `BadMoodleType`: `int`
- `GoodMoodleType`: `int`
- `NeutralMoodleType`: `int`

## Instance methods

- `getGoodBadNeutral(MoodleType moodleType)` -> `int`
- `getMoodleDescriptionString(MoodleType moodleType)` -> `String`
- `getMoodleDisplayString(MoodleType moodleType)` -> `String`
- `getMoodleLevel(MoodleType moodleType)` -> `int`
- `isMaxMoodleLevel(MoodleType moodleType)` -> `boolean`
- `setMoodlesStateChanged(boolean refresh)` -> `void`
- `UI_RefreshNeeded()` -> `boolean`
- `Update()` -> `void`
