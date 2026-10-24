"""X4 script families, nested contexts and lexical shapes; never export values.

Run: python -I modding/tools/survey_components.py [--game PATH].
Only module-level family roots are selected, so a vehicle's nested sound block
does not become a global sound definition. Concrete instance header names are
omitted; component class names and template family names are retained.
"""
import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
import re
import runpy

S = runpy.run_path(str(Path(__file__).with_name("survey_scripts.py")))
FAMILIES = {
    "vehicle": {"vehicle", "template vehicle", "vehicleEngineRPM"},
    "sound": {"sound", "soundTimeline"},
    "fluid": {"fluid", "energy"},
    "entity": {"entity", "template entity", "xuiSkin", "xuiConfig", "xuiLayout",
               "xuiStyle", "xuiDefaultStyle", "xuiGlobalColors",
               "character_trait_definition", "character_profession_definition"},
}


def root_kind(block):
    if block.kind == "template":
        return "template " + block.name.split()[0]
    return block.kind


def segment(block):
    if block.kind == "component":
        return "component:" + block.name
    return "<number>" if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", block.kind) else block.kind


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game", type=Path, default=S["GAME"])
    args = ap.parse_args()
    blocks = [b for r in S["load"](args.game) for b in S["walk"](r)]
    module_children = [b for b in blocks if b.parent.kind == "module"]
    if not module_children:
        raise ValueError("No module children found; check --game")
    inventory = []
    for output, families in FAMILIES.items():
        selected = [b for b in module_children if root_kind(b) in families]
        groups = defaultdict(lambda: {"count": 0, "shapes": set(), "note": ""})

        def add(context, key, shape, note, count=1):
            row = groups[context, key]
            row["count"] += count
            row["shapes"].add(shape)
            row["note"] = note

        for family in sorted(families):
            count = sum(root_kind(b) == family for b in selected)
            add(family, "<block>", "block", "Module-level definitions; zero means absent", count)
            files = sorted({b.file for b in selected if root_kind(b) == family})
            inventory.append((output, family, count, len(files), ";".join(files[:3])))
        for block in selected:
            family = root_kind(block)
            for current in [block, *S["walk"](block)]:
                path, ancestor = [], current
                while ancestor is not block:
                    path.append(segment(ancestor))
                    ancestor = ancestor.parent
                context = "/".join([family, *reversed(path)])
                if current is not block:
                    add(context, "<block>", "block", "Nested block occurrences; instance names omitted")
                for value in current.values:
                    if "=" in value:
                        key, val = value.split("=", 1)
                        add(context, key.strip(), S["shape"](val.strip()), "Assignment occurrences")
                    elif family == "xuiConfig" and re.fullmatch(r"\w+", value):
                        add(context, value, current.kind, "Variable identifier declared in typed config group")
                    else:
                        add(context, "<entry>", S["shape"](value), "Bare comma-delimited entries; source values omitted")
        S["write"](output + "-keys.csv", ["block_type", "key", "count", "value_shape", "notes"],
                   [(context, key, row["count"], "|".join(sorted(row["shapes"])), row["note"])
                    for (context, key), row in sorted(groups.items())])
        print(output, "module roots", len(selected), "scoped key/count rows", len(groups))
    S["write"]("component-blocks.csv", ["family", "block_type", "blocks", "files", "example_files"], inventory)
    config = Counter((c.kind, value) for b in module_children if b.kind == "xuiConfig"
                     for c in b.children for value in c.values if re.fullmatch(r"\w+", value))
    with (S["ROOT"] / "data/script-keys.csv").open(encoding="utf-8", newline="") as f:
        parser_names = {row["key"] for row in csv.DictReader(f) if row["kind"] == "xui-var"}
    config_names = {name for kind, name in config}
    coverage = [(name, kind, count, "both" if name in parser_names else "config-only")
                for (kind, name), count in config.items()]
    coverage.extend((name, "", 0, "parser-only") for name in parser_names - config_names)
    S["write"]("xui-config-coverage.csv", ["variable", "config_type", "count", "catalogue_presence"], sorted(coverage))
    print("XUI config/parser catalogue comparison:", dict(Counter(row[3] for row in coverage)))


if __name__ == "__main__":
    main()
