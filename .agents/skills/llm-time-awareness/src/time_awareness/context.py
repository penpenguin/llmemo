from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


UNKNOWN_TIMEZONE = "unknown"


@dataclass(frozen=True)
class UserTimePreferences:
    """User-specific local wall-clock boundaries.

    All fields are HH:MM local times. Defaults are intentionally generic and can
    be overridden by a host application if it knows the user's schedule.
    """

    timezone_name: str = UNKNOWN_TIMEZONE
    workday_start: str = "09:00"
    workday_end: str = "18:00"
    early_morning_start: str = "04:00"
    early_morning_end: str = "07:00"
    late_night_start: str = "22:00"
    deep_night_start: str = "02:00"
    deep_night_end: str = "04:00"


@dataclass
class TimeState:
    conversation_id: str
    turn_index: int = 0
    last_user_turn_at_utc: str | None = None
    last_assistant_turn_at_utc: str | None = None
    last_interaction_at_utc: str | None = None
    user_timezone: str = UNKNOWN_TIMEZONE


DEFAULT_STATE_DIR = Path(".llm_time_state")


class TimeAwarenessError(ValueError):
    """Raised when time context cannot be constructed from valid inputs."""


def require_user_timezone(user_timezone: str | None) -> str:
    if not user_timezone:
        raise TimeAwarenessError(
            "user_timezone is required; do not fabricate local time when the user's timezone is unknown"
        )
    return user_timezone


def parse_datetime(value: str | None) -> datetime | None:
    """Parse a timezone-aware ISO-8601 datetime string as UTC.

    Accepts strings ending in `Z` and returns a timezone-aware UTC datetime.
    Naive datetimes are rejected because elapsed-time calculation requires an
    explicit source timezone.
    """

    if not value:
        return None

    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)

    if dt.tzinfo is None:
        raise TimeAwarenessError(f"Datetime must be timezone-aware: {value!r}")

    return dt.astimezone(timezone.utc)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def ensure_aware_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise TimeAwarenessError("Datetime must be timezone-aware")
    return dt.astimezone(timezone.utc)


def get_zoneinfo(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise TimeAwarenessError(f"Unknown IANA timezone: {timezone_name!r}") from exc


def _state_path(state_dir: Path, conversation_id: str) -> Path:
    safe_id = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in conversation_id)
    return state_dir / f"{safe_id}.json"


def load_state(
    conversation_id: str,
    *,
    state_dir: str | Path = DEFAULT_STATE_DIR,
    user_timezone: str | None = None,
) -> TimeState:
    state_dir = Path(state_dir)
    path = _state_path(state_dir, conversation_id)

    if not path.exists():
        return TimeState(
            conversation_id=conversation_id,
            user_timezone=require_user_timezone(user_timezone),
        )

    data = json.loads(path.read_text(encoding="utf-8"))
    state = TimeState(**data)

    if user_timezone is not None and state.user_timezone != user_timezone:
        state.user_timezone = require_user_timezone(user_timezone)

    return state


def save_state(state: TimeState, *, state_dir: str | Path = DEFAULT_STATE_DIR) -> None:
    state_dir = Path(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    path = _state_path(state_dir, state.conversation_id)
    path.write_text(json.dumps(asdict(state), ensure_ascii=False, indent=2), encoding="utf-8")


def humanize_elapsed(seconds: float | None) -> str | None:
    if seconds is None:
        return None

    if seconds < 0:
        return None

    seconds = max(0, int(seconds))

    if seconds < 90:
        return "1分未満"

    minutes = seconds // 60
    if minutes < 60:
        return f"約{minutes}分"

    hours = minutes // 60
    rem_minutes = minutes % 60
    if hours < 24:
        return f"約{hours}時間{rem_minutes}分" if rem_minutes else f"約{hours}時間"

    days = hours // 24
    rem_hours = hours % 24
    return f"約{days}日{rem_hours}時間" if rem_hours else f"約{days}日"


def classify_elapsed(seconds: float | None) -> str:
    if seconds is None:
        return "first_turn_or_unknown"

    if seconds < 0:
        return "clock_skew_or_out_of_order"
    if seconds < 90:
        return "immediate_followup"
    if seconds < 15 * 60:
        return "short_pause"
    if seconds < 2 * 60 * 60:
        return "medium_pause"
    if seconds < 8 * 60 * 60:
        return "long_pause"
    if seconds < 36 * 60 * 60:
        return "next_day_or_large_gap"
    return "stale_context"


def _parse_hhmm(value: str) -> time:
    hour, minute = value.split(":", 1)
    return time(hour=int(hour), minute=int(minute))


def _time_in_range(t: time, start: time, end: time) -> bool:
    """Return whether t is in [start, end), supporting ranges over midnight."""

    if start <= end:
        return start <= t < end
    return t >= start or t < end


def classify_time_of_day(local_dt: datetime, preferences: UserTimePreferences | None = None) -> str:
    prefs = preferences or UserTimePreferences(timezone_name=str(local_dt.tzinfo))
    t = local_dt.time().replace(second=0, microsecond=0)

    if _time_in_range(t, _parse_hhmm(prefs.deep_night_start), _parse_hhmm(prefs.deep_night_end)):
        return "deep_night"
    if _time_in_range(t, _parse_hhmm(prefs.early_morning_start), _parse_hhmm(prefs.early_morning_end)):
        return "early_morning"
    if _time_in_range(t, time(7, 0), time(11, 0)):
        return "morning"
    if _time_in_range(t, time(11, 0), time(14, 0)):
        return "midday"
    if _time_in_range(t, time(14, 0), time(18, 0)):
        return "afternoon"
    if _time_in_range(t, time(18, 0), _parse_hhmm(prefs.late_night_start)):
        return "evening"
    return "late_night"


def build_time_flags(
    *,
    elapsed_label: str,
    time_of_day: str,
    local_date_changed: bool,
    elapsed_seconds: float | None,
) -> list[str]:
    flags: list[str] = []

    if elapsed_label == "clock_skew_or_out_of_order":
        flags.append("clock_skew_or_out_of_order")

    if local_date_changed:
        flags.append("local_date_changed")

    if time_of_day in {"late_night", "deep_night"}:
        flags.append("night")

    if time_of_day == "early_morning":
        flags.append("early_morning")

    if elapsed_label in {"long_pause", "next_day_or_large_gap", "stale_context"}:
        flags.append("substantial_gap_since_last_turn")

    if elapsed_label == "stale_context":
        flags.append("stale_context")

    if elapsed_seconds is None:
        flags.append("first_turn_or_unknown_previous_turn")

    return flags


def load_preferences(path: str | Path | None = None, *, timezone_name: str | None = None) -> UserTimePreferences:
    if path is None:
        return UserTimePreferences(timezone_name=require_user_timezone(timezone_name))

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "timezone_name" not in data:
        data["timezone_name"] = require_user_timezone(timezone_name)
    return UserTimePreferences(**data)


def build_time_context(
    conversation_id: str,
    *,
    user_timezone: str | None = None,
    state_dir: str | Path = DEFAULT_STATE_DIR,
    current_user_turn_at_utc: datetime | str | None = None,
    preferences: UserTimePreferences | None = None,
    update_state: bool = True,
) -> dict[str, Any]:
    """Build TIME_CONTEXT for the current user turn.

    Prefer passing the platform's user-message `created_at` timestamp as
    `current_user_turn_at_utc`. If omitted, the runtime clock is used.
    """

    timezone_name = require_user_timezone(user_timezone)
    state = load_state(conversation_id, state_dir=state_dir, user_timezone=timezone_name)
    tz = get_zoneinfo(timezone_name)

    if isinstance(current_user_turn_at_utc, str):
        current_user_utc = parse_datetime(current_user_turn_at_utc)
        assert current_user_utc is not None
    elif isinstance(current_user_turn_at_utc, datetime):
        current_user_utc = ensure_aware_utc(current_user_turn_at_utc)
    else:
        current_user_utc = now_utc()

    current_user_local = current_user_utc.astimezone(tz)
    last_user_utc = parse_datetime(state.last_user_turn_at_utc)
    last_assistant_utc = parse_datetime(state.last_assistant_turn_at_utc)

    last_user_local = last_user_utc.astimezone(tz) if last_user_utc else None
    last_assistant_local = last_assistant_utc.astimezone(tz) if last_assistant_utc else None

    elapsed_since_last_user = (
        (current_user_utc - last_user_utc).total_seconds() if last_user_utc else None
    )
    elapsed_since_last_assistant = (
        (current_user_utc - last_assistant_utc).total_seconds() if last_assistant_utc else None
    )

    local_date_changed = (
        last_user_local.date() != current_user_local.date() if last_user_local else False
    )

    prefs = preferences or UserTimePreferences(timezone_name=timezone_name)
    time_of_day = classify_time_of_day(current_user_local, prefs)
    elapsed_label = classify_elapsed(elapsed_since_last_user)
    flags = build_time_flags(
        elapsed_label=elapsed_label,
        time_of_day=time_of_day,
        local_date_changed=local_date_changed,
        elapsed_seconds=elapsed_since_last_user,
    )

    context: dict[str, Any] = {
        "now_utc": current_user_utc.isoformat(),
        "now_local": current_user_local.isoformat(),
        "user_timezone": timezone_name,
        "turn_index": state.turn_index + 1,
        "last_user_turn_at_utc": state.last_user_turn_at_utc,
        "last_user_turn_at_local": last_user_local.isoformat() if last_user_local else None,
        "last_assistant_turn_at_utc": state.last_assistant_turn_at_utc,
        "last_assistant_turn_at_local": last_assistant_local.isoformat() if last_assistant_local else None,
        "elapsed_since_last_user_turn_seconds": elapsed_since_last_user,
        "elapsed_since_last_user_turn_human": humanize_elapsed(elapsed_since_last_user),
        "elapsed_since_last_assistant_turn_seconds": elapsed_since_last_assistant,
        "elapsed_since_last_assistant_turn_human": humanize_elapsed(elapsed_since_last_assistant),
        "elapsed_label": elapsed_label,
        "local_date_changed_since_last_turn": local_date_changed,
        "time_of_day": time_of_day,
        "time_flags": flags,
    }

    if update_state and elapsed_label != "clock_skew_or_out_of_order":
        state.turn_index += 1
        state.last_user_turn_at_utc = current_user_utc.isoformat()
        state.last_interaction_at_utc = current_user_utc.isoformat()
        state.user_timezone = timezone_name
        save_state(state, state_dir=state_dir)

    return context


def mark_assistant_turn(
    conversation_id: str,
    *,
    user_timezone: str | None = None,
    state_dir: str | Path = DEFAULT_STATE_DIR,
    assistant_turn_at_utc: datetime | str | None = None,
) -> TimeState:
    """Update state after the assistant has responded."""

    timezone_name = require_user_timezone(user_timezone)
    state = load_state(conversation_id, state_dir=state_dir, user_timezone=timezone_name)

    if isinstance(assistant_turn_at_utc, str):
        assistant_utc = parse_datetime(assistant_turn_at_utc)
        assert assistant_utc is not None
    elif isinstance(assistant_turn_at_utc, datetime):
        assistant_utc = ensure_aware_utc(assistant_turn_at_utc)
    else:
        assistant_utc = now_utc()

    state.last_assistant_turn_at_utc = assistant_utc.isoformat()
    state.last_interaction_at_utc = assistant_utc.isoformat()
    state.user_timezone = timezone_name
    save_state(state, state_dir=state_dir)
    return state
