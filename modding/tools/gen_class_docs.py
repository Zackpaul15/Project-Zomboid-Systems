"""Generate modding/lua-api/classes/<Class>.md from exposed-classes.csv and exposed-methods.csv.

Usage:  python -I gen_class_docs.py <data dir> <output dir>

Only declared public members are listed (names, parameter lists, return types); inherited members come from the
superclass chain named in each page. The one-line summaries below are hand-written from member names and are
tagged [inferred].
"""
import csv
import sys
from collections import OrderedDict
from pathlib import Path

CLASSES = OrderedDict([
    ("zombie.characters.IsoGameCharacter", "Base of every living thing in the world (players, zombies, animals): stats, inventory, perks, health, animation state, actions."),
    ("zombie.characters.IsoPlayer", "A player character; indexed by player number for local split-screen. Adds input, XP, and per-player UI hooks."),
    ("zombie.characters.IsoZombie", "A zombie: targeting, state, outfit, and attack/hit helpers."),
    ("zombie.characters.animals.IsoAnimal", "A farm animal: breed, genes, age, hutch and stat helpers."),
    ("zombie.characters.BodyDamage.BodyDamage", "A character's health model: infection, wounds, temperature, and overall health."),
    ("zombie.characters.BodyDamage.BodyPart", "One body part's injury state (bleeding, scratch, bite, fracture, bandage)."),
    ("zombie.characters.BodyDamage.Nutrition", "Weight and macronutrient tracking for a character."),
    ("zombie.characters.Moodles.Moodles", "Moodle (status icon) levels for a character."),
    ("zombie.characters.Stats", "Core survival stats such as hunger, thirst, fatigue, stress, endurance."),
    ("zombie.characters.skills.PerkFactory", "Registry of perks (skills) and their definitions."),
    ("zombie.characters.traits.CharacterTraits", "The trait list of a character."),
    ("zombie.characters.Faction", "Player faction data."),
    ("zombie.iso.IsoMovingObject", "Base of anything that moves in the world: position, velocity, collision, square tracking."),
    ("zombie.iso.IsoObject", "Base of every world object (furniture, walls, containers, doors): sprite, container, modData, tile properties."),
    ("zombie.iso.IsoGridSquare", "One tile column at x, y, z: its objects, floor, flags, neighbours, room and building."),
    ("zombie.iso.IsoCell", "The loaded world cell: grid access, lists of characters and objects, and tile lookup."),
    ("zombie.iso.IsoWorld", "The world singleton: map, zones, spawning, metagrid and world-level state."),
    ("zombie.iso.IsoChunk", "A chunk of squares (the unit of loading)."),
    ("zombie.iso.sprite.IsoSprite", "A tile sprite definition and its properties."),
    ("zombie.iso.IsoLightSource", "A light source in the world."),
    ("zombie.iso.IsoPushableObject", "A pushable world object."),
    ("zombie.iso.objects.IsoThumpable", "Player-built or destructible structures (walls, doors, barricades)."),
    ("zombie.iso.objects.IsoDeadBody", "A corpse in the world."),
    ("zombie.iso.objects.IsoDoor", "A door object: open/close/lock, barricade state."),
    ("zombie.iso.objects.IsoWindow", "A window object: open/close, curtains, glass state, barricade."),
    ("zombie.iso.objects.IsoGenerator", "A generator: fuel, condition, activation, connected power."),
    ("zombie.iso.objects.IsoStove", "A stove or oven: temperature and on/off."),
    ("zombie.iso.objects.IsoLightSwitch", "A light switch and its connected lights."),
    ("zombie.iso.objects.IsoWorldInventoryObject", "An inventory item lying on the ground."),
    ("zombie.iso.areas.IsoRoom", "A room inside a building."),
    ("zombie.iso.areas.IsoBuilding", "A building: rooms, squares, def."),
    ("zombie.iso.areas.SafeHouse", "A claimed safehouse (multiplayer)."),
    ("zombie.iso.weather.ClimateManager", "Weather and climate: temperature, wind, precipitation, fog, day/night colors."),
    ("zombie.inventory.InventoryItem", "Base of every item instance: type, name, weight, condition, modData, container."),
    ("zombie.inventory.ItemContainer", "An item container (bag, crate, player inventory): add, remove, search items."),
    ("zombie.inventory.ItemPickerJava", "Loot distribution helpers (rolling items into containers)."),
    ("zombie.inventory.types.HandWeapon", "Melee and ranged weapon items: damage, range, ammo, parts."),
    ("zombie.inventory.types.Clothing", "Clothing items: protection, insulation, condition and patches."),
    ("zombie.inventory.types.Food", "Food items: hunger, nutrition, cooking, spoilage."),
    ("zombie.inventory.types.Literature", "Books, magazines and skill books."),
    ("zombie.inventory.types.Moveable", "Moveable furniture items."),
    ("zombie.inventory.types.InventoryContainer", "Items that are also containers (backpacks, bags)."),
    ("zombie.vehicles.BaseVehicle", "A vehicle: parts, engine, fuel, passengers, physics."),
    ("zombie.vehicles.VehiclePart", "One vehicle part: condition, container, and install state."),
    ("zombie.GameTime", "Game clock, calendar and day/night helpers."),
    ("zombie.SandboxOptions", "Sandbox settings (world rules chosen at game creation)."),
    ("zombie.core.Core", "Game settings and options (resolution, key bindings, graphics, difficulty flags)."),
    ("zombie.core.textures.Texture", "A texture: lookup by name, size, drawing helpers."),
    ("zombie.ui.UIElement", "Base of Java-backed UI elements; the Lua `ISUIElement` hierarchy wraps it."),
    ("zombie.ui.UIManager", "UI singleton: element list, screen sizes, mouse and picking helpers."),
    ("zombie.ui.TextManager", "Font metrics and text drawing."),
    ("zombie.scripting.ScriptManager", "Script registry: look up item, recipe, vehicle, sound and other script objects by name."),
    ("zombie.scripting.objects.Item", "An item script definition (the template, not an instance)."),
    ("zombie.scripting.objects.Recipe", "A legacy recipe script definition."),
    ("zombie.scripting.entity.components.crafting.CraftRecipe", "A Build 42 crafting recipe definition."),
    ("zombie.scripting.objects.VehicleScript", "A vehicle script definition."),
    ("zombie.audio.BaseSoundEmitter", "A positional sound emitter."),
    ("zombie.SoundManager", "Global sound manager (music, ambient, UI sounds)."),
    ("zombie.world.moddata.ModData", "Global mod data tables (shared persistent storage)."),
    ("zombie.network.ServerOptions", "Server option values (multiplayer)."),
])


def main(data_dir, out_dir):
    data_dir, out_dir = Path(data_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    classes = {r["fqn"]: r for r in csv.DictReader(open(data_dir / "exposed-classes.csv", encoding="utf-8"))}
    members = {}
    for r in csv.DictReader(open(data_dir / "exposed-methods.csv", encoding="utf-8")):
        members.setdefault(r["fqn"], []).append(r)
    index = []
    for fqn, summary in CLASSES.items():
        meta = classes.get(fqn)
        if not meta:
            print("missing", fqn)
            continue
        simple = fqn.rsplit(".", 1)[1]
        rows = members.get(fqn, [])
        ctors = [r for r in rows if r["member"] == "new"]
        sfields = sorted((r for r in rows if r["kind"] == "static-field"), key=lambda r: r["member"])
        smeth = sorted((r for r in rows if r["kind"] == "static" and r["member"] != "new"), key=lambda r: r["member"].lower())
        imeth = sorted((r for r in rows if r["kind"] == "instance"), key=lambda r: r["member"].lower())
        sig = lambda r: f"`{r['member']}({r['params']})` -> `{r['returns_or_type']}`"
        out = [f"# {simple}", "",
               "Survey date: 2026-10-24, Build 42. Generated by `modding/tools/gen_class_docs.py` from "
               "`../../data/exposed-methods.csv`. Names and signatures only.", "",
               f"- Java class: `{fqn}` ({meta['kind']})",
               f"- Extends: `{meta['extends'] or '-'}`; implements: `{meta['implements'] or '-'}`",
               f"- Summary [inferred from member names]: {summary}",
               "- Lua access: static members at the class table (`" + fqn + "` or the short name when unique), "
               "instance members through `obj:method(...)`. Members inherited from the superclass chain are "
               "available too and are not repeated here. See [`../how-binding-works.md`](../how-binding-works.md).",
               f"- Declared public members: {len(imeth)} instance, {len(smeth)} static, {len(sfields)} static fields, {len(ctors)} constructors.",
               ""]
        if ctors:
            out += ["## Constructors (`" + simple + ".new`)", ""] + [f"- `new({r['params']})`" for r in ctors] + [""]
        if sfields:
            out += ["## Static fields (snapshot values)", ""] + [f"- `{r['member']}`: `{r['returns_or_type']}`" for r in sfields] + [""]
        if smeth:
            out += ["## Static methods", ""] + [f"- {sig(r)}" for r in smeth] + [""]
        if imeth:
            out += ["## Instance methods", ""] + [f"- {sig(r)}" for r in imeth] + [""]
        (out_dir / f"{simple}.md").write_text("\n".join(out), encoding="utf-8")
        index.append((simple, fqn, summary, len(imeth), len(smeth)))
    lines = ["# Exposed class pages", "",
             "Survey date: 2026-10-24, Build 42. One page per commonly used Lua-exposed class; the complete list of "
             "999 whitelisted classes is `../../data/exposed-classes.csv` and every declared public member is in "
             "`../../data/exposed-methods.csv`.", "",
             "| Class | Java type | Summary [inferred] | Instance | Static |", "|---|---|---|---|---|"]
    for simple, fqn, summary, ni, ns in index:
        lines.append(f"| [{simple}]({simple}.md) | `{fqn}` | {summary} | {ni} | {ns} |")
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(index)} pages")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
