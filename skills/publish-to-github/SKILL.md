---
name: publish-to-github
description: Publish a local folder (skill, script, or project) to GitHub: initialize git, commit, create a public/private repo, push, add README and topics, and optionally create a release or fork upstream repos. Use when the user says "publish to github", "push this to github", "create a github repo for X", "fork and publish", or wants to share a local skill/project. Also covers publishing a patched fork of an upstream skill with attribution.
---

# Publish to GitHub

End-to-end workflow for turning a local folder into a published GitHub repository, including forks and patched re-publications.

## When to use

- User says "publish to GitHub", "push this to GitHub", "create a GitHub repo for X"
- User wants to share a local skill/project publicly
- User wants to fork an upstream repo and apply their own patches
- User wants to add README, topics, or a release after publishing

## Prerequisites

- `git` installed (`git --version`)
- `gh` CLI installed and authenticated: `gh auth status` must show "Logged in"
  - If missing: `sudo pacman -S github-cli` (Arch) / `brew install gh` (macOS) / `apt install gh`
  - Auth: `gh auth login --hostname github.com --git-protocol https --web` (device flow; user completes in browser)
- Git identity configured (set if empty):
  ```bash
  git config --global user.name "<name>"
  git config --global user.email "<email>"
  ```
  Or use the GitHub login/email from `gh api user`.

## Security gate (required for skills)

Before publishing any skill, run the `audit-skill` skill on the folder and obtain
an APPROVE or CAUTION verdict. Do not publish a skill with a REJECT verdict
without explicit user consent.

## 分工邊界（與 push-repo / push-router）

- **本 skill 負責 GitHub 產品化**：README/歸屬、`gh repo create`（只建 remote）、fork、topics、release。
- **安全推送一律委派 `push-repo`**：preflight、機密/歷史掃描、大檔/巢狀 repo、`_repo_excluded.tsv` 對帳、commit/push、fresh clone md5 驗證、憑證安全。**本 skill 不自行 `git add -A && push` 繞過驗證**。
- 路由依 `push-router`（parent）之 goal→hook 決策。

## Workflow A — Publish a local folder as a new repo

1. **產品化準備（本 skill）**  
   - 清理明顯雜物/快取（不刪使用者內容）；補 `.gitignore`、`README.md`。  
   - 若為第三方 patched skill，README 必須含 upstream URL、變更內容、原作者 credit/license。

2. **建立 GitHub remote（只建 repo，不直推）**  
   ```bash
   gh repo create <repo-name> --public --source=. --remote=origin
   # 私有改 --private；不要加 --push
   ```
   若 remote 已存在，確認 `git remote get-url origin` 後沿用。

3. **委派安全推送（hook `push-repo`）**  
   依 `push-repo` 執行：Phase 0 決策 → preflight → 排除決策/`_repo_excluded.tsv` → commit/push → `verify_push.py` 全 PASS（`fail=0`）。  
   只有 `push-repo` 驗證通過才繼續。

4. **GitHub 產品化收尾（本 skill）**  
   ```bash
   gh repo edit <owner>/<repo> --add-topic <topic1> --add-topic <topic2>
   gh release create v1.0.0 --title "v1.0.0 — initial release" --notes "<notes>"  # 可選
   ```

## Workflow B — Fork an upstream repo

Use when the user wants to keep upstream credit or contribute back.

```bash
gh repo fork <owner>/<repo> --clone=false
```

This creates `phycomp/<repo>` (or the authenticated user's fork) on GitHub without a local clone. To apply local patches, clone the fork, apply changes, commit, push.

## Workflow C — Publish a patched third-party skill

When publishing a modified version of someone else's skill:

1. Copy the skill folder to a temp working dir.
2. Remove caches/secrets; add `.gitignore`.
3. Write a `README.md` that explicitly states:
   - Upstream source URL
   - What changed (the patch)
   - That credit and license belong to the original authors
4. Follow Workflow A steps 2–7.
5. Optionally fork the upstream repo too (Workflow B) so the patch can be PR'd back.

## Gotchas

- **No `gh` CLI?** Install via package manager first; do not use password auth (GitHub removed it).
- **Git identity missing** → commit fails with "Please tell me who you are"; set `user.name`/`user.email`.
- **`__pycache__` / `*.pyc`** must be removed and gitignored before committing Python skills.
- **Global install of skills** reports `PromptScript: does not support global skill installation` — harmless; OpenCode still gets the skill.
- **Device flow auth** expires (~15 min); rerun `gh auth login` if timed out.
- **Large monorepos** (e.g., awesome-copilot, baoyu-skills) take long to clone; prefer `--clone=false` for forks.
- **License:** always preserve upstream license and credit when re-publishing third-party skills.

## Example: publishing this very workflow

```bash
# (already done once)
gh repo create publish-to-github --public --source=. --remote=origin  # 不直推；交 push-repo 驗證後推送
gh repo edit phycomp/publish-to-github --add-topic agent-skill --add-topic github
gh release create v1.0.0 --title "v1.0.0" --notes "Initial release."
```
