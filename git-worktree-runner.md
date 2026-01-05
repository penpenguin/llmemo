# git-worktree-runner
https://github.com/coderabbitai/git-worktree-runner

```bash
git clone https://github.com/coderabbitai/git-worktree-runner.git
cd ./git-worktree-runner
sudo ln -s "$(pwd)/bin/git-gtr" /usr/local/bin/git-gtr

# --global (~/.gitconfig )
cd ${project dir}
gtr config set gtr.editor.default vscode
gtr config set gtr.ai.default codex
gtr config set gtr.worktrees.dir .worktrees
gtr config add gtr.copy.exclude "**/.env"
gtr config add gtr.hook.postCreate 'cd "$WORKTREE_PATH" && npm ci'
gtr config add gtr.hook.postCreate 'uvx --from git+https://github.com/oraios/serena serena project index'
gtr config add gtr.hook.postCreate 'git commit --allow-empty -m "pr commit" && git push -u origin "$BRANCH" && gh pr create --base "$BASE_BRANCH" --head "$BRANCH" --title "$BRANCH" --assignee @me --body "Draft PR for $BRANCH (auto-created from git-worktree-runner postCreate hook)." --draft'
```

```bash
# 作る・開く・AI起動・片付け
gtr new <branch>          # <branch> 用の作業ディレクトリ(worktree)を作成
gtr editor <branch>       # そのworktreeをエディタで開く
gtr ai <branch>           # そのworktreeでAIツールを起動
gtr rm <branch>           # worktreeを削除（必要なら --delete-branch）

# 移動・一覧
cd "$(git gtr go <branch>)"   # worktreeのパスへジャンプ
gtr list                  # すべてのworktreeを一覧

# 設定（1回やればOKが理想）
gtr config set gtr.editor.default cursor
gtr config set gtr.ai.default claude

# フック（作成直後に自動実行する処理を積む例）
gtr config add gtr.hook.postCreate "npm ci"
gtr config add gtr.hook.postCreate "npm run build"

# 診断・環境確認
gtr doctor                # 依存や環境のヘルスチェック
gtr adapter               # 使えるエディタ/AIアダプタの一覧
gtr help                  # ヘルプ
gtr version               # バージョン
```
