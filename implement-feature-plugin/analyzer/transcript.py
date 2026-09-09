"""Transcript reader — the BEST-EFFORT satellite.

Parses the Claude Code session transcript JSONL
(~/.claude/projects/<slug>/*.jsonl) for per-model token usage, split main-thread
vs subagent (sidechain). This is the ground-truth model/token/cost source.

Its format is officially UNSTABLE (LAUNCHING-SUBAGENTS.md / PLAN.md), so this
module is treated as fragile and QUARANTINED. It raises exactly two typed
errors, and the caller (report.py) turns them into two different degradation
messages — it never lets a transcript problem break the run-log analysis:

  - TranscriptAbsent      soft: no transcript file overlaps the run window
                          (e.g. run outside the sandbox). Expected; skip quietly.
  - TranscriptFormatError loud: a transcript WAS found but the fields we depend
                          on are gone -> Claude Code changed the format and THIS
                          PARSER needs updating. Fail loudly, never guess.

This module has ZERO knowledge of runlog.py. The only thing that crosses the
boundary is a time window (two datetimes), passed in by the caller.
"""
from __future__ import annotations

import datetime as _dt
import json
from dataclasses import dataclass, field
from pathlib import Path

from ._util import parse_ts

# Padding on the correlation window: absorbs clock skew and the guard hook's
# seconds-precision rounding so a turn right at the edge is still matched.
WINDOW_PAD = _dt.timedelta(minutes=5)


class TranscriptAbsent(Exception):
    """No transcript file overlaps the run window. Soft, expected degradation."""


class TranscriptFormatError(Exception):
    """A transcript was found but its schema no longer matches. Loud alarm."""


@dataclass
class ModelUsage:
    model: str
    turns: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    thinking_tokens: int = 0

    def add(self, usage: dict) -> None:
        self.turns += 1
        self.input_tokens += int(usage.get("input_tokens") or 0)
        self.output_tokens += int(usage.get("output_tokens") or 0)
        self.cache_read_tokens += int(usage.get("cache_read_input_tokens") or 0)
        self.cache_creation_tokens += int(usage.get("cache_creation_input_tokens") or 0)
        details = usage.get("output_tokens_details") or {}
        self.thinking_tokens += int(details.get("thinking_tokens") or 0)


@dataclass
class TranscriptAnalysis:
    session_file: str
    turns_in_window: int
    main: dict[str, ModelUsage] = field(default_factory=dict)       # model -> usage
    sidechain: dict[str, ModelUsage] = field(default_factory=dict)   # model -> usage


def find_transcript(projects_dir: Path, window_start, window_end) -> Path:
    """Pick the transcript file whose assistant turns overlap the run window (b).

    Correlating by time window (not just "newest file") is robust to stray
    concurrent sessions in the same project dir. Raises TranscriptAbsent if the
    dir is missing/empty or no file overlaps.
    """
    if window_start is None or window_end is None:
        raise TranscriptAbsent("run-log has no usable timestamps to correlate against")
    if not projects_dir.is_dir():
        raise TranscriptAbsent(f"transcript dir not found: {projects_dir}")

    lo, hi = window_start - WINDOW_PAD, window_end + WINDOW_PAD
    candidates = sorted(projects_dir.glob("*.jsonl"))
    if not candidates:
        raise TranscriptAbsent(f"no *.jsonl transcripts in {projects_dir}")

    best: tuple[int, Path] | None = None  # (overlap_count, path)
    for path in candidates:
        overlap = 0
        for ts in _iter_assistant_timestamps(path):
            if lo <= ts <= hi:
                overlap += 1
        if overlap and (best is None or overlap > best[0]):
            best = (overlap, path)

    if best is None:
        raise TranscriptAbsent(
            f"no transcript in {projects_dir} overlaps the run window "
            f"[{window_start:%Y-%m-%d %H:%M}Z .. {window_end:%H:%M}Z]"
        )
    return best[1]


def parse_transcript(path: Path, window_start, window_end) -> TranscriptAnalysis:
    """Aggregate per-model token usage from assistant turns inside the window.

    Runs a schema self-check first: if assistant turns exist but NONE carry the
    model/usage fields we depend on, that is format drift -> TranscriptFormatError
    (loud), never silently-empty output.
    """
    lo = (window_start - WINDOW_PAD) if window_start else None
    hi = (window_end + WINDOW_PAD) if window_end else None

    analysis = TranscriptAnalysis(session_file=str(path), turns_in_window=0)
    assistant_turns = 0
    usable_turns = 0

    try:
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        # Present in the listing but unreadable now: treat as absent, not drift.
        raise TranscriptAbsent(f"could not read transcript {path}: {e}") from e

    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(rec, dict) or rec.get("type") != "assistant":
            continue
        assistant_turns += 1

        ts = parse_ts(str(rec.get("timestamp") or ""))
        if ts is not None and lo is not None and hi is not None and not (lo <= ts <= hi):
            continue

        msg = rec.get("message") or {}
        model = msg.get("model")
        usage = msg.get("usage")
        if not model or not isinstance(usage, dict):
            continue  # this turn lacks the fields; self-check below catches total drift
        usable_turns += 1
        analysis.turns_in_window += 1

        bucket = analysis.sidechain if rec.get("isSidechain") else analysis.main
        mu = bucket.get(model)
        if mu is None:
            mu = bucket[model] = ModelUsage(model=model)
        mu.add(usage)

    # Schema self-check: assistant turns present but none parseable => drift.
    if assistant_turns > 0 and usable_turns == 0:
        raise TranscriptFormatError(
            f"{assistant_turns} assistant turn(s) in {path.name} but none carried "
            f"the expected message.model / message.usage fields. The Claude Code "
            f"transcript format has likely changed; update analyzer/transcript.py."
        )
    if assistant_turns == 0:
        # A file that matched by name but has no assistant turns in window.
        raise TranscriptAbsent(f"no assistant turns found in {path.name}")

    return analysis


def _iter_assistant_timestamps(path: Path):
    """Yield tz-aware timestamps of assistant turns in a file (best-effort)."""
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(rec, dict) and rec.get("type") == "assistant":
                    ts = parse_ts(str(rec.get("timestamp") or ""))
                    if ts is not None:
                        yield ts
    except OSError:
        return
