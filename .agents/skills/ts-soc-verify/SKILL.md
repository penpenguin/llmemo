---
name: ts-soc-verify
description: Verify TypeScript changes against separation-of-concerns rules and file-size limits. Use this after any non-trivial code edit, extraction, or new file creation.
---

## Tooling contract

This skill expects each TypeScript package being verified to provide:

- npm package:
  - `dependency-cruiser` installed as a devDependency
- dependency-cruiser config at that package root:
  - `.dependency-cruiser.cjs`
  - `.dependency-cruiser.js`
  - `.dependency-cruiser.mjs`
  - `.dependency-cruiser.json`

Preferred config file:
- `.dependency-cruiser.cjs`

Preferred npm script:
- `verify:soc`

Preferred command:
```bash
npm run verify:soc
```

Run commands from the package directory that owns the TypeScript changes. In a
monorepo, identify package ownership from changed file paths:
- if all changed TypeScript files are under one package root containing
  `package.json`, verify that package
- if changed TypeScript files span multiple package roots, check and run
  verification for each affected package separately
- if the package root is unclear, report `Unable to verify` under Blockers and
  ask for the package path needed to rerun this skill

Determine changed TypeScript paths from the user-provided diff or PR diff when
available. Otherwise, from the repository root, use the current working tree
against `HEAD`: `git diff --name-only HEAD` plus
`git ls-files --others --exclude-standard` for untracked files. If multiple
`package.json` files are ancestors of a changed file, use the nearest ancestor
as the package root unless a workspace config clearly assigns ownership
elsewhere.

Before running verification, check the tooling contract in the package where
the TypeScript change lives:
- `package.json` exists
- `verify:soc` script exists
- `dependency-cruiser` is available as a devDependency
- one dependency-cruiser config file exists for that package

If any of these are missing, do not invent a fallback verifier. Report
`Unable to verify` under Blockers with the missing prerequisite and the next
action needed to rerun this skill.

## Verification

Run:
- npm run verify:soc

Then review the same diff scope used to identify changed TypeScript paths and
report:
1. Blockers
2. Warnings
3. Residual debt

Use only `verify:soc` output, the dependency-cruiser config, or an explicit
project convention as evidence for soft and hard file-size thresholds. If the
threshold is not visible, report file-size status as undetermined; do not infer
soft or hard violations from line counts alone.

Blockers:
- domain imports ui or infrastructure
- application imports ui or concrete infrastructure
- new circular dependency
- any file exceeds the hard size limit
- business rules were added inside component/route/repository files

Warnings:
- any file exceeds the soft size limit
- utility modules accumulating unrelated helpers
- feature internals leaking across boundaries
