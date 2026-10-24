# Exposed class pages

Survey date: 2026-10-24, Build 42. One page per commonly used Lua-exposed class; the complete list of 999 whitelisted classes is `../../data/exposed-classes.csv` and every declared public member is in `../../data/exposed-methods.csv`.

| Class | Java type | Summary [inferred] | Instance | Static |
|---|---|---|---|---|
| [IsoGameCharacter](IsoGameCharacter.md) | `zombie.characters.IsoGameCharacter` | Base of every living thing in the world (players, zombies, animals): stats, inventory, perks, health, animation state, actions. | 1184 | 11 |
| [IsoPlayer](IsoPlayer.md) | `zombie.characters.IsoPlayer` | A player character; indexed by player number for local split-screen. Adds input, XP, and per-player UI hooks. | 356 | 30 |
| [IsoZombie](IsoZombie.md) | `zombie.characters.IsoZombie` | A zombie: targeting, state, outfit, and attack/hit helpers. | 207 | 1 |
| [IsoAnimal](IsoAnimal.md) | `zombie.characters.animals.IsoAnimal` | A farm animal: breed, genes, age, hutch and stat helpers. | 236 | 3 |
| [BodyDamage](BodyDamage.md) | `zombie.characters.BodyDamage.BodyDamage` | A character's health model: infection, wounds, temperature, and overall health. | 219 | 2 |
| [BodyPart](BodyPart.md) | `zombie.characters.BodyDamage.BodyPart` | One body part's injury state (bleeding, scratch, bite, fracture, bandage). | 133 | 0 |
| [Nutrition](Nutrition.md) | `zombie.characters.BodyDamage.Nutrition` | Weight and macronutrient tracking for a character. | 23 | 0 |
| [Moodles](Moodles.md) | `zombie.characters.Moodles.Moodles` | Moodle (status icon) levels for a character. | 8 | 0 |
| [Stats](Stats.md) | `zombie.characters.Stats` | Core survival stats such as hunger, thirst, fatigue, stress, endurance. | 33 | 0 |
| [PerkFactory](PerkFactory.md) | `zombie.characters.skills.PerkFactory` | Registry of perks (skills) and their definitions. | 0 | 10 |
| [CharacterTraits](CharacterTraits.md) | `zombie.characters.traits.CharacterTraits` | The trait list of a character. | 13 | 0 |
| [Faction](Faction.md) | `zombie.characters.Faction` | Player faction data. | 17 | 11 |
| [IsoMovingObject](IsoMovingObject.md) | `zombie.iso.IsoMovingObject` | Base of anything that moves in the world: position, velocity, collision, square tracking. | 184 | 3 |
| [IsoObject](IsoObject.md) | `zombie.iso.IsoObject` | Base of every world object (furniture, walls, containers, doors): sprite, container, modData, tile properties. | 400 | 15 |
| [IsoGridSquare](IsoGridSquare.md) | `zombie.iso.IsoGridSquare` | One tile column at x, y, z: its objects, floor, flags, neighbours, room and building. | 616 | 20 |
| [IsoCell](IsoCell.md) | `zombie.iso.IsoCell` | The loaded world cell: grid access, lists of characters and objects, and tile lookup. | 171 | 13 |
| [IsoWorld](IsoWorld.md) | `zombie.iso.IsoWorld` | The world singleton: map, zones, spawning, metagrid and world-level state. | 102 | 8 |
| [IsoChunk](IsoChunk.md) | `zombie.iso.IsoChunk` | A chunk of squares (the unit of loading). | 104 | 12 |
| [IsoSprite](IsoSprite.md) | `zombie.iso.sprite.IsoSprite` | A tile sprite definition and its properties. | 97 | 11 |
| [IsoLightSource](IsoLightSource.md) | `zombie.iso.IsoLightSource` | A light source in the world. | 26 | 0 |
| [IsoPushableObject](IsoPushableObject.md) | `zombie.iso.IsoPushableObject` | A pushable world object. | 7 | 0 |
| [IsoThumpable](IsoThumpable.md) | `zombie.iso.objects.IsoThumpable` | Player-built or destructible structures (walls, doors, barricades). | 161 | 2 |
| [IsoDeadBody](IsoDeadBody.md) | `zombie.iso.objects.IsoDeadBody` | A corpse in the world. | 113 | 8 |
| [IsoDoor](IsoDoor.md) | `zombie.iso.objects.IsoDoor` | A door object: open/close/lock, barricade state. | 87 | 14 |
| [IsoWindow](IsoWindow.md) | `zombie.iso.objects.IsoWindow` | A window object: open/close, curtains, glass state, barricade. | 74 | 10 |
| [IsoGenerator](IsoGenerator.md) | `zombie.iso.objects.IsoGenerator` | A generator: fuel, condition, activation, connected power. | 33 | 5 |
| [IsoStove](IsoStove.md) | `zombie.iso.objects.IsoStove` | A stove or oven: temperature and on/off. | 28 | 0 |
| [IsoLightSwitch](IsoLightSwitch.md) | `zombie.iso.objects.IsoLightSwitch` | A light switch and its connected lights. | 53 | 1 |
| [IsoWorldInventoryObject](IsoWorldInventoryObject.md) | `zombie.iso.objects.IsoWorldInventoryObject` | An inventory item lying on the ground. | 55 | 2 |
| [IsoRoom](IsoRoom.md) | `zombie.iso.areas.IsoRoom` | A room inside a building. | 42 | 0 |
| [IsoBuilding](IsoBuilding.md) | `zombie.iso.areas.IsoBuilding` | A building: rooms, squares, def. | 36 | 0 |
| [SafeHouse](SafeHouse.md) | `zombie.iso.areas.SafeHouse` | A claimed safehouse (multiplayer). | 47 | 32 |
| [ClimateManager](ClimateManager.md) | `zombie.iso.weather.ClimateManager` | Weather and climate: temperature, wind, precipitation, fog, day/night colors. | 133 | 15 |
| [InventoryItem](InventoryItem.md) | `zombie.inventory.InventoryItem` | Base of every item instance: type, name, weight, condition, modData, container. | 627 | 5 |
| [ItemContainer](ItemContainer.md) | `zombie.inventory.ItemContainer` | An item container (bag, crate, player inventory): add, remove, search items. | 366 | 2 |
| [ItemPickerJava](ItemPickerJava.md) | `zombie.inventory.ItemPickerJava` | Loot distribution helpers (rolling items into containers). | 0 | 44 |
| [HandWeapon](HandWeapon.md) | `zombie.inventory.types.HandWeapon` | Melee and ranged weapon items: damage, range, ammo, parts. | 312 | 1 |
| [Clothing](Clothing.md) | `zombie.inventory.types.Clothing` | Clothing items: protection, insulation, condition and patches. | 105 | 3 |
| [Food](Food.md) | `zombie.inventory.types.Food` | Food items: hunger, nutrition, cooking, spoilage. | 171 | 0 |
| [Literature](Literature.md) | `zombie.inventory.types.Literature` | Books, magazines and skill books. | 46 | 0 |
| [Moveable](Moveable.md) | `zombie.inventory.types.Moveable` | Moveable furniture items. | 32 | 0 |
| [InventoryContainer](InventoryContainer.md) | `zombie.inventory.types.InventoryContainer` | Items that are also containers (backpacks, bags). | 28 | 0 |
| [BaseVehicle](BaseVehicle.md) | `zombie.vehicles.BaseVehicle` | A vehicle: parts, engine, fuel, passengers, physics. | 564 | 22 |
| [VehiclePart](VehiclePart.md) | `zombie.vehicles.VehiclePart` | One vehicle part: condition, container, and install state. | 103 | 1 |
| [GameTime](GameTime.md) | `zombie.GameTime` | Game clock, calendar and day/night helpers. | 124 | 15 |
| [SandboxOptions](SandboxOptions.md) | `zombie.SandboxOptions` | Sandbox settings (world rules chosen at game creation). | 57 | 3 |
| [Core](Core.md) | `zombie.core.Core` | Game settings and options (resolution, key bindings, graphics, difficulty flags). | 488 | 19 |
| [Texture](Texture.md) | `zombie.core.textures.Texture` | A texture: lookup by name, size, drawing helpers. | 79 | 17 |
| [UIElement](UIElement.md) | `zombie.ui.UIElement` | Base of Java-backed UI elements; the Lua `ISUIElement` hierarchy wraps it. | 169 | 0 |
| [UIManager](UIManager.md) | `zombie.ui.UIManager` | UI singleton: element list, screen sizes, mouse and picking helpers. | 0 | 113 |
| [TextManager](TextManager.md) | `zombie.ui.TextManager` | Font metrics and text drawing. | 33 | 0 |
| [ScriptManager](ScriptManager.md) | `zombie.scripting.ScriptManager` | Script registry: look up item, recipe, vehicle, sound and other script objects by name. | 112 | 9 |
| [Item](Item.md) | `zombie.scripting.objects.Item` | An item script definition (the template, not an instance). | 347 | 0 |
| [Recipe](Recipe.md) | `zombie.scripting.objects.Recipe` | A legacy recipe script definition. | 22 | 0 |
| [CraftRecipe](CraftRecipe.md) | `zombie.scripting.entity.components.crafting.CraftRecipe` | A Build 42 crafting recipe definition. | 123 | 1 |
| [VehicleScript](VehicleScript.md) | `zombie.scripting.objects.VehicleScript` | A vehicle script definition. | 123 | 0 |
| [BaseSoundEmitter](BaseSoundEmitter.md) | `zombie.audio.BaseSoundEmitter` | A positional sound emitter. | 41 | 0 |
| [SoundManager](SoundManager.md) | `zombie.SoundManager` | Global sound manager (music, ambient, UI sounds). | 82 | 0 |
| [ModData](ModData.md) | `zombie.world.moddata.ModData` | Global mod data tables (shared persistent storage). | 0 | 10 |
| [ServerOptions](ServerOptions.md) | `zombie.network.ServerOptions` | Server option values (multiplayer). | 19 | 4 |
