# State Contract

State is stored per `conversation_id`. The default local state directory is `.llm_time_state/`, but host applications should use their own durable state store when available.

## State fields

```json
{
  "conversation_id": "conv_123",
  "turn_index": 4,
  "last_user_turn_at_utc": "2026-06-18T13:42:10+00:00",
  "last_assistant_turn_at_utc": "2026-06-18T13:42:25+00:00",
  "last_interaction_at_utc": "2026-06-18T13:42:25+00:00",
  "user_timezone": "Asia/Tokyo"
}
```

## Update rules

Before an LLM call:

1. Build `TIME_CONTEXT` for the current user turn.
2. Increment `turn_index`.
3. Save `last_user_turn_at_utc`.
4. Save `last_interaction_at_utc` as the current user turn time.

After the LLM call:

1. Save `last_assistant_turn_at_utc`.
2. Save `last_interaction_at_utc` as the assistant response time.

## Out-of-order events

If the current user turn time is earlier than the saved previous user turn time, classify elapsed time as `clock_skew_or_out_of_order` and include the flag for model awareness. By default, do not advance persisted `turn_index`, `last_user_turn_at_utc`, or `last_interaction_at_utc`; otherwise a replayed event can roll conversation state backward.

Only change persisted state for an out-of-order event when the host explicitly chooses a recovery action:

- Ignore replay: keep persisted state unchanged and use the flag only for the current LLM call.
- Accept replay: intentionally overwrite state because the host has determined the older event is canonical.
- Reset state: clear or replace the conversation state after host-level reconciliation.

## Privacy note

The state stores timestamps and conversation identifiers. Avoid storing raw message content in this state file.
