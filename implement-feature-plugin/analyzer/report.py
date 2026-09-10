"""Report assembler — pure Markdown rendering, no I/O, no exception handling.

The orchestration (which reader to call, and catching the transcript's typed
errors) lives in analyze_run.py. This module only turns already-computed results
into text, so it is trivially testable and cannot itself fail a run.

The run-log section is ALWAYS rendered. The transcript section is rendered from
one of three inputs the caller supplies after quarantining the satellite:
  - a TranscriptAnalysis            -> the token/cost table
  - ("absent", reason)              -> a soft, expected "skipped" note
  - ("drift",  reason)              -> a LOUD "format changed, update parser" alarm
"""
from __future__ import annotations

from .runlog import RunLogAnalysis
from .transcript import ModelUsage, TranscriptAnalysis


def _fmt(n: int) -> str:
    return f"{n:,}"


def render_runlog(a: RunLogAnalysis) -> str:
    lines: list[str] = ["## Run-log analysis (stable / load-bearing)", ""]
    window = "—"
    if a.window_start and a.window_end:
        window = f"{a.window_start:%Y-%m-%d %H:%M:%S}Z .. {a.window_end:%H:%M:%S}Z"
    lines += [
        f"- Source: `{a.path}`",
        f"- Tool calls: **{_fmt(a.total_entries)}**"
        + (f"  ({a.malformed_lines} malformed line(s) skipped)" if a.malformed_lines else ""),
        f"- Run window: {window}",
        "",
        "### Per-agent activity",
        "",
        "| Agent | Calls | Tools | Files read | Files written |",
        "|---|---:|---|---:|---:|",
    ]
    # Conductor first, then subagents alphabetically.
    for atype in sorted(a.agents, key=lambda t: (t != "", t)):
        act = a.agents[atype]
        tools = ", ".join(f"{k}×{v}" for k, v in sorted(act.tool_counts.items()))
        lines.append(
            f"| {act.label} | {act.total_calls} | {tools} "
            f"| {len(act.reads)} | {len(act.writes)} |"
        )

    lines += ["", "### Isolation compliance", ""]
    for c in a.checks:
        mark = "✅" if c.passed else "❌"
        lines.append(f"- {mark} **{c.name}** — {c.detail}")
        if not c.passed and c.evidence:
            for ev in c.evidence[:10]:
                lines.append(f"    - `{ev}`")
    verdict = "✅ all isolation checks passed" if a.all_passed else "❌ isolation VIOLATION(S) detected"
    lines += ["", f"**Verdict: {verdict}.**", ""]
    return "\n".join(lines)


def _render_usage_table(title: str, buckets: dict[str, ModelUsage]) -> list[str]:
    if not buckets:
        return [f"_{title}: none_", ""]
    out = [
        f"**{title}**", "",
        "| Model | Turns | Input | Output | Thinking | Cache read | Cache write |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for mu in sorted(buckets.values(), key=lambda m: m.model):
        out.append(
            f"| {mu.model} | {mu.turns} | {_fmt(mu.input_tokens)} | {_fmt(mu.output_tokens)} "
            f"| {_fmt(mu.thinking_tokens)} | {_fmt(mu.cache_read_tokens)} "
            f"| {_fmt(mu.cache_creation_tokens)} |"
        )
    out.append("")
    return out


def _render_subagent_table(subs: list) -> list[str]:
    if not subs:
        return ["_Per-subagent (isolated gates): none found_", ""]
    out = [
        "**Per-subagent (isolated gates) — the per-gate model split**", "",
        "| Subagent | Model | Turns | Input | Output | Thinking |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for sub in sorted(subs, key=lambda s: s.agent_label):
        for mu in sorted(sub.by_model.values(), key=lambda m: m.model):
            out.append(
                f"| {sub.agent_label} | {mu.model} | {mu.turns} | {_fmt(mu.input_tokens)} "
                f"| {_fmt(mu.output_tokens)} | {_fmt(mu.thinking_tokens)} |"
            )
    out.append("")
    return out


def render_transcript(t: TranscriptAnalysis) -> str:
    lines = [
        "## Token / cost analysis (best-effort, from transcript)", "",
        f"- Source: `{t.session_file}`",
        f"- Assistant turns in window: **{t.turns_in_window}**",
        f"- Subagent transcripts found: **{len(t.subagents)}**", "",
    ]
    lines += _render_usage_table("Conductor / main thread", t.main)
    lines += _render_subagent_table(t.subagents)
    lines += _render_usage_table("Subagents / sidechains (aggregate by model)", t.sidechain)
    return "\n".join(lines)


def render_transcript_unavailable(mode: str, reason: str) -> str:
    if mode == "absent":
        return "\n".join([
            "## Token / cost analysis (best-effort, from transcript)", "",
            f"ℹ️  **Skipped — no transcript found.** {reason}",
            "",
            ("This is expected when the run happened outside the sandbox or the "
             "session log is unavailable. The run-log analysis above is complete."),
            "",
        ])
    # "drift" or any unexpected failure -> loud alarm.
    return "\n".join([
        "## Token / cost analysis (best-effort, from transcript)", "",
        "⚠️  **TRANSCRIPT ANALYSIS UNAVAILABLE**",
        "",
        f"    Reason: {reason}",
        "",
        "    A transcript WAS found but could not be parsed. The Claude Code",
        "    transcript format has likely changed; the analyzer's transcript",
        "    parser needs updating (see `analyzer/transcript.py`).",
        "",
        "    ► The run-log analysis above is unaffected and complete.",
        "",
    ])


def assemble(sections: list[str]) -> str:
    header = "# /implement-feature run report\n"
    return header + "\n" + "\n".join(sections).rstrip() + "\n"
