# IsoPushableObject

Survey date: 2026-10-24, Build 42. Reference: `../../data/exposed-methods.csv`. Names and signatures only.

- Java class: `zombie.iso.IsoPushableObject` (class)
- Extends: `IsoMovingObject`; implements: `-`
- Summary [inferred from member names]: A pushable world object.
- Lua access: static members at the class table (`zombie.iso.IsoPushableObject` or the short name when unique), instance members through `obj:method(...)`. Members inherited from the superclass chain are available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).
- Declared public members: 7 instance, 0 static, 0 static fields, 3 constructors.

## Constructors (`IsoPushableObject.new`)

- `new(IsoCell cell)`
- `new(IsoCell cell, int x, int y, int z)`
- `new(IsoCell cell, IsoGridSquare square, IsoSprite spr)`

## Instance methods

- `DoCollideNorS()` -> `void`
- `DoCollideWorE()` -> `void`
- `getObjectName()` -> `String`
- `getWeight(float x, float y)` -> `float`
- `load(ByteBuffer input, int worldVersion, boolean isDebugSave)` -> `void`
- `save(ByteBuffer output, boolean isDebugSave)` -> `void`
- `update()` -> `void`
