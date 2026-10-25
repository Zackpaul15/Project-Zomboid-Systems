# Recipe

Survey date: 2026-10-24, Build 42. Reference: `../../data/exposed-methods.csv`. Names and signatures only.

- Java class: `zombie.scripting.objects.Recipe` (class)
- Extends: `BaseScriptObject`; implements: `-`
- Summary [inferred from member names]: A legacy recipe script definition.
- Lua access: static members at the class table (`zombie.scripting.objects.Recipe` or the short name when unique), instance members through `obj:method(...)`. Members inherited from the superclass chain are available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).
- Declared public members: 22 instance, 0 static, 0 static fields, 1 constructors.

## Constructors (`Recipe.new`)

- `new()`

## Instance methods

- `addRequiredSkill(PerkFactory.Perk perk, int level)` -> `void`
- `clearRequiredSkills()` -> `void`
- `DoResult(String type)` -> `void`
- `DoSource(String type)` -> `void`
- `findSource(String sourceFullType)` -> `Recipe.Source`
- `getFullType()` -> `String`
- `getHeat()` -> `float`
- `getName()` -> `String`
- `getNearItem()` -> `String`
- `getNumberOfNeededItem()` -> `int`
- `getOriginalname()` -> `String`
- `getRequiredSkill(int index)` -> `Recipe.RequiredSkill`
- `getRequiredSkillCount()` -> `int`
- `getRequiredSkills()` -> `ArrayList<String>`
- `getResult()` -> `Recipe.Result`
- `getResults()` -> `ArrayList<Recipe.Result>`
- `getSource()` -> `ArrayList<Recipe.Source>`
- `getStationMultiplier()` -> `float`
- `isRequiresWorkstation()` -> `boolean`
- `Load(String name, String totalFile)` -> `void`
- `setNearItem(String nearItem)` -> `void`
- `setOriginalname(String originalname)` -> `void`
