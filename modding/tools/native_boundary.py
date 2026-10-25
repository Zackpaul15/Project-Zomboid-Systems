"""Build modding/data/native-boundary.csv: one row per `native` method declaration under <src>/zombie.

Usage:  python -I native_boundary.py <decompiled src root> <projectzomboid.jar> <javap.exe> <output csv>

Columns: class,method,jni_signature,dll,dll_confidence,lua_exposed,java_caller
  - rows come from the decompiled source (declaration lines containing the `native` modifier);
  - jni_signature is the JVM descriptor, taken from `javap -p -s` of the same class in the jar;
  - dll is the candidate DLL or DLL pair, see CLASS_DLL below; loading is not proof of symbol ownership;
  - dll_confidence is direct (own loader), observed (existing export evidence), inferred (sibling), or unknown;
    unresolved DLL pairs take precedence over own-loader evidence;
  - lua_exposed is `yes` only for a public native on a class listed in modding/data/exposed-classes.csv;
  - java_caller is one representative calling class (heuristic text match, not a call-graph).
Only names, signatures and counts are written. No source bodies are copied.
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPOSED_CSV = HERE.parent / "data" / "exposed-classes.csv"

NET = "ZNetJNI64.dll|ZNetNoSteam64.dll"
# class -> DLL(s). Basis per entry is documented in notes/native-boundary.md.
CLASS_DLL = {
    "zombie.popman.ZombiePopulationManager": "PZPopMan64.dll",
    "zombie.popman.ZombiePopulationRenderer": "PZPopMan64.dll",
    "zombie.popman.MPDebugInfo": "PZPopMan64.dll",
    "zombie.popman.DebugCommands": "PZPopMan64.dll",
    "zombie.MapCollisionData": "PZPopMan64.dll",
    "zombie.core.physics.Bullet": "PZBullet64.dll",
    "zombie.core.physics.PhysicsDebugRenderer": "PZBullet64.dll",
    "zombie.pathfind.nativeCode.PathfindNative": "PZPathFind64.dll",
    "zombie.pathfind.nativeCode.PathfindNativeRenderer": "PZPathFind64.dll",
    "zombie.iso.LightingJNI": "Lighting64.dll",
    "zombie.vehicles.Clipper": "PZClipper64.dll",
    "zombie.vehicles.ClipperOffset": "PZClipper64.dll",
    "zombie.core.textures.VideoTexture": "bink64.dll|bink2w64.dll",
    "zombie.pzexe": "[unknown]",
    "zombie.jsig": "[unknown]",
}
for _c in ("ZNet", "SteamWorkshop", "SteamUtils", "SteamUser", "SteamRemotePlay", "SteamGameServer",
           "SteamFriends", "ServerBrowser", "PortMapper"):
    CLASS_DLL["zombie.core.znet." + _c] = NET
for _c in ("RakVoice", "RakNetPeerInterface"):
    CLASS_DLL["zombie.core.raknet." + _c] = NET

DIRECT_LOADERS = {
    "zombie.popman.ZombiePopulationManager",
    "zombie.core.physics.Bullet",
    "zombie.pathfind.nativeCode.PathfindNative",
    "zombie.iso.LightingJNI",
    "zombie.vehicles.Clipper",
    "zombie.core.textures.VideoTexture",
    "zombie.core.znet.SteamUtils",
    "zombie.pzexe",
    "zombie.jsig",
}
INFERRED_CLASSES = {
    "zombie.core.physics.PhysicsDebugRenderer",
    "zombie.vehicles.ClipperOffset",
    "zombie.popman.ZombiePopulationRenderer",
    "zombie.popman.MPDebugInfo",
    "zombie.popman.DebugCommands",
    "zombie.pathfind.nativeCode.PathfindNativeRenderer",
}


def dll_confidence(cls, dll):
    # Pair ownership is unresolved even when the class itself loads both candidates.
    if "|" in dll:
        return "unknown"
    if cls == "zombie.MapCollisionData":
        return "observed"
    if cls in INFERRED_CLASSES:
        return "inferred"
    if cls in DIRECT_LOADERS:
        return "direct"
    return "unknown"

NATIVE_RE = re.compile(r"^\s*(?P<mods>(?:\w+\s+)*?)native\s+(?P<rest>.+?)\s+(?P<name>\w+)\((?P<params>[^)]*)\)\s*(?:throws [\w., ]+)?;\s*$")
JAVAP_NATIVE_RE = re.compile(r"^\s+(?:[\w<>\[\], ?]+\s)?native\s+.*?(\w+)\(.*\)(?: throws [\w., ]+)?;\s*$")


def read_lines(p):
    return p.read_text(encoding="utf-8", errors="replace").splitlines()


def collect_natives(src_zombie, src_root):
    rows = []
    for p in sorted(src_zombie.rglob("*.java")):
        cls = ".".join(p.relative_to(src_root).with_suffix("").parts)
        lines = read_lines(p)
        for i, ln in enumerate(lines):
            if re.search(r"\bnative\b", ln) and "(" in ln:
                while not ln.rstrip().endswith(";") and i + 1 < len(lines):  # wrapped declaration
                    i += 1
                    ln = ln + " " + lines[i].strip()
            m = NATIVE_RE.match(ln)
            if m:
                mods = m.group("mods").split()
                rows.append({"class": cls, "method": m.group("name"), "mods": mods,
                             "static": "static" in mods, "path": p})
    return rows


def javap_descriptors(javap, jar, classes):
    """class -> list of (name, descriptor) for native members, in class-file order."""
    out = {}
    for cls in classes:
        r = subprocess.run([javap, "-p", "-s", "-cp", jar, cls], capture_output=True, text=True, check=True)
        lines = r.stdout.splitlines()
        res = []
        for i, ln in enumerate(lines):
            if " native " in ln and "(" in ln:
                name = re.search(r"(\w+)\(", ln).group(1)
                desc = lines[i + 1].split("descriptor:")[1].strip()
                res.append((name, desc))
        out[cls] = res
    return out


def load_exposed():
    with open(EXPOSED_CSV, newline="", encoding="utf-8") as f:
        return {r["fqn"] for r in csv.DictReader(f)}


def find_callers(rows, src_zombie, src_root):
    files = {}
    for p in sorted(src_root.rglob("*.java")):
        files[p] = [ln for ln in read_lines(p) if "native " not in ln]
    fqn_of = {p: ".".join(p.relative_to(src_root).with_suffix("").parts) for p in files}
    for r in rows:
        simple = r["class"].rsplit(".", 1)[1]
        m = r["method"]
        call_any = re.compile(r"\b" + re.escape(m) + r"\(")
        call_q = re.compile(r"\b" + re.escape(simple) + r"\s*\.\s*" + re.escape(m) + r"\(")
        best = None
        if r["static"] and "private" not in r["mods"]:
            hits = [(sum(len(call_q.findall(l)) for l in ls), fqn_of[p]) for p, ls in files.items()
                    if fqn_of[p] != r["class"]]
            hits = [h for h in hits if h[0] > 0]
            if hits:
                best = sorted(hits, key=lambda h: (-h[0], h[1]))[0][1]
        if best is None and any(call_any.search(l) for l in files[r["path"]]):
            best = r["class"]
        if best is None and not r["static"] and "private" not in r["mods"]:
            pkg = r["class"].rsplit(".", 1)[0]
            ref = re.compile(r"\b" + re.escape(simple) + r"\b")
            dot = re.compile(r"\.\s*" + re.escape(m) + r"\(")
            hits = []
            for p, ls in files.items():
                if fqn_of[p] == r["class"]:
                    continue
                txt = "\n".join(ls)
                if ref.search(txt) and dot.search(txt):
                    same = fqn_of[p].rsplit(".", 1)[0] == pkg
                    hits.append((0 if same else 1, fqn_of[p]))
            if hits:
                best = sorted(hits)[0][1]
        r["caller"] = best or "[unknown]"


def main():
    src_root, jar, javap, out = (Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4]))
    src_zombie = src_root / "zombie"
    rows = collect_natives(src_zombie, src_root)
    classes = sorted({r["class"] for r in rows})
    desc = javap_descriptors(javap, jar, classes)
    exposed = load_exposed()
    seen = {}
    for r in rows:
        k = (r["class"], r["method"])
        idx = seen.get(k, 0)
        seen[k] = idx + 1
        cands = [d for n, d in desc[r["class"]] if n == r["method"]]
        r["sig"] = cands[idx] if idx < len(cands) else "[unknown]"
        r["dll"] = CLASS_DLL.get(r["class"], "[unknown]")
        r["dll_confidence"] = dll_confidence(r["class"], r["dll"])
        yes = r["class"] in exposed and "public" in r["mods"]
        r["lua"] = "yes" if yes else "no"
    find_callers(rows, src_zombie, src_root)
    rows.sort(key=lambda r: (r["class"], r["method"], r["sig"]))
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["class", "method", "jni_signature", "dll", "dll_confidence", "lua_exposed", "java_caller"])
        for r in rows:
            w.writerow([r["class"], r["method"], r["sig"], r["dll"], r["dll_confidence"], r["lua"], r["caller"]])
    print(f"{len(rows)} rows, {len(classes)} classes")
    for c in classes:
        if len(desc[c]) != sum(1 for r in rows if r["class"] == c):
            print("MISMATCH javap vs src:", c, len(desc[c]))


if __name__ == "__main__":
    main()
