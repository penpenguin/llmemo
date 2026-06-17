---
name: ts-soc-plan
description: Before editing TypeScript code, detect mixed concerns and propose file/module boundaries. Use this when a change touches UI, application flow, domain rules, persistence, transport, or would enlarge an existing file.
---

Goal:
Keep one primary concern per file and one primary reason to change per file.

Use this skill when:
- the task touches React/Next route handlers and business rules together
- the task touches domain logic and Prisma/DB/HTTP together
- the target file is already broad or likely to exceed the file-size threshold
- the request says "just add this here" to an already mixed file

Before writing code, produce:
1. Concern map
2. Proposed file boundaries
3. Allowed dependency direction
4. Extraction sequence
5. Risk notes

Planning scope:
- Inspect the target file, imports, callers, and nearby tests before finalizing boundaries.
- If the contents are not available yet, label the concern map and boundaries as provisional, list what must be inspected, and do not infer existing concerns from the filename alone.
- Even when provisional, still emit all five planning sections and list ui / transport-facing, application, domain, and infrastructure entries when they are relevant.
- If no existing layer or module conventions are found, propose concrete provisional file paths using the feature name and mark them replaceable after repo conventions are inspected.
- For urgent or explicitly small fixes in an already mixed file, plan the smallest extraction that isolates the behavior being changed first; defer broader layer cleanup unless it is required for the fix.

TypeScript layer defaults:
- ui / transport-facing: components, route handlers, middleware, request/response mapping
- application: use cases, orchestration, transaction flow
- domain: entities, value objects, policies, pure functions
- infrastructure: prisma/sql, repositories, http clients, cache, queue

For non-React HTTP APIs such as Express, Hono, or Nest, treat route handlers, middleware, request parsing, and response mapping as the ui / transport-facing boundary.

Hard rules:
- domain must not import react, next/*, express, hono, @nestjs/*, @prisma/*, axios, fetch wrappers
- application must not import ui
- ui may call application, but should not own domain policy
- infrastructure implements ports and adapters, but should not define domain policy

When the smallest edit would mix concerns, prefer extraction over appending.
