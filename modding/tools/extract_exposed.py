"""Build modding/data/lua-globals.csv, exposed-classes.csv and exposed-methods.csv from a Vineflower decompile.

Usage:  python -I extract_exposed.py <decompiled src root> <output data dir>

Sources (all in the decompile of zombie/Lua/LuaManager.java):
  - Exposer.exposeAll(): the explicit setExposed(X.class) whitelist -> exposed-classes.csv
  - LuaManager.GlobalObject: methods annotated @LuaMethod(global = true) -> lua-globals.csv
  - each exposed class's own public members -> exposed-methods.csv (declared members only; inherited members are
    reachable from Lua through the superclass chain and are not repeated)
Only names, parameter lists and types are recorded. No method bodies are copied.
"""
import csv
import re
import sys
from pathlib import Path

SET_RE = re.compile(r"this\.setExposed\(\s*([\w.]+)\.class\s*\)")
IMPORT_RE = re.compile(r"^import\s+([\w.]+);", re.M)
LM_RE = re.compile(r"@LuaMethod\(([^)]*)\)")
SIG_RE = re.compile(
    r"^(?P<ind> *)(?P<mods>(?:public |protected |private |static |final |abstract |synchronized |default )*)"
    r"(?P<generic><[^>]*> )?(?P<ret>[\w.<>\[\], ?]+?) (?P<name>\w+)\((?P<params>[^)]*)\)(?: throws [\w., ]+)?\s*(?:\{|;)\s*$"
)
CTOR_RE_T = r"^ *public {name}\(([^)]*)\)"
FIELD_RE = re.compile(r"^ *public (?P<mods>(?:static |final |volatile |transient )*)(?P<type>[\w.<>\[\], ?]+?) (?P<name>\w+)( =.*)?;\s*$")
KEYWORDS = {"return", "new", "else", "throw", "if", "while", "for", "switch", "catch", "super", "this"}


def join_wrapped(raw):
    """Merge wrapped signatures (unbalanced parentheses) into one line; returns (lines, original 1-based numbers)."""
    out, nums, i = [], [], 0
    while i < len(raw):
        ln, n = raw[i], i + 1
        sig_start = re.match(r" *(public|protected|private|static|final|abstract) ", ln) and "=" not in ln
        while (sig_start and ln.count("(") > ln.count(")") and not ln.rstrip().endswith(("{", ";"))
               and i + 1 < len(raw)):
            i += 1
            ln = ln + " " + raw[i].strip()
        out.append(ln)
        nums.append(n)
        i += 1
    return out, nums


def clean_params(p):
    p = re.sub(r"@[\w.]+(\([^)]*\))?\s*", "", p)
    return re.sub(r"\s+", " ", p).strip()


def find_source(src_root, fqn_parts):
    """Resolve Outer.Inner chains to (path, [nested names])."""
    for i in range(len(fqn_parts), 0, -1):
        p = src_root.joinpath(*fqn_parts[:i]).with_suffix(".java")
        if p.exists():
            return p, fqn_parts[i:]
    return None, []


def class_body(lines, nested):
    """Return (start, end, indent) line range of the target class body."""
    start, end, indent = 0, len(lines), 0
    for name in nested:
        decl = re.compile(rf"^( *)(?:public |protected |private |static |final |abstract |sealed |non-sealed )*(?:class|interface|enum|record) {name}\b")
        for i in range(start, end):
            m = decl.match(lines[i])
            if m:
                indent = len(m.group(1))
                j = i + 1
                while j < end and lines[j] != " " * indent + "}":
                    j += 1
                start, end = i + 1, j
                break
        else:
            return None
    return start, end, indent


def main(src_root, out_dir):
    src_root, out_dir = Path(src_root), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    mgr_path = src_root / "zombie" / "Lua" / "LuaManager.java"
    text = mgr_path.read_text(encoding="utf-8", errors="replace")
    lines, nums = join_wrapped(text.splitlines())
    imports = {}
    for fq in IMPORT_RE.findall(text):
        imports[fq.rsplit(".", 1)[1]] = fq

    # --- exposed classes (registration order)
    start = text.index("public void exposeAll()")
    end = text.index("for (Class<?> clazz : this.exposed)", start)
    exposed = []
    for ref in SET_RE.findall(text[start:end]):
        head = ref.split(".")[0]
        fq = imports.get(head)
        if head[0].islower():
            full = ref  # written fully qualified in LuaManager
        elif fq:
            full = fq + ref[len(head):]
        elif head in ("Boolean", "Double", "Long", "Float", "Integer", "Math", "Void", "String", "Object"):
            full = "java.lang." + ref
        else:
            full = "zombie.Lua." + ref  # same package as LuaManager
        if full not in [e[1] for e in exposed]:
            exposed.append((ref, full))

    # --- global functions
    gstart = text.index("public static class GlobalObject")
    globals_rows = []
    i = text.count("\n", 0, gstart)
    while i < len(lines):
        m = LM_RE.search(lines[i])
        if m and "global = true" in m.group(1):
            nm = re.search(r'name\s*=\s*"([^"]+)"', m.group(1))
            j = i + 1
            while j < len(lines) and not SIG_RE.match(lines[j]) and j < i + 6:
                j += 1
            sig = SIG_RE.match(lines[j]) if j < len(lines) else None
            if sig:
                java_name = sig.group("name")
                globals_rows.append([
                    nm.group(1) if nm else java_name, java_name, clean_params(sig.group("params")),
                    sig.group("ret").strip(), nums[i],
                ])
            i = j
        i += 1
    with open(out_dir / "lua-globals.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["lua_name", "java_method", "params", "returns", "line_in_LuaManager"])
        w.writerows(sorted(globals_rows, key=lambda r: r[0].lower()))

    # --- exposed classes + their declared public members
    cls_rows, meth_rows, missing = [], [], []
    for ref, fq in exposed:
        parts = fq.split(".")
        path, nested = find_source(src_root, parts)
        simple = parts[-1]
        if path is None:
            cls_rows.append([simple, fq, "external", "", "", "", "", "", ""])
            if not fq.startswith(("java.", "se.", "javax.")):
                missing.append(fq)
            continue
        ls, _ = join_wrapped(path.read_text(encoding="utf-8", errors="replace").splitlines())
        body = class_body(ls, nested)
        if body is None:
            missing.append(fq)
            continue
        s, e, ind = body
        decl_idx = s - 1 if nested else 0
        if not nested:
            for k, ln in enumerate(ls):
                if re.match(rf".*\b(class|interface|enum|record) {simple}\b", ln):
                    decl_idx = k
                    break
        decl = ls[decl_idx] if ls else ""
        kind = re.search(r"\b(class|interface|enum|record)\b", decl)
        kind = kind.group(1) if kind else "?"
        ext = re.search(r"\bextends ([\w.<>, ?]+?)(?: implements|\s*\{|$)", decl)
        impl = re.search(r"\bimplements ([\w.<>, ?]+?)\s*\{", decl)
        n_pub = n_stat = n_field = n_ctor = 0
        member_indent = " " * (ind + 3)
        hidden_prev = False
        k = s
        while k < e:
            ln = ls[k]
            if ln.startswith(member_indent) and not ln.startswith(member_indent + " "):
                st = ln.strip()
                if st.startswith("@") and "HiddenFromLua" in st:
                    hidden_prev = True
                elif st.startswith("@"):
                    pass
                else:
                    if not hidden_prev:
                        sg = SIG_RE.match(ln)
                        cm = re.match(CTOR_RE_T.format(name=re.escape(simple)), ln)
                        if cm and kind != "interface":
                            n_ctor += 1
                            meth_rows.append([fq, "new", "static", clean_params(cm.group(1)), simple])
                        elif sg and sg.group("name") not in KEYWORDS and (
                                "public" in sg.group("mods") or kind == "interface"):
                            is_static = "static" in sg.group("mods")
                            n_pub += 1
                            n_stat += is_static
                            meth_rows.append([fq, sg.group("name"), "static" if is_static else "instance",
                                              clean_params(sg.group("params")), sg.group("ret").strip()])
                        else:
                            fm = FIELD_RE.match(ln)
                            if fm and "static" in fm.group("mods"):
                                n_field += 1
                                meth_rows.append([fq, fm.group("name"), "static-field", "", fm.group("type").strip()])
                    hidden_prev = False
            k += 1
        cls_rows.append([simple, fq, kind, ext.group(1).strip() if ext else "", impl.group(1).strip() if impl else "",
                         n_pub, n_stat, n_field, n_ctor])
    with open(out_dir / "exposed-classes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["class", "fqn", "kind", "extends", "implements", "public_methods", "static_methods",
                    "static_fields", "constructors"])
        w.writerows(cls_rows)
    with open(out_dir / "exposed-methods.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fqn", "member", "kind", "params", "returns_or_type"])
        w.writerows(meth_rows)
    print(f"exposed={len(exposed)} globals={len(globals_rows)} members={len(meth_rows)} unresolved={len(missing)}")
    if missing:
        print("unresolved:", ", ".join(missing[:40]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
