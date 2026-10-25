# IsoWindow

Survey date: 2026-10-24, Build 42. Reference: `../../data/exposed-methods.csv`. Names and signatures only.

- Java class: `zombie.iso.objects.IsoWindow` (class)
- Extends: `IsoObject`; implements: `BarricadeAble, Thumpable`
- Summary [inferred from member names]: A window object: open/close, curtains, glass state, barricade.
- Lua access: static members at the class table (`zombie.iso.objects.IsoWindow` or the short name when unique), instance members through `obj:method(...)`. Members inherited from the superclass chain are available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).
- Declared public members: 74 instance, 10 static, 3 static fields, 2 constructors.

## Constructors (`IsoWindow.new`)

- `new(IsoCell cell)`
- `new(IsoCell cell, IsoGridSquare gridSquare, IsoSprite gid, boolean north)`

## Static fields (snapshot values)

- `NoWeaponDoorDamage`: `float`
- `SMASH_SOUND_RADIUS`: `int`
- `WeaponDoorDamageModifier`: `float`

## Static methods

- `addSheetRope(IsoPlayer player, IsoGridSquare sq, boolean north, String itemType)` -> `boolean`
- `canAddSheetRope(IsoGridSquare sq, boolean north)` -> `boolean`
- `canClimbHere(IsoGridSquare sq)` -> `boolean`
- `canClimbThroughHelper(IsoGameCharacter chr, IsoGridSquare sq, IsoGridSquare oppositeSq, boolean north)` -> `boolean`
- `countAddSheetRope(IsoGridSquare sq, boolean north)` -> `int`
- `isSheetRopeHere(IsoGridSquare sq)` -> `boolean`
- `isTopOfSheetRopeHere(IsoGridSquare sq)` -> `boolean`
- `isTopOfSheetRopeHere(IsoGridSquare sq, boolean north)` -> `boolean`
- `removeSheetRope(IsoPlayer player, IsoGridSquare square, boolean north)` -> `boolean`
- `resetCurrentCellWindows()` -> `void`

## Instance methods

- `addBarricadesDebug(int numPlanks, boolean metal)` -> `IsoBarricade`
- `addBrokenGlass(IsoMovingObject chr)` -> `void`
- `addBrokenGlass(boolean onOppositeSquare)` -> `void`
- `addRandomBarricades()` -> `void`
- `addSheet(IsoGameCharacter chr)` -> `void`
- `addSheetRope(IsoPlayer player, String itemType)` -> `boolean`
- `addToWorld()` -> `void`
- `AttackObject(IsoGameCharacter owner)` -> `void`
- `canAddSheetRope()` -> `boolean`
- `canAttackBypassIsoBarricade(IsoGameCharacter isoGameCharacter, HandWeapon handWeapon)` -> `boolean`
- `canClimbThrough(IsoGameCharacter chr)` -> `boolean`
- `countAddSheetRope()` -> `int`
- `Damage(float amount)` -> `void`
- `getAddSheetSquare(IsoGameCharacter chr)` -> `IsoGridSquare`
- `getBarricadeForCharacter(IsoGameCharacter chr)` -> `IsoBarricade`
- `getBarricadeOnOppositeSquare()` -> `IsoBarricade`
- `getBarricadeOnSameSquare()` -> `IsoBarricade`
- `getBarricadeOppositeCharacter(IsoGameCharacter chr)` -> `IsoBarricade`
- `getFacingPosition(Vector2 pos)` -> `Vector2`
- `getFirstCharacterClimbingThrough()` -> `IsoGameCharacter`
- `getFirstCharacterClimbingThrough(IsoGridSquare square)` -> `IsoGameCharacter`
- `getFirstCharacterClosing()` -> `IsoGameCharacter`
- `getFirstCharacterClosing(IsoGridSquare square)` -> `IsoGameCharacter`
- `getHealth()` -> `int`
- `getIndoorSquare()` -> `IsoGridSquare`
- `getNorth()` -> `boolean`
- `getObjectName()` -> `String`
- `getOpenSprite()` -> `IsoSprite`
- `getSmashedSprite()` -> `IsoSprite`
- `getThumpableFor(IsoGameCharacter chr)` -> `Thumpable`
- `getThumpableFor(IsoGameCharacter chr, HandWeapon weapon)` -> `Thumpable`
- `getThumpCondition()` -> `float`
- `HasCurtains()` -> `IsoCurtain`
- `haveSheetRope()` -> `boolean`
- `isBarricadeAllowed()` -> `boolean`
- `isBarricaded()` -> `boolean`
- `isBlocked()` -> `boolean`
- `isBlocked(GridSquareEdgeFacingDirection facingDirection)` -> `boolean`
- `isDestroyed()` -> `boolean`
- `isExterior()` -> `boolean`
- `isGlassRemoved()` -> `boolean`
- `isInvincible()` -> `boolean`
- `isLocked()` -> `boolean`
- `isNorth()` -> `boolean`
- `IsOpen()` -> `boolean`
- `isPermaLocked()` -> `boolean`
- `isSmashed()` -> `boolean`
- `load(ByteBuffer input, int worldVersion, boolean isDebugSave)` -> `void`
- `loadState(ByteBuffer bb)` -> `void`
- `onMouseLeftClick(int x, int y)` -> `boolean`
- `openCloseCurtain(IsoGameCharacter chr)` -> `void`
- `removeBrokenGlass()` -> `void`
- `removeFromWorld()` -> `void`
- `removeSheet(IsoGameCharacter chr)` -> `void`
- `removeSheetRope(IsoPlayer player)` -> `boolean`
- `reset()` -> `void`
- `save(ByteBuffer output, boolean isDebugSave)` -> `void`
- `saveState(ByteBuffer bb)` -> `void`
- `setGlassRemoved(boolean removed)` -> `void`
- `setIsLocked(boolean lock)` -> `void`
- `setOpenSprite(IsoSprite sprite)` -> `void`
- `setPermaLocked(Boolean permaLock)` -> `void`
- `setSmashed(boolean destroyed)` -> `void`
- `setSmashedSprite(IsoSprite sprite)` -> `void`
- `smashWindow(boolean bRemote, boolean doAlarm)` -> `void`
- `smashWindow(boolean bRemote)` -> `void`
- `smashWindow()` -> `void`
- `syncIsoObjectReceive(ByteBufferReader bb)` -> `void`
- `syncIsoObjectSend(ByteBufferWriter b)` -> `void`
- `TestCollide(IsoMovingObject obj, IsoGridSquare from, IsoGridSquare to)` -> `boolean`
- `TestVision(IsoGridSquare from, IsoGridSquare to)` -> `IsoObject.VisionResult`
- `Thump(IsoMovingObject thumper, int thumpEventCount)` -> `void`
- `ToggleWindow(IsoGameCharacter chr)` -> `void`
- `WeaponHit(IsoGameCharacter owner, HandWeapon weapon)` -> `void`
