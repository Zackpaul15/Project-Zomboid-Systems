# IsoBuilding

Survey date: 2026-10-24, Build 42. Reference: `../../data/exposed-methods.csv`. Names and signatures only.

- Java class: `zombie.iso.areas.IsoBuilding` (class)
- Extends: `-`; implements: `-`
- Summary [inferred from member names]: A building: rooms, squares, def.
- Lua access: static members at the class table (`zombie.iso.areas.IsoBuilding` or the short name when unique), instance members through `obj:method(...)`. Members inherited from the superclass chain are available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).
- Declared public members: 36 instance, 0 static, 3 static fields, 2 constructors.

## Constructors (`IsoBuilding.new`)

- `new()`
- `new(IsoCell cell)`

## Static fields (snapshot values)

- `goodBuildingScore`: `float`
- `idCount`: `int`
- `poorBuildingScore`: `float`

## Instance methods

- `addDoor(IsoDoor obj, boolean bOtherTile, IsoGridSquare from, IsoBuilding building)` -> `void`
- `addDoor(IsoDoor obj, boolean bOtherTile)` -> `void`
- `AddRoom(IsoRoom room)` -> `void`
- `addWindow(IsoWindow obj, boolean bOtherTile, IsoGridSquare from, IsoBuilding building)` -> `void`
- `addWindow(IsoWindow obj, boolean bOtherTile)` -> `void`
- `CalculateExits()` -> `void`
- `CalculateWindows()` -> `void`
- `ContainsAllItems(Stack<String> items)` -> `boolean`
- `containsRoom(String room)` -> `boolean`
- `CreateFrom(BuildingDef building, IsoMetaCell metaCell)` -> `void`
- `FillContainers()` -> `void`
- `forceAwake()` -> `void`
- `getContainerWith(ItemType itemType)` -> `ItemContainer`
- `getDef()` -> `BuildingDef`
- `getFreeTile()` -> `IsoGridSquare`
- `getID()` -> `int`
- `getRandomContainer(String type)` -> `ItemContainer`
- `getRandomContainerSingle(String type)` -> `ItemContainer`
- `getRandomFirstFloorWindow()` -> `IsoWindow`
- `getRandomRoom()` -> `IsoRoom`
- `getRandomRoom(String room)` -> `IsoRoom`
- `getRandomRoomExcluding(List<String> badRooms)` -> `IsoRoom`
- `getRoomsNumber()` -> `int`
- `hasBasement()` -> `boolean`
- `hasRoom(String room)` -> `boolean`
- `hasWater()` -> `boolean`
- `isAllExplored()` -> `boolean`
- `isEntirelyEmptyOutside()` -> `boolean`
- `isResidential()` -> `boolean`
- `isToxic()` -> `boolean`
- `ScoreBuildingPersonSpecific(SurvivorDesc desc, boolean bFarGood)` -> `float`
- `setAllExplored(boolean b)` -> `void`
- `setAllExplored(boolean b, IsoRoom exception)` -> `void`
- `setToxic(boolean isToxic)` -> `void`
- `TriggerAlarm()` -> `void`
- `update()` -> `void`
