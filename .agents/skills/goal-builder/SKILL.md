---
name: goal-builder
description: Turn rough coding, repo, research, refactor, migration, audit, bug-fix, testing, or documentation requests into a verifiable GOAL.md plus a copy-pasteable Codex /goal command. Use when the user wants to create, draft, tighten, review, or improve a /goal objective; says completion criteria are hard to write; asks for wall-ball questioning before /goal; mentions GOAL.md, done_when, success criteria, verification, stop rules, autonomous Codex work, persistent goals, long-running tasks, or Japanese phrases like 「/goalに渡す」「完了条件」「壁打ち」「停止条件」「検証方法」. Do not use for one-shot explanations, tiny edits, or tasks without a durable evidence-based finish line.
---

# Goal Builder

Convert a fuzzy request into a durable, evidence-checked `GOAL.md` and a short `/goal` launcher. Act as a goal contract designer, not as an implementer.  
Please output GOAL.md as the final deliverable.

## Core contract

A valid goal must define:

- one primary end state;
- allowed scope and forbidden scope;
- constraints and anti-gaming rules;
- concrete `Done when` criteria;
- a fast feedback loop and a final verification gate;
- mechanically detectable stop rules;
- a completion receipt showing evidence, risks, and remaining work.

Default output language: match the user's language. If the user writes Japanese, produce Japanese `GOAL.md` content and keep the slash command prefix as `/goal`.

## Do not execute the work

In this skill, do not implement the feature, fix the bug, run long tasks, deploy, commit, open PRs, or start `/goal` unless the user explicitly asks for activation in an environment that supports it. The normal deliverable is a drafted or updated goal contract.

Read files only when they are needed to make the goal accurate. Prefer read-only inspection of `README`, `AGENTS.md`, `CLAUDE.md`, specs, issues, package files, test config, or existing `SPEC.md`. Please do not modify any files in the repository except for GOAL.md.

## Decide whether `/goal` is appropriate

Use `/goal` when the task is larger than one prompt and has a durable objective, iterative work, and verifiable evidence of completion.

Prefer a normal prompt instead of `/goal` when the task is:

- a simple explanation or Q&A;
- a one-line edit;
- a short code review with no continuation loop;
- pure brainstorming with no acceptance criteria;
- too broad to verify, such as "make the whole repo better".

If `/goal` is not appropriate, output `Better as a normal prompt` with a concise replacement prompt and the reason.

## Operating modes

Choose the smallest mode that fits.

### 1. Interview mode

Use when the request is vague or missing acceptance criteria. Ask at most five targeted questions per round. Prefer questions that force product, architecture, scope, or verification decisions. Do not ask checklist questions whose answers can be safely inferred from repo context.

If a missing answer is low-risk, proceed with an explicit `[Assumption]`. If a missing answer could change product behavior, architecture, data safety, security, permissions, billing, migrations, public API behavior, or maintainability, ask before compiling the final goal.

### 2. Tighten mode

Use when the user already has a draft goal, spec, issue, or plan. Critique it before rewriting. Identify weak spots such as vague verbs, missing scope, missing non-goals, untestable acceptance criteria, fakeable metrics, broad stop rules, and missing final evidence.

### 3. Compile mode

Use when enough information is available. Produce `GOAL.md`, a short `/goal` launcher, assumptions, and a compact quality check.

### 4. Review-only mode

Use when the user asks whether an existing goal is safe or good. Return a scorecard, blocking issues, recommended edits, and a revised draft only if useful.

## Project/context detection

Before asking the user for project facts, infer what you can from the current context or read-only repo inspection.

Look for:

- project type: `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `Package.swift`, `*.xcodeproj`, framework config, docs config;
- repo instructions: `AGENTS.md`, `CLAUDE.md`, `README`, contributing docs;
- verification commands: package scripts, CI config, test config, Makefile, task runner files;
- existing specs: `SPEC.md`, `GOAL.md`, issues, design docs, ADRs;
- sensitive surfaces: auth, permissions, billing, migrations, secrets, production data, external APIs, release/publish automation.

Announce inferred project type and assumptions in one short sentence so the user can correct them.

## Task classification

Classify the goal before drafting. Use the classification to choose the right proof and stop rules.

- Feature implementation
- Bug fix
- Refactor
- Migration
- Test addition or test repair
- Documentation
- Investigation / archaeology
- Audit / review
- UI / behavior / accessibility check
- Release / packaging / deployment preparation
- Other

## Information to gather

Gather only missing information. The required fields are:

1. Objective: what must be true at the end.
2. Context: issue, spec, files, symptoms, expected behavior, known constraints.
3. Scope: files, directories, services, tools, branches, environments, or data the agent may touch.
4. Non-goals: what must not be changed.
5. Constraints: compatibility, API behavior, security, dependencies, style, performance, migration rules.
6. Done when: observable acceptance criteria.
7. Verification: exact commands, manual checks, screenshots, logs, benchmark, review, or artifact inspection.
8. Feedback loop: the fastest useful check during work and the slower final gate.
9. Stop rules: concrete conditions that require user input or should block continuation.
10. Completion receipt: exact evidence the agent must report before declaring done.

## Hard gates

Do not render a final `/goal` until these pass, unless the user explicitly asks for a weak draft labeled as such.

- The objective has one primary end state.
- `Done when` has at least three concrete items for non-trivial implementation work.
- Every `Done when` item names a command, artifact, file path, log, screenshot, behavior, or explicit user confirmation.
- Verification includes at least one exact command or explicit manual check.
- Scope and non-goals are both present for brownfield repos.
- Stop rules are concrete and mechanically detectable.
- Constraints prevent obvious shortcuts and metric-gaming.
- The launcher objective is short enough for the target host; for Codex CLI, keep the `/goal` objective at or below 4,000 characters and put details in `GOAL.md` when needed.

## Vague language to challenge

Push back on vague or oversized phrasing. Ask for a measurable replacement or convert it into a bounded assumption.

Examples to challenge:

- improve, optimize, clean up, make better, polish, harden, fix properly;
- all, everything, entire repo, complete rewrite, fully, thoroughly;
- いい感じに, よしなに, 全部, 徹底的に, いい具合に, 壊れているところ全部;
- tests pass, works, done, production-ready, high quality, fast.

Prefer replacements such as exact files, enumerated cases, measured thresholds, specific commands, user-visible behavior, or reviewable artifacts.

## Anti-gaming defaults

Add relevant `Do not` constraints when the agent could satisfy a metric while violating the intent.

Use these by default when applicable:

- Do not delete, skip, weaken, or rewrite tests merely to make checks pass.
- Do not hide integration failures behind mocks when real integration behavior is required.
- Do not disable build paths, type checks, lint rules, feature flags, or safety checks to claim success.
- Do not broaden scope to make unrelated improvements easier.
- Do not mutate live data, credentials, permissions, billing, production systems, or external accounts without explicit authorization.
- Do not declare completion without exact validation output or clearly labeled manual evidence.
- For visual/UI work, do not fake visual fidelity by embedding, cropping, or copying reference images instead of implementing behavior and design constraints.

## Stop-rule quality

Bad stop rule: `Stop if unclear.`

Good stop rules are concrete:

- a required credential, account, paid service, or production secret is unavailable;
- a destructive migration, data deletion, or irreversible operation appears necessary;
- public API, auth, permissions, billing, or security semantics must change;
- a new dependency, license exposure, or external service is required without prior approval;
- expected source files or specs are missing after read-only discovery;
- verification cannot run because the local environment lacks a documented prerequisite;
- the required change exceeds the approved scope or touches a forbidden path;
- existing tests fail for reasons unrelated to the goal, and fixing them would require changing product behavior or weakening tests.

## Risk tier and review depth

Assign a risk tier and put it in `GOAL.md`.

Low risk: docs, read-only investigation, small local cleanup, narrow tests. Require one self-review.

Medium risk: normal feature work, bug fixes, refactors, generated artifacts, behavior docs. Require focused verification and one adversarial review pass.

High risk: auth, permissions, billing, public API, migrations, data loss, release/publish, packaging, production-facing behavior, broad cross-cutting changes. Require stronger review: at least two clean review passes or explicit human approval before completion, depending on context.

## Working memory for long-running goals

For goals likely to run for hours, include durable tracking files or status artifacts. Use only the minimum necessary.

Recommended:

- `PLAN.md`: current plan, checkpoints, current next action.
- `ATTEMPTS.md`: failed attempts, commands run, outcomes, hypotheses.
- `NOTES.md`: decisions, edge cases, discovered constraints.
- `STATUS.md` or a completion section in `GOAL.md`: concise current state for resume/compaction.

Treat these as operational state, not documentation ceremony. Skip them for short linear tasks.

## GOAL.md output shape

Use this structure unless the user requests a different one.

```md
# Goal

## Objective
One sentence describing the end state.

## Context
Relevant repo, issue, spec, current symptom, expected behavior, and assumptions.

## Scope
What may be changed or inspected.

## Non-goals
What must not be changed in this run.

## Constraints and anti-gaming rules
Hard requirements and forbidden shortcuts.

## Risk tier and review depth
Low / Medium / High, with required review behavior.

## Required first reads
Files, docs, issues, logs, or commands the agent must inspect before editing.

## Work loop
How to choose the next action, how often to verify, and how to record progress.

## Implementation checkpoints
Small reviewable phases.

## Done when
- Observable acceptance criterion 1.
- Observable acceptance criterion 2.
- Observable acceptance criterion 3.

## Verification
### Fast feedback loop
Commands or checks to run repeatedly while iterating.

### Final gate
Commands, manual checks, review, screenshots, logs, or artifacts required before declaring done.

## Working memory
Tracking files or state artifacts to maintain, or a note that none are needed.

## Completion receipt
What to report at completion: changed files, exact commands and exit codes, artifacts, screenshots/logs, review result, assumptions, unresolved risks, and remaining work.

## Stop rules
Concrete blocked conditions requiring user input.

## Open questions
Only unresolved questions that are not blockers, if any.
```

## `/goal` launcher shape

Prefer a short launcher that points to `GOAL.md` rather than stuffing the entire plan into the slash command.

Use this shape:

```text
/goal Read `GOAL.md` first. Complete the Objective and every Done when item while staying within Scope, Non-goals, Constraints, and Stop rules. Use the Work loop, run Verification, maintain Working memory if specified, and do not declare completion until the Completion receipt can be reported with evidence.
```

If no file will be written and the final objective is short enough, a compact inline `/goal` is acceptable:

```text
/goal Outcome: ... Scope: ... Constraints: ... Verify: ... Done when: ... Stop if: ... Completion receipt: ...
```

Do not invent slash-command flags such as token budgets unless the host explicitly supports them. If the user wants a budget, write it as a separate note or as a plain constraint inside `GOAL.md`.

## Quality check before final output

Before showing the final goal, internally check:

- Is `/goal` actually the right tool?
- Does the objective have one end state?
- Are scope and non-goals bounded?
- Are at least three acceptance criteria concrete for non-trivial work?
- Can each acceptance item be verified by a command, file, artifact, log, screenshot, behavior, or explicit confirmation?
- Are fast and final checks separated when useful?
- Are stop rules concrete, not generic?
- Are anti-gaming constraints included where relevant?
- Is the risk tier appropriate?
- Is the launcher short enough for the host?

If the quality check fails, show the blocking gaps and ask only the minimum questions needed to fix them.

## Final response format

When a goal is appropriate, return exactly these sections:

1. `Path to GOAL.md`
2. `/goal に貼る指示`
3. `Assumptions`
4. `Quality check`

Keep explanations short. The user came for a usable goal contract.

When a goal is not appropriate, return:

1. `Better as a normal prompt`
2. `Why not /goal`
3. Optional improved prompt
