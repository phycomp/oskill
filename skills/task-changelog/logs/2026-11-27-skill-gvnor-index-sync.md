# 2026-11-27 — skill-gvnor 觸發微測與索引同步

- **日期**：2026-11-27
- **標題**：skill-gvnor description 微測 6/6 通過；allow-list SSOT → chain-skill → skill-family 索引同步完成
- **類型**：`docs + chore + refactor`

## 涉及技能／檔案

修改：
- `/home/sam/.config/skill-timer/self-developed.list`（SSOT，新增 `skill-gvnor` 一列，33→34）
- `/home/sam/.agents/skills/chain-skill/SKILL.md`（inventory 更新 `skill-crud` 列 + 新增 `skill-gvnor` 列 + Logic check 一行）
- `/home/sam/.agents/skills/skill-family/SKILL.md`（Index 新增 `skill-gvnor` 列 + Routing 一條 + Version 1.2.0→1.3.0 + Logic check 一行）
- `/home/sam/.opencode/skills/task-changelog/{logs,CHANGELOG.md,references/log-index.md}`（本筆）

新增：
- `/home/sam/.agents/skills/skill-gvnor/tests/test_index_sync.py`（7 項索引同步契約測試）

證據：
- `~/skill-reports/chain-skill-gvnor-index-{pre,post}-20261127-*.md` 與 manifests
- `~/skill-reports/skill-family-gvnor-index-{pre,post}-20261127-*.md` 與 manifests
- `~/skill-reports/manifests/self-developed-list-gvnor-index-pre.bak`
- `~/skill-reports/evidence/skill-gvnor-index-sync-20261127.md`

## 變更摘要

1. **description 微測（writing-skills micro-test）**：派 fresh-context subagent 只看 frontmatter description 對 6 個提示判斷 → **6/6 正確**（3 should-trigger 全 YES、3 near-miss 全 NO）。最大 near-miss 風險是題 6「明確點名 writing-skills 寫新技能」，靠「意圖橫跨兩個以上技能治理技能」擋住；subagent 建議可補「不知如何取捨／統一分派」讓定位更明確——**本輪不改**（6/6 已達標，避免為未觀察到的失敗做過度修正）。
2. **索引同步（SSOT 順序）**：先改 allow-list，再同步 `chain-skill` Inventory 與 `skill-family` Index／Routing／Version Log。這完成上一輪使用者裁決「索引同步留到下一輪」。
3. **別名維持文件化**：`inspect-skill`→`chain-skill`（已改名）、`inspec-skill`（現行）的指向**未改**；`skill-family` 仍把 `inspect-skill` 列在「永不 push」清單——與 `skill-gvnor` 的別名對照表並存，不視為衝突（一個是 push 黑名單、一個是路由現況說明）。

## 驗證結果（實跑）

| Gate | 結果 |
|---|---|
| 微測 | fresh-context subagent，6/6 正確（含 3 near-miss 全 NO） |
| Gate 1 Pre-audit | `chain-skill` 7/100 LOW SAFE（1 finding LP3 MEDIUM，verdict APPROVE）；`skill-family` 0/100 LOW SAFE（0 findings，verdict APPROVE） |
| Gate 2 RED | `tests/test_index_sync.py` → 7 項中 **6 失敗、1 通過**（`test_alias_unchanged` 本來就該 PASS） |
| Gate 3 GREEN | 索引同步後 `test_index_sync.py` **7/7 OK**；既有 `test_contract.py` **12/12 OK**（無回歸） |
| Gate 4 Cleanup | 清除 `tests/__pycache__`／`.pyc` |
| Gate 5 Post-audit | `chain-skill` 7/100（finding 同 pre）、`skill-family` 0/100；皆 verdict APPROVE，無新 finding |
| Gate 5 Drift | 兩技能皆 `CHANGED SKILL.md`（預期）；allow-list diff 僅 `> skill-gvnor` 一列 |

## 上下級鏈影響

- `skill-gvnor` 已進入 allow-list SSOT 與兩個索引表，成為正式 self-developed skill；`skill-family` v1.3.0 的 Routing 新增技能治理家族入口。
- `chain-skill` inventory 同步反映 `skill-crud` R/U 已 hook `skill-gvnor`，消除「skill-crud 為合併全文」的過時說法。
- 本輪未改任何 child 技能規則，只改索引／版本紀錄。

## 待辦／已知限制

1. **完整 TDD 壓力情境仍未跑**：micro-test 只驗證 wording（writing-skills 明確說「micro-test 不取代紀律型技能的壓力情境」）。仍需 3+ 複合壓力（時間／沉沒成本／權威）＋no-guidance 控制組、每變體 ≥5 reps、手讀命中。
2. **未 commit／push**：無 push 授權；本機 commit 亦未執行。
3. **新增事件產物**：Code Mode 新增 `generate_image`／`generate_video` 工具與 `evolv-skill` 技能上線；本輪與技能治理任務無直接關聯，未觸發使用。
