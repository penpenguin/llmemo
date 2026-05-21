---
name: ts-soc-verify
description: Verify TypeScript changes against separation-of-concerns rules and file-size limits. Use this after any non-trivial code edit, extraction, or new file creation.
---

## Tooling contract

This skill expects the target repository to provide:

- npm package:
  - `dependency-cruiser` installed as a devDependency
- dependency-cruiser config at repository root:
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

## Verification

Run:
- npm run verify:soc

Then review the diff and report:
1. Blockers
2. Warnings
3. Residual debt

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