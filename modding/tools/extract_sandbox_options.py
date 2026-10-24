#!/usr/bin/env python3
"""Extract the built-in sandbox option table (Build 42).

Usage (run as `python -I`):
    extract_sandbox_options.py <decompiled src> <game media/lua> <out csv>

Reads, never copies into the output beyond names and numbers:
  - <src>/zombie/SandboxOptions.java        option declarations (name, type, range, default, translation keys)
  - <src>/zombie/characters/*.java          constant counts for the two enum-class-backed options
  - <lua>/shared/Sandbox/Apocalypse.lua     the preset that is applied over the Java defaults at construction
  - <lua>/client/OptionScreens/ServerSettingsScreen.lua   which settings page each option is listed on

String-valued options record only the default's length, so item lists are not reproduced.
"""
import csv
import os
import re
import sys

KINDS = {"Boolean": "boolean", "Double": "double", "Enum": "enum", "Integer": "integer", "String": "string"}
DECL = re.compile(r"new(Boolean|Double|Enum|Integer|String)Option\(\s*\"([A-Za-z0-9_.]+)\"")
CHAIN = re.compile(r"\s*\.(\w+)\(\s*(\"[^\"]*\"|[^()]*)\)")
INT_MAX = 2147483647


def split_call(text, start):
    """text[start] is just after the opening paren of a call. Return (args, index after ')')."""
    depth, i, quote, args, cur = 1, start, False, [], []
    while i < len(text):
        c = text[i]
        if quote:
            cur.append(c)
            if c == "\\":
                i += 1
                cur.append(text[i])
            elif c == '"':
                quote = False
        elif c == '"':
            quote = True
            cur.append(c)
        elif c in "([{":
            depth += 1
            cur.append(c)
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                args.append("".join(cur).strip())
                return args, i + 1
            cur.append(c)
        elif c == "," and depth == 1:
            args.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    raise ValueError("unterminated call")


def num(tok):
    tok = tok.strip()
    if tok == "Integer.MAX_VALUE":
        return INT_MAX
    if tok == "Integer.MIN_VALUE":
        return -INT_MAX - 1
    if tok in ("true", "false"):
        return tok
    t = re.sub(r"[fFdDlL]$", "", tok)
    try:
        v = float(t)
    except ValueError:
        return None
    return int(v) if re.fullmatch(r"-?\d+", t) else v


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return repr(round(v, 9)).rstrip("0").rstrip(".") if "e" not in repr(v) else repr(v)
    return str(v)


def enum_constants(src, cls):
    path = os.path.join(src, "zombie", "characters", cls + ".java")
    text = open(path, encoding="utf-8").read()
    body = text[text.index("{") + 1:]
    names = re.findall(r"^\s{3}([A-Z_0-9]+)\s*(?:\(|,|;)", body, re.M)
    return names


def parse_java(src):
    text = open(os.path.join(src, "zombie", "SandboxOptions.java"), encoding="utf-8").read()
    rows, unknown_chain = [], {}
    for m in DECL.finditer(text):
        kind, name = KINDS[m.group(1)], m.group(2)
        args, end = split_call(text, text.index("(", m.start()) + 1)
        chain = {}
        while True:
            cm = CHAIN.match(text, end)
            if not cm:
                break
            chain[cm.group(1)] = cm.group(2).strip().strip('"')
            end = cm.end()
        for k in chain:
            if k not in ("setTranslation", "setValueTranslation"):
                unknown_chain[k] = unknown_chain.get(k, 0) + 1
        row = {"name": name, "type": kind, "min": "", "max": "", "java_default": "", "str_len": "",
               "translation": chain.get("setTranslation", ""), "value_translation": chain.get("setValueTranslation", ""),
               "enum_class": ""}
        a = args[1:]
        if kind == "boolean":
            row["java_default"] = a[0]
        elif kind in ("double", "integer"):
            row["min"], row["max"], row["java_default"] = (fmt(num(a[0])), fmt(num(a[1])), fmt(num(a[2])))
        elif kind == "enum":
            if len(a) == 2 and a[0].endswith(".class"):
                cls = a[0][:-6]
                consts = enum_constants(src, cls)
                const = a[1].split(".")[-1]
                row.update(min="1", max=str(len(consts)), java_default=str(consts.index(const) + 1), enum_class=cls)
            else:
                row.update(min="1", max=str(num(a[0])), java_default=str(num(a[1])))
        elif kind == "string":
            row["java_default"] = ""
            row["str_len"] = str(len(a[0].strip('"')))
            row["max_length"] = str(num(a[1]))
        rows.append(row)
    return rows, unknown_chain


def parse_preset(path):
    """Parse the `return { Key = v, Group = { ... } }` preset into {(group, key): value}."""
    out, group, version = {}, "", None
    for line in open(path, encoding="utf-8"):
        s = line.strip().rstrip(",")
        m = re.match(r"(\w+)\s*=\s*\{$", s)
        if m:
            group = m.group(1)
            continue
        if s == "}":
            group = ""
            continue
        m = re.match(r"(\w+)\s*=\s*(.+)$", s)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if key.lower() == "version":
            version = val
            continue
        if val.startswith('"'):
            out[(group, key)] = ("str", len(val.strip('"')))
        else:
            out[(group, key)] = ("val", val)
    return out, version


def parse_pages(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    start = next(i for i, l in enumerate(lines) if l == '\t\tname = "Sandbox",')
    page, mapping, order = "", {}, []
    for l in lines[start + 1:]:
        if re.match(r"^\t\t\},?$", l):
            break
        pm = re.match(r'^\t\t\t\t(?:name|title) = (?:getText\()?"([^"]+)"', l)
        if pm:
            page = pm.group(1)
            order.append(page)
        if l.lstrip().startswith("--"):
            continue
        for sm in re.finditer(r'\{\s*name\s*=\s*"([^"]+)"\s*[,}]', l):
            if not sm.group(1).startswith("Sandbox_"):
                mapping[sm.group(1)] = page
    return mapping, order


def main():
    src, lua, out = sys.argv[1:4]
    rows, unknown_chain = parse_java(src)
    preset, version = parse_preset(os.path.join(lua, "shared", "Sandbox", "Apocalypse.lua"))
    pages, order = parse_pages(os.path.join(lua, "client", "OptionScreens", "ServerSettingsScreen.lua"))
    cols = ["name", "table", "short_name", "type", "min", "max", "java_default", "apocalypse_value", "effective_default",
            "string_default_length", "enum_class", "translation", "value_translation", "settings_page"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        seen_preset = set()
        for r in rows:
            tbl, _, short = r["name"].rpartition(".")
            pv = preset.get((tbl, short))
            if pv:
                seen_preset.add((tbl, short))
            apoc = ""
            if pv:
                apoc = "<string len %d>" % pv[1] if pv[0] == "str" else (
                    pv[1] if pv[1] in ("true", "false") else fmt(num(pv[1])))
            if r["type"] == "string":
                eff = "<string len %d>" % (pv[1] if pv else int(r["str_len"]))
            else:
                eff = apoc if pv else r["java_default"]
            w.writerow([r["name"], tbl, short, r["type"], r["min"], r["max"], r["java_default"], apoc, eff,
                        r["str_len"], r["enum_class"], r["translation"], r["value_translation"],
                        pages.get(r["name"], "")])
    counts = {}
    for r in rows:
        counts[r["type"]] = counts.get(r["type"], 0) + 1
    tables = {}
    for r in rows:
        t = r["name"].rpartition(".")[0] or "(top level)"
        tables[t] = tables.get(t, 0) + 1
    print("options:", len(rows), counts)
    print("tables:", tables)
    print("preset version key:", version, "preset entries:", len(preset), "unmatched preset keys:",
          sorted(set(preset) - seen_preset))
    print("java options with no page:", sum(1 for r in rows if r["name"] not in pages))
    print("page settings with no java option:", sorted(set(pages) - {r["name"] for r in rows}))
    print("page order:", order)
    print("unknown chain methods:", unknown_chain)


if __name__ == "__main__":
    main()
