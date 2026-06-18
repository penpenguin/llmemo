# Time Source Priority

## User-turn timestamp

Use this priority order:

1. Explicit host-provided `TIME_CONTEXT`.
2. User message metadata such as `message.created_at`.
3. Server receive timestamp such as `server_received_at`.
4. Runtime/terminal current time.
5. Static system date only for coarse date awareness, not elapsed-time calculation.

## Assistant-turn timestamp

Use this priority order:

1. Platform assistant message metadata.
2. Server send timestamp.
3. Runtime/terminal current time after the response.

## Timezone

Use this priority order:

1. Explicit user profile timezone.
2. Workspace/account timezone setting.
3. User-provided timezone in the current task.
4. A safe default configured by the application.
5. `unknown`; do not pretend to know the user's local time.

The CLI and Python helpers require an explicit IANA timezone when generating local-time `TIME_CONTEXT`. If the priority order resolves to `unknown`, do not call them just to obtain `now_local` or `time_of_day`; ask for a trustworthy timezone, use a host-configured safe default, or omit local time context.

Example values such as `Asia/Tokyo` in commands, JSON, or preferences are examples only. They are not default fallback behavior for an unknown user timezone.

## Terminal caveat

Terminal time is usually the server or sandbox time. Treat it as a way to obtain UTC `now`; do not assume its local timezone is the user's local timezone.
