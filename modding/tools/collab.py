"""Coordination helper for the Claude/Codex split described in modding/SCOPE.md.

Subcommands (run as `python -I modding/tools/collab.py <cmd>` from anywhere in the repo):

  status                      who has finished what, open [review]/[question] lines, uncommitted files by owner
  next --agent A              ready-to-paste prompt for the agent's next job (open reviews first, then next WP)
  gates [--agent A] [--all]   checks on uncommitted docs/tables (or everything with --all)
  commit --agent A --wp ID --message TEXT PATH... [--yes]
                              gate-check, then stage exactly PATH... and commit; dry run unless --yes

It never pushes, never runs `git add -A`, and never touches a path the named agent does not own.
Reads SCOPE.md (work-package tables) and HANDOFF.md (progress log); writes nothing except via `commit --yes`.
"""
import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODDING = ROOT / "modding"
SCOPE = MODDING / "SCOPE.md"
HANDOFF = MODDING / "HANDOFF.md"
AGENTS = ("claude", "codex")
TRAILER = "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
# docs that must carry a survey date + build line near the top
HEADER_DIRS = ("modding/lua-api/", "modding/lua-library/", "modding/workflow/", "modding/scripts/")
# files allowed to mention local machine paths
LOCAL_PATH_OK = ("modding/SCOPE.md", "modding/CODEX_PROMPT.md", "modding/HANDOFF.md", "AGENTS.md")
LONG_FENCE_LINES = 40

CLAUDE_DATA = {"events", "lua-globals", "exposed-classes", "exposed-methods", "script-keys", "sandbox-options"}
CLAUDE_TOOLS = {"collab", "gen_class_docs"}


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        sys.exit("git %s failed: %s" % (" ".join(args), r.stderr.strip()))
    return r


def owner_of(path):
    """Owner of a repo-relative posix path: claude, codex, or both (shared / unknown)."""
    p = path.replace("\\", "/")
    stem = Path(p).stem
    if p.startswith(("modding/lua-api/",)) or p.startswith(("notes/",)) or p == "README.md":
        return "claude"
    if p.startswith(("modding/lua-library/", "modding/workflow/")):
        return "codex"
    if p.startswith("modding/scripts/"):
        return "claude" if Path(p).name == "parser-keys.md" else "codex"
    if p == "modding/HANDOFF.md":
        return "both"
    if p in ("modding/README.md", "modding/SCOPE.md", "modding/CODEX_PROMPT.md"):
        return "claude"
    if p.startswith("modding/data/"):
        return "claude" if stem in CLAUDE_DATA else "codex"
    if p.startswith("modding/tools/"):
        if stem in CLAUDE_TOOLS or stem.startswith("extract_"):
            return "claude"
        return "codex" if stem.startswith("survey_") else "both"
    return "both"


def changed_paths():
    """Uncommitted paths (modified, staged, untracked files), repo-relative posix."""
    out = git("status", "--porcelain", "-z", "-uall").stdout
    parts = out.split("\0")
    paths, i = [], 0
    while i < len(parts):
        e = parts[i]
        i += 1
        if len(e) < 4:
            continue
        xy, p = e[:2], e[3:]
        if "R" in xy or "C" in xy:
            i += 1  # skip the original name
        paths.append(p)
    return paths


def read_text(p):
    return Path(p).read_text(encoding="utf-8", errors="replace")


def load_scope():
    """[(id, owner, package, output)] in table order, from SCOPE.md work-package tables."""
    rows = []
    for line in read_text(SCOPE).splitlines():
        m = re.match(r"^\|\s*([CXJ]\d+)\s*\|(.*?)\|(.*?)\|", line)
        if m:
            wp = m.group(1)
            owner = {"C": "claude", "X": "codex", "J": "both"}[wp[0]]
            rows.append((wp, owner, m.group(2).strip(), m.group(3).strip()))
    return rows


def load_handoff():
    """(done ids, reviews, resolved, questions); reviews/questions are (line_no, path, text)."""
    done, reviews, resolved, questions = set(), [], [], []
    for n, line in enumerate(read_text(HANDOFF).splitlines(), 1):
        m = re.match(r"^\[done\]\s+([CXJ]\d+)(?:-([CXJ]?\d+))?", line)
        if m:
            first = m.group(1)
            done.add(first)
            if m.group(2):
                last = m.group(2) if m.group(2)[0].isalpha() else first[0] + m.group(2)
                for k in range(int(first[1:]), int(last[1:]) + 1):
                    done.add("%s%d" % (first[0], k))
            continue
        m = re.match(r"^\[(review|resolved|question)\]\s+([^\s:]+)", line)
        if m:
            kind, path = m.group(1), m.group(2).strip("`")
            item = (n, path, line)
            {"review": reviews, "resolved": resolved, "question": questions}[kind].append(item)
    return done, reviews, resolved, questions


def open_items(items, resolved):
    """Count-based pairing: each [resolved] <path> closes the earliest open item for that path."""
    left = list(items)
    for _, rpath, _ in resolved:
        for k, it in enumerate(left):
            if it[1] == rpath:
                del left[k]
                break
    return left


def addressed_to(item_path):
    """A review/question on a path goes to that path's owner."""
    own = owner_of(item_path)
    return own if own in AGENTS else "both"


def cmd_status(_args):
    scope = load_scope()
    done, reviews, resolved, questions = load_handoff()
    open_rev = open_items(reviews, resolved)
    open_q = open_items(questions, resolved)
    print("Work packages")
    for agent in AGENTS:
        mine = [r for r in scope if r[1] == agent]
        d = [r[0] for r in mine if r[0] in done]
        todo = [r[0] for r in mine if r[0] not in done]
        print("  %-7s done %-2d/%-2d  next: %s" % (agent, len(d), len(mine), todo[0] if todo else "-"))
    joint = [r for r in scope if r[1] == "both"]
    jt = [r[0] for r in joint if r[0] not in done]
    print("  joint   open: %s" % (", ".join(jt) or "-"))
    print("\nOpen reviews (%d)" % len(open_rev))
    for n, path, line in open_rev:
        print("  HANDOFF:%d -> %s: %s" % (n, addressed_to(path), line[:110]))
    print("\nOpen questions (%d)" % len(open_q))
    for n, path, line in open_q:
        print("  HANDOFF:%d: %s" % (n, line[:110]))
    print("\nUncommitted files by owner")
    by = {"claude": [], "codex": [], "both": []}
    for p in changed_paths():
        by[owner_of(p)].append(p)
    for k, v in by.items():
        print("  %-6s %d" % (k, len(v)))
        for p in v[:12]:
            print("    " + p)
        if len(v) > 12:
            print("    ... %d more" % (len(v) - 12))
    ahead = git("rev-list", "--count", "@{u}..HEAD", check=False)
    if ahead.returncode == 0:
        print("\nUnpushed commits: %s (push only when the user asks)" % ahead.stdout.strip())


def cmd_next(args):
    scope = load_scope()
    done, reviews, resolved, _ = load_handoff()
    open_rev = [r for r in open_items(reviews, resolved) if addressed_to(r[1]) == args.agent]
    lines = ["Read modding/SCOPE.md, modding/HANDOFF.md and AGENTS.md first. You are %s." % args.agent]
    if open_rev:
        lines.append("First resolve these review items (then append `[resolved] <path>: <what changed>`):")
        for n, _, text in open_rev:
            lines.append("  - HANDOFF line %d: %s" % (n, text))
    todo = [r for r in scope if r[1] == args.agent and r[0] not in done]
    if todo:
        wp, _, pkg, out = todo[0]
        lines.append("Then do %s: %s" % (wp, pkg))
        lines.append("Output: %s" % out)
        lines.append("Verify 3 random claims against the game files, append `[done] %s ...; checked: ...` to "
                     "HANDOFF.md, run `python -I modding/tools/collab.py gates --agent %s`, then commit explicit "
                     "paths only. Do not push." % (wp, args.agent))
    elif not open_rev:
        lines.append("No owned work package is open. Check the joint packages (J1-J3) and HANDOFF.")
    print("\n".join(lines))


# ---------------------------------------------------------------- gates

class Result:
    def __init__(self):
        self.fail, self.warn = [], []

    def add(self, level, path, msg):
        (self.fail if level == "FAIL" else self.warn).append("%s: %s" % (path, msg))


def md_links(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.findall(r"\]\(([^)\s]+)\)", text)


def check_doc(rel, res):
    path = ROOT / rel
    text = read_text(path)
    head = "\n".join(text.splitlines()[:15])
    if rel.startswith(HEADER_DIRS) and "/classes/" not in rel:
        if not re.search(r"\d{4}-\d{2}-\d{2}", head) or "build" not in head.lower():
            res.add("FAIL", rel, "no survey date + build line in the first 15 lines")
        if not re.search(r"\[(observed|inferred|unknown)\]", text, re.I):
            res.add("WARN", rel, "no [observed]/[inferred]/[unknown] tags")
    for target in md_links(text):
        if re.match(r"^(https?:|mailto:|#)", target):
            continue
        t = target.split("#")[0]
        if t and not (path.parent / t).resolve().exists():
            res.add("FAIL", rel, "broken link -> %s" % target)
    for m in re.finditer(r"```[^\n]*\n(.*?)```", text, flags=re.S):
        n = m.group(1).count("\n")
        if n > LONG_FENCE_LINES:
            res.add("WARN", rel, "code fence of %d lines (is any of it copied game code?)" % n)
    if rel not in LOCAL_PATH_OK and re.search(r"[A-Za-z]:\\Users\\", text):
        res.add("WARN", rel, "mentions a local user path; the repo is meant to be shareable")


def check_csv(rel, res):
    with open(ROOT / rel, newline="", encoding="utf-8", errors="replace") as f:
        rows = list(csv.reader(f))
    if not rows:
        res.add("FAIL", rel, "empty csv")
        return
    width = len(rows[0])
    bad = [i + 1 for i, r in enumerate(rows) if len(r) != width]
    if bad:
        res.add("FAIL", rel, "%d rows differ from the %d-column header (first at line %d)" % (len(bad), width, bad[0]))


def check_handoff(res):
    for n, line in enumerate(read_text(HANDOFF).splitlines(), 1):
        if line.startswith("[done]"):
            for tok in re.findall(r"\bmodding/[\w./-]+\.(?:md|csv|py)\b", line):
                if not (ROOT / tok).exists():
                    res.add("WARN", "HANDOFF.md:%d" % n, "[done] names a missing path %s" % tok)


def run_gates(paths, agent=None):
    res = Result()
    for rel in paths:
        if not (ROOT / rel).is_file():
            continue
        if agent:
            own = owner_of(rel)
            if own not in (agent, "both"):
                res.add("FAIL", rel, "owned by %s, not %s" % (own, agent))
        if rel.endswith(".md") and rel != "modding/HANDOFF.md":
            check_doc(rel, res)
        elif rel.endswith(".csv"):
            check_csv(rel, res)
    check_handoff(res)
    return res


def modding_files():
    return [p.relative_to(ROOT).as_posix() for p in MODDING.rglob("*") if p.is_file()
            and p.suffix in (".md", ".csv", ".py") and "__pycache__" not in p.parts]


def report(res):
    for w in res.warn:
        print("WARN  " + w)
    for f in res.fail:
        print("FAIL  " + f)
    print("%d failure(s), %d warning(s)" % (len(res.fail), len(res.warn)))
    return 1 if res.fail else 0


def cmd_gates(args):
    paths = modding_files() if args.all else [p for p in changed_paths() if p.startswith(("modding/", "notes/", "README"))]
    res = run_gates(paths, args.agent)
    print("Checked %d file(s)%s" % (len(paths), " (all)" if args.all else " (uncommitted)"))
    sys.exit(report(res))


def cmd_commit(args):
    if args.agent not in AGENTS:
        sys.exit("--agent must be claude or codex")
    if git("diff", "--cached", "--quiet", check=False).returncode != 0:
        sys.exit("Something is already staged; commit or unstage it first.")
    changed = set(changed_paths())
    paths = [p.replace("\\", "/") for p in args.paths]
    missing = [p for p in paths if p not in changed]
    if missing:
        sys.exit("Not modified/untracked (or wrong path): " + ", ".join(missing))
    done, *_ = load_handoff()
    if args.wp not in done:
        print("WARN  no `[done] %s` line in HANDOFF.md yet" % args.wp)
    elif "modding/HANDOFF.md" not in paths and "modding/HANDOFF.md" in changed:
        print("WARN  HANDOFF.md has uncommitted changes and is not in PATH list")
    res = run_gates(paths, args.agent)
    if report(res):
        sys.exit("Gates failed; nothing staged.")
    msg = "%s: %s" % (args.wp, args.message)
    if args.agent == "claude":
        msg += "\n\n" + TRAILER
    print("\nPlanned commit (%s):\n  %s\n  files: %d" % (args.agent, msg.splitlines()[0], len(paths)))
    for p in paths:
        print("    " + p)
    if not args.yes:
        print("\nDry run. Re-run with --yes to stage these exact paths and commit. Nothing is pushed.")
        return
    git("add", "--", *paths)
    git("commit", "-q", "-m", msg)
    print(git("log", "--oneline", "-n", "1").stdout.strip())


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    p = sub.add_parser("next")
    p.add_argument("--agent", choices=AGENTS, required=True)
    p.set_defaults(fn=cmd_next)
    p = sub.add_parser("gates")
    p.add_argument("--agent", choices=AGENTS)
    p.add_argument("--all", action="store_true")
    p.set_defaults(fn=cmd_gates)
    p = sub.add_parser("commit")
    p.add_argument("--agent", required=True)
    p.add_argument("--wp", required=True)
    p.add_argument("--message", required=True)
    p.add_argument("--yes", action="store_true")
    p.add_argument("paths", nargs="+")
    p.set_defaults(fn=cmd_commit)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
