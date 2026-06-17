---
name: skill-improver
description: Improve a Codex or Agent Skill by empirically evaluating it with fresh subagents across fixed median, edge, and hold-out scenarios, then applying minimal one-theme patches.
---

# Skill Improver

Use this skill when the user asks to improve, tune, review, harden, debug, or make more reproducible a Codex/Agent Skill, especially a `SKILL.md` workflow.

The goal is not to make the skill sound better. The goal is to make a fresh agent succeed with less ambiguity, fewer hidden assumptions, and more repeatable outputs.

## Inputs

Required:
- Target skill path, usually `.../SKILL.md`.

Optional:
- Intended use cases.
- User-provided evaluation scenarios.
- Maximum iterations. Default: 3.
- Whether to edit files directly. Default: propose a patch first unless the user clearly asked for edits.
- Whether to produce an evaluation log file. Default: no durable log unless asked.

If the target skill path is missing, ask for it. If scenarios are missing, generate them from the target skill's `name`, `description`, and body.

## Non-negotiable rules

- Do not judge the target skill only by rereading it yourself.
- Do not let the same evaluator agent retry after seeing previous feedback.
- Do not change the evaluation scenarios or checklist after baseline results, except when adding a separate hold-out scenario.
- Do not patch multiple unrelated themes in one iteration.
- Do not optimize for shorter text if that removes required examples, decision rules, or error handling.
- Do not fabricate metrics. If token counts, tool call counts, elapsed time, or retry counts are unavailable, write `unavailable`.
- Evaluator subagents must not edit the target skill. They only execute/evaluate and report. The parent agent aggregates and patches.

## Workflow

### 1. Static preflight

Read the target skill and inspect nearby files such as `references/`, `scripts/`, `assets/`, and `agents/openai.yaml` when present.

Check:
- Front matter has `name` and `description`.
- `description` clearly says when the skill should and should not trigger.
- The body covers the scope promised by `description`.
- Required inputs and outputs are explicit.
- Commands, files, config paths, and expected artifacts are concrete.
- References are discoverable from the main `SKILL.md`.
- Critical success criteria are present or inferable.
- Error paths and fallback behavior are described.

Record preflight findings, but do not patch yet.

### 2. Freeze evaluation scenarios

Create at least three scenarios unless the user provided scenarios:

1. `median`: a normal, expected use case.
2. `edge`: a realistic edge case with missing context, unusual repo shape, conflicting constraints, or partial failure.
3. `hold-out`: a scenario not used to decide the first patch. Use it after at least one patch to detect overfitting.

For each scenario, define a requirement checklist with at least one `[critical]` item. A run fails if any `[critical]` item is not satisfied.

Keep the scenarios and checklist stable across iterations. Show them briefly before dispatch if the user has not already approved a similar evaluation loop.

### 3. Spawn fresh evaluator subagents

Spawn one fresh subagent per active scenario. Use separate subagent threads. Ask each evaluator to treat the target skill as if it were reading it for the first time.

Use this evaluator prompt template:

```text
You are an independent evaluator for a Codex/Agent Skill. Do not edit files. Do not use the parent agent's interpretation of the skill. Read the target skill as a fresh agent would.

Target skill path:
<TARGET_SKILL_PATH>

Scenario:
<SCENARIO>

Requirement checklist:
<CHECKLIST_WITH_CRITICAL_TAGS>

Task:
1. Read the target skill and any referenced local resources that the skill itself tells you to use.
2. Execute the scenario mentally or in the repository as appropriate, without modifying the target skill.
3. Produce the requested artifact or a faithful execution summary.
4. Report exactly in the structure below.

Report structure:
- Scenario name:
- Outcome: success | partial | failure
- Artifact or execution summary:
- Requirement results: each checklist item as pass | partial | fail, with reason
- Critical failures:
- Ambiguities: unclear wording, missing definitions, missing decision rules
- Discretionary fills: choices you had to make because the skill did not specify them
- Rework/retries: count and reason, or unavailable
- Files read:
- Tools/commands used: count and list, or unavailable
- Elapsed time: if visible, otherwise unavailable
- Suggested minimal fix: one concrete change to the target skill
```

If subagents cannot be spawned in the current environment, stop and tell the user that empirical evaluation was not run. Offer a manual fallback prompt for separate Codex sessions. Do not replace subagent evaluation with self-review.

### 4. Aggregate results

Create an iteration report with:
- Score table by scenario.
- Critical failures.
- Ambiguities grouped by root cause.
- Discretionary fills grouped by missing rule.
- Tool/command/read count anomalies when available.
- The single highest-leverage patch theme.

Classify root causes using this taxonomy:
- trigger mismatch: `description` promises something the body does not support
- missing input contract: user/repo prerequisites are unclear
- missing output contract: expected artifact shape is unclear
- missing decision rule: evaluator had to choose among valid alternatives
- missing command/config example: exact command or file content is absent
- missing environment assumption: versions, tools, OS, permissions, or sandbox expectations are absent
- reference discoverability: evaluator had to hunt through references or missed them
- error handling gap: failure path or recovery instruction is missing
- overbroad scope: skill tries to cover too many unrelated jobs
- under-specified edge case: median works but realistic edge case fails

### 5. Patch one theme only

Choose one patch theme by this priority:
1. Any `[critical]` failure.
2. Ambiguity that caused divergent evaluator behavior.
3. Discretionary fill that affects user-visible output or file changes.
4. Missing minimal example for commands/configs.
5. Reference discoverability or efficiency issue.

Apply the smallest patch that resolves that theme. Prefer adding:
- exact input/output contracts,
- decision tables,
- minimal complete examples,
- explicit command/file paths,
- clear fallback/error behavior,
- references index lines saying when to read each reference.

Avoid broad rewrites unless the same class of failure persists for 3 iterations.

### 6. Re-evaluate with fresh subagents

After patching, spawn new evaluator subagents for the same scenarios. Do not reuse old subagent threads.

Compare before vs after:
- critical pass rate,
- total pass/partial/fail count,
- number of ambiguities,
- number of discretionary fills,
- retries/rework when available,
- tools/commands/read counts when available,
- elapsed time when available.

Run the hold-out scenario after the first patch or before final recommendation. If hold-out drops materially while trained scenarios improve, flag likely overfitting and revert or generalize the patch.

### 7. Stop conditions

Stop when one of these is true:
- All critical requirements pass and two consecutive iterations produce no new material ambiguities.
- Improvement is negligible: score improves by 3 percentage points or less and ambiguity count does not materially decrease.
- Three iterations still show the same root-cause class; recommend structural rewrite instead of more patching.
- The user-specified iteration budget is exhausted.

### 8. Final response format

Return:

```text
## Summary
<one paragraph>

## Evaluation scenarios
<table or compact list>

## Iteration results
<before/after scores and critical status>

## Changes made or proposed
<one-theme patches, with file paths>

## Remaining risks
<overfitting, unsupported environment assumptions, missing metrics, unresolved edge cases>

## Next recommended action
<one concrete next step>
```

If edits were made, include exact files changed. If no empirical subagent evaluation was run, say so explicitly and provide the manual evaluator prompt instead.
