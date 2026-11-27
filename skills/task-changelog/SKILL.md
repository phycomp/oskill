---
name: task-changelog
description: "常態化變更日誌：每當完成 task、新增/修改/刪除技能、功能變更、重構、bug 修復時，在交付前寫下一筆結構化日誌，維護單一真相來源與索引。Use when the user says 寫日誌, 變更紀錄, 變更日誌, 記錄這次變更, 記一筆, 記下來, 寫一筆, task log, changelog, log this change, record this change, what did we change, 這次改了什麼, 交付紀錄, or whenever any task/feature/skill change is completed and must be logged before delivery. Not for generating release notes from git commits (use changelog-generator instead)."
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# Task Changelog — 常態化變更日誌

本技能把「寫日誌」變成每次交付前的固定動作。本機沒有統一變更日誌；
`changelog-generator` 是從 git commits 產生 release notes，用途不同，不要混用。

## 單一真相來源（Single Source of Truth）

- **每日一檔**：`logs/YYYY-MM-DD-<slug>.md`，一天多筆可放同一檔（用 `##` 分節）或各自一檔（slug 區分）。
- **索引**：`references/log-index.md` 記錄「日期 → 檔案 → 標題」，所有查詢從索引進入。
- **彙總入口**：`CHANGELOG.md` 由索引反向整理，便於人類快速瀏覽最近變更。

> 規則：寫完日誌後**必須**同步更新 `references/log-index.md` 與 `CHANGELOG.md`，否則視為未完成交付。

## 何時寫（觸發時機）

每當下列任一事件發生，**在交付前**寫一筆：

- 完成任何 task（不論大小）
- 新增 / 修改 / 刪除技能（SKILL.md、scripts、references）
- 功能變更、重構、bug 修復
- 索引、文件、流程規則的結構性調整

「只是查資料 / 問問題 / 純對話」不需要寫。拿捏不定時，寫一筆比漏寫好。

## 日誌格式欄位

詳細規範與範例見 `references/format.md`。每筆至少包含：

| 欄位 | 說明 |
|------|------|
| 日期 | `YYYY-MM-DD` |
| 標題 | 一句話講清這次變更 |
| 類型 | `feature` / `refactor` / `fix` / `docs` / `chore`（可複合，如 `refactor + feature`） |
| 涉及技能/檔案 | 列出被新增/修改/刪除的路徑與版本 |
| 變更摘要 | 條列，如實陳述做了什麼（含溯源、出處、決策） |
| 驗證結果 | 實跑過的檢查與結果（PASS/FAIL/OK），不要只寫「應可」 |
| 上下級鏈影響 | 若適用：對技能鏈上級/下級的影響與雙向交叉引用 |
| 待辦/已知限制 | 未解決項、動態值、N/A 揭露 |

## 流程

1. **判斷**：這次工作是否落在「何時寫」清單？是則繼續。
2. **決定 slug**：`<date>-<short-slug>.md`（例：`2026-11-18-thermal-load-chain.md`）。
3. **寫日誌**：依 `references/format.md` 建立或追加 `logs/` 下的檔案。
4. **更新索引**：在 `references/log-index.md` 加一列（日期、標題、類型、檔案連結）。
5. **更新彙總**：在 `CHANGELOG.md` 最上方加一筆摘要（日期 + 標題 + 一句話）。
6. **交付前核對**：路徑、欄位、驗證結果是否如實；索引是否指向存在的檔案。

## 位置

```
/home/sam/.opencode/skills/task-changelog/
├── SKILL.md                     # 本檔：觸發、格式概要、流程、位置
├── references/
│   ├── format.md                # 日誌條目格式規範與範例
│   └── log-index.md             # 所有日誌條目的索引（日期 → 檔案）
├── logs/
│   └── YYYY-MM-DD-<slug>.md     # 每日日誌本體
└── CHANGELOG.md                 # centrally 彙總入口
```

## 刻意不做

- 不從 git commits 自動生成（那是 `changelog-generator`）。
- 不修改既有技能或 `/home/sam/量傳線/` 的檔案；本技能只寫自己的目錄。
- 不虛構驗證結果；沒跑過就寫「未驗證」並列為待辦。
