# 2026-11-24 — push/git family 重整（publish-to-github vs push-repo）

## 動機
使用者要求「比對 publish-to-github vs push-repo 建議如何重整」→ 裁決「直接實作」。以 `push-router` 為父節點，消除安全繞路與職責重疊，不硬合併。

## 決策
- `push-repo` = canonical 安全引擎（preflight/排除/verify/push）；`.agents` 版為 master。
- `publish-to-github` = GitHub 產品化 child（README/gh create remote/fork/topics/release），安全 push 一律委派 `push-repo`。
- `gh repo create` 去 `--push`（只建 remote），避免繞過 `push-repo` 驗證。
- 路由與索引文字標註分工，不將兩者改為 deprecated stub（非純冗餘）。

## 變更
1. `oskill/skills/publish-to-github/SKILL.md` + `.agents` 同步：新增「分工邊界」段、Workflow A 改為「準備→建 remote→hook push-repo→產品化收尾」、移除自行 `git init/add/commit/push`、尾端垃圾行（`EOF`/`echo "written"`）清除、範例去 `--push`。
2. `oskill/skills/push-repo/{SKILL.md, scripts/verify_push.py, references/troubleshooting.md}` 以 `.agents` 增強版同步：憑證唯一真相來源、GIT_ASKPASS `mktemp` 取代 process substitution、safe-read 豁免、404/403/workflow scope 診斷、gotchas。
3. `.agents/skills/push-router/SKILL.md`：goal→hook 表、boundary、skill 表、使用情境標註 canonical / 委派。
4. `.agents/skills/skill-family/SKILL.md`：索引補 `publish-to-github → push-repo`（safe push/verify；不直推）。

## 驗證
- `publish-to-github` `.agents`/`oskill` md5 一致（df92e754...）。
- `push-repo` 5 檔案 `.agents`/`oskill` 全數一致。
- `verify_push.py` ×2 py_compile PASS。
- 敏感面：`--push`/`GIT_ASKPASS=<(` 命中皆為警示文字；無新增 host/eval/token 字面值。
- `__pycache__` untracked 已清除。

## Audit
- 報告：`/home/sam/skill-reports/push-repo-family-20261124.{md,json}`
- Manifest：`/home/sam/skill-reports/manifests/push-repo-family-20261124.sha256`
- Verdict：`APPROVE` / `Low`

## 範圍
- 僅本機改動，**未 commit / push**（依使用者指示）。
- `oskill` 既有無關髒改動 `quant-algo-auto/{README.md,SKILL.md}`、`viz-dboard/SKILL.md` 保持原樣，未混入。
