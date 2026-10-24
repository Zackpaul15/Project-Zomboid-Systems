"""X3 read-only crafting survey; run with python -I modding/tools/survey_crafting.py.

Exports identifiers, counts and abstract shapes. Mapper item identifiers and all
source values are omitted. This measures textual grammar, not runtime validity.
"""
import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
import re
import runpy

S = runpy.run_path(str(Path(__file__).with_name("survey_scripts.py")))
FAMILIES = ("craftRecipe", "recipe", "evolvedrecipe", "fixing")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game", type=Path, default=S["GAME"])
    args = ap.parse_args()
    blocks = [b for r in S["load"](args.game) for b in S["walk"](r)]
    recipes = [b for b in blocks if b.kind in FAMILIES]
    if not recipes:
        raise ValueError("No crafting-family blocks found; check --game")
    groups = defaultdict(lambda: {"count": 0, "shapes": set(), "note": ""})
    tokens = Counter()
    direct = Counter()

    def add(context, key, shape, note, amount=1):
        row = groups[context, key]
        row["count"] += amount
        row["shapes"].add(shape)
        row["note"] = note

    for family in FAMILIES:
        add(family, "<block>", "block", "Textual block occurrences; zero means absent",
            sum(b.kind == family for b in recipes))
    for block in recipes:
        for key, value in S["pairs"](block):
            add(block.kind, key, S["shape"](value), "Direct assignment occurrences")
            direct[block.kind, key] += 1
        for child in block.children:
            context = block.kind + "/" + child.kind
            add(block.kind, "<child:" + child.kind + ">", "block", "Immediate child block occurrences")
            if child.kind in ("itemMapper", "overlayMapper"):
                for key, value in S["pairs"](child):
                    add(context, "default" if key == "default" else "<mapping-key>",
                        S["shape"](value), "Mapping assignments; concrete mapping identifiers omitted")
                continue
            if child.kind not in ("inputs", "outputs"):
                raise ValueError(f"Unclassified crafting child: {child.kind}")
            for line in child.values:
                words = line.split()
                if len(words) < 3:
                    raise ValueError(f"Unclassified crafting entry in {block.file}")
                resource = words[0]
                if resource not in ("item", "-fluid", "fluid", "energy", "+item", "+fluid", "-item", "-energy", "+energy"):
                    raise ValueError(f"Unknown resource grammar: {resource}")
                add(context, "<line:" + resource + ">", "resource amount selector [options]",
                    "Comma-delimited entry occurrences; leading signs retained")
                add(context, "<amount>", "variable[min:max]" if words[1].startswith("variable[")
                    else S["shape"](words[1]), "Second whitespace token")
                selector = words[2]
                if selector.startswith("["):
                    selector_shape = "bracketed-list-or-wildcard"
                elif selector.startswith("mapper:"):
                    selector_shape = "mapper:<identifier>"
                elif selector.startswith("tags["):
                    selector_shape = "tags[<namespace>:<tag>;...]"
                else:
                    selector_shape = S["shape"](selector)
                add(context, "<selector>", selector_shape, "Third whitespace token; no concrete selectors exported")
                # tags[...] may itself occupy the selector position.
                for position, word in enumerate(words[2:], start=2):
                    match = re.fullmatch(r"(flags|tags|categories|mappers)\[([^\]]*)\]", word)
                    if match:
                        key, value = match.groups()
                        add(context, key + "[]", "semicolon-list-in-brackets", "Option token occurrences")
                        if key == "flags":
                            tokens.update((context, "flags", name) for name in value.split(";"))
                    elif word.startswith(("mode:", "chance:", "shapedIndex:", "apply:")):
                        key, value = word.split(":", 1)
                        add(context, key + ":", S["shape"](value), "Option token occurrences")
                        if key in ("mode", "apply"):
                            tokens[context, key, value] += 1
                    elif word == "overlayMapper":
                        add(context, word, "marker", "Bare option token occurrences")
                    elif position != 2:
                        # Position 3 is a selector; later tokens must be classified.
                        raise ValueError(f"Unclassified crafting option in {block.file}: {word}")

    S["write"]("recipe-keys.csv", ["block_type", "key", "count", "value_shape", "notes"],
               [(context, key, row["count"], "|".join(sorted(row["shapes"])), row["note"])
                for (context, key), row in sorted(groups.items())])
    S["write"]("recipe-grammar-identifiers.csv", ["block_type", "grammar_key", "identifier", "count"],
               [(*key, count) for key, count in sorted(tokens.items())])
    parser_table = S["ROOT"] / "data/script-keys.csv"
    if not parser_table.is_file():
        raise FileNotFoundError("Claude's data/script-keys.csv is required for the cross-check")
    with parser_table.open(encoding="utf-8", newline="") as f:
        accepted = {(row["block"], row["key"].casefold()) for row in csv.DictReader(f)
                    if row["kind"] == "key"}
    S["write"]("recipe-parser-coverage.csv", ["block_type", "key", "count", "parser_key_match"],
               [(kind, key, count, "yes" if (kind, key.casefold()) in accepted else "not-in-extractor")
                for (kind, key), count in sorted(direct.items())])
    print("X3 blocks:", dict(Counter(b.kind for b in recipes)))
    print("Observed key/grammar rows:", len(groups), "; mode/flag identifiers:", len(tokens))
    print("Direct keys not in parser extractor:", [key for key in sorted(direct)
          if (key[0], key[1].casefold()) not in accepted])


if __name__ == "__main__":
    main()
