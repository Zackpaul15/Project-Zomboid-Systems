"""Read-only Lua identifier surveys. Run: python -I modding/tools/survey_lua.py ui.

No Lua bodies or source values are exported. Comment and string masking preserves
offsets/newlines so identifier matches can be rejected inside literal strings.
"""
import argparse
import csv
from collections import Counter
from pathlib import Path
import re

GAME = Path(r"F:\SteamLibrary\steamapps\common\ProjectZomboid")
ROOT = Path(__file__).resolve().parents[1]
DERIVE = re.compile(r'''(?m)^\s*([A-Za-z_][\w.]*)\s*=\s*([A-Za-z_][\w.]*)\s*:\s*derive\s*\(\s*["']''')


def mask(text, strings=False):
    out, i = [], 0
    while i < len(text):
        start = i
        comment = text.startswith("--", i)
        pos = i + 2 if comment else i
        long = re.match(r"\[(=*)\[", text[pos:]) if text[pos:pos + 1] == "[" else None
        quoted = not comment and text[i] in "\"'"
        if long:
            end = text.find("]" + long[1] + "]", pos + len(long[0]))
            if end < 0:
                raise ValueError("Unclosed Lua long comment/string")
            i = end + len(long[1]) + 2
        elif comment:
            end = text.find("\n", i)
            i = len(text) if end < 0 else end
        elif quoted:
            quote = text[i]
            i += 1
            while i < len(text):
                if text[i] == "\\":
                    i += 2
                elif text[i] == quote:
                    i += 1
                    break
                else:
                    i += 1
        else:
            out.append(text[i])
            i += 1
            continue
        chunk = text[start:i]
        out.append(re.sub(r"[^\n]", " ", chunk) if comment or strings else chunk)
    return "".join(out)


def files(game):
    for side in ("client", "server", "shared"):
        for path in sorted((game / "media/lua" / side).rglob("*.lua")):
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            yield side, path.relative_to(game / "media/lua").as_posix(), mask(text), mask(text, True)


def write(name, columns, rows):
    path = ROOT / "data" / name
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def ui(game):
    rows, counts = [], Counter()
    for side, path, text, code in files(game):
        if not path.startswith(("client/ISUI/", "client/OptionScreens/")):
            continue
        counts[path.split("/")[1]] += 1
        for m in DERIVE.finditer(text):
            if code[m.start(1):m.end(1)].strip():
                rows.append((m[2], m[1], path))
    if not counts:
        raise ValueError("No UI Lua files found; check --game")
    write("ui-inheritance.csv", ["parent", "child", "file"], sorted(rows))
    write("ui-folder-counts.csv", ["folder", "lua_files"], sorted(counts.items()))
    print("X5 UI files:", dict(counts), "derive declarations:", len(rows))


def role(side, path):
    parts = path.split("/")
    folder = parts[1] if len(parts) > 2 else "<root>"
    labels = {
        "TimedActions": "Timed-action class or queue helper",
        "ISUI": "UI widget or interface helper", "OptionScreens": "Menu/options interface module",
        "DebugUIs": "Debug interface module", "Definitions": "Definition-table module",
        "BuildingObjects": "Building-object implementation or helper",
        "BuildingRooms": "Room-construction helper", "Vehicles": "Vehicle-system module",
        "Farming": "Farming-system module", "Fishing": "Fishing-system module",
        "Foraging": "Foraging-system module", "Items": "Item creation or distribution helper",
        "Entity": "Entity-system module", "WorldGen": "World-generation module",
        "Camping": "Camping-system module", "Traps": "Trapping-system module",
    }
    return labels.get(folder, side.capitalize() + " " + folder + " module") + ": " + Path(path).stem


def library(game):
    index, derives, folders = [], [], Counter()
    methods, declared_methods = [], []
    for side, path, text, code in files(game):
        globals_seen = set()
        # Candidates at column zero, not a full Lua scope analysis. Comments and
        # strings have been masked, while function bodies are never exported.
        for pattern in (r"(?m)^([A-Za-z_][\w.]*)\s*=(?!=)",
                        r"(?m)^function\s+([A-Za-z_][\w.:]*)\s*\("):
            for m in re.finditer(pattern, code):
                globals_seen.add(re.split(r"[.:]", m[1])[0])
        local_names = set()
        for match in re.finditer(r"\blocal\s+(?:function\s+)?([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)", code):
            local_names.update(name.strip() for name in match[1].split(","))
        globals_seen -= local_names | {"self"}
        index.append((side, path, ";".join(sorted(globals_seen)), role(side, path)))
        parts = path.split("/")
        folders[side, parts[1] if len(parts) > 2 else "<root>"] += 1
        for m in DERIVE.finditer(text):
            if code[m.start(1):m.end(1)].strip():
                derives.append((side, path, m[2], m[1]))
        declared_methods.extend((m[1], m[2], path) for m in re.finditer(
            r"(?m)^function\s+([A-Za-z_][\w.]*):([A-Za-z_]\w*)\s*\(", code))
        if path == "shared/TimedActions/ISBaseTimedAction.lua":
            methods.extend((m[1], path) for m in re.finditer(
                r"(?m)^function\s+ISBaseTimedAction:([A-Za-z_]\w*)\s*\(", code))
    if not index:
        raise ValueError("No Lua files found; check --game")
    path = ROOT / "lua-library/index.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["side", "path", "main_globals", "one_line_role"])
        writer.writerows(sorted(index))
    write("lua-folder-inventory.csv", ["side", "folder", "lua_files"],
          [(*key, count) for key, count in sorted(folders.items())])
    actions = {"ISBaseTimedAction"}
    while True:
        expanded = actions | {child for side, path, parent, child in derives if parent in actions}
        if expanded == actions:
            break
        actions = expanded
    action_rows = [row for row in derives if row[2] in actions]
    write("timed-action-inheritance.csv", ["side", "path", "parent", "child"], sorted(action_rows))
    write("base-timed-action-methods.csv", ["method", "path"], sorted(methods))
    hooks = Counter(method for cls, method, path in declared_methods if cls in actions)
    write("timed-action-hooks.csv", ["method", "files", "declarations"],
          [(method, len({path for cls, name, path in declared_methods if cls in actions and name == method}), count)
           for method, count in sorted(hooks.items())])
    print("X6 files:", dict(Counter(row[0] for row in index)), "timed-action declarations:", len(action_rows))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("section", choices=["ui", "library"])
    ap.add_argument("--game", type=Path, default=GAME)
    args = ap.parse_args()
    {"ui": ui, "library": library}[args.section](args.game)


if __name__ == "__main__":
    main()
