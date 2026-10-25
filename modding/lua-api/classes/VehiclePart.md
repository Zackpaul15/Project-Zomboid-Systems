# VehiclePart

Survey date: 2026-10-24, Build 42. Reference: `../../data/exposed-methods.csv`. Names and signatures only.

- Java class: `zombie.vehicles.VehiclePart` (class)
- Extends: `GameEntity`; implements: `ChatElementOwner, WaveSignalDevice`
- Summary [inferred from member names]: One vehicle part: condition, container, and install state.
- Lua access: static members at the class table (`zombie.vehicles.VehiclePart` or the short name when unique), instance members through `obj:method(...)`. Members inherited from the superclass chain are available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).
- Declared public members: 103 instance, 1 static, 0 static fields, 1 constructors.

## Constructors (`VehiclePart.new`)

- `new(VehiclePartOwner vehicle)`

## Static methods

- `getNumberByCondition(float number, float cond, float min)` -> `float`

## Instance methods

- `addChild(VehiclePart child)` -> `void`
- `AddDeviceText(String line, float r, float g, float b, String guid, String codes, int distance)` -> `void`
- `clearFlags()` -> `void`
- `createSignalDevice()` -> `DeviceData`
- `createSpotLight(float xOffset, float yOffset, float dist, float intensity, float dot, int focusing)` -> `void`
- `createSpotLightColor(float xOffset, float yOffset, float dist, float intensity, float dot, int focusing, float r, float g, float b)` -> `void`
- `damage(int amount)` -> `void`
- `doInventoryItemStats(InventoryItem newItem, int mechanicSkill)` -> `void`
- `findWindow()` -> `VehicleWindow`
- `getAnimById(String id)` -> `VehicleScript.Anim`
- `getArea()` -> `String`
- `getCategory()` -> `String`
- `getChatElement()` -> `ChatElement`
- `getChild(int index)` -> `VehiclePart`
- `getChildCount()` -> `int`
- `getChildWindow()` -> `VehiclePart`
- `getCondition()` -> `int`
- `getContainerCapacity()` -> `int`
- `getContainerCapacity(IsoGameCharacter chr)` -> `int`
- `getContainerCloseSound()` -> `String`
- `getContainerContentAmount()` -> `float`
- `getContainerContentType()` -> `String`
- `getContainerOpenSound()` -> `String`
- `getContainerPutSound()` -> `String`
- `getContainerSeatNumber()` -> `int`
- `getContainerTakeSound()` -> `String`
- `getDelta()` -> `float`
- `getDeviceData()` -> `DeviceData`
- `getDoor()` -> `VehicleDoor`
- `getDurability()` -> `float`
- `getEnclosingDoor()` -> `VehicleDoor`
- `getEngineLoudness()` -> `float`
- `getEntityNetID()` -> `long`
- `getFlag(short flag)` -> `boolean`
- `getGameEntityType()` -> `GameEntityType`
- `getId()` -> `String`
- `getIndex()` -> `int`
- `getInventoryItem()` -> `T`
- `getItemContainer()` -> `ItemContainer`
- `getItemType()` -> `ArrayList<String>`
- `getLastUpdated()` -> `float`
- `getLight()` -> `VehicleLight`
- `getLightDistance()` -> `float`
- `getLightFocusing()` -> `float`
- `getLightIntensity()` -> `float`
- `getLuaFunction(String name)` -> `String`
- `getMechanicArea()` -> `String`
- `getMechanicSkillInstaller()` -> `int`
- `getModData()` -> `KahluaTable`
- `getOwner()` -> `VehiclePartOwner`
- `getParent()` -> `VehiclePart`
- `getScriptPart()` -> `VehicleScript.Part`
- `getSquare()` -> `IsoGridSquare`
- `getSuspensionCompression()` -> `float`
- `getSuspensionDamping()` -> `float`
- `getTable(String id)` -> `KahluaTable`
- `getVehicle()` -> `BaseVehicle`
- `getVehicleEngine()` -> `VehicleEngine`
- `getWheelFriction()` -> `float`
- `getWheelIndex()` -> `int`
- `getWindow()` -> `VehicleWindow`
- `getX()` -> `float`
- `getY()` -> `float`
- `getZ()` -> `float`
- `hasDevicePower()` -> `boolean`
- `hasModData()` -> `boolean`
- `HasPlayerInRange()` -> `boolean`
- `isContainer()` -> `boolean`
- `isEntityValid()` -> `boolean`
- `isInventoryItemUninstalled()` -> `boolean`
- `isSeat()` -> `boolean`
- `isSetAllModelsVisible()` -> `boolean`
- `isSpecificItem()` -> `boolean`
- `isVehicleTrunk()` -> `boolean`
- `load(ByteBuffer input, int worldVersion)` -> `void`
- `repair()` -> `void`
- `save(ByteBuffer output)` -> `void`
- `setAllModelsVisible(boolean visible)` -> `void`
- `setCategory(String category)` -> `void`
- `setCondition(int condition)` -> `void`
- `setContainerCapacity(int cap)` -> `void`
- `setContainerContentAmount(float amount)` -> `void`
- `setContainerContentAmount(float amount, boolean force, boolean noUpdateMass)` -> `void`
- `setDelta(float d)` -> `void`
- `setDeviceData(DeviceData data)` -> `void`
- `setDurability(float durability)` -> `void`
- `setEngineLoudness(float engineLoudness)` -> `void`
- `setFlag(short flag)` -> `void`
- `setGeneralCondition(InventoryItem item, float baseQuality, float chanceToSpawnDamaged)` -> `void`
- `setInventoryItem(InventoryItem item, int mechanicSkill)` -> `void`
- `setInventoryItem(InventoryItem item)` -> `void`
- `setItemContainer(ItemContainer container)` -> `void`
- `setLastUpdated(float hours)` -> `void`
- `setLightActive(boolean active)` -> `void`
- `setMechanicSkillInstaller(int mechanicSkillInstaller)` -> `void`
- `setModelVisible(String id, boolean visible)` -> `void`
- `setRandomCondition(InventoryItem item)` -> `void`
- `setScriptPart(VehicleScript.Part scriptPart)` -> `void`
- `setSpecificItem(boolean specificItem)` -> `void`
- `setSuspensionCompression(float suspensionCompression)` -> `void`
- `setSuspensionDamping(float suspensionDamping)` -> `void`
- `setWheelFriction(float wheelFriction)` -> `void`
- `updateSignalDevice()` -> `void`
