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

TypeScript layer defaults:
- ui: components, route handlers, request/response mapping
- application: use cases, orchestration, transaction flow
- domain: entities, value objects, policies, pure functions
- infrastructure: prisma/sql, repositories, http clients, cache, queue

Hard rules:
- domain must not import react, next/*, express, hono, @nestjs/*, @prisma/*, axios, fetch wrappers
- application must not import ui
- ui may call application, but should not own domain policy
- infrastructure implements ports and adapters, but should not define domain policy

When the smallest edit would mix concerns, prefer extraction over appending.