"""Cross-check committed catalogues; run with python -I from any directory.

Standard library only. Inputs come from one resolved HEAD, never the worktree.
No game files, decompile, network, clock, or existing output are read. Matching
means catalogue overlap, not runtime validity. Unresolved scope stays unknown.
"""

import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "modding/data/key-coverage.csv"
FIELDS = (
    "domain", "side", "name", "present_java", "present_lua", "present_data",
    "classification", "evidence",
)
SCHEMAS = {
    "events.csv": ("event", "registered", "reg_index", "methods", "arg_counts",
                   "trigger_classes", "sample_args", "lua_trigger_files"),
    "vanilla-event-subscriptions.csv": ("event", "file", "side"),
    "vanilla-lua-event-triggers.csv": ("event", "file", "side"),
    "script-keys.csv": ("block", "kind", "key", "value_type", "case_sensitive",
                        "source_class", "reader", "java_line"),
    "item-properties.csv": ("property", "count", "types_seen_on", "value_shape", "example_shape"),
    "item-component-properties.csv": ("block_path", "property", "count", "types_seen_on",
                                      "value_shape", "example_shape"),
}
DATA_TABLES = (
    "item-properties.csv", "item-component-properties.csv", "recipe-keys.csv",
    "vehicle-keys.csv", "sound-keys.csv", "fluid-keys.csv", "entity-keys.csv",
)
for _table in DATA_TABLES[2:]:
    SCHEMAS[_table] = ("block_type", "key", "count", "value_shape", "notes")

# Deliberately small, explicit crosswalk: only assignment readers with a known
# block path. No generic rule equates a Java family label with a nested path.
# Remaining readers are retained as unknown, with possible same-family matches.
CONTEXTS = {
    ("item", "Item", "DoParam"): "item",
    ("recipe", "Recipe", "Load"): "recipe",
    ("evolvedrecipe", "EvolvedRecipe", "Load"): "evolvedrecipe",
    ("fixing", "Fixing", "Load"): "fixing",
    ("craftRecipe", "CraftRecipe", "Load"): "craftRecipe",
    ("energy", "EnergyDefinitionScript", "Load"): "energy",
    ("sound", "GameSoundScript", "Load"): "sound",
    ("sound", "GameSoundScript", "LoadClip"): "sound/clip",
    ("character_trait_definition", "CharacterTraitDefinitionScript",
     "loadCharacterTraitDefinition"): "character_trait_definition",
    ("character_profession_definition", "CharacterProfessionDefinitionScript",
     "loadCharacterProfessionDefinition"): "character_profession_definition",
}


def git(*args):
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_inputs(revision):
    tables = {}
    for filename, schema in SCHEMAS.items():
        path = "modding/data/" + filename
        raw = git("show", revision + ":" + path)
        digest = hashlib.sha256(raw).hexdigest()
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
        if reader.fieldnames != list(schema):
            raise ValueError(path + ": unexpected header: " + repr(reader.fieldnames))
        records = []
        for number, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"{path}: record {number}: malformed CSV row")
            records.append({"row": row, "ref": f"{path}#record={number}",
                            "sha256": digest})
        tables[filename] = records
    return tables


def event_rows(tables):
    by_name = {}
    roles = (
        ("events.csv", "java_catalogue", "java"),
        ("vanilla-event-subscriptions.csv", "lua_subscription", "lua"),
        ("vanilla-lua-event-triggers.csv", "lua_trigger", "lua"),
    )
    for filename, role, side in roles:
        for entry in tables[filename]:
            name = entry["row"]["event"]
            if not name:
                raise ValueError(entry["ref"] + ": empty event identifier")
            by_name.setdefault(name, []).append((entry, role, side))
    for name, entries in sorted(by_name.items()):
        java = any(role == "java_catalogue" for _, role, _ in entries)
        lua = any(side == "lua" for _, _, side in entries)
        trigger = any(role == "lua_trigger" for _, role, _ in entries)
        if java and lua:
            classification, reason = "matched", "exact_case_catalogue_overlap"
        elif not java and trigger:
            classification, reason = "explained", "literal_lua_trigger_provenance"
        else:
            classification, reason = "unknown", "one_sided_static_catalogue"
        for entry, role, side in entries:
            yield ("events", side, name, str(int(java)), str(int(lua)), "n/a",
                   classification, {"source": entry, "role": role, "reason": reason,
                                    "related": sorted(e["ref"] for e, _, _ in entries)})


def data_entries(tables):
    for filename in DATA_TABLES:
        for entry in tables[filename]:
            row = entry["row"]
            if filename == "item-properties.csv":
                context, kind, key = "item", "key", row["property"]
            elif filename == "item-component-properties.csv":
                context, kind, key = "item/" + row["block_path"], "key", row["property"]
            else:
                context, key = row["block_type"], row["key"]
                # Keep all structural/count markers; they are not assignments.
                kind = "survey-marker" if key.startswith("<") else "key"
            count = int(row["count"])
            if count < 0 or not context or not key:
                raise ValueError(entry["ref"] + ": invalid context, key or count")
            yield {"source": entry, "context": context, "kind": kind,
                   "key": key, "present": count > 0}


def same_key(parser, data):
    if parser["key"] == data["key"]:
        return True
    # Java equalsIgnoreCase is not Python casefold. Avoid guessing non-ASCII.
    return (parser["case_sensitive"] == "no"
            and parser["key"].isascii() and data["key"].isascii()
            and parser["key"].lower() == data["key"].lower())


def family_candidate(parser, data):
    """Broad discovery only; never establishes presence or a match."""
    block = parser["block"]
    root = data["context"].split("/", 1)[0]
    if root.startswith("template "):
        root = root[len("template "):]
    return (same_key(parser, data) and (
        block == "(every script block)" or block == "item / entity attributes"
        or block.split(" > ", 1)[0] == root
        or ("/component:" in data["context"] and block.startswith("entity > component "))
        or (root.startswith("xui") and block.startswith("xui"))))


def script_rows(tables):
    data = list(data_entries(tables))
    java = tables["script-keys.csv"]
    links = {entry["ref"]: [] for entry in java}
    reverse = {entry["source"]["ref"]: [] for entry in data}
    candidates = {entry["ref"]: [] for entry in java}
    reverse_candidates = {entry["source"]["ref"]: [] for entry in data}
    for entry in java:
        parser = entry["row"]
        context = CONTEXTS.get((parser["block"], parser["source_class"], parser["reader"]))
        for observed in data:
            if not observed["present"]:
                continue
            if (context is not None and parser["kind"] == observed["kind"] == "key"
                    and context == observed["context"] and same_key(parser, observed)):
                links[entry["ref"]].append(observed)
                reverse[observed["source"]["ref"]].append(entry)
            elif family_candidate(parser, observed):
                candidates[entry["ref"]].append(observed["source"]["ref"])
                reverse_candidates[observed["source"]["ref"]].append(entry["ref"])

    for entry in java:
        parser = entry["row"]
        matches = links[entry["ref"]]
        possible = candidates[entry["ref"]]
        exact = any(parser["key"] == match["key"] for match in matches)
        classification = ("matched" if exact else "explained") if matches else "unknown"
        reason = ("exact_scoped_assignment_overlap" if exact else "case_insensitive_parser_overlap")
        if not matches:
            reason = "scope_or_grammar_unresolved" if possible else "no_observation_in_input_catalogues"
        name = packed({k: parser[k] for k in ("block", "kind", "key", "source_class", "reader")})
        yield ("script_keys", "java", name, "1", "n/a",
               "1" if matches else "unknown" if possible else "0", classification,
               {"source": entry, "reason": reason,
                "mapped_context": CONTEXTS.get((parser["block"], parser["source_class"], parser["reader"])),
                "matches": sorted(m["source"]["ref"] for m in matches), "candidates": sorted(possible)})

    for observed in data:
        entry = observed["source"]
        matches = reverse[entry["ref"]]
        possible = reverse_candidates[entry["ref"]]
        exact = any(m["row"]["key"] == observed["key"] for m in matches)
        classification = ("matched" if exact else "explained") if matches else "unknown"
        reason = "exact_scoped_assignment_overlap" if exact else "case_insensitive_parser_overlap"
        if not matches:
            reason = "scope_or_grammar_unresolved" if possible else "no_parser_match_in_input_catalogue"
        if not observed["present"]:
            classification, reason = "explained", "zero_count_survey_marker_not_an_occurrence"
        name = packed({k: observed[k] for k in ("context", "kind", "key")})
        yield ("script_keys", "data", name,
               "1" if matches else "unknown" if possible else "0", "n/a",
               str(int(observed["present"])), classification,
               {"source": entry, "reason": reason,
                "matches": sorted(m["ref"] for m in matches), "candidates": sorted(possible)})


def main():
    revision = git("rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()
    tables = load_inputs(revision)
    # Build and validate everything before touching the previous output.
    rows = []
    for row in (*event_rows(tables), *script_rows(tables)):
        *values, evidence = row
        if values[6] not in {"matched", "explained", "defect", "unknown"}:
            raise ValueError("invalid classification")
        evidence["input_revision"] = revision
        rows.append((*values, packed(evidence)))
    rows.sort()
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(FIELDS)
    writer.writerows(rows)
    OUTPUT.write_bytes(buffer.getvalue().encode("utf-8"))
    print(f"Wrote {len(rows)} rows to modding/data/key-coverage.csv; input revision {revision}")


if __name__ == "__main__":
    main()
