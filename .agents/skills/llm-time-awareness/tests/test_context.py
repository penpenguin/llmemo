from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import pytest

from time_awareness import (
    TimeAwarenessError,
    build_time_context,
    classify_elapsed,
    classify_time_of_day,
    load_preferences,
    load_state,
    mark_assistant_turn,
)


def utc_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def aware_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_classify_elapsed() -> None:
    assert classify_elapsed(None) == "first_turn_or_unknown"
    assert classify_elapsed(-1) == "clock_skew_or_out_of_order"
    assert classify_elapsed(30) == "immediate_followup"
    assert classify_elapsed(120) == "short_pause"
    assert classify_elapsed(20 * 60) == "medium_pause"
    assert classify_elapsed(3 * 60 * 60) == "long_pause"
    assert classify_elapsed(12 * 60 * 60) == "next_day_or_large_gap"
    assert classify_elapsed(48 * 60 * 60) == "stale_context"


def test_classify_time_of_day_uses_local_wall_clock() -> None:
    assert classify_time_of_day(aware_dt("2026-06-18T20:00:00+09:00")) == "evening"
    assert classify_time_of_day(aware_dt("2026-06-18T23:00:00+09:00")) == "late_night"
    assert classify_time_of_day(aware_dt("2026-06-18T03:00:00+09:00")) == "deep_night"
    assert classify_time_of_day(aware_dt("2026-06-18T05:30:00+09:00")) == "early_morning"
    assert classify_time_of_day(aware_dt("2026-06-18T09:30:00+09:00")) == "morning"


def test_build_time_context_detects_gap_and_date_change() -> None:
    with TemporaryDirectory() as tmp:
        first = build_time_context(
            "conv-1",
            user_timezone="Asia/Tokyo",
            state_dir=tmp,
            current_user_turn_at_utc=utc_dt("2026-06-17T14:30:00Z"),  # 23:30 JST
        )
        assert first["elapsed_label"] == "first_turn_or_unknown"
        assert "first_turn_or_unknown_previous_turn" in first["time_flags"]

        second = build_time_context(
            "conv-1",
            user_timezone="Asia/Tokyo",
            state_dir=tmp,
            current_user_turn_at_utc=utc_dt("2026-06-18T00:30:00Z"),  # 09:30 JST next local date
        )
        assert second["elapsed_label"] == "next_day_or_large_gap"
        assert second["local_date_changed_since_last_turn"] is True
        assert "local_date_changed" in second["time_flags"]
        assert "substantial_gap_since_last_turn" in second["time_flags"]


def test_mark_assistant_turn_and_elapsed_from_assistant() -> None:
    with TemporaryDirectory() as tmp:
        build_time_context(
            "conv-2",
            user_timezone="Asia/Tokyo",
            state_dir=tmp,
            current_user_turn_at_utc="2026-06-18T00:00:00Z",
        )
        mark_assistant_turn(
            "conv-2",
            user_timezone="Asia/Tokyo",
            state_dir=tmp,
            assistant_turn_at_utc="2026-06-18T00:01:00Z",
        )
        ctx = build_time_context(
            "conv-2",
            user_timezone="Asia/Tokyo",
            state_dir=tmp,
            current_user_turn_at_utc="2026-06-18T00:03:30Z",
        )
        assert ctx["elapsed_since_last_user_turn_seconds"] == 210
        assert ctx["elapsed_since_last_assistant_turn_seconds"] == 150


def test_rejects_naive_datetime() -> None:
    with TemporaryDirectory() as tmp:
        with pytest.raises(TimeAwarenessError):
            build_time_context(
                "conv-3",
                user_timezone="Asia/Tokyo",
                state_dir=tmp,
                current_user_turn_at_utc=datetime(2026, 6, 18, 0, 0, 0),
            )


def test_build_time_context_requires_explicit_user_timezone() -> None:
    with TemporaryDirectory() as tmp:
        with pytest.raises(TimeAwarenessError):
            build_time_context(
                "conv-4",
                state_dir=tmp,
                current_user_turn_at_utc="2026-06-18T00:00:00Z",
            )


def test_build_time_context_cli_requires_explicit_timezone() -> None:
    root = Path(__file__).resolve().parents[1]

    with TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "build_time_context.py"),
                "--conversation-id",
                "conv-cli",
                "--state-dir",
                tmp,
                "--current-user-turn-at-utc",
                "2026-06-18T00:00:00Z",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    assert result.returncode != 0
    assert "--timezone" in result.stderr


def test_mark_assistant_turn_requires_explicit_user_timezone() -> None:
    with TemporaryDirectory() as tmp:
        with pytest.raises(TimeAwarenessError):
            mark_assistant_turn(
                "conv-5",
                state_dir=tmp,
                assistant_turn_at_utc="2026-06-18T00:01:00Z",
            )


def test_mark_assistant_turn_cli_requires_explicit_timezone() -> None:
    root = Path(__file__).resolve().parents[1]

    with TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "mark_assistant_turn.py"),
                "--conversation-id",
                "conv-cli",
                "--state-dir",
                tmp,
                "--assistant-turn-at-utc",
                "2026-06-18T00:01:00Z",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    assert result.returncode != 0
    assert "--timezone" in result.stderr


def test_load_state_requires_explicit_timezone_for_new_state() -> None:
    with TemporaryDirectory() as tmp:
        with pytest.raises(TimeAwarenessError):
            load_state("conv-6", state_dir=tmp)


def test_load_preferences_requires_explicit_timezone_without_file() -> None:
    with pytest.raises(TimeAwarenessError):
        load_preferences()


def test_out_of_order_user_turn_does_not_roll_back_persisted_state() -> None:
    with TemporaryDirectory() as tmp:
        build_time_context(
            "conv-out-of-order",
            user_timezone="Asia/Tokyo",
            state_dir=tmp,
            current_user_turn_at_utc="2026-06-18T15:00:00Z",
        )

        ctx = build_time_context(
            "conv-out-of-order",
            user_timezone="Asia/Tokyo",
            state_dir=tmp,
            current_user_turn_at_utc="2026-06-18T14:30:00Z",
        )

        assert ctx["elapsed_label"] == "clock_skew_or_out_of_order"
        assert "clock_skew_or_out_of_order" in ctx["time_flags"]
        assert ctx["elapsed_since_last_user_turn_human"] is None

        state_path = Path(tmp) / "conv-out-of-order.json"
        persisted = json.loads(state_path.read_text(encoding="utf-8"))

    assert persisted["turn_index"] == 1
    assert persisted["last_user_turn_at_utc"] == "2026-06-18T15:00:00+00:00"
    assert persisted["last_interaction_at_utc"] == "2026-06-18T15:00:00+00:00"
