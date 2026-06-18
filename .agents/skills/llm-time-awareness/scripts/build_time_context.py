#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from time_awareness import build_time_context, load_preferences  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Build TIME_CONTEXT for an LLM conversation turn.")
    parser.add_argument("--conversation-id", required=True, help="Stable conversation/thread identifier.")
    parser.add_argument("--timezone", required=True, help="User IANA timezone, e.g. Asia/Tokyo.")
    parser.add_argument("--state-dir", default=".llm_time_state", help="Directory for persisted time state.")
    parser.add_argument(
        "--current-user-turn-at-utc",
        default=None,
        help="Optional timezone-aware ISO-8601 timestamp. Prefer message.created_at when available.",
    )
    parser.add_argument(
        "--preferences",
        default=None,
        help="Optional JSON file containing local time boundary preferences.",
    )
    parser.add_argument(
        "--no-update-state",
        action="store_true",
        help="Build context without saving this user turn as the latest user turn.",
    )
    parser.add_argument(
        "--as-tag",
        action="store_true",
        help="Wrap JSON as <TIME_CONTEXT>...</TIME_CONTEXT> for direct prompt injection.",
    )
    args = parser.parse_args()

    preferences = load_preferences(args.preferences, timezone_name=args.timezone) if args.preferences else None

    context = build_time_context(
        args.conversation_id,
        user_timezone=args.timezone,
        state_dir=args.state_dir,
        current_user_turn_at_utc=args.current_user_turn_at_utc,
        preferences=preferences,
        update_state=not args.no_update_state,
    )

    payload = json.dumps(context, ensure_ascii=False, indent=2)
    if args.as_tag:
        print(f"<TIME_CONTEXT>\n{payload}\n</TIME_CONTEXT>")
    else:
        print(payload)


if __name__ == "__main__":
    main()
