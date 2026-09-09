"""CLI entry point for the /implement-feature observability analyzer.

    python -m implement_feature_plugin.analyzer.analyze_run --runlog if-runlog.jsonl
    # or, from inside implement-feature-plugin/:
    python -m analyzer.analyze_run --runlog /path/to/if-runlog.jsonl

This is the ONLY place that orchestrates the two readers and quarantines the
best-effort transcript satellite. Order of operations:

  1. Parse the run-log (load-bearing). If this file is missing/unreadable, that
     is a hard, user-facing error — there is nothing to report without it.
  2. Render the run-log section (always).
  3. Attempt the transcript section inside try/except:
        TranscriptAbsent      -> soft "skipped" note
        TranscriptFormatError -> loud "format changed, update parser" alarm
        any OTHER exception   -> ALSO the loud path (unknown failure is treated
                                 as drift; silent degradation is worse than loud).

Nothing here calls a model or drives a gate — measurement only (P40).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import report
from .runlog import parse_runlog
from .transcript import (
    TranscriptAbsent,
    TranscriptFormatError,
    find_transcript,
    parse_transcript,
)


def _default_runlog() -> str:
    return (os.environ.get("IF_RUNLOG")
            or (os.path.join(os.environ["CLAUDE_PROJECT_DIR"], "if-runlog.jsonl")
                if os.environ.get("CLAUDE_PROJECT_DIR") else None)
            or "if-runlog.jsonl")


def _default_projects_dir() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude"))) / "projects"


def _slug_for(cwd: Path) -> str:
    """Claude Code names a project dir by its abs path with '/' -> '-'."""
    return str(cwd.resolve()).replace("/", "-")


def build_report(runlog_path: str, projects_root: Path | None, slug: str | None,
                 use_transcript: bool = True) -> str:
    # 1-2. Run-log: load-bearing, always rendered.
    runlog = parse_runlog(runlog_path)
    sections = [report.render_runlog(runlog)]

    # 3. Transcript: quarantined best-effort satellite.
    if not use_transcript:
        sections.append(report.render_transcript_unavailable(
            "absent", "transcript analysis disabled (--no-transcript)."))
        return report.assemble(sections)

    try:
        projects_root = projects_root or _default_projects_dir()
        slug = slug or _slug_for(Path.cwd())
        project_dir = projects_root / slug
        tpath = find_transcript(project_dir, runlog.window_start, runlog.window_end)
        tanalysis = parse_transcript(tpath, runlog.window_start, runlog.window_end)
        sections.append(report.render_transcript(tanalysis))
    except TranscriptAbsent as e:
        sections.append(report.render_transcript_unavailable("absent", str(e)))
    except TranscriptFormatError as e:
        sections.append(report.render_transcript_unavailable("drift", str(e)))
    except Exception as e:  # noqa: BLE001 - deliberate: any unknown transcript
        # failure must route to the LOUD path; silent degradation is worse.
        sections.append(report.render_transcript_unavailable(
            "drift", f"unexpected {type(e).__name__}: {e}"))

    return report.assemble(sections)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Analyze an /implement-feature run.")
    p.add_argument("--runlog", default=_default_runlog(),
                   help="path to if-runlog.jsonl (default: $IF_RUNLOG or ./if-runlog.jsonl)")
    p.add_argument("--projects-dir", default=None,
                   help="Claude Code projects dir (default: ~/.claude/projects)")
    p.add_argument("--slug", default=None,
                   help="project slug under projects-dir (default: derived from cwd)")
    p.add_argument("--no-transcript", action="store_true",
                   help="skip the best-effort transcript/token analysis")
    args = p.parse_args(argv)

    if not Path(args.runlog).is_file():
        print(f"error: run-log not found: {args.runlog}", file=sys.stderr)
        print("(nothing to report without the run-log; pass --runlog PATH)", file=sys.stderr)
        return 2

    projects_root = Path(args.projects_dir) if args.projects_dir else None
    print(build_report(args.runlog, projects_root, args.slug,
                        use_transcript=not args.no_transcript))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
