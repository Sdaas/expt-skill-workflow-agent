# Observability analyzer

A **deterministic, after-the-fact** reporter for an `/implement-feature` run —
**measurement, never orchestration** (PATTERNS.md **P40**). It reads the two
pieces of evidence a finished run leaves behind and prints a Markdown report. It
never calls a model, makes a decision, or drives a gate.

## Run it

```bash
# from implement-feature-plugin/
python -m analyzer.analyze_run --runlog /path/to/if-runlog.jsonl

# options
--projects-dir DIR   # Claude Code projects dir (default: ~/.claude/projects)
--slug SLUG          # project subdir under projects-dir (default: derived from cwd)
--no-transcript      # skip the best-effort token/cost analysis
```

The run-log path defaults to `$IF_RUNLOG`, else `$CLAUDE_PROJECT_DIR/if-runlog.jsonl`,
else `./if-runlog.jsonl` — mirroring `hooks/scripts/guard.py`.

## Architecture — two independent readers

```
analyze_run.py            entry point; orchestrates + QUARANTINES the satellite
├── runlog.py             LOAD-BEARING. Parses if-runlog.jsonl only.
│                         Per-agent activity + the 4 isolation verdicts.
│                         Zero knowledge of the transcript; cannot be broken by it.
├── transcript.py         BEST-EFFORT satellite. Parses the Claude Code session
│                         transcript for per-model tokens (main vs sidechain).
│                         Format is officially unstable -> fully quarantined.
├── report.py             Pure Markdown rendering (no I/O, no exception handling).
└── _util.py              Leaf helpers (tolerant timestamp parsing). Shared, but
                          does NOT couple the two readers to each other.
```

### Failure handling (fail loud, not silent)
The run-log section is **always** rendered. The transcript section is attempted
inside `try/except` and degrades two ways:

- **absent** (no transcript overlaps the run window) → soft "skipped" note.
- **drift** (a transcript was found but the fields we depend on are gone) → a
  **loud** "format changed, update `analyzer/transcript.py`" alarm. An *unknown*
  exception also routes here — silent degradation is worse than a loud alarm.

`transcript.py` runs a **schema self-check**: assistant turns present but none
carrying `message.model` / `message.usage` ⇒ deliberate `TranscriptFormatError`.

### Transcript↔run selection
The transcript file is chosen by **time-window correlation** (option *b*): the
file whose assistant turns most overlap the run-log's `[min ts, max ts]` window
(padded ±5 min for skew). Robust to stray concurrent sessions. Requires the
run-log and transcript to share a clock — `guard.py` logs **UTC/tz-aware** on
purpose so it lines up with the transcript's `Z` stamps.

## The isolation verdicts (from the run-log alone)
1. test-writer never *attempted* to read `design-internal.md`
2. implementer never *attempted* to write/edit a test file
3. no agent *attempted* to read secrets/`.env`
4. distinct expected subagents actually ran

> The audit records **attempts**, not outcomes: `guard.py` logs every call
> (job #1) *before* it may deny it (jobs #2–4). A forbidden entry here means an
> agent *tried*; the guard blocks it at runtime. Preventive (guard) + detective
> (analyzer) together. The secret/test-path predicates here **mirror `guard.py`**
> and must be kept in sync.

## Known minor semantics
`Bash` counts as a "read-ish" tool (so `cat .env` is caught by the secret
check), so a Bash command target is included in an agent's "files read" count.
The per-tool breakdown column disambiguates.

## Tests
`python -m pytest analyzer/tests -q` — synthetic run-logs + transcripts,
including both degradation modes. Run inside the dev container (pinned toolchain).
