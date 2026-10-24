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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("section", choices=["ui"])
    ap.add_argument("--game", type=Path, default=GAME)
    args = ap.parse_args()
    ui(args.game)


if __name__ == "__main__":
    main()
