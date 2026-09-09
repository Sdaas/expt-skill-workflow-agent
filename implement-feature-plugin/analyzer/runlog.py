"""Run-log reader — the LOAD-BEARING half of the analyzer.

Parses the guard hook's audit log (if-runlog.jsonl): one JSON object per line,
one line per tool call, written by hooks/scripts/guard.py. Schema:

    {"ts": "<UTC ISO>", "agent_type": "<str>", "agent_id": "<str>",
     "tool": "Read|Bash|Grep|Glob|Edit|Write|...", "target": "<path/cmd>"}

From this it derives, WITHOUT ever touching the transcript:
  - per-agent activity (tool-call counts, files read / written)
  - the run's time window (min/max ts) — the single value handed to the
    transcript layer for correlation (a value, never code or shared state)
  - isolation-compliance verdicts — the proof that the guard's invariants held

IMPORTANT — the audit records ATTEMPTS, not outcomes. guard.py logs every call
(job #1) BEFORE it may deny it (jobs #2-4). So a forbidden entry appearing here
means an agent *tried* — the guard blocks it at runtime; this layer *detects*
the attempt after the fact. Preventive (guard) + detective (analyzer) together.

This module has ZERO knowledge of transcript.py.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
from dataclasses import dataclass, field

from ._util import parse_ts

# Mirror guard.py's tool classification (keep in sync with hooks/scripts/guard.py).
READISH = {"Read", "Bash", "Grep", "Glob"}
WRITEISH = {"Write", "Edit", "NotebookEdit"}

# The conductor logs with an empty agent_type; give it a readable name.
CONDUCTOR = "conductor"

# The subagent gates we expect a full run to exercise (namespaced, per SKILL.md).
EXPECTED_AGENTS = (
    "implement-feature:test-writer",
    "implement-feature:test-reviewer",
    "implement-feature:implementer",
    "implement-feature:verifier",
    "implement-feature:code-reviewer",
)

# --- predicates mirrored from guard.py -------------------------------------
# KEEP IN SYNC with hooks/scripts/guard.py (SECRET_HINTS / looks_secret /
# is_test_path). The detective checks here must match the preventive rules there,
# or the report could pass a run the guard would actually have blocked.
_SECRET_HINTS = (".env", "id_rsa", "id_ed25519", "credentials", ".pem", ".key",
                 ".ssh/", ".aws/credentials", "secrets.", ".netrc", ".pgpass")


def looks_secret(target: str) -> bool:
    t = target.lower()
    base = os.path.basename(t)
    if base == ".env" or base.startswith(".env") or base.endswith((".pem", ".key")):
        return True
    return any(h in t for h in _SECRET_HINTS)


def is_test_path(target: str) -> bool:
    base = os.path.basename(target)
    return ("/tests/" in target or "/test/" in target
            or base.startswith("test_") or base.endswith("_test.py")
            or base == "conftest.py")


# --- data model ------------------------------------------------------------
@dataclass
class AgentActivity:
    agent_type: str
    total_calls: int = 0
    tool_counts: dict[str, int] = field(default_factory=dict)
    reads: list[str] = field(default_factory=list)   # targets of read-ish calls
    writes: list[str] = field(default_factory=list)   # targets of write-ish calls

    @property
    def label(self) -> str:
        """Human-friendly name (strip the plugin namespace; name the conductor)."""
        if not self.agent_type:
            return CONDUCTOR
        return self.agent_type.split(":", 1)[-1]


@dataclass
class IsolationCheck:
    name: str
    passed: bool
    detail: str
    evidence: list[str] = field(default_factory=list)  # offending log lines


@dataclass
class RunLogAnalysis:
    path: str
    total_entries: int
    malformed_lines: int
    window_start: _dt.datetime | None
    window_end: _dt.datetime | None
    agents: dict[str, AgentActivity]
    checks: list[IsolationCheck]

    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks)


# --- parsing ---------------------------------------------------------------
def parse_runlog(path: str) -> RunLogAnalysis:
    """Read if-runlog.jsonl and compute per-agent activity + isolation verdicts.

    Robust to malformed lines (skipped and counted), mirroring guard.py's own
    "never fail on bad input" stance.
    """
    agents: dict[str, AgentActivity] = {}
    times: list[_dt.datetime] = []
    total = 0
    malformed = 0

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            if not isinstance(rec, dict):
                malformed += 1
                continue

            total += 1
            atype = str(rec.get("agent_type") or "")
            tool = str(rec.get("tool") or "")
            target = str(rec.get("target") or "")

            act = agents.get(atype)
            if act is None:
                act = agents[atype] = AgentActivity(agent_type=atype)
            act.total_calls += 1
            act.tool_counts[tool] = act.tool_counts.get(tool, 0) + 1
            if tool in READISH:
                act.reads.append(target)
            elif tool in WRITEISH:
                act.writes.append(target)

            ts = parse_ts(str(rec.get("ts") or ""))
            if ts is not None:
                times.append(ts)

    checks = _run_isolation_checks(agents)
    return RunLogAnalysis(
        path=path,
        total_entries=total,
        malformed_lines=malformed,
        window_start=min(times) if times else None,
        window_end=max(times) if times else None,
        agents=agents,
        checks=checks,
    )


def _run_isolation_checks(agents: dict[str, AgentActivity]) -> list[IsolationCheck]:
    """The four detective verdicts, derived purely from per-agent activity."""
    checks: list[IsolationCheck] = []

    # 1. test-writer must not have attempted to read design-internal.md
    tw_hits = [
        t for a in agents.values() if "test-writer" in a.agent_type
        for t in a.reads if "design-internal" in t
    ]
    checks.append(IsolationCheck(
        name="test-writer stayed algorithm-blind",
        passed=not tw_hits,
        detail=("no attempt to read design-internal.md"
                if not tw_hits else
                f"{len(tw_hits)} attempt(s) to read design-internal.md (guard blocks at runtime)"),
        evidence=tw_hits,
    ))

    # 2. implementer must not have attempted to write/edit a test file
    impl_hits = [
        t for a in agents.values() if "implementer" in a.agent_type
        for t in a.writes if is_test_path(t)
    ]
    checks.append(IsolationCheck(
        name="implementer did not touch tests",
        passed=not impl_hits,
        detail=("no attempt to write/edit test files"
                if not impl_hits else
                f"{len(impl_hits)} attempt(s) to write a test file (guard blocks at runtime)"),
        evidence=impl_hits,
    ))

    # 3. no agent must have attempted to read secrets/.env
    secret_hits = [
        f"{a.label}: {t}" for a in agents.values()
        for t in a.reads if looks_secret(t)
    ]
    checks.append(IsolationCheck(
        name="no secret/.env access by any agent",
        passed=not secret_hits,
        detail=("no attempt to read secrets/.env"
                if not secret_hits else
                f"{len(secret_hits)} attempt(s) to read secrets/.env (guard blocks at runtime)"),
        evidence=secret_hits,
    ))

    # 4. distinct expected agents actually ran (proves isolation, not just intent)
    seen = {a.agent_type for a in agents.values() if a.agent_type}
    missing = [e for e in EXPECTED_AGENTS if e not in seen]
    # Informational, not a hard failure: a partial/aborted run legitimately lacks
    # later gates. We report presence but only fail if NO subagent ran at all.
    checks.append(IsolationCheck(
        name="distinct subagents observed",
        passed=bool(seen),
        detail=(f"{len(seen)} subagent type(s) ran"
                + (f"; not yet seen: {', '.join(m.split(':', 1)[-1] for m in missing)}"
                   if missing else " (all expected gates present)")),
        evidence=sorted(seen),
    ))

    return checks
