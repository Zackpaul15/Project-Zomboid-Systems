"""X8 metadata/layout survey. Exports paths, identifiers, counts and shapes only.

Run python -I modding/tools/survey_workflow.py [--game PATH] [--source PATH].
The optional source input is Claude's read-only decompile, used to corroborate
mod.info keys and launch flags absent from the legacy installed samples.
"""
import argparse
import csv
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
GAME = Path(r"F:\SteamLibrary\steamapps\common\ProjectZomboid")
SOURCE = Path(r"C:\Users\zackp\Documents\Code stuff\tools\pz-work\src")


def read(path):
    return path.read_text(encoding="utf-8-sig", errors="replace")


def write(name, columns, rows):
    with (ROOT / "data" / name).open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def shape(value):
    if not value:
        return "empty"
    if re.fullmatch(r"\d+", value):
        return "int"
    return "string"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game", type=Path, default=GAME)
    ap.add_argument("--source", type=Path, default=SOURCE)
    args = ap.parse_args()
    sources = [args.game / "Workshop/ModTemplate", args.game / "mods/examplemod",
               args.game / "media/luaexamples"]
    inventory, mod_keys, workshop_keys = [], defaultdict(list), defaultdict(list)
    for base in sources:
        if not base.is_dir():
            raise FileNotFoundError(base)
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(args.game).as_posix()
            inventory.append((base.relative_to(args.game).as_posix(), rel, path.suffix.lower()))
            if path.name not in ("mod.info", "workshop.txt"):
                continue
            keys = mod_keys if path.name == "mod.info" else workshop_keys
            for line in read(path).splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    if re.fullmatch(r"\w+", key.strip()):
                        keys[key.strip()].append((rel, shape(value.strip())))
    java = read(args.source / "zombie/gameStates/ChooseGameInfo.java")
    java = java.split("private static ChooseGameInfo.Mod readModInfoAux", 1)[1].split("public static final class Map", 1)[0]
    parser_keys = set(re.findall(r'inputLine\.(?:contains|startsWith)\("(\w+)="\)', java))
    write("mod-info-keys.csv", ["key", "sample_files", "sample_occurrences", "observed_value_shapes", "parser_recognized"],
          [(key, len({p for p, s in mod_keys.get(key, [])}), len(mod_keys.get(key, [])),
            "|".join(sorted({s for p, s in mod_keys.get(key, [])})) or "not-sampled",
            "yes" if key in parser_keys else "not-in-extractor")
           for key in sorted(mod_keys.keys() | parser_keys)])
    write("workshop-metadata-keys.csv", ["key", "sample_files", "occurrences", "value_shapes"],
          [(key, len({p for p, s in rows}), len(rows), "|".join(sorted({s for p, s in rows})))
           for key, rows in sorted(workshop_keys.items())])
    write("mod-sample-files.csv", ["sample", "file", "extension"], inventory)
    translations = []
    trans_root = args.game / "media/lua/shared/Translate"
    for path in sorted(trans_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".json", ".txt"):
            continue
        rel = path.relative_to(trans_root)
        count = "not-json"
        if path.suffix.lower() == ".json":
            obj = json.loads(read(path))
            count = len(obj) if isinstance(obj, (dict, list)) else "scalar"
        translations.append((rel.parts[0], rel.as_posix(), path.suffix.lower(), count))
    write("translation-layout.csv", ["language", "file", "format", "entries"], translations)
    flags = ["-debug", "-debuglog=", "-debugLogFile=", "-debugtranslation", "-cachedir=",
             "-imgui", "-imguidebugviewports", "-debugcfg="]
    launch_rows = []
    launch_sources = [("engine/MainScreenState.java", read(args.source / "zombie/gameStates/MainScreenState.java"))]
    launch_sources.extend((p.name, read(p)) for p in sorted(args.game.glob("*.bat")))
    for path, text in launch_sources:
        for flag in flags:
            count = len(re.findall(re.escape(flag) + (r"(?![\w=])" if not flag.endswith("=") else ""), text))
            if count:
                launch_rows.append((path, flag, count))
    write("debug-launch-flags.csv", ["source", "flag", "literal_occurrences"], launch_rows)
    print("X8 sample files:", dict(Counter(row[0] for row in inventory)))
    print("Sample mod.info keys:", sorted(mod_keys), "parser keys:", len(parser_keys))
    print("Workshop keys:", sorted(workshop_keys))
    print("Translation files:", len(translations), "languages:", len({row[0] for row in translations}),
          "formats:", dict(Counter(row[2] for row in translations)))


if __name__ == "__main__":
    main()
