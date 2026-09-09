"""Tests for the best-effort transcript satellite: parsing + both degradations."""
from __future__ import annotations

import datetime as dt

import pytest

from analyzer.transcript import (
    TranscriptAbsent,
    TranscriptFormatError,
    find_transcript,
    parse_transcript,
)

from .conftest import assistant_turn, write_transcript

WIN_START = dt.datetime(2026, 9, 9, 7, 40, 0, tzinfo=dt.timezone.utc)
WIN_END = dt.datetime(2026, 9, 9, 7, 40, 9, tzinfo=dt.timezone.utc)


def test_parse_aggregates_main_vs_sidechain_by_model(tmp_path):
    tpath = write_transcript(tmp_path / "s.jsonl", [
        assistant_turn("claude-opus-4-8", i=1, input_tokens=100, output_tokens=40),
        assistant_turn("claude-opus-4-8", i=2, input_tokens=100, output_tokens=40),
        assistant_turn("claude-sonnet-5", sidechain=True, i=3, input_tokens=10, output_tokens=5),
    ])
    a = parse_transcript(tpath, WIN_START, WIN_END)
    assert a.turns_in_window == 3
    assert a.main["claude-opus-4-8"].turns == 2
    assert a.main["claude-opus-4-8"].input_tokens == 200
    assert a.main["claude-opus-4-8"].output_tokens == 80
    assert a.sidechain["claude-sonnet-5"].turns == 1
    assert "claude-opus-4-8" not in a.sidechain


def test_find_transcript_picks_overlapping_file(tmp_path):
    good = write_transcript(tmp_path / "good.jsonl", [assistant_turn("m", i=2)])
    # An unrelated session far outside the window.
    off = tmp_path / "off.jsonl"
    off.write_text(
        '{"type":"assistant","timestamp":"2020-01-01T00:00:00.000Z",'
        '"message":{"model":"m","usage":{"input_tokens":1,"output_tokens":1}}}\n',
        encoding="utf-8",
    )
    picked = find_transcript(tmp_path, WIN_START, WIN_END)
    assert picked == good


def test_find_transcript_absent_when_no_overlap(tmp_path):
    (tmp_path / "old.jsonl").write_text(
        '{"type":"assistant","timestamp":"2020-01-01T00:00:00.000Z",'
        '"message":{"model":"m","usage":{"input_tokens":1,"output_tokens":1}}}\n',
        encoding="utf-8",
    )
    with pytest.raises(TranscriptAbsent):
        find_transcript(tmp_path, WIN_START, WIN_END)


def test_find_transcript_absent_when_dir_missing(tmp_path):
    with pytest.raises(TranscriptAbsent):
        find_transcript(tmp_path / "nope", WIN_START, WIN_END)


def test_schema_drift_raises_format_error(tmp_path):
    # Assistant turns present, but NONE carry model/usage -> loud drift alarm.
    tpath = write_transcript(tmp_path / "drift.jsonl", [
        assistant_turn("whatever", i=1, with_usage=False),
        assistant_turn("whatever", i=2, with_usage=False),
    ])
    with pytest.raises(TranscriptFormatError) as exc:
        parse_transcript(tpath, WIN_START, WIN_END)
    assert "format has likely changed" in str(exc.value)


def test_no_assistant_turns_is_absent_not_drift(tmp_path):
    tpath = tmp_path / "empty.jsonl"
    tpath.write_text('{"type":"user","message":{}}\n', encoding="utf-8")
    with pytest.raises(TranscriptAbsent):
        parse_transcript(tpath, WIN_START, WIN_END)
