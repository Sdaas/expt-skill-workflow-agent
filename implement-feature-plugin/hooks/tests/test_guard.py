"""Tests for the PreToolUse guard hook (hooks/scripts/guard.py).

The hook is a stdin/stdout/exit-code contract, so we drive the real script as a
subprocess: feed it the hook JSON on stdin, set its env, and assert on the exit
code (0 allow / 2 deny), the deny JSON on stdout, and the audit line it appends.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

GUARD = Path(__file__).resolve().parent.parent / "scripts" / "guard.py"


def run_guard(payload: dict, env_extra: dict | None = None, project_dir: str | None = None):
    """Invoke guard.py with `payload` as stdin JSON. Returns (returncode, stdout)."""
    env = {"PATH": "/usr/bin:/bin"}
    if project_dir is not None:
        env["CLAUDE_PROJECT_DIR"] = project_dir
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps(payload),
        capture_output=True, text=True, env=env,
    )
    return proc.returncode, proc.stdout


def call(tool: str, target: str, *, agent_type: str = "", **kw) -> dict:
    key = "command" if tool == "Bash" else "file_path"
    return {"tool_name": tool, "tool_input": {key: target}, "agent_type": agent_type, **kw}


# --- audit + run-log resolution (#10) --------------------------------------

def test_audit_written_to_if_runlog(tmp_path):
    log = tmp_path / "explicit.jsonl"
    rc, _ = run_guard(call("Read", "somefile.py"), env_extra={"IF_RUNLOG": str(log)})
    assert rc == 0
    line = json.loads(log.read_text().strip())
    assert line["tool"] == "Read" and line["target"] == "somefile.py"


def test_runlog_resolved_via_active_run_pointer(tmp_path):
    # Layout: <proj>/.implement-feature/.active-run -> <workdir>; log at <workdir>/handoff/.
    proj = tmp_path
    workdir = proj / ".implement-feature" / "01-foo-202609101200"
    (workdir / "handoff").mkdir(parents=True)
    (proj / ".implement-feature" / ".active-run").write_text(str(workdir))

    rc, _ = run_guard(call("Read", "x.py"), project_dir=str(proj))
    assert rc == 0
    derived = workdir / "handoff" / "run-log.jsonl"
    assert derived.is_file()
    assert json.loads(derived.read_text().strip())["target"] == "x.py"


def test_runlog_falls_back_to_project_dir_when_no_pointer(tmp_path):
    rc, _ = run_guard(call("Read", "x.py"), project_dir=str(tmp_path))
    assert rc == 0
    assert (tmp_path / "if-runlog.jsonl").is_file()


# --- draft-confinement (#11) -----------------------------------------------

def test_subagent_denied_reading_handoff_draft(tmp_path):
    rc, out = run_guard(
        call("Read", "/repo/.implement-feature/r/handoff/draft/02-design-interface.md",
             agent_type="implement-feature:test-writer"),
        env_extra={"IF_RUNLOG": str(tmp_path / "l.jsonl")},
    )
    assert rc == 2
    assert json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_conductor_may_read_handoff_draft(tmp_path):
    # Empty agent_type == the conductor; it authors and reviews the drafts.
    rc, _ = run_guard(
        call("Read", "/repo/.implement-feature/r/handoff/draft/02-design-interface.md",
             agent_type=""),
        env_extra={"IF_RUNLOG": str(tmp_path / "l.jsonl")},
    )
    assert rc == 0


def test_subagent_may_read_promoted_handoff_file(tmp_path):
    rc, _ = run_guard(
        call("Read", "/repo/.implement-feature/r/handoff/02-design-interface.md",
             agent_type="implement-feature:test-writer"),
        env_extra={"IF_RUNLOG": str(tmp_path / "l.jsonl")},
    )
    assert rc == 0


# --- existing guardrails still hold, with numbered names (#17) -------------

def test_secret_read_denied_for_any_agent(tmp_path):
    rc, out = run_guard(call("Read", "/repo/.env"),
                        env_extra={"IF_RUNLOG": str(tmp_path / "l.jsonl")})
    assert rc == 2
    assert "secret" in json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"].lower()


def test_test_writer_denied_numbered_design_internal(tmp_path):
    rc, out = run_guard(
        call("Read", "/repo/.implement-feature/r/handoff/03-design-internal.md",
             agent_type="implement-feature:test-writer"),
        env_extra={"IF_RUNLOG": str(tmp_path / "l.jsonl")},
    )
    assert rc == 2  # numeric prefix still trips the substring match
    assert json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_implementer_denied_writing_test_file(tmp_path):
    rc, out = run_guard(
        call("Write", "/repo/tests/test_foo.py", agent_type="implement-feature:implementer"),
        env_extra={"IF_RUNLOG": str(tmp_path / "l.jsonl")},
    )
    assert rc == 2
    assert json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "deny"
