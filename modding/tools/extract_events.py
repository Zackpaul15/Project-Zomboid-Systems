"""Build modding/data/events.csv from a Vineflower decompile of zombie/**.

Usage:  python -I extract_events.py <decompiled src root> <output csv>
        e.g. ...\\pz-work\\src  ..\\data\\events.csv

Reads LuaEventManager.AddEvents() for the registered event list (in registration order) and scans every .java
file for LuaEventManager.triggerEvent* calls. Only names and argument expressions are recorded; no code bodies.
Columns: event, registered, reg_index, methods, arg_counts, trigger_classes, sample_args, lua_trigger_files
lua_trigger_files = number of vanilla Lua files that call triggerEvent("<name>", ...) (only if a Lua root is given); Lua comments are stripped first.
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

CALL_RE = re.compile(r"\b(triggerEvent(?:Garbage|Unique)?)\s*\(")
ADD_RE = re.compile(r'AddEvent\(\s*"([^"]+)"\s*\)')


def split_args(text, start):
    """Return (args, end_index) for a call whose '(' is just before `start`."""
    depth, i, args, cur = 1, start, [], []
    in_str = None
    while i < len(text) and depth:
        c = text[i]
        if in_str:
            cur.append(c)
            if c == "\\":
                i += 1
                cur.append(text[i])
            elif c == in_str:
                in_str = None
        elif c in "\"'":
            in_str = c
            cur.append(c)
        elif c in "([{":
            depth += 1
            cur.append(c)
        elif c in ")]}":
            depth -= 1
            if depth:
                cur.append(c)
        elif c == "," and depth == 1:
            args.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    last = "".join(cur).strip()
    if last:
        args.append(last)
    return args, i


LUA_TRIG_RE = re.compile(r'triggerEvent\s*\(\s*"([^"]+)"')
LONG_OPEN_RE = re.compile(r"\[(=*)\[")


def strip_lua_comments(text):
    """Remove Lua comments so commented-out triggerEvent calls are not counted.

    Handled: `-- ...` line comments, `--[[ ... ]]` and `--[==[ ... ]==]` block comments (any level of `=`), with
    string awareness ('...' and "..." with backslash escapes, and [[ ... ]] long strings are left intact so a `--`
    inside them is not a comment). Newlines inside block comments are kept so line numbers stay stable.
    Not handled: comment forms produced by string concatenation or generated code, and `--[=[` openers with
    unbalanced levels (an unterminated block comment swallows the rest of the file, as the Lua lexer would).
    """
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c in "\"'":
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        elif c == "[" and (m := LONG_OPEN_RE.match(text, i)):
            close = "]" + m.group(1) + "]"
            j = text.find(close, m.end())
            j = n if j < 0 else j + len(close)
            out.append(text[i:j])
            i = j
        elif text.startswith("--", i):
            m = LONG_OPEN_RE.match(text, i + 2)
            if m:
                close = "]" + m.group(1) + "]"
                j = text.find(close, m.end())
                j = n if j < 0 else j + len(close)
                out.append("\n" * text.count("\n", i, j))
                i = j
            else:
                j = text.find("\n", i)
                i = n if j < 0 else j  # keep the newline
        else:
            out.append(c)
            i += 1
    return "".join(out)


def main(src_root, out_csv, lua_root=None):
    src_root = Path(src_root)
    mgr = next(src_root.rglob("LuaEventManager.java"))
    mgr_text = mgr.read_text(encoding="utf-8", errors="replace")
    reg_body = mgr_text[mgr_text.index("private static void AddEvents()"):]
    registered = []
    for name in ADD_RE.findall(reg_body):
        if name not in registered:
            registered.append(name)
    reg_index = {n: i for i, n in enumerate(registered)}

    sites = defaultdict(lambda: {"methods": set(), "counts": set(), "classes": set(), "sample": None})
    dynamic = defaultdict(set)
    for path in sorted(src_root.rglob("*.java")):
        if path == mgr:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        cls = ".".join(path.relative_to(src_root).with_suffix("").parts)
        for m in CALL_RE.finditer(text):
            # require the LuaEventManager receiver (or a static import style bare call is not used in this codebase)
            before = text[max(0, m.start() - 20):m.start()]
            if "LuaEventManager." not in before:
                continue
            args, _ = split_args(text, m.end())
            if not args:
                continue
            first = args[0]
            lit = re.fullmatch(r'"([^"]+)"', first)
            if not lit:
                dynamic[cls].add(m.group(1))
                continue
            rec = sites[lit.group(1)]
            rec["methods"].add(m.group(1))
            rec["counts"].add(len(args) - 1)
            rec["classes"].add(cls)
            if rec["sample"] is None:
                rec["sample"] = ", ".join(a.replace("\n", " ")[:60] for a in args[1:])

    lua_files = defaultdict(set)
    if lua_root:
        for lp in Path(lua_root).rglob("*.lua"):
            for n in LUA_TRIG_RE.findall(strip_lua_comments(lp.read_text(encoding="utf-8", errors="replace"))):
                lua_files[n].add(lp.name)

    names = list(registered) + sorted(n for n in sites if n not in reg_index)
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["event", "registered", "reg_index", "methods", "arg_counts", "trigger_classes", "sample_args", "lua_trigger_files"])
        for n in names:
            rec = sites.get(n)
            w.writerow([
                n,
                "Y" if n in reg_index else "N",
                reg_index.get(n, ""),
                "|".join(sorted(rec["methods"])) if rec else "",
                "|".join(str(c) for c in sorted(rec["counts"])) if rec else "",
                "|".join(sorted(rec["classes"])) if rec else "",
                rec["sample"] if rec else "",
                len(lua_files[n]) if lua_root else "",
            ])
    never = [n for n in registered if n not in sites]
    unreg = [n for n in sites if n not in reg_index]
    if lua_root:
        orphan = [n for n in never if not lua_files.get(n)]
        print(f"registered_never_triggered_in_java_or_vanilla_lua={len(orphan)}")
    print(f"registered={len(registered)} triggered_names={len(sites)} registered_never_triggered_in_java={len(never)} "
          f"triggered_but_unregistered={len(unreg)} classes_with_dynamic_names={len(dynamic)}")
    if dynamic:
        print("dynamic-name callers:", ", ".join(sorted(dynamic)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
