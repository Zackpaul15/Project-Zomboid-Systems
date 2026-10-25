# Moveable

Survey date: 2026-10-24, Build 42. Reference: `../../data/exposed-methods.csv`. Names and signatures only.

- Java class: `zombie.inventory.types.Moveable` (class)
- Extends: `InventoryItem`; implements: `-`
- Summary [inferred from member names]: Moveable furniture items.
- Lua access: static members at the class table (`zombie.inventory.types.Moveable` or the short name when unique), instance members through `obj:method(...)`. Members inherited from the superclass chain are available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).
- Declared public members: 32 instance, 0 static, 0 static fields, 2 constructors.

## Constructors (`Moveable.new`)

- `new(String module, String name, String type, String tex)`
- `new(String module, String name, String type, Item item)`

## Instance methods

- `CanBeDroppedOnFloor()` -> `boolean`
- `getCustomIcon(String sprite)` -> `void`
- `getCustomNameFull()` -> `String`
- `getDisplayName()` -> `String`
- `getLightB()` -> `float`
- `getLightBulbItem()` -> `String`
- `getLightDelta()` -> `float`
- `getLightG()` -> `float`
- `getLightPower()` -> `float`
- `getLightR()` -> `float`
- `getMovableFullName()` -> `String`
- `getName()` -> `String`
- `getName(IsoPlayer player)` -> `String`
- `getSpriteGrid()` -> `IsoSpriteGrid`
- `getWorldSprite()` -> `String`
- `isLight()` -> `boolean`
- `isLightHasBattery()` -> `boolean`
- `isLightUseBattery()` -> `boolean`
- `isMultiGridAnchor()` -> `boolean`
- `load(ByteBuffer input, int worldVersion)` -> `void`
- `ReadFromWorldSprite(String sprite)` -> `boolean`
- `save(ByteBuffer output, boolean net)` -> `void`
- `setLight(boolean isLight)` -> `void`
- `setLightB(float lightB)` -> `void`
- `setLightBulbItem(String lightBulbItem)` -> `void`
- `setLightDelta(float lightDelta)` -> `void`
- `setLightG(float lightG)` -> `void`
- `setLightHasBattery(boolean lightHasBattery)` -> `void`
- `setLightPower(float lightPower)` -> `void`
- `setLightR(float lightR)` -> `void`
- `setLightUseBattery(boolean lightUseBattery)` -> `void`
- `setWorldSprite(String worldSprite)` -> `void`
