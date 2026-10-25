# Literature

Survey date: 2026-10-24, Build 42. Reference: `../../data/exposed-methods.csv`. Names and signatures only.

- Java class: `zombie.inventory.types.Literature` (class)
- Extends: `InventoryItem`; implements: `-`
- Summary [inferred from member names]: Books, magazines and skill books.
- Lua access: static members at the class table (`zombie.inventory.types.Literature` or the short name when unique), instance members through `obj:method(...)`. Members inherited from the superclass chain are available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).
- Declared public members: 46 instance, 0 static, 0 static fields, 2 constructors.

## Constructors (`Literature.new`)

- `new(String module, String name, String itemType, String texName)`
- `new(String module, String name, String itemType, Item item)`

## Instance methods

- `addPage(Integer index, String text)` -> `void`
- `canBeWrite()` -> `boolean`
- `containsBuildRecipe()` -> `boolean`
- `containsCraftOrBuildRecipe()` -> `boolean`
- `containsCraftRecipe()` -> `boolean`
- `containsGrowingSeason()` -> `boolean`
- `containsKnownRecipe(IsoGameCharacter chr)` -> `boolean`
- `containsMiscRecipe()` -> `boolean`
- `DoTooltip(ObjectTooltip tooltipUI, ObjectTooltip.Layout layout)` -> `void`
- `finishupdate()` -> `boolean`
- `getAlreadyReadPages()` -> `int`
- `getBookName()` -> `String`
- `getBoredomChange()` -> `float`
- `getCategory()` -> `String`
- `getCustomPages()` -> `HashMap<Integer, String>`
- `getKnownMiscRecipes(IsoGameCharacter chr)` -> `List<String>`
- `getKnownRecipes(IsoGameCharacter chr)` -> `List<String>`
- `getLearnedRecipes()` -> `List<String>`
- `getLockedBy()` -> `String`
- `getLvlSkillTrained()` -> `int`
- `getMaxLevelTrained()` -> `int`
- `getNumberOfPages()` -> `int`
- `getNumLevelsTrained()` -> `int`
- `getPageToWrite()` -> `int`
- `getReadType()` -> `String`
- `getSkillTrained()` -> `String`
- `getStressChange()` -> `float`
- `getUnhappyChange()` -> `float`
- `hasRecipe(String recipe)` -> `boolean`
- `isEmptyPages()` -> `boolean`
- `IsLiterature()` -> `boolean`
- `load(ByteBuffer input, int worldVersion)` -> `void`
- `save(ByteBuffer output, boolean net)` -> `void`
- `seePage(Integer index)` -> `String`
- `setAlreadyReadPages(int alreadyReadPages)` -> `void`
- `setBookName(String bookName)` -> `void`
- `setCanBeWrite(boolean canBeWrite)` -> `void`
- `setCustomPages(HashMap<Integer, String> customPages)` -> `void`
- `setLearnedRecipes(List<String> learnedRecipes)` -> `void`
- `setLockedBy(String lockedBy)` -> `void`
- `setLvlSkillTrained(int lvlSkillTrained)` -> `void`
- `setNumberOfPages(int numberOfPages)` -> `void`
- `setNumLevelsTrained(int numLevelsTrained)` -> `void`
- `setPageToWrite(int pageToWrite)` -> `void`
- `setSkillTrained(String skillTrained)` -> `void`
- `update()` -> `void`
