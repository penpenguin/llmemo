# SpecKit


```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

```bash
specify init . --ai codex

# CODEX_HOMEの設定が必要？
CODEX_HOME
```

| コマンド                         | 役割（何をするか）                                                                    | 主な入力（あなたが与える情報）                                                      | 主な出力（成果物/更新）                                                                                                                    | 推奨タイミング                                  | コツ/注意点                                                                                                                                                           |
| -------------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/speckit.constitution`          | プロジェクトの原則・開発ガイドラインを作る/更新する（以後の判断軸）([GitHub][1])      | 品質方針、テスト方針、命名、レビュー観点、禁止事項、非機能（性能/セキュリティ）など | 原則ドキュメント（例：`.specify/memory/constitution.md`）を作成/更新([GitHub][1])                                                          | 最初に1回（以降は方針変更時のみ）               | “守るべき制約” を具体に（例：TDD必須、依存追加条件、i18n方針、ログ方針）。曖昧だと後工程でブレます                                                                    |
| `/speckit.specify`               | 何を作るか（要件・ユーザーストーリー）を定義する([GitHub][1])                         | 目的/背景、対象ユーザー、成功条件、スコープ/非スコープ、主要フロー、制約            | `spec.md`（機能仕様）を生成/更新（通常 `specs/<feature>/spec.md`）([GitHub][1])                                                            | 原則の次                                        | “技術”ではなく “価値/振る舞い/境界” を書く（Planで技術に落とす）                                                                                                      |
| `/speckit.clarify`               | 仕様の曖昧点を質問で洗い出して埋める（旧 `/quizme`）([GitHub][1])                     | 追加で決めたい点（例：権限、例外、データ保持、UX、制約）※基本は対話で回答           | `spec.md` の具体化（不足要件の追記・整合）                                                                                                 | **Planの前**（強く推奨）([GitHub][1])           | ここをサボると `/plan` が勝手に仮定して後で手戻り。質問には「決定」と「未決」を分けて答えると良い                                                                     |
| `/speckit.plan`                  | 選んだ技術スタックで実装計画（アーキ/設計判断）を作る([GitHub][1])                    | 技術スタック、デプロイ先、アーキ制約、既存構成、品質要件（テスト/観測/性能）        | `plan.md`（実装計画）＋必要に応じて設計補助ドキュメント（例：`data-model.md` / `research.md` など）([サーバーワークスエンジニアブログ][2]) | Clarifyの後                                     | “採用理由/トレードオフ” を明文化させるとブレ止めになります（後のレビューにも効く）                                                                                    |
| **`/speckit.tasks`（追加）**     | 計画を「実行可能なタスク」に分解する（チェックリスト化）([GitHub][1])                 | `plan.md` と関連設計（必要なら現状コード）                                          | `tasks.md`（フェーズ/依存/並列可否つきのタスク列）([SIOS Tech Lab][3])                                                                     | Planの後                                        | `tasks.md` の粒度は「PR単位」か「安全にレビューできる単位」まで落とす。例として `[P]`（並列可）などの表記が使われます([SIOS Tech Lab][3])                             |
| `/speckit.analyze`               | 成果物（spec/plan/tasks）の整合性・抜け漏れを横断チェック([GitHub][1])                | `spec.md` / `plan.md` / `tasks.md`                                                  | 指摘と修正提案（必要ならドキュメント更新）                                                                                                 | **Tasksの後、Implementの前**([GitHub][1])       | ここで “未カバー要件” が出たら、先に spec/plan/tasks を直してから進むのが最短です                                                                                     |
| **`/speckit.checklist`（追加）** | 独自の品質チェックリストを生成（要件の完全性・明確性・一貫性の検証など）([GitHub][1]) | 「何を満たせばOKか」の観点（例：アクセシビリティ、セキュリティ、i18n、運用）        | チェックリスト（レビュー観点のテンプレ）([GitHub][1])                                                                                      | Clarify〜Implement前の任意タイミング            | “Definition of Done” を作る用途に強い。チーム開発ならレビュー表に転用しやすい                                                                                         |
| `/speckit.implement`             | `tasks.md` を順に実行して実装を進める（コード生成/変更）([GitHub][1])                 | `tasks.md`（＋既存コード/制約）                                                     | コード変更、タスクのチェック進行など                                                                                                       | Analyze後（最終実装フェーズ）([speckit.org][4]) | いきなり全部走らせるより「小さくコミット/レビュー」前提の運用が安定。逸脱が出たら spec/plan に戻る                                                                    |
| `/speckit.taskstoissues`         | `tasks.md` を GitHub Issues に変換して登録（追跡をIssue駆動に寄せる）([Zread][5])     | `tasks.md`、GitHub連携（トークン等）、Issueの粒度/ラベル方針                        | GitHub Issue 群の作成（依存順などを反映しやすい）([Zread][5])                                                                              | Tasks作成後（Implement前でも後でも）            | MCP連携ツール（例：`github/github-mcp-server/issue_write`）を使う調整が入っています([GitHub][6]) 運用ルール（ラベル/担当/マイルストン）も constitution に入れると綺麗 |

[1]: https://github.com/github/spec-kit "GitHub - github/spec-kit:  Toolkit to help you get started with Spec-Driven Development"
[2]: https://blog.serverworks.co.jp/github-spec-kit-guide?utm_source=chatgpt.com "GitHub Spec Kitで始める「仕様駆動開発（Spec-Driven ..."
[3]: https://tech-lab.sios.jp/archives/50783?utm_source=chatgpt.com "GitHub Spec Kit入門｜AIコーディングエージェントで仕様駆動 ..."
[4]: https://speckit.org/ "Spec Kit - AI-Powered Specification-Driven Development Toolkit"
[5]: https://zread.ai/github/spec-kit/15-task-breakdown-and-execution?utm_source=chatgpt.com "Task Breakdown and Execution | github/spec-kit"
[6]: https://github.com/github/spec-kit/releases?utm_source=chatgpt.com "Releases · github/spec-kit"
