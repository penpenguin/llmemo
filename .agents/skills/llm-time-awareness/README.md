# LLM Time Awareness Skill

A reusable skill bundle for generating and injecting structured `TIME_CONTEXT` into LLM chat workflows.

This package follows the common skill bundle layout: one top-level folder with a required `SKILL.md`, plus optional `scripts/`, `references/`, `assets/`, and `agents/` directories.

## Directory layout

```text
llm-time-awareness/
├── SKILL.md
├── README.md
├── pyproject.toml
├── requirements.txt
├── agents/
│   └── openai.yaml
├── assets/
│   ├── default_time_preferences.json
│   ├── example_messages.json
│   ├── example_time_context.json
│   └── time_context.schema.json
├── references/
│   ├── integration-guide.md
│   ├── prompt-rules.md
│   ├── state-contract.md
│   ├── time-classification.md
│   └── time-source-priority.md
├── scripts/
│   ├── build_time_context.py
│   ├── mark_assistant_turn.py
│   └── validate_skill_bundle.py
├── src/
│   └── time_awareness/
│       ├── __init__.py
│       └── context.py
└── tests/
    └── test_context.py
```

## What it does

The skill creates a deterministic JSON object that tells the LLM:

- what time it is in UTC and the user's local timezone;
- how much time elapsed since the previous user turn;
- how much time elapsed since the previous assistant turn;
- whether the local date changed;
- whether the turn happens in early morning, late night, deep night, etc.;
- whether the chat should be treated as continuous, resumed, next-day, or stale.

The LLM then uses this context only when it helps the user experience.

## Minimal usage

```bash
python scripts/build_time_context.py \
  --conversation-id example-conversation \
  --timezone Asia/Tokyo
```

With platform metadata:

```bash
python scripts/build_time_context.py \
  --conversation-id example-conversation \
  --timezone Asia/Tokyo \
  --current-user-turn-at-utc 2026-06-18T13:42:10Z
```

After the assistant responds:

```bash
python scripts/mark_assistant_turn.py \
  --conversation-id example-conversation \
  --timezone Asia/Tokyo
```

## Python usage

```python
from time_awareness import build_time_context, mark_assistant_turn

ctx = build_time_context(
    "example-conversation",
    user_timezone="Asia/Tokyo",
    current_user_turn_at_utc="2026-06-18T13:42:10Z",
)

# Inject ctx into the model call as <TIME_CONTEXT>...</TIME_CONTEXT>.

mark_assistant_turn("example-conversation", user_timezone="Asia/Tokyo")
```

## Packaging note

When zipping for skill upload or distribution, zip the top-level directory so the archive contains exactly one skill folder and exactly one `SKILL.md` / `skill.md` file.
