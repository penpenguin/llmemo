---
name: llm-time-awareness
description: Generate and use structured TIME_CONTEXT for LLM chat turns, including current time, elapsed time since previous turns, local date changes, and time-of-day cues. Use when a workflow needs time-aware conversation continuity, metadata timestamps, terminal clock fallback, or temporal UX adjustment.
---

# LLM Time Awareness Skill

## Purpose

Use this skill when a chat workflow needs the assistant to understand temporal context across turns: current local time, elapsed time since the previous user or assistant turn, local date changes, and time-of-day cues such as early morning, late night, or a stale conversation gap.

The skill must not ask the model to guess time. It creates a deterministic `TIME_CONTEXT` object from trusted metadata or a runtime clock, then makes the model use that object only when it improves the response.

## Files to use

- `scripts/build_time_context.py`: CLI entry point for creating `TIME_CONTEXT` before an LLM call.
- `scripts/mark_assistant_turn.py`: CLI entry point for recording the assistant response time after the LLM call.
- `src/time_awareness/context.py`: Python helper library used by the scripts.
- `assets/time_context.schema.json`: JSON Schema for the generated context.
- `assets/default_time_preferences.json`: Default time-of-day boundaries.
- `references/integration-guide.md`: How to inject the context into chat messages.
- `references/prompt-rules.md`: Rules the model should follow when consuming `TIME_CONTEXT`.
- `references/time-classification.md`: Default elapsed-time and time-of-day classifications.
- `references/state-contract.md`: State fields and update rules.
- `references/time-source-priority.md`: Priority order for metadata, server time, and fallback clocks.

## Trigger conditions

Use this skill when the user or application asks for any of the following:

- Awareness of elapsed time between chat turns.
- Behavior changes for late night, early morning, day changes, long pauses, or stale context.
- A reusable skill or workflow that injects temporal metadata into LLM calls.
- Deterministic time handling based on `message.created_at`, server metadata, terminal time, or a stored conversation state.

Do not use this skill for unrelated scheduling, calendar edits, or live weather/timezone lookup unless the task explicitly requires chat-turn temporal context.

## Inputs

Required inputs for generating a new local-time `TIME_CONTEXT`:

1. `conversation_id`: stable identifier for a conversation or thread.
2. `user_timezone`: explicit IANA timezone name, for example `Asia/Tokyo`.
3. `state_dir`: directory used to persist per-conversation state.

Preferred input:

1. `current_user_turn_at_utc`: timezone-aware ISO-8601 timestamp from message metadata, if available.

If `user_timezone` is unknown, do not fabricate `now_local`, `time_of_day`, or local date-change behavior by relying on a CLI/API default. Ask the host for a trustworthy timezone, use an explicitly configured application default, or skip generating `TIME_CONTEXT` and tell the model that local time context is unavailable when the task depends on it.

This also applies to lower-level helpers such as `load_state(...)` and `load_preferences(...)`: pass an explicit timezone when creating new state or default preferences. `Asia/Tokyo` in examples is only an example value, not a fallback.

Time source priority:

1. Explicit `TIME_CONTEXT` supplied by the host application.
2. Platform message metadata such as `message.created_at`.
3. Server receive timestamp such as `server_received_at`.
4. Terminal/runtime clock, converted through UTC.
5. Static system date only as a last resort, and never for precise elapsed-time calculation.

## Procedure

Before each LLM call:

1. Get the current user-turn timestamp. Prefer message metadata over runtime `now`.
2. Load the previous state for `conversation_id`.
3. Convert current and previous timestamps to UTC.
4. Convert the current timestamp to the user timezone.
5. Calculate elapsed seconds since the previous user turn and previous assistant turn.
6. Detect whether the local date changed since the previous user turn.
7. Classify elapsed time and local time of day.
8. Emit a JSON `TIME_CONTEXT` object.
9. Inject `TIME_CONTEXT` into the LLM call as a high-priority context message.

After the assistant responds:

1. Record the assistant response timestamp with `scripts/mark_assistant_turn.py` or `mark_assistant_turn(...)`.
2. Persist `last_assistant_turn_at_utc` and `last_interaction_at_utc`.

## Output contract

The generated object should conform to `assets/time_context.schema.json` and include at least:

```json
{
  "now_utc": "2026-06-18T13:42:10+00:00",
  "now_local": "2026-06-18T22:42:10+09:00",
  "user_timezone": "Asia/Tokyo",
  "turn_index": 18,
  "elapsed_since_last_user_turn_human": "約4時間36分",
  "elapsed_label": "long_pause",
  "local_date_changed_since_last_turn": false,
  "time_of_day": "late_night",
  "time_flags": ["night", "substantial_gap_since_last_turn"]
}
```

## Model behavior rules

When consuming `TIME_CONTEXT`, the assistant should:

- Treat `TIME_CONTEXT` as the source of truth for current time and elapsed time.
- Never infer the current time from memory or conversation wording.
- Avoid mentioning time for immediate follow-ups unless the user asked about time.
- Briefly restore context after a long pause or stale gap.
- Be careful with relative dates when `local_date_changed_since_last_turn` is true.
- Use late-night or early-morning cues to reduce user burden, not to moralize or nag.
- Prefer concise summaries and next actions when the user returns after a large gap.
- Say that time context is unavailable if the host did not provide a trustworthy time source or timezone.

See `references/prompt-rules.md` for a fuller prompt block.

## How to run

Generate context before the LLM call:

```bash
python scripts/build_time_context.py \
  --conversation-id example-conversation \
  --timezone Asia/Tokyo
```

`--timezone` is required. The CLI intentionally fails without it so the host does not silently invent a user's local time.

Use metadata when available:

```bash
python scripts/build_time_context.py \
  --conversation-id example-conversation \
  --timezone Asia/Tokyo \
  --current-user-turn-at-utc 2026-06-18T13:42:10Z
```

Mark the assistant turn after the LLM response:

```bash
python scripts/mark_assistant_turn.py \
  --conversation-id example-conversation \
  --timezone Asia/Tokyo
```

## Validation

Run:

```bash
python scripts/validate_skill_bundle.py .
python -m pytest tests
```

The validation script checks that the bundle has one top-level `SKILL.md`, required frontmatter, and the expected skill folders.
