"""Shared fixtures/factories for analyzer tests: synthetic run-logs + transcripts."""
from __future__ import annotations

import json
from pathlib import Path

# A fixed run window used across tests. Run-log stamps use tz-aware UTC (matching
# the guard.py fix); transcript stamps use the "Z" suffix (matching Claude Code).
BASE_RUNLOG_TS = "2026-09-09T07:40:0{}+00:00"
BASE_TRANSCRIPT_TS = "2026-09-09T07:40:0{}.500Z"


def write_runlog(path: Path, records: list[dict]) -> Path:
    """Write records as JSONL; each record may omit 'ts' (auto-filled in window)."""
    lines = []
    for i, rec in enumerate(records):
        rec = dict(rec)
        rec.setdefault("ts", BASE_RUNLOG_TS.format(i % 10))
        rec.setdefault("agent_id", "a")
        lines.append(json.dumps(rec))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def call(agent_type: str, tool: str, target: str, ts: str | None = None) -> dict:
    rec = {"agent_type": agent_type, "tool": tool, "target": target}
    if ts is not None:
        rec["ts"] = ts
    return rec


def assistant_turn(model: str, *, sidechain: bool = False, i: int = 0,
                   input_tokens: int = 100, output_tokens: int = 50,
                   thinking: int = 10, with_usage: bool = True) -> dict:
    message: dict[str, object] = {"model": model}
    if with_usage:
        message["usage"] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_input_tokens": 200,
            "cache_creation_input_tokens": 300,
            "output_tokens_details": {"thinking_tokens": thinking},
        }
    return {
        "type": "assistant",
        "timestamp": BASE_TRANSCRIPT_TS.format(i % 10),
        "isSidechain": sidechain,
        "message": message,
    }


def write_transcript(path: Path, turns: list[dict], extra_lines: list[dict] | None = None) -> Path:
    lines = [json.dumps(t) for t in turns]
    for e in (extra_lines or []):
        lines.append(json.dumps(e))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
