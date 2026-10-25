# IsoDoor

Survey date: 2026-10-24, Build 42. Reference: `../../data/exposed-methods.csv`. Names and signatures only.

- Java class: `zombie.iso.objects.IsoDoor` (class)
- Extends: `IsoObject`; implements: `BarricadeAble, Thumpable, IHasHealth, ILockableDoor, ICurtain`
- Summary [inferred from member names]: A door object: open/close/lock, barricade state.
- Lua access: static members at the class table (`zombie.iso.objects.IsoDoor` or the short name when unique), instance members through `obj:method(...)`. Members inherited from the superclass chain are available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).
- Declared public members: 87 instance, 14 static, 2 static fields, 4 constructors.

## Constructors (`IsoDoor.new`)

- `new(IsoCell cell)`
- `new(IsoCell cell, IsoGridSquare gridSquare, IsoSprite gid, boolean north)`
- `new(IsoCell cell, IsoGridSquare gridSquare, String gid, boolean north)`
- `new(IsoCell cell, IsoGridSquare gridSquare, String gid, boolean north, KahluaTable table)`

## Static fields (snapshot values)

- `BREAK_SOUND_RADIUS`: `int`
- `tempo`: `Vector2`

## Static methods

- `destroyDoubleDoor(IsoObject oneOfFour)` -> `boolean`
- `destroyGarageDoor(IsoObject oneOfThree)` -> `boolean`
- `forEachDoorObject(IsoObject object, Consumer<IsoObject> consumer)` -> `void`
- `getDoubleDoorIndex(IsoObject oneOfFour)` -> `int`
- `getDoubleDoorObject(IsoObject oneOfFour, int index)` -> `IsoObject`
- `getDoubleDoorPartnerIndex(int ddIndex)` -> `int`
- `getGarageDoorFirst(IsoObject oneOfThree)` -> `IsoObject`
- `getGarageDoorIndex(IsoObject oneOfThree)` -> `int`
- `getGarageDoorNext(IsoObject oneOfThree)` -> `IsoObject`
- `getGarageDoorPrev(IsoObject oneOfThree)` -> `IsoObject`
- `isDoorObstructed(IsoObject object)` -> `boolean`
- `isDoubleDoorObstructed(IsoObject oneOfFour)` -> `boolean`
- `toggleDoubleDoor(IsoObject oneOfFour, boolean doSync)` -> `void`
- `toggleGarageDoor(IsoObject oneOfThree, boolean doSync)` -> `void`

## Instance methods

- `addRandomBarricades()` -> `void`
- `addSheet(IsoGameCharacter chr)` -> `void`
- `addSheet(boolean inside, IsoGameCharacter chr)` -> `void`
- `addToWorld()` -> `void`
- `canAddCurtain()` -> `boolean`
- `canClimbOver(IsoGameCharacter chr)` -> `boolean`
- `changeSprite(IsoDoor door)` -> `void`
- `checkKeyHighlight(int playerIndex)` -> `void`
- `checkKeyId()` -> `int`
- `couldBeOpen(IsoGameCharacter chr)` -> `boolean`
- `destroy()` -> `void`
- `forEachDoorObject(Consumer<IsoDoor> consumer)` -> `void`
- `getAddSheetSquare(IsoGameCharacter chr)` -> `IsoGridSquare`
- `getBarricadeForCharacter(IsoGameCharacter chr)` -> `IsoBarricade`
- `getBarricadeOnOppositeSquare()` -> `IsoBarricade`
- `getBarricadeOnSameSquare()` -> `IsoBarricade`
- `getBarricadeOppositeCharacter(IsoGameCharacter chr)` -> `IsoBarricade`
- `getFacingPosition(Vector2 pos)` -> `Vector2`
- `getFacingPositionAlt(Vector2 pos)` -> `Vector2`
- `getHealth()` -> `int`
- `getKeyId()` -> `int`
- `getMaxHealth()` -> `int`
- `getNorth()` -> `boolean`
- `getObjectName()` -> `String`
- `getOpenSprite()` -> `IsoSprite`
- `getOtherSideOfDoor(IsoGameCharacter chr)` -> `IsoGridSquare`
- `getRenderEffectMaster()` -> `IsoObject`
- `getRenderEffectObjectByIndex(int index)` -> `IsoObject`
- `getRenderEffectObjectCount()` -> `int`
- `getSheetSquare()` -> `IsoGridSquare`
- `getSoundPrefix()` -> `String`
- `getSpriteEdge(boolean ignoreOpen)` -> `IsoDirections`
- `getSpriteModel()` -> `SpriteModel`
- `getThumpableFor(IsoGameCharacter chr)` -> `Thumpable`
- `getThumpCondition()` -> `float`
- `getThumpSound()` -> `String`
- `HasCurtains()` -> `IsoDoor`
- `haveKey()` -> `boolean`
- `isAdjacentToSquare(IsoGridSquare square2)` -> `boolean`
- `isBarricadeAllowed()` -> `boolean`
- `isBarricaded()` -> `boolean`
- `isBlocked()` -> `boolean`
- `isBlocked(GridSquareEdgeFacingDirection facingDirection)` -> `boolean`
- `isCurtainOpen()` -> `boolean`
- `isDestroyed()` -> `boolean`
- `isExterior()` -> `boolean`
- `isExteriorDoor(IsoGameCharacter chr)` -> `boolean`
- `isFacingSheet(IsoGameCharacter chr)` -> `boolean`
- `isHoppable()` -> `boolean`
- `isLocked()` -> `boolean`
- `isLockedByKey()` -> `boolean`
- `isObstructed()` -> `boolean`
- `isOpen()` -> `boolean`
- `IsOpen()` -> `boolean`
- `IsStrengthenedByPushedItems()` -> `boolean`
- `load(ByteBuffer input, int worldVersion, boolean isDebugSave)` -> `void`
- `loadChange(IsoObjectChange change, ByteBufferReader bb)` -> `void`
- `loadState(ByteBuffer bb)` -> `void`
- `onMouseLeftClick(int x, int y)` -> `boolean`
- `removeFromWorld()` -> `void`
- `removeSheet(IsoGameCharacter chr)` -> `void`
- `render(float x, float y, float z, ColorInfo info, boolean bDoAttached, boolean bWallLightingPass, Shader shader)` -> `void`
- `renderWallTile(IsoDirections dir, float x, float y, float z, ColorInfo col, boolean bDoAttached, boolean bWallLightingPass, Shader shader, Consumer<TextureDraw> texdModifier)` -> `void`
- `save(ByteBuffer output, boolean isDebugSave)` -> `void`
- `saveChange(IsoObjectChange change, KahluaTable tbl, ByteBufferWriter bb)` -> `void`
- `saveState(ByteBuffer bb)` -> `void`
- `setCurtainOpen(boolean open)` -> `void`
- `setHaveKey(boolean haveKey)` -> `void`
- `setHealth(int health)` -> `void`
- `setIsLocked(boolean lock)` -> `void`
- `setLocked(boolean bLocked)` -> `void`
- `setLockedByKey(boolean lockedByKey)` -> `void`
- `setLockedByKey(boolean lockedByKey, boolean doSync)` -> `void`
- `setOpen(boolean open)` -> `void`
- `setOpenSprite(IsoSprite sprite)` -> `void`
- `syncIsoObject(boolean bRemote, byte val, UdpConnection source, ByteBufferReader bb)` -> `void`
- `syncIsoObjectSend(ByteBufferWriter b)` -> `void`
- `TestCollide(IsoMovingObject obj, IsoGridSquare from, IsoGridSquare to)` -> `boolean`
- `TestPathfindCollide(IsoMovingObject obj, IsoGridSquare from, IsoGridSquare to)` -> `boolean`
- `TestVision(IsoGridSquare from, IsoGridSquare to)` -> `IsoObject.VisionResult`
- `Thump(IsoMovingObject thumper, int thumpEventCount)` -> `void`
- `toggleCurtain()` -> `void`
- `ToggleDoor(IsoGameCharacter chr)` -> `void`
- `ToggleDoorActual(IsoGameCharacter chr)` -> `void`
- `ToggleDoorSilent()` -> `void`
- `transmitSetCurtainOpen(boolean open)` -> `void`
- `WeaponHit(IsoGameCharacter owner, HandWeapon weapon)` -> `void`
