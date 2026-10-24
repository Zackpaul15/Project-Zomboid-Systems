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
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import contextmanager, redirect_stdout
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

def git_retry(*args, tries=8, fatal=True):
    """git(), retrying with backoff while another process holds .git/index.lock.
    On final failure: exit (fatal) or return the failed result (fatal=False) so the caller can report it."""
    delay = 0.1
    for attempt in range(tries):
        r = git(*args, check=False)
        if r.returncode == 0:
            return r
        if "index.lock" not in r.stderr or attempt == tries - 1:
            if not fatal:
                return r
            sys.exit("git %s failed: %s" % (" ".join(args), r.stderr.strip()))
        time.sleep(delay)
        delay = min(delay * 1.6, 2.0)


ALIVE, DEAD, UNKNOWN = "alive", "dead", "unknown"  # pid liveness; only DEAD authorises breaking a lock


class _Win32:
    """kernel32 with explicit ctypes signatures (OpenProcess returns a HANDLE, not the default c_int)."""

    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self._ct = ctypes
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k.OpenProcess.restype = wintypes.HANDLE
        k.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        k.GetExitCodeProcess.restype = wintypes.BOOL
        k.CloseHandle.argtypes = [wintypes.HANDLE]
        k.CloseHandle.restype = wintypes.BOOL
        self._k, self._dword = k, wintypes.DWORD

    def open(self, pid):  # PROCESS_QUERY_LIMITED_INFORMATION; falsy on failure
        return self._k.OpenProcess(0x1000, False, pid)

    def last_error(self):
        return self._ct.get_last_error()

    def exit_code(self, h):  # None when the query itself failed
        code = self._dword()
        return code.value if self._k.GetExitCodeProcess(h, self._ct.byref(code)) else None

    def close(self, h):
        self._k.CloseHandle(h)


def _win_liveness(pid, api):
    """Tri-state liveness through an injectable Win32 adapter. Any failure that is not a definite answer is UNKNOWN."""
    try:
        h = api.open(pid)
        if not h:
            err = api.last_error()
            if err == 87:  # ERROR_INVALID_PARAMETER: no such process
                return DEAD
            return ALIVE if err == 5 else UNKNOWN  # access denied: it exists; anything else: cannot tell
        try:
            code = api.exit_code(h)
        finally:
            try:
                api.close(h)
            except Exception:
                pass
        if code is None:
            return UNKNOWN
        return ALIVE if code == 259 else DEAD  # STILL_ACTIVE
    except Exception:
        return UNKNOWN


def pid_alive(pid):
    """ALIVE / DEAD / UNKNOWN for `pid`; DEAD only on a definite "no such process". Injectable (module global)."""
    if pid <= 0:
        return DEAD
    if sys.platform == "win32":  # os.kill(pid, 0) would TerminateProcess on Windows, so query the handle instead
        try:
            return _win_liveness(pid, _Win32())
        except Exception:
            return UNKNOWN
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return DEAD
    except PermissionError:
        return ALIVE
    except OSError:
        return UNKNOWN
    return ALIVE


def _read_lock(lock_path):
    """(pid, token) from a lock file, or None when unreadable / not in `pid token` form."""
    try:
        parts = Path(lock_path).read_text().split()
        return int(parts[0]), parts[1]
    except (OSError, ValueError, IndexError):
        return None


def _observe_lock(lock_path):
    """Snapshot of an existing lock: (raw text, mtime_ns, parsed (pid, token) or None). OSError if it vanished."""
    st = os.stat(lock_path)
    raw = Path(lock_path).read_text()
    return raw, st.st_mtime_ns, _read_lock(lock_path)


def _claim_path(lock_path, observed):
    """Recovery claim name unique to one observed dead lock (its text carries a never-reused token; an
    unparseable lock is keyed by text + mtime instead)."""
    raw, mtime_ns, parsed = observed
    key = raw if parsed else "%s@%d" % (raw, mtime_ns)
    return "%s.recover.%s" % (lock_path, hashlib.sha1(key.encode()).hexdigest()[:16])


def _break_stale(lock_path, observed):
    """Atomically recover a lock that was observed dead. Returns True if it was removed by us, False if we must
    back off (someone else is recovering it, or it is no longer the lock we observed).
    Mutual exclusion is an O_EXCL claim file named after the observed lock's unique token: for a given dead lock
    only one contender can ever create the claim. Under the claim we re-validate the lock is still byte-identical
    to the observation and only then unlink it. The lock path cannot change under a claimant: its dead owner will
    never release it, other recoverers of this observation are excluded, and new owners cannot create the path
    while it exists. A contender holding a stale observation therefore either loses the claim or fails validation,
    so it can never unlink a lock it did not observe (the check-then-act race). A claimant that crashes inside the
    microsecond validate+unlink leaves the claim behind: acquirers then time out with a message naming the file."""
    claim = _claim_path(lock_path, observed)
    try:
        os.close(os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        return False
    try:
        try:
            if _observe_lock(lock_path)[:2] != observed[:2]:
                return False
        except OSError:
            return False
        os.unlink(lock_path)
        return True
    finally:
        try:
            os.unlink(claim)
        except OSError:
            pass


@contextmanager
def commit_lock(lock_path=None, timeout=30.0, stale=300.0):
    """Exclusive lockfile (O_EXCL) so only one collab.py stages/commits at a time.
    The file holds `<pid> <token>`. A lock is broken only when its owner pid is DEAD (tri-state pid_alive: ALIVE
    and UNKNOWN both preserve it); age alone never breaks it (a slow hook is not a dead owner). `stale` applies
    only to a lock whose content cannot be parsed (e.g. owner crashed between create and write). Breaking goes
    through _break_stale (atomic). PID reuse errs on the safe side: the lock then looks alive and we wait/time out.
    The holder unlinks the lock only if the token is still its own."""
    if lock_path is None:
        lock_path = Path(git("rev-parse", "--absolute-git-dir").stdout.strip()) / "collab.lock"
    token = uuid.uuid4().hex
    mine = "%d %s" % (os.getpid(), token)
    deadline, delay = time.time() + timeout, 0.1
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, mine.encode())
            os.close(fd)
            break
        except FileExistsError:
            try:
                observed = _observe_lock(lock_path)
                if observed[2] is None:
                    dead = time.time() - observed[1] / 1e9 > stale
                else:
                    dead = pid_alive(observed[2][0]) == DEAD
                if dead and _break_stale(lock_path, observed):
                    continue
            except OSError:
                continue
            if time.time() >= deadline:
                raise TimeoutError("could not acquire %s within %ds (if no collab.py is running, remove it and any "
                                   "%s.recover.* file)" % (lock_path, timeout, lock_path))
            time.sleep(delay)
            delay = min(delay * 1.5, 1.0)
    try:
        yield
    finally:
        try:
            if _read_lock(lock_path) == (os.getpid(), token):
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
                what = "unexpected: %s; not staged: %s" % (", ".join(extra) or "-", ", ".join(short) or "-")
                r = git_retry("--literal-pathspecs", "reset", "-q", "--", *paths, fatal=False)
                if r.returncode == 0:
                    sys.exit("Staged set differs from the intended paths (%s); aborted, my paths unstaged." % what)
                sys.exit("Staged set differs from the intended paths (%s); aborted, but UNSTAGING FAILED (%s). "
                         "My paths may still be staged: run `git reset -q -- <paths>` before anything else."
                         % (what, r.stderr.strip()))
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


class FakeGit:
    """In-memory stand-in for git() used by the selftest; never touches a repo, index or network."""

    def __init__(self, foreign=None, add_lock_fails=0, reset_fail=False, reset_lock_fails=0, commit_raises=False):
        self.index, self.foreign = set(), foreign
        self.add_lock_fails, self.reset_fail, self.reset_lock_fails = add_lock_fails, reset_fail, reset_lock_fails
        self.commit_raises = commit_raises
        self.commits, self.resets, self.mutations, self.add_calls = [], [], [], 0
        self.lock_file, self.lock_seen = None, []  # lock_seen: was the lock file present during each mutation?

    def _mutating(self):
        self.lock_seen.append(self.lock_file is not None and self.lock_file.exists())

    @staticmethod
    def _r(rc=0, out="", err=""):
        return subprocess.CompletedProcess([], rc, out, err)

    def __call__(self, *args, check=True):
        a = [x for x in args if x != "--literal-pathspecs"]
        paths = a[a.index("--") + 1:] if "--" in a else []
        if a[:2] == ["diff", "--cached"]:
            return self._r(out="\0".join(sorted(self.index)))
        if a[0] == "add":
            self.add_calls += 1
            if self.add_lock_fails > 0:
                self.add_lock_fails -= 1
                return self._r(128, err="fatal: Unable to create '.git/index.lock': File exists.")
            self._mutating()
            self.mutations.append(a)
            self.index |= set(paths) | ({self.foreign} if self.foreign else set())
            return self._r()
        if a[0] == "reset":
            if self.reset_lock_fails > 0:
                self.reset_lock_fails -= 1
                return self._r(128, err="Unable to create '.git/index.lock'")
            if self.reset_fail:
                return self._r(1, err="fatal: reset exploded")
            self._mutating()
            self.mutations.append(a)
            self.resets.append(paths)
            self.index -= set(paths)
            return self._r()
        if a[0] == "commit":
            self._mutating()
            if self.commit_raises:
                raise RuntimeError("commit blew up")
            self.mutations.append(a)
            self.commits.append(list(args))
            self.index -= set(paths)
            return self._r()
        if a[0] == "log":
            return self._r(out="abc1234 fake")
        raise AssertionError("unexpected git call: %r" % (args,))


@contextmanager
def patched(**names):
    """Temporarily replace module-level names (git, changed_paths, pid_alive, ...) and time.sleep."""
    g, saved, sleep = globals(), {}, time.sleep
    for k, v in names.items():
        saved[k] = g[k]
        g[k] = v
    time.sleep = lambda _s: None
    try:
        yield
    finally:
        time.sleep = sleep
        g.update(saved)


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

        # R1-1: liveness (injected pid_alive), never age, decides whether a lock is broken
        old = time.time() - 100000
        lk.write_text("4242 tok")
        os.utime(lk, (old, old))
        with patched(pid_alive=lambda pid: DEAD):
            with commit_lock(lk, timeout=0.3):
                pass
        check("R1-1 lock of a dead owner is broken", not lk.exists())
        for state in (ALIVE, UNKNOWN):
            lk.write_text("4242 tok")
            os.utime(lk, (old, old))
            blocked = False
            with patched(pid_alive=lambda pid: state):
                try:
                    with commit_lock(lk, timeout=0.3):
                        pass
                except TimeoutError:
                    blocked = True
            check("R1-1/R2-2 very old lock of an owner that is %s is not broken" % state,
                  blocked and lk.exists() and lk.read_text() == "4242 tok")
        lk.unlink()
        with commit_lock(lk):
            lk.write_text("4242 other-token")  # someone else's lock replaced ours
        check("R1-1 holder never unlinks another invocation's lock", lk.exists() and lk.read_text() == "4242 other-token")
        lk.unlink()
        try:
            with commit_lock(lk):
                raise RuntimeError("body failed")
        except RuntimeError:
            pass
        check("R1-3c lock is released when the body raises", not lk.exists())
        check("R1-1 pid_alive: this process is ALIVE, pid 0 is DEAD",
              pid_alive(os.getpid()) == ALIVE and pid_alive(0) == DEAD)

        # R2-1: stale-lock recovery is atomic; interleavings are driven explicitly, no timing involved
        lk.write_text("4242 D-token")
        d_obs = _observe_lock(lk)  # both A and B observed dead lock D
        b_obs = _observe_lock(lk)
        with patched(pid_alive=lambda pid: DEAD):
            with commit_lock(lk, timeout=0.3):  # A recovers D and enters the protected body
                a_text = lk.read_text()
                b_unlinked = _break_stale(lk, b_obs)  # B resumes with its stale observation
                still_a = lk.exists() and lk.read_text() == a_text
        check("R2-1 a recoverer holding a stale observation cannot unlink the lock that replaced it",
              not b_unlinked and still_a and a_text.split()[1] != "D-token")
        lk.write_text("4242 D-token")
        obs = _observe_lock(lk)
        claim = Path(_claim_path(lk, obs))
        claim.write_text("")  # contender A is mid-recovery of exactly this lock
        lost = _break_stale(lk, obs)
        check("R2-1 a second recoverer of the same dead lock loses the claim and backs off",
              lost is False and lk.exists() and claim.exists())
        claim.unlink()
        won = _break_stale(lk, obs)
        check("R2-1 the claim winner removes the lock and its claim file", won is True and not lk.exists() and not claim.exists())
        lk.write_text("4242 D-token")
        obs = _observe_lock(lk)
        lk.write_text("4242 D-token")
        os.utime(lk, ns=(obs[1] + 10**9, obs[1] + 10**9))  # same text, different file instance
        check("R2-1 a lock that changed since observation is not removed",
              _break_stale(lk, obs) is False and lk.exists() and not claim.exists())
        lk.unlink()

        # R2-2: tri-state liveness and Win32 failure branches via injected API results
        class W32:
            def __init__(self, handle=1, err=0, code=259, query_raises=False, close_raises=False):
                self.handle, self.err, self.code, self.query_raises, self.close_raises = handle, err, code, query_raises, close_raises
                self.closed = []

            def open(self, pid):
                return self.handle

            def last_error(self):
                return self.err

            def exit_code(self, h):
                if self.query_raises:
                    raise OSError("boom")
                return self.code

            def close(self, h):
                self.closed.append(h)
                if self.close_raises:
                    raise OSError("close boom")

        w = W32(handle=0, err=87)
        check("R2-2 OpenProcess ERROR_INVALID_PARAMETER -> DEAD", _win_liveness(9, w) == DEAD)
        check("R2-2 OpenProcess access denied -> ALIVE", _win_liveness(9, W32(handle=0, err=5)) == ALIVE)
        check("R2-2 OpenProcess any other error -> UNKNOWN (not DEAD)",
              all(_win_liveness(9, W32(handle=0, err=e)) == UNKNOWN for e in (0, 6, 1450, 8)))
        w = W32(code=None)
        check("R2-2 failed GetExitCodeProcess -> UNKNOWN, handle closed", _win_liveness(9, w) == UNKNOWN and w.closed == [1])
        w = W32(query_raises=True)
        check("R2-2 exception while querying -> UNKNOWN, handle still closed", _win_liveness(9, w) == UNKNOWN and w.closed == [1])
        w = W32(code=259)
        check("R2-2 STILL_ACTIVE -> ALIVE, handle closed", _win_liveness(9, w) == ALIVE and w.closed == [1])
        w = W32(code=0)
        check("R2-2 exited process -> DEAD, handle closed", _win_liveness(9, w) == DEAD and w.closed == [1])
        check("R2-2 CloseHandle failure does not change the answer", _win_liveness(9, W32(code=0, close_raises=True)) == DEAD)
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes
            k = _Win32()._k
            check("R2-2 Win32 signatures are declared (HANDLE restype, DWORD/BOOL/HANDLE argtypes)",
                  k.OpenProcess.restype is wintypes.HANDLE
                  and k.OpenProcess.argtypes == [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
                  and k.GetExitCodeProcess.argtypes == [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
                  and k.GetExitCodeProcess.restype is wintypes.BOOL
                  and k.CloseHandle.argtypes == [wintypes.HANDLE] and k.CloseHandle.restype is wintypes.BOOL)

    # R1-3: drive the real cmd_commit / cmd_gates / git_retry through an in-memory fake git
    with tempfile.TemporaryDirectory() as td:
        lk = Path(td) / "collab.lock"
        real_lock = commit_lock
        fake_done = ({"M1F"}, [], [], [])
        no_gates = lambda ps, ag=None: check_paths([], ag)

        def run_commit(fg, yes=True, paths=("modding/lua-api/a.md", "modding/lua-api/b.md")):
            fg.lock_file = lk
            a =argparse.Namespace(agent="claude", wp="M1F", message="msg", yes=yes, paths=list(paths))
            out, code = io.StringIO(), None
            with patched(git=fg, changed_paths=lambda: list(paths), load_handoff=lambda: fake_done,
                         run_gates=no_gates, commit_lock=lambda: real_lock(lk, timeout=0.3)), redirect_stdout(out):
                try:
                    cmd_commit(a)
                except SystemExit as e:
                    code = e.code
            return code, out.getvalue()

        both = ["modding/lua-api/a.md", "modding/lua-api/b.md"]
        fg = FakeGit()
        code, _ = run_commit(fg)
        argv = fg.commits[0] if fg.commits else []
        check("R1-3a cmd_commit stages then commits with explicit `-- <paths>` pathspec",
              code is None and len(fg.commits) == 1 and argv[-3:] == ["--"] + both
              and "--literal-pathspecs" in argv and "-a" not in argv and not lk.exists(), "%s %s" % (code, argv))
        fg = FakeGit()
        run_commit(fg, yes=False)
        check("R1-3a dry run touches nothing", not fg.mutations)

        theirs = "modding/lua-library/theirs.md"
        fg = FakeGit(foreign=theirs)
        code, _ = run_commit(fg)
        check("R1-3b foreign staged path aborts, no commit, only my paths unstaged",
              isinstance(code, str) and "paths unstaged" in code and not fg.commits
              and fg.resets == [both] and fg.index == {theirs} and not lk.exists(), "%s %s" % (code, fg.index))
        fg = FakeGit(foreign=theirs, reset_fail=True)
        code, _ = run_commit(fg)
        check("R1-2 failed rollback is reported, not claimed as unstaged; lock released",
              isinstance(code, str) and "UNSTAGING FAILED" in code and "paths unstaged" not in code
              and not fg.commits and not lk.exists(), str(code))
        fg = FakeGit(foreign=theirs, reset_lock_fails=2)
        code, _ = run_commit(fg)
        check("R1-2 rollback reset is retried through index.lock contention",
              isinstance(code, str) and "paths unstaged" in code and fg.index == {theirs}, str(code))

        fg = FakeGit(add_lock_fails=3)
        code, _ = run_commit(fg)
        check("R1-3d index.lock contention is retried (add failed 3x, then commit succeeded)",
              code is None and fg.add_calls == 4 and len(fg.commits) == 1, "%s %s" % (code, fg.add_calls))
        fg = FakeGit(add_lock_fails=99)
        code, _ = run_commit(fg)
        check("R1-3d persistent index.lock gives up with an error and no commit",
              isinstance(code, str) and "index.lock" in code and not fg.commits and not lk.exists(), str(code))
        fg = FakeGit(commit_raises=True)
        raised = False
        try:
            run_commit(fg)
        except RuntimeError:
            raised = True
        check("R1-3c lock released when git commit raises mid-body (and the injected exception was observed)",
              raised and fg.lock_seen and all(fg.lock_seen) and not lk.exists(), "%s %s" % (raised, fg.lock_seen))
        fg = FakeGit()
        run_commit(fg)
        check("R2-3 the lock file exists during every mutation (add and commit)",
              len(fg.lock_seen) == 2 and all(fg.lock_seen), str(fg.lock_seen))
        fg = FakeGit(foreign=theirs)
        run_commit(fg)
        check("R2-3 the lock file exists during add and the rollback reset too",
              len(fg.lock_seen) == 2 and all(fg.lock_seen), str(fg.lock_seen))
        lk.write_text("4242 other-holder")
        fg = FakeGit()
        with patched(pid_alive=lambda pid: ALIVE):
            code, _ = run_commit(fg)
        check("R2-3 cmd_commit cannot mutate while another holder owns the lock",
              isinstance(code, str) and "could not acquire" in code and not fg.mutations and not fg.add_calls
              and lk.exists() and lk.read_text() == "4242 other-holder", "%s %s" % (code, fg.mutations))
        lk.unlink()

    seen = []
    dirty = ["modding/lua-api/x.md", "modding/lua-library/y.md", "modding/tools/z.py"]
    spy = lambda ps, ag=None: seen.append(list(ps)) or check_paths([], ag)
    with patched(changed_paths=lambda: dirty, run_gates=spy), redirect_stdout(io.StringIO()):
        for ns in (argparse.Namespace(agent="codex", all=False, paths=[]),
                   argparse.Namespace(agent=None, all=False, paths=[])):
            try:
                cmd_gates(ns)
            except SystemExit:
                pass
    check("R1-3e cmd_gates --agent applies scope_paths (other agent's WIP not checked)",
          seen[:1] == [["modding/lua-library/y.md", "modding/tools/z.py"]], str(seen))
    check("R1-3e cmd_gates without --agent checks every dirty path", len(seen) == 2 and seen[1] == dirty, str(seen))

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
