# Time Classification

## Elapsed-time labels

| Elapsed time | Label | Default behavior |
|---:|---|---|
| Unknown | `first_turn_or_unknown` | Treat as first turn or missing state. |
| Negative | `clock_skew_or_out_of_order` | Flag possible clock skew, duplicated replay, or out-of-order event. Do not emit a normal human-readable pause string for negative elapsed time. |
| 0-90 sec | `immediate_followup` | Continuous turn. Do not mention time. |
| 90 sec-15 min | `short_pause` | Context continues. Usually do not mention time. |
| 15 min-2 hours | `medium_pause` | Light continuity handling if helpful. |
| 2-8 hours | `long_pause` | Briefly restore previous context if needed. |
| 8-36 hours | `next_day_or_large_gap` | Check date-sensitive assumptions. |
| 36+ hours | `stale_context` | Resume from a concise recap and avoid assuming all prior context is fresh. |

## Time-of-day labels

Default local wall-clock classification:

| Local time | Label |
|---|---|
| 02:00-03:59 | `deep_night` |
| 04:00-06:59 | `early_morning` |
| 07:00-10:59 | `morning` |
| 11:00-13:59 | `midday` |
| 14:00-17:59 | `afternoon` |
| 18:00-21:59 | `evening` |
| 22:00-01:59 | `late_night` |

These boundaries are defaults, not moral judgments. Override them with `assets/default_time_preferences.json` or host-specific user preferences if the user's schedule is known.

## Flags

Common `time_flags` values:

- `first_turn_or_unknown_previous_turn`
- `clock_skew_or_out_of_order`
- `local_date_changed`
- `night`
- `early_morning`
- `substantial_gap_since_last_turn`
- `stale_context`
