#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from time_awareness import mark_assistant_turn  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Record the assistant response time for a conversation.")
    parser.add_argument("--conversation-id", required=True)
    parser.add_argument("--timezone", required=True)
    parser.add_argument("--state-dir", default=".llm_time_state")
    parser.add_argument(
        "--assistant-turn-at-utc",
        default=None,
        help="Optional timezone-aware ISO-8601 assistant timestamp. Defaults to runtime now.",
    )
    args = parser.parse_args()

    state = mark_assistant_turn(
        args.conversation_id,
        user_timezone=args.timezone,
        state_dir=args.state_dir,
        assistant_turn_at_utc=args.assistant_turn_at_utc,
    )
    print(json.dumps(asdict(state), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
