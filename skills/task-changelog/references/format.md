# 日誌條目格式規範（Entry Format）

本檔定義 `logs/YYYY-MM-DD-<slug>.md` 的條目格式。一個檔案可含一或多筆條目；
多筆時每筆用 `##` 標題分隔，並共用同一個 H1 日期標頭。

## 檔案骨架

```markdown
# YYYY-MM-DD — <當日主题>

## <標題>

- **日期**：YYYY-MM-DD
- **類型**：feature / refactor / fix / docs / chore（可複合）
- **涉及技能/檔案**：
  - `<path>` — <vX.Y.Z → vA.B.C 或 新建/修改/刪除>
  - ...

### 變更摘要
1. ...
2. ...

### 驗證結果
- <檢查項>：PASS / FAIL / OK（<實證>）
- ...

### 上下級鏈影響（若適用）
- 上級 ← ...
- 下級 → ...
- 雙向交叉引用：...

### 待辦／已知限制
- ...
```

## 欄位規則

| 欄位 | 必填 | 規則 |
|------|------|------|
| 日期 | ✅ | `YYYY-MM-DD`，與檔名日期一致；語意為「寫日誌日」，若為隔日補記前一日變更，請在內文註明實際變更日 |
| 標題 | ✅ | 一句話，動詞開頭，可被索引直接引用 |
| 類型 | ✅ | 限 `feature`/`refactor`/`fix`/`docs`/`chore`；複合用 ` + ` 連接 |
| 涉及技能/檔案 | ✅ | 绝对或仓库相对路径；標版本变化或新建/修改/删除 |
| 變更摘要 | ✅ | 條列、如實；含溯源與出處（DOI/URL/表號）時務必寫明 |
| 驗證結果 | ✅ | 只寫實跑過的；格式 `<檢查>：<結果>（<證據>）`；沒跑過寫「未驗證」 |
| 上下級鏈影響 | 選填 | 僅當涉及技能鏈/依賴時填；標上級、下級、交叉引用 |
| 待辦／已知限制 | 選填 | 動態值、N/A、未修 bug 等如實揭露 |

## 類型定義

- **feature**：新增技能、功能、檔案
- **refactor**：結構調整、索引重構、鏈路改寫（不改變外在行為）
- **fix**：bug 修復
- **docs**：純文件/索引/ descriptors 更新
- **chore**：機制、流程、腳手架（含本日誌機制本身）

## slug 命名

`YYYY-MM-DD-<short-slug>.md`——小寫英文、以 `-` 分隔、2–4 字，描述主題
（例：`thermal-load-chain`、`skill-index-refactor`、`syspath-fix`）。
同日多主題用不同 slug 各自成檔。

## 範例（完整條目）

````markdown
# 2026-11-18 — 熱負載技能鏈重構

## 熱負載技能上下級鏈重構 + 新建 heatload-coff-nist

- **日期**：2026-11-18
- **類型**：refactor + feature
- **涉及技能/檔案**：
  - `/home/sam/.opencode/skills/qcable-index/SKILL.md` — v1.1.0 → v1.2.0
  - `/home/sam/.opencode/skills/heatload-coff-nist/` — 新建
  - `/home/sam/.opencode/skills/task-changelog/` — 新建

### 變更摘要
1. 溯源：確認公式與 9 係數來源（Raicu et al. 2025 / NIST / Flynn）。
2. 下游：找到 Excel 產出路徑；記錄 sys.path bug（未修改既有檔）。
3. 9 係數：c0..c8 log-log 多項式；4 組權威出處 + NIST 48 材料 + 2 組自推導。
4. 新技能：54 材料對照表 + 計算引擎 + citations + MANIFEST。
5. 索引重構：熱負載鏈雙向交叉引用。
6. 建立 task-changelog 常態日誌機制。

### 驗證結果
- 交叉引用：PASS
- MANIFEST：`sha256sum -c` 6 項全成功

### 上下級鏈影響
- 上級 ← 出處；下級 → Excel 產出 → measurement → units → sop

### 待辦／已知限制
- NbTi 9 係數為執行期 polyfit，表中標 N/A，引擎要求自傳 coeffs。
````

## 與索引的契約

每次新增/修改條目後，`references/log-index.md` 必須新增或更新對應列，
`CHANGELOG.md` 必須在最上方補一筆摘要。索引列格式：

```
| 日期 | 標題 | 類型 | 檔案 |
|------|------|------|------|
| 2026-11-18 | 熱負載技能上下級鏈重構... | refactor + feature | [logs/2026-11-18-thermal-load-chain.md](../logs/2026-11-18-thermal-load-chain.md) |
```
