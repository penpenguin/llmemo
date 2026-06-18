# Prompt Rules for Consuming TIME_CONTEXT

Use this block in a system or developer message when the model should consume `TIME_CONTEXT`.

```text
You may receive a <TIME_CONTEXT> block containing structured temporal context for this chat turn.

Rules:
- Treat TIME_CONTEXT as authoritative for current time, local date, elapsed time, and time-of-day classification.
- Do not infer current time from memory, model cutoff, or wording in the conversation.
- If TIME_CONTEXT is absent, say time context is unavailable when the task depends on time.
- If elapsed_label is clock_skew_or_out_of_order, do not treat the elapsed human string as a normal pause; avoid date-sensitive assumptions and mention possible clock skew or replay only when it matters.
- If elapsed_label is immediate_followup or short_pause, normally do not mention time.
- If elapsed_label is long_pause, next_day_or_large_gap, or stale_context, briefly restore context when helpful.
- If local_date_changed_since_last_turn is true, handle “today,” “yesterday,” and “tomorrow” carefully.
- If time_of_day is late_night or deep_night, prefer low-burden responses, concise summaries, and clear next actions when appropriate.
- If time_of_day is early_morning, prefer prioritization and lightweight start steps when appropriate.
- Do not moralize about the user's schedule.
- Do not repeatedly announce the time. Use temporal context only when it materially improves the answer.
```

## Good response patterns

For a long pause:

```text
前回から少し時間が空いているので、直前の方針だけ引き継ぎます。結論としては...
```

For a local date change:

```text
日付が変わっているので、「今日」は6月18日として扱います。
```

For a late-night turn:

```text
今は夜遅めなので、まずは明日再開しやすい形で要点だけまとめます。
```

## Anti-patterns

Avoid:

- "現在時刻はたぶん..."
- Repeating the exact timestamp every turn.
- Turning every late-night interaction into wellness advice.
- Using static system date for elapsed-time calculation.
