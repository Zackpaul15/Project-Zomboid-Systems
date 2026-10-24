"""Extract the keys and nested block types that each script parser reads, from the decompiled Java.

Usage:  python -I extract_script_keys.py <decompiled src root> <out csv>

Reads `<src>/zombie/scripting/**`, `zombie/entity/ComponentType.java`, `zombie/entity/components/attributes/Attribute.java`
and a few non-ScriptManager file parsers. A "key" is a string literal compared with the key variable of a
`name = value,` line (`param`, `key`, `k`); a "block" is a literal compared with a nested block's `type`
(`child.type`, `block.type`). The value type is guessed from the code that follows the comparison and is [inferred].

Output columns: block, kind, key, value_type, case_sensitive, source_class, reader, java_line
  kind: key | block | block-id | xui-var | attribute | token (line-grammar word) | flag (enum constant)
  reader: Java method that holds the comparison (shows which nested block a key belongs to)
"""
import csv
import re
import sys
from pathlib import Path

# source file (relative to zombie/) -> script block tag it parses (ScriptType tags, see ScriptType.java)
BLOCKS = {
    "scripting/objects/Item.java": "item",
    "scripting/objects/Recipe.java": "recipe",
    "scripting/objects/UniqueRecipe.java": "uniquerecipe",
    "scripting/objects/EvolvedRecipe.java": "evolvedrecipe",
    "scripting/objects/Fixing.java": "fixing",
    "scripting/objects/AnimationsMesh.java": "animationsMesh",
    "scripting/objects/MannequinScript.java": "mannequin",
    "scripting/objects/ModelScript.java": "model",
    "iso/SpriteModel.java": "spriteModel",
    "scripting/objects/GameSoundScript.java": "sound",
    "scripting/objects/SoundTimelineScript.java": "soundTimeline",
    "scripting/objects/VehicleScript.java": "vehicle",
    "core/skinnedmodel/runtime/RuntimeAnimationScript.java": "animation",
    "vehicles/VehicleEngineRPM.java": "vehicleEngineRPM",
    "scripting/itemConfig/ItemConfig.java": "itemConfig",
    "scripting/entity/GameEntityScript.java": "entity",
    "scripting/objects/XuiConfigScript.java": "xuiConfig",
    "scripting/objects/XuiLayoutScript.java": "xuiLayout/xuiStyle/xuiDefaultStyle",
    "scripting/objects/XuiColorsScript.java": "xuiGlobalColors",
    "scripting/objects/XuiSkinScript.java": "xuiSkin",
    "scripting/objects/ItemFilterScript.java": "itemFilter",
    "scripting/objects/FluidFilterScript.java": "fluidFilter",
    "scripting/entity/components/crafting/CraftRecipe.java": "craftRecipe",
    "scripting/objects/StringListScript.java": "stringList",
    "scripting/objects/EnergyDefinitionScript.java": "energy",
    "scripting/objects/FluidDefinitionScript.java": "fluid",
    "scripting/objects/PhysicsShapeScript.java": "physicsShape",
    "scripting/objects/TimedActionScript.java": "timedAction",
    "scripting/objects/RagdollScript.java": "ragdoll",
    "scripting/objects/PhysicsHitReactionScript.java": "physicsHitReaction",
    "scripting/objects/ClockScript.java": "clock",
    "scripting/objects/CharacterTraitDefinitionScript.java": "character_trait_definition",
    "scripting/objects/CharacterProfessionDefinitionScript.java": "character_profession_definition",
    "scripting/objects/BaseScriptObject.java": "(every script block)",
    # helper classes reached from the blocks above
    "scripting/entity/components/crafting/InputScript.java": "craftRecipe > inputs line",
    "scripting/entity/components/crafting/OutputScript.java": "craftRecipe > outputs line",
    "scripting/itemConfig/script/BucketRootScript.java": "itemConfig > root",
    "scripting/itemConfig/script/SelectorBucketScript.java": "itemConfig > selector",
    "scripting/ui/XuiScript.java": "xui element (layout/style)",
    "scripting/ui/XuiTableScript.java": "xui table",
    "scripting/ui/XuiLuaStyle.java": "xui lua style",
    # files parsed with ScriptParser but outside the ScriptManager buckets
    "characters/skills/CustomPerks.java": "(file) custom perks",
    "sandbox/CustomSandboxOptions.java": "(file) custom sandbox options",
    "modding/ActiveModsFile.java": "(file) active mods",
    "iso/SpriteModelsFile.java": "(file) sprite models",
    "seams/SeamFile.java": "(file) seams",
    "seating/SeatingFile.java": "(file) seating",
    "tileDepth/TileDepthTextureAssignments.java": "(file) tile depth assignments",
    "tileDepth/TileGeometryFile.java": "(file) tile geometry",
    "ui/FontsFile.java": "(file) fonts",
}

KEY_VARS = r"(?:param(?:\.trim\(\))?|key|k)"
BLOCK_VARS = r"(?:child\.type|block\.type)"
RE_KEY_A = re.compile(KEY_VARS + r'\.(equalsIgnoreCase|equals)\("([^"]+)"\)')
RE_KEY_B = re.compile(r'"([^"]+)"\.(equalsIgnoreCase|equals)\((?:k|key)\)')
RE_BLK_A = re.compile(BLOCK_VARS + r'\.(equalsIgnoreCase|equals)\("([^"]+)"\)')
RE_BLK_B = re.compile(r'"([^"]+)"\.(equalsIgnoreCase|equals)\((?:child\.type|block\.type)\)')
# throwaway literals in the game's sample/dead branches (e.g. "something", "xxx"); not real script keys
PLACEHOLDERS = {"something", "xxx", "someType", "someKey", "someOtherKey", "null"}
RE_TOKEN = re.compile(r'(?:\bs|elems\[\d\])\.(startsWith|equalsIgnoreCase)\("([^"]+)"\)')
FLAG_ENUMS = {"entity/components/crafting/InputFlag.java": "craftRecipe > inputs line", "entity/components/crafting/OutputFlag.java": "craftRecipe > outputs line"}
RE_XUI = re.compile(r'new XuiScript\.(Xui\w+)\(this, "(\w+)"')
RE_METHOD = re.compile(r"^   (?:(?:public|private|protected|static|final|abstract|synchronized)\s+)+[\w<>\[\],.? ]+?\s+(\w+)\(", re.M)
RE_CASE = re.compile(r'case "([^"]+)":')
TYPE_RULES = [
    ("float", r"Float\.parseFloat|parseFloat"),
    ("int", r"Integer\.parseInt|parseInt"),
    ("double", r"Double\.parseDouble"),
    ("long", r"Long\.parseLong"),
    ("bool", r"Boolean\.parseBoolean|equalsIgnoreCase\(\"true\"\)|\"true\"\.equalsIgnoreCase"),
    ("vector3", r"LoadVector3|LoadVector3f"),
    ("list", r"\.split\("),
    ("resource-location", r"ResourceLocation"),
    ("enum", r"\.valueOf\(|\.get\("),
]


def guess_type(snippet):
    for name, rx in TYPE_RULES:
        if re.search(rx, snippet):
            return name
    return "string/other"


def method_at(text, pos, methods):
    name = ""
    for m_pos, m_name in methods:
        if m_pos > pos:
            break
        name = m_name
    return name


def scan_file(path, label, rel):
    text = path.read_text(encoding="utf-8", errors="replace")
    methods = [(m.start(), m.group(1)) for m in RE_METHOD.finditer(text)]
    cls = rel.rsplit("/", 1)[1][:-5]
    hits = []
    starts = []
    for rx, kind, lit, eq in ((RE_KEY_A, "key", 2, 1), (RE_KEY_B, "key", 1, 2), (RE_BLK_A, "block", 2, 1), (RE_BLK_B, "block", 1, 2)):
        for m in rx.finditer(text):
            starts.append(m.start())
            hits.append((m.start(), m.end(), kind, m.group(lit), m.group(eq)))
    starts.sort()
    rows = []
    for start, end, kind, lit, eq in sorted(hits):
        following = [s for s in starts if s > start]
        stop = min(following[0] if following else len(text), end + 600)
        snippet = text[end:stop]
        # only the branch body: cut at the next sibling branch
        cut = snippet.find("} else")
        if cut != -1:
            snippet = snippet[:cut]
        line = text.count("\n", 0, start) + 1
        vtype = guess_type(snippet) if kind == "key" else ""
        rows.append((label, kind, lit, vtype, "no" if eq == "equalsIgnoreCase" else "yes", cls, method_at(text, start, methods), line))
    if cls in ("InputScript", "OutputScript"):
        for m in RE_TOKEN.finditer(text):
            tok = m.group(2)
            if tok == "something":
                continue  # dead branch in InputScript.LoadBlock
            line = text.count("\n", 0, m.start()) + 1
            rows.append((label, "token", tok, "", "no" if m.group(1) == "equalsIgnoreCase" else "prefix", cls, method_at(text, m.start(), methods), line))
    for m in RE_XUI.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        rows.append((label, "xui-var", m.group(2), m.group(1)[3:].lower(), "n/a", cls, method_at(text, m.start(), methods), line))
    return rows, text, methods


def vehicle_block_ids(text, methods, label, cls):
    rows = []
    idx = text.find("switch (block.id)")
    if idx != -1:
        end = text.find("default:", idx)
        for m in RE_CASE.finditer(text, idx, end):
            line = text.count("\n", 0, m.start()) + 1
            rows.append((label, "block-id", "physics " + m.group(1), "", "yes", cls, method_at(text, m.start(), methods), line))
    return rows


def component_labels(src):
    ct = (src / "zombie/entity/ComponentType.java").read_text(encoding="utf-8", errors="replace")
    out = {}
    for m in re.finditer(r"^\s+(\w+)\(\(short\)\d+,\s*\w+\.class,\s*(\w+Script)\.class", ct, re.M):
        out[m.group(2)] = m.group(1)
    for m in re.finditer(r"^\s+(\w+)\(\s*\(short\)\d+,\s*\w+\.class,\s*(\w+Script)\.class", ct, re.M):
        out[m.group(2)] = m.group(1)
    return out


def attribute_rows(src):
    text = (src / "zombie/entity/components/attributes/Attribute.java").read_text(encoding="utf-8", errors="replace")
    rows = []
    for m in re.finditer(r"AttributeType\.(\w+)(?:<\w*>)?\(\s*\(short\)(\d+),\s*\"(\w+)\"", text):
        line = text.count("\n", 0, m.start()) + 1
        rows.append(("item / entity attributes", "attribute", m.group(3), m.group(1).lower(), "no", "Attribute", "static init", line))
    return rows


def main(src_root, out_csv):
    src = Path(src_root)
    zroot = src / "zombie"
    comp = component_labels(src)
    rows = []
    unlabeled = []
    seen = set()
    for rel, label in BLOCKS.items():
        p = zroot / rel
        if not p.exists():
            print("missing", rel)
            continue
        seen.add(rel)
        r, text, methods = scan_file(p, label, rel)
        rows += r
        if rel.endswith("VehicleScript.java"):
            rows += vehicle_block_ids(text, methods, label, "VehicleScript")
    for p in sorted((zroot / "scripting/entity/components").rglob("*Script.java")):
        rel = p.relative_to(zroot).as_posix()
        if rel in seen:
            continue
        cls = p.stem
        name = comp.get(cls)
        if name is None:
            unlabeled.append(rel)
            continue
        r, _, _ = scan_file(p, "entity > component " + name, rel)
        rows += r
        seen.add(rel)
    rows += attribute_rows(src)
    for rel, label in FLAG_ENUMS.items():
        ftext = (zroot / rel).read_text(encoding="utf-8", errors="replace")
        body = ftext[ftext.find("{"):ftext.find(";", ftext.find("{"))]
        for m in re.finditer(r"^\s+(\w+)\s*[,;]?\s*$", body, re.M):
            line = ftext.count("\n", 0, ftext.find(m.group(0))) + 1
            rows.append((label, "flag", m.group(1), "", "yes", rel.rsplit("/", 1)[1][:-5], "enum", line))
    for p in sorted((zroot / "scripting").rglob("*.java")):
        rel = p.relative_to(zroot).as_posix()
        if rel not in seen and (RE_KEY_A.search(p.read_text(encoding="utf-8", errors="replace"))):
            unlabeled.append(rel)
    seen_rows = set()
    out = []
    for r in rows:
        if r[2] in PLACEHOLDERS and r[1] in ("key", "block"):
            continue
        if r in seen_rows:
            continue
        seen_rows.add(r)
        out.append(r)
    out.sort(key=lambda r: (r[0].lower(), {"key": 0, "xui-var": 1, "attribute": 2, "token": 3, "flag": 4, "block": 5, "block-id": 6}[r[1]], r[2].lower(), r[7]))
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["block", "kind", "key", "value_type", "case_sensitive", "source_class", "reader", "java_line"])
        w.writerows(out)
    print(f"wrote {len(out)} rows to {out_csv}")
    if unlabeled:
        print("files with comparisons but no label:", ", ".join(unlabeled))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
