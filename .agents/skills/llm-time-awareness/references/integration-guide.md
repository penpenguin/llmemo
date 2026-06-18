# Integration Guide

## Recommended flow

```text
User message arrives
  ↓
Read platform metadata: message.created_at / server_received_at
  ↓
Run scripts/build_time_context.py or build_time_context(...)
  ↓
Inject <TIME_CONTEXT> JSON into the LLM call
  ↓
LLM responds using TIME_CONTEXT only when useful
  ↓
Run scripts/mark_assistant_turn.py or mark_assistant_turn(...)
```

## Message injection example

```json
[
  {
    "role": "system",
    "content": "Use TIME_CONTEXT as the source of truth for temporal chat context. Do not mention it unless it improves the answer."
  },
  {
    "role": "system",
    "content": "<TIME_CONTEXT>\n{ ... }\n</TIME_CONTEXT>"
  },
  {
    "role": "user",
    "content": "続きをお願い"
  }
]
```

## CLI example

```bash
python scripts/build_time_context.py \
  --conversation-id conv_123 \
  --timezone Asia/Tokyo \
  --current-user-turn-at-utc 2026-06-18T13:42:10Z \
  --as-tag
```

## Python example

```python
import json
from time_awareness import build_time_context, mark_assistant_turn

ctx = build_time_context(
    "conv_123",
    user_timezone="Asia/Tokyo",
    current_user_turn_at_utc="2026-06-18T13:42:10Z",
)

messages = [
    {
        "role": "system",
        "content": "Use TIME_CONTEXT only when it improves the answer.",
    },
    {
        "role": "system",
        "content": "<TIME_CONTEXT>\n"
        + json.dumps(ctx, ensure_ascii=False, indent=2)
        + "\n</TIME_CONTEXT>",
    },
]

# Call the LLM here.

mark_assistant_turn("conv_123", user_timezone="Asia/Tokyo")
```

## Metadata vs terminal time

Prefer metadata for the user's message timestamp because it describes when the turn actually happened. Use terminal/runtime time as a fallback or for assistant response time.

If the runtime is hosted in another region, do not treat the terminal timezone as the user's timezone. Get a UTC timestamp from the runtime and convert it through the user's IANA timezone.
