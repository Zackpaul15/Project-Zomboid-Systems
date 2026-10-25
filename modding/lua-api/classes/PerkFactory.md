# PerkFactory

Survey date: 2026-10-24, Build 42. Reference: `../../data/exposed-methods.csv`. Names and signatures only.

- Java class: `zombie.characters.skills.PerkFactory` (class)
- Extends: `-`; implements: `-`
- Summary [inferred from member names]: Registry of perks (skills) and their definitions.
- Lua access: static members at the class table (`zombie.characters.skills.PerkFactory` or the short name when unique), instance members through `obj:method(...)`. Members inherited from the superclass chain are available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).
- Declared public members: 0 instance, 10 static, 1 static fields, 0 constructors.

## Static fields (snapshot values)

- `PerkList`: `ArrayList<PerkFactory.Perk>`

## Static methods

- `AddPerk(PerkFactory.Perk perk, String translation, int xp1, int xp2, int xp3, int xp4, int xp5, int xp6, int xp7, int xp8, int xp9, int xp10)` -> `PerkFactory.Perk`
- `AddPerk(PerkFactory.Perk perk, String translation, int xp1, int xp2, int xp3, int xp4, int xp5, int xp6, int xp7, int xp8, int xp9, int xp10, boolean passiv)` -> `PerkFactory.Perk`
- `AddPerk(PerkFactory.Perk perk, String translation, PerkFactory.Perk parent, int xp1, int xp2, int xp3, int xp4, int xp5, int xp6, int xp7, int xp8, int xp9, int xp10)` -> `PerkFactory.Perk`
- `AddPerk(PerkFactory.Perk perk, String translation, PerkFactory.Perk parent, int xp1, int xp2, int xp3, int xp4, int xp5, int xp6, int xp7, int xp8, int xp9, int xp10, boolean passiv)` -> `PerkFactory.Perk`
- `getPerk(PerkFactory.Perk perk)` -> `PerkFactory.Perk`
- `getPerkFromName(String name)` -> `PerkFactory.Perk`
- `getPerkName(PerkFactory.Perk type)` -> `String`
- `init()` -> `void`
- `initTranslations()` -> `void`
- `Reset()` -> `void`
