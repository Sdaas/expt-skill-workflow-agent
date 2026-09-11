#!/usr/bin/env python3
"""PreToolUse guard hook for /implement-feature.

Does six jobs on every Read/Bash/Grep/Glob/Edit/Write (conductor AND every subagent):
  1. AUDIT  — append one JSONL line per tool call (agent_id/agent_type/tool/target).
  2. SECRETS GUARDRAIL — deny reads of .env / keys / credentials for ANY agent.
  3. ALGORITHM-BLIND — deny reads of design-internal for the test-writer agent only.
  3b. DRAFT-CONFINEMENT — deny ANY subagent reading anything under handoff/draft/ (an
     unapproved draft must never reach an isolated gate; the conductor promotes on
     approval, and only then is a file readable at handoff/).
  4. TEST-INTEGRITY — deny the implementer editing/writing any test file (it must make
     the code pass the tests, never weaken the tests to pass).
  5. REVIEWER-CONFINEMENT — deny the test-reviewer any write (Write/Edit or a Bash
     redirection) outside its handoff/ outbox and a scratch dir; it is an analytical
     critic and must never mutate the product tree (build no reference implementation).

Reads the hook JSON on stdin. To DENY: print a hookSpecificOutput deny decision and
exit 2. To ALLOW: exit 0.

Run-log resolution (hooks are separate processes and do NOT inherit the conductor's
exported env, hence the pointer file rather than an env var):
  1. $IF_RUNLOG (explicit override), else
  2. the pointer file $CLAUDE_PROJECT_DIR/.implement-feature/.active-run — its contents
     are the active <artifact_dir>; the run-log is <artifact_dir>/handoff/run-log.jsonl, else
  3. today's fallback $CLAUDE_PROJECT_DIR/if-runlog.jsonl, else
  4. /tmp/if-runlog.jsonl.
"""
import json, os, re, sys, datetime, shlex

def _active_run_runlog():
    """Resolve the run-log from the .active-run pointer file, if present/usable."""
    proj = os.environ.get("CLAUDE_PROJECT_DIR")
    if not proj:
        return None
    pointer = os.path.join(proj, ".implement-feature", ".active-run")
    try:
        workdir = open(pointer, encoding="utf-8").read().strip()
    except OSError:
        return None
    if not workdir:
        return None
    return os.path.join(workdir, "handoff", "run-log.jsonl")

def runlog_path():
    return (os.environ.get("IF_RUNLOG")
            or _active_run_runlog()
            or (os.path.join(os.environ["CLAUDE_PROJECT_DIR"], "if-runlog.jsonl")
                if os.environ.get("CLAUDE_PROJECT_DIR") else None)
            or "/tmp/if-runlog.jsonl")

# --- secret detection (PATH-aware, not raw-substring) ----------------------
# KEEP IN SYNC with analyzer/runlog.py (the detective mirror of this predicate).
#
# #16: the old code substring-matched these hints against the tool's whole target.
# For a Bash call the target is the ENTIRE command string, so a benign command like
# `python -c "os.environ.get('X')"` tripped the `.env` hint (".env" is inside
# "os.environ"). Fix: match on PATH COMPONENTS, and for Bash scan tokens that actually
# look like file paths — never the raw command body.
_SECRET_EXTS = (".pem", ".key")                       # matched as a component suffix
_SECRET_NAMES = ("id_rsa", "id_ed25519", "credentials", ".netrc", ".pgpass")  # in a component
_SECRET_FRAGMENTS = (".ssh/", ".aws/credentials")     # matched anywhere in the path

def _is_secret_component(comp: str) -> bool:
    return (comp == ".env" or comp.startswith(".env.")
            or comp.startswith("secrets.")
            or comp.endswith(_SECRET_EXTS)
            or any(n in comp for n in _SECRET_NAMES))

def _is_secret_path(target: str) -> bool:
    """True if `target`, read as a filesystem path, points at a secret. Over-broad on
    purpose for real file targets (a false positive just makes an agent ask again)."""
    t = target.strip().strip("'\"").lower().replace("\\", "/")
    if not t:
        return False
    if any(frag in t for frag in _SECRET_FRAGMENTS):
        return True
    return any(_is_secret_component(c) for c in t.split("/") if c)

def _bash_token_is_secret(token: str) -> bool:
    """Stricter than _is_secret_path: only flag a Bash token that clearly denotes a
    secret FILE (a path, a dotfile, or a secret extension). A bare identifier like
    `environ` or `credentials` in a command is NOT a file read — don't false-deny it."""
    t = token.strip().strip("'\"").lower().replace("\\", "/")
    if not t:
        return False
    pathlike = ("/" in t) or t.startswith(".") or t.endswith(_SECRET_EXTS)
    return pathlike and _is_secret_path(t)

def _bash_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        return command.split()  # unbalanced quotes (common in code heredocs): degrade safely

def looks_secret(tool: str, target: str) -> bool:
    """Secret-read predicate, split by tool. Bash scans path-like tokens (never the raw
    command body, #16); every other tool's target IS a path -> path-component match."""
    if tool == "Bash":
        return any(_bash_token_is_secret(tok) for tok in _bash_tokens(target))
    return _is_secret_path(target)

READISH = {"Read", "Bash", "Grep", "Glob"}
WRITEISH = {"Write", "Edit", "NotebookEdit"}

def is_test_path(target: str) -> bool:
    base = os.path.basename(target)
    return ("/tests/" in target or "/test/" in target
            or base.startswith("test_") or base.endswith("_test.py")
            or base == "conftest.py")

# --- test-reviewer write-confinement (#12) ---------------------------------
# A Bash-granted critic can't be made read-only by removing Write/Edit (P44), so we
# enforce the property we actually want: the test-reviewer NEVER mutates the product
# tree. Its only sanctioned writes are its outbox (under handoff/) and throwaway probes
# in a scratch/temp dir. Everything else — the repo's src/tests — is denied.
def _is_scratch_path(t: str) -> bool:
    return ("/tmp/" in t or t.startswith("/tmp") or "/private/tmp/" in t
            or "/var/folders/" in t or "scratchpad" in t or "/scratch/" in t)

def reviewer_write_denied(target: str) -> bool:
    """True if the test-reviewer must NOT write here (i.e. not its outbox/scratchpad)."""
    t = target.strip().strip("'\"").replace("\\", "/")
    if not t:
        return False
    if t.startswith("/dev/"):
        return False   # /dev/null etc. are the bit bucket, not the product tree
    if "/handoff/" in t or t.startswith("handoff/"):
        return False   # its named outbox (06-test-review-findings.md) lives under handoff/
    if _is_scratch_path(t):
        return False   # tiny throwaway probes are legitimate (P45)
    return True        # anything else = the product tree / repo -> denied

# Heredoc start: `<<`, optional `-`, optional ws, optional quote, delimiter word.
_HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

def _strip_heredocs(command: str) -> str:
    """Drop heredoc *bodies* so their literal text (e.g. markdown `>` blockquotes) is never
    mistaken for shell redirections. The `cmd > file <<EOF` redirection sits OUTSIDE the
    body and is preserved. KEEP IN SYNC with analyzer/runlog.py."""
    lines = command.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        m = _HEREDOC_RE.search(lines[i])
        i += 1
        if m:
            delim = m.group(2)
            while i < len(lines) and lines[i].strip() != delim:
                i += 1
            i += 1  # consume the terminator line (not a command)
    return "\n".join(out)

def bash_write_targets(command: str) -> list[str]:
    """Best-effort: the paths a Bash command redirects/writes into (`>`, `>>`, `tee`).
    Bash write-detection is inherently fragile (P44) — key on the targets we can see."""
    toks = _bash_tokens(_strip_heredocs(command))
    targets: list[str] = []
    for i, tok in enumerate(toks):
        stripped = tok.lstrip("012")  # 1>, 2>> ...
        if stripped in (">", ">>", ">|") and i + 1 < len(toks):
            targets.append(toks[i + 1])
        elif stripped.startswith(">") and len(stripped) > 1:
            targets.append(stripped.lstrip(">|"))   # `>file` with no space
        elif tok == "tee" and i + 1 < len(toks):
            nxt = toks[i + 1]
            targets.append(nxt if not nxt.startswith("-") else (toks[i + 2] if i + 2 < len(toks) else ""))
    # Drop fd-duplication targets (`2>&1`, `>&2`, ...): `&N` is a file descriptor, not a
    # file write — parsing it as one false-flagged a reviewer's `pytest ... 2>&1`.
    return [t for t in targets if t and not t.startswith("&")]

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # never break the tool on a parse error

    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}
    agent_type = str(data.get("agent_type") or "")
    agent_id = str(data.get("agent_id") or "")
    target = str(ti.get("file_path") or ti.get("path") or ti.get("command")
                 or ti.get("pattern") or "")

    # 1. AUDIT (best-effort; never fail the tool because of logging)
    try:
        with open(runlog_path(), "a") as f:
            f.write(json.dumps({
                # UTC + tz-aware ("…+00:00") on purpose: the observability analyzer
                # correlates this run-log against the Claude Code session transcript
                # (which stamps UTC/"Z"). A naive local time would be off by the tz
                # offset and break the time-window match. See analyzer/transcript.py.
                "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                "agent_type": agent_type, "agent_id": agent_id,
                "tool": tool, "target": target[:300],
            }) + "\n")
    except Exception:
        pass

    def deny(reason):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }}))
        sys.exit(2)

    # 2. SECRETS GUARDRAIL — any agent, read-ish tools
    if tool in READISH and looks_secret(tool, target):
        deny(f"Blocked by implement-feature guard: reading secrets/.env is not allowed "
             f"(target: {os.path.basename(target) or target[:60]}).")

    # 3. ALGORITHM-BLIND — only the test-writer is denied design-internal
    #    (substring match is prefix-tolerant: "03-design-internal.md" still trips it).
    if "test-writer" in agent_type and "design-internal" in target:
        deny("Blocked by implement-feature guard: the test-writer is algorithm-blind and "
             "must not read design-internal.md.")

    # 3b. DRAFT-CONFINEMENT — no subagent may read an unapproved draft. Only the
    #     conductor (empty agent_type) authors/reviews drafts; a subagent seeing
    #     handoff/draft/ means an unpromoted artifact is leaking into an isolated gate.
    if agent_type and tool in READISH and "handoff/draft/" in target.replace("\\", "/"):
        deny("Blocked by implement-feature guard: handoff/draft/ holds unapproved drafts. "
             "Subagents read only promoted files under handoff/. (Conductor promotes on approval.)")

    # 4. TEST-INTEGRITY — the implementer may not edit/write test files
    if "implementer" in agent_type and tool in WRITEISH and is_test_path(target):
        deny("Blocked by implement-feature guard: the implementer must make the code pass "
             "the tests, not modify the tests. Editing test files is not allowed.")

    # 5. REVIEWER-CONFINEMENT (#12) — the test-reviewer never mutates the product tree.
    #    Sanctioned writes: its handoff/ outbox and throwaway probes in a scratch dir.
    if "test-reviewer" in agent_type:
        if tool in WRITEISH and reviewer_write_denied(target):
            deny("Blocked by implement-feature guard: the test-reviewer is an analytical "
                 "critic — it may write only its handoff/ findings outbox and throwaway "
                 f"probes in a scratch dir, never the product tree (target: {target[:80]}).")
        if tool == "Bash":
            bad = [t for t in bash_write_targets(target) if reviewer_write_denied(t)]
            if bad:
                deny("Blocked by implement-feature guard: the test-reviewer must not write "
                     "into the product tree via Bash (build no reference implementation; use "
                     f"a scratch dir for probes). Offending write target(s): {', '.join(bad)[:120]}.")

    sys.exit(0)

if __name__ == "__main__":
    main()
