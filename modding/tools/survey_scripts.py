"""Read-only vanilla script survey. Run: python -I modding/tools/survey_scripts.py X1.

Only identifiers, counts and abstract shapes are exported. No game bodies or
per-object values are written. A structural survey is not a runtime parser.
"""
import argparse
import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

GAME = Path(r"F:\SteamLibrary\steamapps\common\ProjectZomboid")
ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return path.read_text(encoding="utf-8-sig", errors="replace")


def uncomment(text):
    # Nested /* */ comments occur in script source; retain newlines for auditing.
    out, depth, i = [], 0, 0
    while i < len(text):
        pair = text[i:i + 2]
        if pair == "/*":
            depth += 1
            out.append(" ")
            i += 2
        elif pair == "*/" and depth:
            depth -= 1
            i += 2
        else:
            out.append(text[i] if not depth or text[i] == "\n" else " ")
            i += 1
    if depth:
        raise ValueError("Unclosed block comment")
    return "".join(out)


@dataclass
class Block:
    kind: str
    name: str
    parent: object
    file: str
    values: list = field(default_factory=list)
    children: list = field(default_factory=list)


def parse(text, file):
    root = Block("<root>", "", None, file)
    stack, start = [root], 0
    text = uncomment(text)
    for m in re.finditer(r"[{},]", text):
        token, chunk = m.group(), text[start:m.start()].strip()
        if token == "{":
            bits = chunk.split(None, 1)
            if not bits:
                raise ValueError(f"{file}: empty block header")
            b = Block(bits[0], bits[1] if len(bits) > 1 else "", stack[-1], file)
            stack[-1].children.append(b)
            stack.append(b)
        elif token == "}":
            if len(stack) == 1:
                raise ValueError(f"{file}: unmatched close brace")
            if chunk:
                stack[-1].values.append(chunk)
            stack.pop()
        elif chunk:
            stack[-1].values.append(chunk)
        start = m.end()
    if len(stack) != 1:
        raise ValueError(f"{file}: unclosed block")
    if text[start:].strip():
        root.values.append(text[start:].strip())
    return root


def walk(b):
    for child in b.children:
        yield child
        yield from walk(child)


def load(game):
    roots = []
    for p in sorted((game / "media/scripts").rglob("*.txt")):
        roots.append(parse(read(p), p.relative_to(game / "media/scripts").as_posix()))
    return roots


def write(name, columns, rows):
    path = ROOT / "data" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def pairs(b):
    for v in b.values:
        if "=" in v:
            k, value = v.split("=", 1)
            yield k.strip(), value.strip()


def shape(v):
    if not v:
        return "empty"
    if v.lower() in ("true", "false"):
        return "bool"
    if re.fullmatch(r"[+-]?\d+", v):
        return "int"
    if re.fullmatch(r"[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?", v):
        return "float"
    if ";" in v:
        return "list;"
    if "[" in v:
        return "selector[]"
    if re.fullmatch(r"[\w]+:[\w]+", v):
        return "namespaced-id"
    if re.fullmatch(r"[\w]+\.[\w]+", v):
        return "qualified-id"
    if re.fullmatch(r"[+-]?[\d.]+(?:\s+[+-]?[\d.]+)+", v):
        return "numeric-vector"
    return "string"


def x1(roots):
    groups = defaultdict(list)
    file_rows = []
    for root in roots:
        blocks = list(walk(root))
        for b in blocks:
            groups[b.kind].append(b)
        file_rows.append((root.file, len(blocks), ";".join(sorted({b.kind for b in blocks})),
                          "blocks" if blocks else "empty-or-comment-only", len(root.values)))
    write("script-blocks.csv", ["block_type", "files", "blocks", "folder_hint", "nested_in"],
          [(kind, len({b.file for b in bs}), len(bs),
            ";".join(sorted({str(Path(b.file).parent).replace("\\", "/") for b in bs})),
            ";".join(sorted({b.parent.kind for b in bs}))) for kind, bs in sorted(groups.items())])
    write("script-files.csv", ["file", "blocks", "block_types", "classification", "root_values"], file_rows)
    print(f"X1: {len(roots)} files, {sum(len(list(walk(r))) for r in roots)} structural blocks; "
          f"{len(groups)} distinct header types; empty={sum(not r.children for r in roots)}")
    print("Top-level module children:", dict(sorted(Counter(b.kind for r in roots for b in walk(r)
                                                          if b.parent.kind == 'module').items())))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("package", choices=["X1"])
    ap.add_argument("--game", type=Path, default=GAME)
    args = ap.parse_args()
    x1(load(args.game))


if __name__ == "__main__":
    main()
