# Communication / Language
- 本プロジェクトに関する会話は原則として日本語で行います。
- コミットメッセージやコード内コメントは英語でも問題ありません。

# Development Approach (TDD - MUST)
- Strict policy: all code changes follow TDD.
- Red → Green → Refactor in the smallest possible steps.
- Start from the simplest failing test; use triangulation to evolve behavior.
- Write a failing test for any bug before fixing it.
- Prefer fast unit tests with Vitest + jsdom; add E2E only for critical flows.
- Keep production code minimal to satisfy current tests; refactor safely after green.
- Commit in small increments that reflect TDD phases where practical.
