"""X2: export item property identifiers, counts and abstract value shapes only.

Run with python -I modding/tools/survey_items.py [--game PATH]. The sibling
X1 structural reader is loaded by absolute path, without importing game code.
No source values or per-item identifiers are written to the repository.
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import runpy

survey = runpy.run_path(str(Path(__file__).with_name("survey_scripts.py")))

PATTERNS = {
    "empty": "<empty>", "bool": "true|false", "int": "<integer>",
    "float": "<decimal>", "string": "<text-or-identifier>",
    "list;": "<entry>;<entry>", "selector[]": "<selector>[<entry>]",
    "namespaced-id": "<namespace>:<identifier>",
    "qualified-id": "<qualifier>.<identifier>",
    "numeric-vector": "<number> <number> [<number>...]",
    "tag-list": "<namespace>:<tag>;<namespace>:<tag>",
}


def value_shape(key, value):
    if key == "Tags":
        return "tag-list" if ";" in value else survey["shape"](value)
    return survey["shape"](value)


def add(groups, key, item_type, property_name, value):
    entry = groups[key]
    entry["count"] += 1
    entry["types"].add(item_type)
    entry["shapes"].add(value_shape(property_name, value))


def rows(groups):
    for key, entry in sorted(groups.items()):
        prefix = key if isinstance(key, tuple) else (key,)
        shapes = sorted(entry["shapes"])
        yield (*prefix, entry["count"], ";".join(sorted(entry["types"])),
               "|".join(shapes), " | ".join(PATTERNS[s] for s in shapes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", type=Path, default=survey["GAME"])
    args = parser.parse_args()
    roots = survey["load"](args.game)
    items = [b for root in roots for b in survey["walk"](root) if b.kind == "item"]
    if not items:
        raise ValueError("No item blocks found; check --game")

    def group():
        return {"count": 0, "types": set(), "shapes": set()}

    direct, nested = defaultdict(group), defaultdict(group)
    types, presence = Counter(), Counter()
    components = Counter()
    for item in items:
        pairs = list(survey["pairs"](item))
        # Reject unrecognised direct entries rather than silently losing them.
        if len(pairs) != len(item.values):
            raise ValueError(f"Non-property entry in item in {item.file}")
        values = dict(pairs)
        item_type = values.get("ItemType", values.get("Type", "<missing>"))
        types[item_type] += 1
        presence.update({k for k, v in pairs})
        for key, value in pairs:
            add(direct, key, item_type, key, value)
        for block in survey["walk"](item):
            path, ancestor = [], block
            while ancestor is not item:
                path.append(ancestor.kind + (":" + ancestor.name if ancestor.name else ""))
                ancestor = ancestor.parent
            context = "/".join(reversed(path))
            components[context] += 1
            for key, value in survey["pairs"](block):
                add(nested, (context, key), item_type, key, value)

    columns = ["property", "count", "types_seen_on", "value_shape", "example_shape"]
    survey["write"]("item-properties.csv", columns, rows(direct))
    survey["write"]("item-component-properties.csv", ["block_path", *columns], rows(nested))
    survey["write"]("item-types.csv", ["item_type", "item_blocks", "exclusive_properties"],
                    [(t, n, sum(e["types"] == {t} for e in direct.values()))
                     for t, n in sorted(types.items())])
    blocks = [b for root in roots for b in survey["walk"](root)]
    resources = []
    for key, kind in [("StaticModel", "model"), ("WorldStaticModel", "model"),
                      ("SwingSound", "sound"), ("CookingSound", "sound")]:
        names = {b.name for b in blocks if b.kind == kind}
        values = [v for item in items for k, v in survey["pairs"](item) if k == key]
        resources.append((key, len(values), sum(v in names for v in values),
                          "exact identifier match to " + kind + " block"))
    clothing = [v for item in items for k, v in survey["pairs"](item) if k == "ClothingItem"]
    resources.append(("ClothingItem", len(clothing), sum(
        (args.game / "media/clothing/clothingItems" / (v + ".xml")).is_file()
        for v in clothing), "exact XML filename stem match"))
    translations = json.loads(survey["read"](
        args.game / "media/lua/shared/Translate/EN/ItemName.json"))
    resources.append(("<module>.<item>", len(items), sum(
        item.parent.name + "." + item.name in translations for item in items),
        "exact EN/ItemName.json key match"))
    survey["write"]("item-resource-links.csv", ["property_or_identifier", "occurrences",
                    "matched", "match_kind"], resources)
    print(f"X2: {len(items)} item blocks; {len(direct)} direct property names; "
          f"{len(nested)} scoped nested properties; {len(types)} item types")
    print("Properties present on every item:", ";".join(sorted(
        key for key, n in presence.items() if n == len(items))))
    print("Nested block counts:", dict(sorted(components.items())))


if __name__ == "__main__":
    main()
