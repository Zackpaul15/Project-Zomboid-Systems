"""Coordination helper for the Claude/Codex split described in modding/SCOPE.md.

Subcommands (run as `python -I modding/tools/collab.py <cmd>` from anywhere in the repo):

  status                      who has finished what, open [review]/[question] lines, uncommitted files by owner
  next --agent A              ready-to-paste prompt for the agent's next job (open reviews and questions first,
                              then the next owned WP, else a joint package: J1 both agents, J2/J3 claude)
  gates [--agent A] [--all] [PATH...]
                              checks on uncommitted docs/tables (or everything with --all); with --agent A only
                              paths A owns (or 'both') plus the named PATHs are checked, other owners' dirty
                              paths are reported as INFO, never FAIL
  commit --agent A --wp ID --message TEXT PATH... [--yes]
                              gate-check, then stage exactly PATH... and commit with an explicit pathspec under
                              a lockfile (.git/collab.lock); aborts if the staged set != PATH...; dry run unless --yes
  selftest                    read-only checks of the parsers and fixes against inline fixtures; one PASS/FAIL
                              line per check, non-zero exit on any failure

Routing: a review/question goes to the owner of its path; items on shared ('both') or unknown paths go to both
agents. A `[resolved] <path>` line closes exactly one open item: name it with `HANDOFF:<line>` / `line <n>`
and/or `section <tok>` (the review's own section token). If that does not pick exactly one item the resolution
is reported as ambiguous and every candidate stays open (a lone open item on the path is closed unnamed).
Ownership is decided by path; deleted paths still have an owner.

It never pushes, never runs `git add -A`, and never touches a path the named agent does not own.
Reads SCOPE.md (work-package tables) and HANDOFF.md (progress log); writes nothing except via `commit --yes`.
"""
import argparse
import csv
import os
import re
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
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


def parse_scope(text):
    """[(id, owner, package, output)] in table order, from SCOPE.md work-package tables."""
    rows = []
    for line in text.splitlines():
        m = re.match(r"^\|\s*([CXJ]\d+)\s*\|(.*?)\|(.*?)\|", line)
        if m:
            wp = m.group(1)
            owner = {"C": "claude", "X": "codex", "J": "both"}[wp[0]]
            rows.append((wp, owner, m.group(2).strip(), m.group(3).strip()))
    return rows


def load_scope():
    return parse_scope(read_text(SCOPE))


def parse_handoff(text):
    """(done ids, reviews, resolved, questions); reviews/resolved/questions are (line_no, path, text)."""
    done, reviews, resolved, questions = set(), [], [], []
    for n, line in enumerate(text.splitlines(), 1):
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


def load_handoff():
    return parse_handoff(read_text(HANDOFF))


SECTION_RE = re.compile(r"\bsections?\s+([\w.-]*\w)", re.I)
LINE_REF_RE = re.compile(r"\b(?:HANDOFF(?:\.md)?(?:\s+line)?[:\s]+|line\s+)(\d+)\b", re.I)


def _section(text):
    m = SECTION_RE.search(text)
    return m.group(1).lower() if m else None


def resolve_items(reviews, questions, resolved):
    """Match each [resolved] line to ONE specific open review/question.

    A resolution names its target by `HANDOFF:<n>` / `line <n>` and/or `section <tok>` (the item's own section
    token). With neither, it closes the item only when exactly one earlier open item shares its path. Anything
    that does not pick exactly one item closes nothing and is returned as a problem, so disagreements stay open.
    Returns (open_reviews, open_questions, problems); problems are (resolved_line_no, message).
    """
    live = {it[0]: it for it in list(reviews) + list(questions)}
    problems = []
    for rn, rpath, rline in sorted(resolved):
        rest = rline.split(rpath, 1)[-1]
        earlier = [it for it in live.values() if it[0] < rn]
        same = [it for it in earlier if it[1] == rpath]
        lm = LINE_REF_RE.search(rest)
        if lm:
            target = live.get(int(lm.group(1)))
            if target is None or target[0] >= rn or target[1] != rpath:
                problems.append((rn, "[resolved] names HANDOFF:%s, which is not an open item on %s" % (lm.group(1), rpath)))
            else:
                del live[target[0]]
            continue
        sec = _section(rest)
        cands = [it for it in same if _section(it[2]) == sec] if sec else same
        if len(cands) == 1 and (sec or len(same) == 1):
            del live[cands[0][0]]
        elif not cands:
            problems.append((rn, "[resolved] %s%s matches no open item" % (rpath, " section " + sec if sec else "")))
        else:
            problems.append((rn, "[resolved] %s is ambiguous (open items at HANDOFF:%s); add `HANDOFF:<n>` or `section <tok>`"
                             % (rpath, ",".join(str(c[0]) for c in cands))))
    keep = lambda items: [it for it in items if it[0] in live]
    return keep(reviews), keep(questions), problems


def open_items(items, resolved):
    """Open subset of one kind of item after applying unique-target resolutions."""
    return resolve_items(items, [], resolved)[0]


def routed_to(item_path):
    """Agents an item on this path is shown to: the path's owner, or both agents for shared/unknown paths."""
    own = owner_of(item_path)
    return (own,) if own in AGENTS else AGENTS


def addressed_to(item_path):
    """A review/question on a path goes to that path's owner ('both' for shared paths)."""
    r = routed_to(item_path)
    return r[0] if len(r) == 1 else "both"


# which agents work each joint package when they have no owned WP open (unknown J ids go to both)
JOINT_ROUTES = {"J1": AGENTS, "J2": ("claude",), "J3": ("claude",)}


def cmd_status(_args):
    scope = load_scope()
    done, reviews, resolved, questions = load_handoff()
    open_rev, open_q, problems = resolve_items(reviews, questions, resolved)
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
        print("  HANDOFF:%d -> %s: %s" % (n, addressed_to(path), line[:110]))
    if problems:
        print("\nResolutions needing attention (%d)" % len(problems))
        for n, msg in problems:
            print("  HANDOFF:%d: %s" % (n, msg))
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


def build_next(agent, scope, done, open_rev, open_q, problems=()):
    """Lines of the paste-ready prompt for `agent` (pure: all inputs are parsed data)."""
    rev = [r for r in open_rev if agent in routed_to(r[1])]
    qs = [q for q in open_q if agent in routed_to(q[1])]
    lines = ["Read modding/SCOPE.md, modding/HANDOFF.md and AGENTS.md first. You are %s." % agent]
    if rev:
        lines.append("First resolve these review items (then append `[resolved] <path> HANDOFF:<line>: <what changed>`):")
        for n, _, text in rev:
            lines.append("  - HANDOFF line %d: %s" % (n, text))
    if qs:
        lines.append("Answer these open questions (then append `[resolved] <path> HANDOFF:<line>: <answer>`):")
        for n, _, text in qs:
            lines.append("  - HANDOFF line %d: %s" % (n, text))
    if problems:
        lines.append("Resolution lines needing attention:")
        for n, msg in problems:
            lines.append("  - HANDOFF line %d: %s" % (n, msg))
    todo = [r for r in scope if r[1] == agent and r[0] not in done]
    if todo:
        wp, _, pkg, out = todo[0]
        lines.append("Then do %s: %s" % (wp, pkg))
        lines.append("Output: %s" % out)
        lines.append("Verify 3 random claims against the game files, append `[done] %s ...; checked: ...` to "
                     "HANDOFF.md, run `python -I modding/tools/collab.py gates --agent %s`, then commit explicit "
                     "paths only. Do not push." % (wp, agent))
        return lines
    joint = [r for r in scope if r[1] == "both" and r[0] not in done and agent in JOINT_ROUTES.get(r[0], AGENTS)]
    if joint:
        wp, _, pkg, out = joint[0]
        lines.append("No owned work package is open. Joint package %s%s: %s" % (
            wp, " (shared by both agents)" if len(JOINT_ROUTES.get(wp, AGENTS)) > 1 else "", pkg))
        lines.append("Output: %s" % out)
        lines.append("Append `[done] %s ...` to HANDOFF.md when finished, run `python -I modding/tools/collab.py "
                     "gates --agent %s`, then commit explicit paths only. Do not push." % (wp, agent))
    elif not (rev or qs):
        lines.append("No owned or joint work package is open for you. Check HANDOFF.")
    return lines


def cmd_next(args):
    scope = load_scope()
    done, reviews, resolved, questions = load_handoff()
    open_rev, open_q, problems = resolve_items(reviews, questions, resolved)
    print("\n".join(build_next(args.agent, scope, done, open_rev, open_q, problems)))


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


def check_paths(paths, agent=None):
    """Per-path checks. Ownership comes from the path alone, so deleted paths are still owner-checked;
    only the content checks (header, links, CSV shape) need the file to exist."""
    res = Result()
    for rel in paths:
        if agent:
            own = owner_of(rel)
            if own not in (agent, "both"):
                res.add("FAIL", rel, "owned by %s, not %s" % (own, agent))
        if not (ROOT / rel).is_file():
            continue
        if rel.endswith(".md") and rel != "modding/HANDOFF.md":
            check_doc(rel, res)
        elif rel.endswith(".csv"):
            check_csv(rel, res)
    return res


def run_gates(paths, agent=None):
    res = check_paths(paths, agent)
    check_handoff(res)
    return res


def scope_paths(changed, agent, asked=()):
    """Split dirty paths for `gates --agent A`: (paths to check, other owners' paths to report as INFO).
    Checked = paths A owns (or 'both') plus any path A was explicitly asked about, even if another agent owns it."""
    asked = [p.replace("\\", "/") for p in asked]
    check = [p for p in changed if owner_of(p) in (agent, "both") or p in asked]
    check += [p for p in asked if p not in check]
    info = [p for p in changed if p not in check]
    return check, info


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
    info = []
    if args.all:
        paths = modding_files()
    else:
        changed = [p for p in changed_paths() if p.startswith(("modding/", "notes/", "README"))]
        asked = [p.replace("\\", "/") for p in args.paths]
        if args.agent:
            paths, info = scope_paths(changed, args.agent, asked)
        else:
            paths = changed + [p for p in asked if p not in changed]
    for p in info:
        print("INFO  %s: owned by %s, not checked for %s" % (p, owner_of(p), args.agent))
    res = run_gates(paths, args.agent)
    print("Checked %d file(s)%s" % (len(paths), " (all)" if args.all else " (uncommitted)"))
    sys.exit(report(res))


# ---------------------------------------------------------------- commit (shared index)

def git_retry(*args, tries=8):
    """git(), retrying with backoff while another process holds .git/index.lock."""
    delay = 0.1
    for attempt in range(tries):
        r = git(*args, check=False)
        if r.returncode == 0:
            return r
        if "index.lock" not in r.stderr or attempt == tries - 1:
            sys.exit("git %s failed: %s" % (" ".join(args), r.stderr.strip()))
        time.sleep(delay)
        delay = min(delay * 1.6, 2.0)


@contextmanager
def commit_lock(lock_path=None, timeout=30.0, stale=300.0):
    """Exclusive lockfile (O_EXCL) so only one collab.py stages/commits at a time. Stale locks are broken."""
    if lock_path is None:
        lock_path = Path(git("rev-parse", "--absolute-git-dir").stdout.strip()) / "collab.lock"
    deadline, delay = time.time() + timeout, 0.1
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            break
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(lock_path) > stale:
                    os.unlink(lock_path)
                    continue
            except OSError:
                continue
            if time.time() >= deadline:
                raise TimeoutError("could not acquire %s within %ds" % (lock_path, timeout))
            time.sleep(delay)
            delay = min(delay * 1.5, 1.0)
    try:
        yield
    finally:
        try:
            os.unlink(lock_path)
        except OSError:
            pass


def staged_names():
    out = git("diff", "--cached", "--name-only", "--no-renames", "-z").stdout
    return {p for p in out.split("\0") if p}


def staged_mismatch(staged, intended):
    """(extra, missing): staged paths that were not asked for, and asked-for paths that did not get staged."""
    staged, intended = set(staged), {p.replace("\\", "/") for p in intended}
    return sorted(staged - intended), sorted(intended - staged)


def commit_args(msg, paths):
    """git argv for the commit: explicit pathspec, so nothing else in the index can ride along."""
    return ["--literal-pathspecs", "commit", "-q", "-m", msg, "--", *paths]


def cmd_commit(args):
    if args.agent not in AGENTS:
        sys.exit("--agent must be claude or codex")
    if staged_names():
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
    try:
        with commit_lock():
            pre = staged_names()
            if pre:
                sys.exit("Something got staged meanwhile (%s); nothing done." % ", ".join(sorted(pre)))
            git_retry("--literal-pathspecs", "add", "--", *paths)
            extra, short = staged_mismatch(staged_names(), paths)
            if extra or short:
                git("--literal-pathspecs", "reset", "-q", "--", *paths, check=False)
                sys.exit("Staged set differs from the intended paths (unexpected: %s; not staged: %s); aborted, "
                         "my paths unstaged." % (", ".join(extra) or "-", ", ".join(short) or "-"))
            git_retry(*commit_args(msg, paths))
    except TimeoutError as e:
        sys.exit(str(e))
    print(git("log", "--oneline", "-n", "1").stdout.strip())


# ---------------------------------------------------------------- selftest

FIX_SCOPE = """
| C1 | claude pkg | out |
| X1 | codex pkg | out |
| J1 | joint one | out1 |
| J2 | cookbook | out2 |
| J3 | index | out3 |
"""
FIX_HANDOFF = """[done] C1 a
[done] X1 b
[review] modding/lua-library/a.md section 1: foo
[review] modding/lua-library/a.md section 2: bar
[resolved] modding/lua-library/a.md: fixed it
[review] modding/tools/shared.py section 3: baz
[question] modding/HANDOFF.md: why?
[resolved] modding/lua-library/a.md section 2: fixed
[review] modding/scripts/parser-keys.md section 8: cl
[resolved] modding/scripts/parser-keys.md: ok
[resolved] modding/lua-library/a.md HANDOFF:3: ok
"""


def cmd_selftest(_args):
    fails = []

    def check(name, ok, detail=""):
        print("%s  %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  (%s)" % detail))
        if not ok:
            fails.append(name)

    lines = FIX_HANDOFF.splitlines()
    scope = parse_scope(FIX_SCOPE)
    check("parse_scope: 5 rows, J rows owned by both",
          [r[0] for r in scope] == ["C1", "X1", "J1", "J2", "J3"] and scope[2][1] == "both", str(scope))
    done, rev, res_, qs = parse_handoff(FIX_HANDOFF)
    check("parse_handoff: done / reviews / resolved / questions",
          done == {"C1", "X1"} and [r[0] for r in rev] == [3, 4, 6, 9] and [r[0] for r in res_] == [5, 8, 10, 11]
          and [q[0] for q in qs] == [7], "%s %s %s %s" % (done, rev, res_, qs))
    check("owner_of: path decides (lua-api claude, lua-library codex, HANDOFF both)",
          owner_of("modding/lua-api/x.md") == "claude" and owner_of("modding/lua-library/x.md") == "codex"
          and owner_of("modding/HANDOFF.md") == "both")

    # D2: ownership of a path that no longer exists
    gone = "modding/lua-library/__selftest_deleted__.md"
    r = check_paths([gone], "claude")
    check("D2 deleted codex-owned path FAILs for claude", len(r.fail) == 1 and "owned by codex" in r.fail[0], str(r.fail))
    r = check_paths([gone, "modding/data/__selftest_deleted__.csv"], "codex")
    check("D2 deleted path owned by the named agent is not a failure", len(r.fail) == 0, str(r.fail))
    r = check_paths(["modding/data/events.csv.__selftest_deleted__"], None)
    check("D2 no --agent: missing file skipped, no failure", len(r.fail) == 0)

    # D3: a resolution closes exactly one specific item
    h5 = parse_handoff("\n".join(lines[:5]))
    o_rev, _, probs = resolve_items(h5[1], h5[3], h5[2])
    check("D3 unnamed [resolved] with 2 open items on the path closes neither and is reported ambiguous",
          [r[0] for r in o_rev] == [3, 4] and len(probs) == 1 and probs[0][0] == 5 and "ambiguous" in probs[0][1], str(probs))
    o_rev, o_q, probs = resolve_items(rev, qs, res_)
    check("D3 section/line-named and lone-item resolutions close their own item; unresolved items survive",
          [r[0] for r in o_rev] == [6] and [q[0] for q in o_q] == [7], "%s %s" % (o_rev, o_q))
    check("D3 ambiguous resolution still reported when the whole log is processed", [p[0] for p in probs] == [5], str(probs))
    wrong = parse_handoff("[review] modding/lua-library/a.md section 1: x\n[resolved] modding/tools/b.py HANDOFF:1: y")
    o_rev, _, probs = resolve_items(wrong[1], wrong[3], wrong[2])
    check("D3 line reference to an item on another path closes nothing", len(o_rev) == 1 and len(probs) == 1, str(probs))
    sec = parse_handoff("[review] modding/lua-library/a.md section 1: x\n[review] modding/lua-library/a.md section 2: y\n"
                        "[resolved] modding/lua-library/a.md section 9: z")
    o_rev, _, probs = resolve_items(sec[1], sec[3], sec[2])
    check("D3 section token matching no item closes nothing", len(o_rev) == 2 and len(probs) == 1, str(probs))

    # D5: routing of 'both' items, questions and joint packages
    pre = parse_handoff("\n".join(lines[:7]))
    o_rev, o_q, probs = resolve_items(pre[1], pre[3], pre[2])
    text = {a: "\n".join(build_next(a, scope, done, o_rev, o_q, probs)) for a in AGENTS}
    check("D5 'both' review (HANDOFF line 6) is routed to both agents",
          "HANDOFF line 6" in text["claude"] and "HANDOFF line 6" in text["codex"])
    check("D5 open [question] on a shared path is routed to both agents",
          "HANDOFF line 7" in text["claude"] and "HANDOFF line 7" in text["codex"])
    check("D5 codex-owned review goes to codex only",
          "HANDOFF line 3" in text["codex"] and "HANDOFF line 3" not in text["claude"])
    check("D5 routed_to: shared/unknown path -> both, owned path -> owner",
          routed_to("modding/tools/zzz.py") == AGENTS and routed_to("modding/lua-api/a.md") == ("claude",))
    check("D5 next with no owned WP offers J1 to both agents", "Joint package J1" in text["claude"] and "Joint package J1" in text["codex"])
    d1 = done | {"J1"}
    t_c = "\n".join(build_next("claude", scope, d1, [], [], []))
    t_x = "\n".join(build_next("codex", scope, d1, [], [], []))
    check("D5 after J1: J2 goes to claude, codex has nothing", "Joint package J2" in t_c and "Joint package" not in t_x, t_c + "|" + t_x)
    t_c = "\n".join(build_next("claude", scope, d1 | {"J2"}, [], [], []))
    check("D5 J3 goes to claude", "Joint package J3" in t_c)
    t_own = "\n".join(build_next("codex", scope, {"C1"}, [], [], []))
    check("D5 owned WP still takes precedence over joint packages", "Then do X1" in t_own and "Joint package" not in t_own)

    # D4: other agents' dirty paths are INFO for --agent, never FAIL
    changed = ["modding/lua-api/x.md", "modding/lua-library/y.md", "modding/tools/z.py", "notes/n.md"]
    chk, info = scope_paths(changed, "codex")
    check("D4 codex scope = codex-owned + shared; claude WIP goes to INFO",
          chk == ["modding/lua-library/y.md", "modding/tools/z.py"] and info == ["modding/lua-api/x.md", "notes/n.md"], "%s %s" % (chk, info))
    check("D4 checking the scoped set yields no FAIL", len(check_paths(chk, "codex").fail) == 0)
    chk, info = scope_paths(changed, "codex", ["modding/lua-api/x.md"])
    check("D4 an explicitly asked other-owner path is still checked and FAILs",
          "modding/lua-api/x.md" in chk and len(check_paths(chk, "codex").fail) == 1)
    chk, info = scope_paths(changed, "claude")
    check("D4 claude scope excludes codex-owned file", "modding/lua-library/y.md" in info and "modding/lua-api/x.md" in chk)

    # D1: intended-set verification, pathspec commit, lock
    extra, short = staged_mismatch({"a.md", "b.md"}, ["a.md"])
    check("D1 staged_mismatch flags a path staged by someone else", extra == ["b.md"] and short == [])
    extra, short = staged_mismatch({"a.md"}, ["a.md", "c.md"])
    check("D1 staged_mismatch flags an intended path that was not staged", extra == [] and short == ["c.md"])
    check("D1 staged_mismatch passes on an exact match", staged_mismatch({"a.md", "b.md"}, ["b.md", "a.md"]) == ([], []))
    argv = commit_args("m", ["p1", "p2"])
    check("D1 commit argv ends with `-- <paths>` (explicit pathspec)", argv[-3:] == ["--", "p1", "p2"] and "-a" not in argv, str(argv))
    with tempfile.TemporaryDirectory() as td:
        lk = Path(td) / "collab.lock"
        ok_block = False
        with commit_lock(lk):
            try:
                with commit_lock(lk, timeout=0.3):
                    pass
            except TimeoutError:
                ok_block = True
        check("D1 second locker is blocked while the lock is held", ok_block)
        check("D1 lock released afterwards", not lk.exists())
        lk.write_text("999")
        os.utime(lk, (time.time() - 1000, time.time() - 1000))
        with commit_lock(lk, timeout=0.3, stale=10):
            pass
        check("D1 stale lock is broken", not lk.exists())

    print("\n%d check(s) failed" % len(fails) if fails else "\nall checks passed")
    sys.exit(1 if fails else 0)


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
    p.add_argument("paths", nargs="*", help="extra paths to check even if another agent owns them")
    p.set_defaults(fn=cmd_gates)
    p = sub.add_parser("commit")
    p.add_argument("--agent", required=True)
    p.add_argument("--wp", required=True)
    p.add_argument("--message", required=True)
    p.add_argument("--yes", action="store_true")
    p.add_argument("paths", nargs="+")
    p.set_defaults(fn=cmd_commit)
    sub.add_parser("selftest").set_defaults(fn=cmd_selftest)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
