#!/usr/bin/env python3
"""PreToolUse guard hook for /implement-feature.

Does five jobs on every Read/Bash/Grep/Glob/Edit/Write (conductor AND every subagent):
  1. AUDIT  — append one JSONL line per tool call (agent_id/agent_type/tool/target).
  2. SECRETS GUARDRAIL — deny reads of .env / keys / credentials for ANY agent.
  3. ALGORITHM-BLIND — deny reads of design-internal for the test-writer agent only.
  4. TEST-INTEGRITY — deny the implementer editing/writing any test file (it must make
     the code pass the tests, never weaken the tests to pass).
  5. DRAFT-CONFINEMENT — deny ANY subagent reading anything under handoff/draft/ (an
     unapproved draft must never reach an isolated gate; the conductor promotes on
     approval, and only then is a file readable at handoff/).

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
import json, os, sys, datetime

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

# --- secret patterns (basename / path fragments) ---
SECRET_HINTS = (".env", "id_rsa", "id_ed25519", "credentials", ".pem", ".key",
                ".ssh/", ".aws/credentials", "secrets.", ".netrc", ".pgpass")

def looks_secret(target: str) -> bool:
    t = target.lower()
    base = os.path.basename(t)
    if base == ".env" or base.startswith(".env") or base.endswith((".pem", ".key")):
        return True
    return any(h in t for h in SECRET_HINTS)

READISH = {"Read", "Bash", "Grep", "Glob"}
WRITEISH = {"Write", "Edit", "NotebookEdit"}

def is_test_path(target: str) -> bool:
    base = os.path.basename(target)
    return ("/tests/" in target or "/test/" in target
            or base.startswith("test_") or base.endswith("_test.py")
            or base == "conftest.py")

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
    if tool in READISH and looks_secret(target):
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

    sys.exit(0)

if __name__ == "__main__":
    main()
