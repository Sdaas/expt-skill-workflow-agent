"""Tests for the load-bearing run-log reader."""
from __future__ import annotations

from analyzer.runlog import parse_runlog

from .conftest import call, write_runlog


def _check(analysis, name):
    return next(c for c in analysis.checks if c.name == name)


def test_parse_counts_and_per_agent_activity(tmp_path):
    log = write_runlog(tmp_path / "rl.jsonl", [
        call("", "Read", "SKILL.md"),                                  # conductor
        call("", "Bash", "ls"),
        call("implement-feature:implementer", "Read", "src/foo.py"),
        call("implement-feature:implementer", "Write", "src/foo.py"),
    ])
    a = parse_runlog(str(log))
    assert a.total_entries == 4
    assert a.malformed_lines == 0
    assert a.window_start is not None and a.window_end is not None

    conductor = a.agents[""]
    assert conductor.label == "conductor"
    assert conductor.total_calls == 2
    assert conductor.tool_counts == {"Read": 1, "Bash": 1}

    impl = a.agents["implement-feature:implementer"]
    assert impl.label == "implementer"
    assert impl.reads == ["src/foo.py"]
    assert impl.writes == ["src/foo.py"]


def test_clean_run_passes_all_isolation_checks(tmp_path):
    log = write_runlog(tmp_path / "rl.jsonl", [
        call("implement-feature:test-writer", "Read", "handoff/design-interface.md"),
        call("implement-feature:test-reviewer", "Read", "handoff/tests.py"),
        call("implement-feature:implementer", "Write", "src/foo.py"),
        call("implement-feature:verifier", "Bash", "pytest"),
        call("implement-feature:code-reviewer", "Read", "src/foo.py"),
    ])
    a = parse_runlog(str(log))
    assert a.all_passed
    assert _check(a, "distinct subagents observed").passed
    assert "all expected gates present" in _check(a, "distinct subagents observed").detail


def test_test_writer_reading_design_internal_is_a_violation(tmp_path):
    log = write_runlog(tmp_path / "rl.jsonl", [
        call("implement-feature:test-writer", "Read", "handoff/design-internal.md"),
    ])
    a = parse_runlog(str(log))
    c = _check(a, "test-writer stayed algorithm-blind")
    assert not c.passed
    assert c.evidence == ["handoff/design-internal.md"]
    assert not a.all_passed


def test_implementer_writing_test_file_is_a_violation(tmp_path):
    log = write_runlog(tmp_path / "rl.jsonl", [
        call("implement-feature:implementer", "Write", "tests/test_foo.py"),
        call("implement-feature:implementer", "Edit", "src/foo.py"),  # allowed
    ])
    a = parse_runlog(str(log))
    c = _check(a, "implementer did not touch tests")
    assert not c.passed
    assert c.evidence == ["tests/test_foo.py"]


def test_any_agent_reading_secrets_is_a_violation(tmp_path):
    log = write_runlog(tmp_path / "rl.jsonl", [
        call("implement-feature:verifier", "Read", "/repo/.env"),
    ])
    a = parse_runlog(str(log))
    c = _check(a, "no secret/.env access by any agent")
    assert not c.passed
    assert any(".env" in e for e in c.evidence)


def test_malformed_lines_are_skipped_and_counted(tmp_path):
    p = tmp_path / "rl.jsonl"
    p.write_text(
        '{"agent_type":"","tool":"Read","target":"a","ts":"2026-09-09T07:40:01+00:00"}\n'
        "not json at all\n"
        "\n"  # blank line ignored, not counted as malformed
        '["a","list","not","a","dict"]\n',
        encoding="utf-8",
    )
    a = parse_runlog(str(p))
    assert a.total_entries == 1
    assert a.malformed_lines == 2
