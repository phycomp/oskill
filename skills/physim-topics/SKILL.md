---
name: physim-topics
description: "物理模擬 repo（/home/sam/物理模擬）的主題蒸餾索引：平台架構/演進、古典力學、天體渾沌、波動流體、電磁光學、量子、能帶拓撲、相對論與跨域接口。Use when the user asks about 物理模擬 topics、physim 主題、能帶/拓撲/量子/電磁/微波級聯/量子傳輸線，或要查 /home/sam/物理模擬 內容。蒸餾檔只做路由，定量計算必須回讀原始檔。"
version: "1.3.0"
user-invocable: true
allowed-tools: Read, Bash, Glob, Grep
---

# physim-topics — 物理模擬主題蒸餾

## 定位
本技能是 `/home/sam/物理模擬` repo 的主題蒸餾路由層。蒸餾檔位於 `references/`，只做路由與索引；定量計算、公式、程式碼必須回讀原始檔。

**Master 關係（v1.3.0 收斂）**：`/home/sam/物理模擬/topics/` 是唯一 master（domain 聚類，12 檔）；本技能 `references/` 為其逐檔 md5 一致的同步副本。更新蒸餾內容改 master，再同步副本；兩處不得各自演化。

## 入口
- 總覽：`references/00_索引.md`
- 子主題：`references/01_*.md` … `references/11_*.md`

## 快速路由

| 需求 | 讀這份 |
|------|--------|
| 平台架構/契約/service/CLI/快取/測試 | `references/01_平台架構與契約.md` |
| 平台四代演進/legacy/遷移/CodeInsight | `references/02_平台演進與工具鏈.md` |
| 古典力學/剛體/穩定性/畫布/遊戲物理 | `references/03_古典力學與剛體.md` |
| 天體/天體物理/Lorenz-Chen/OGY 控制 | `references/04_天體與渾沌.md` |
| 波動/流體/熱力/統計/聲學 | `references/05_波動流體熱力統計聲學.md` |
| 電磁光學/CST S 參數四步級聯/scikit-rf | `references/06_電磁光學與微波級聯.md` |
| 量子 AB/隧道/瞬子/電路閘/Bell-GHZ/Rabi-JC | `references/07_量子與量子電路.md` |
| 能帶/Berry-Chern/Wannier/變分加速/最小作用量 | `references/08_能帶固態拓撲與變分加速.md` |
| 相對論/客戶需求/qcable 接口/22 domain 總表 | `references/09_相對論與跨域接口.md` |
| 驗收規格（FR/NFR/AC，329 passed） | `references/10_驗收規格.md` |
| 概念圖（Mermaid 架構/資料流/渲染管線） | `references/11_概念圖.md` |

## 接口技能
- `physim-refactor`：平台重構流程（`/home/sam/物理模擬/.opencode/skills/physim-refactor/`）。
- `topological-insulator`：TI 材料/拓撲超導深度內容（`~/.opencode/skills/topological-insulator/`）。
- `qcable-index`：量子傳輸線技能群（`~/.opencode/skills/qcable-index/`）。

## 鐵律
1. 蒸餾檔只做路由；定量計算必須回讀原始檔。
2. `topo/` 已沉澱於 `topological-insulator`，不重抄。
3. 不確定的聲明標 `> ⚠️ 未驗證`；爭議聲明（如 OpenAI 2026-09 Navier-Stokes 進展）不得當定案事實。
4. Master 唯一：`/home/sam/物理模擬/topics/` 為 master；本技能 `references/` 為逐檔 md5 一致的同步副本，更新先改 master 再同步，不得各自演化。

## 版本
- 1.3.0 (2026-11-24)：收斂兩套蒸餾——master 改為 repo `topics/`（domain 聚類 12 檔）；技能 `references/` 同步副本對齊；原功能聚類 01–08 刪除，其 S4 獨有內容（Navier-Stokes/OpenAI 2026-09，標爭議）搬入 master `05_`； 獨有驗收規格/概念圖搬入 master `10_`/`11_`；入口改 `00_索引.md`；修正 `~/.agents` → `~/.opencode` 路徑漂移。
- 1.2.0 (2026-11-12)：搬移至 `~/.opencode/skills/physim-topics`；入口改名 `00_主題總覽.md`；新增 09/10；快速路由改指 references/；與 topological-insulator 對齊。

---

## 驗證紀律（不輕信回報 — `audit-worker-subagent`）

**Iron Law（沿用 `audit-worker-subagent`）：** 任何「完成 / PASS / 已更新 / 已驗證 ✓ / agent 回報」都是**宣稱，不是證據**。採信或據以行動前必須獨立查證。

- **獨立驗證**：重開檔案 / 重跑指令 / 查 VCS（`git status --porcelain`、`git log <base>..HEAD --stat`）/ 讀原始檔 —— 而非轉述他人回報或既有 ✓。
- **ATTRIBUTE**：確認證據屬於「本輪」：比對 commit hash / 檔案 mtime / 時間戳；舊成果 ≠ 本次產出。
- **CROSS-CHECK**：若完成回報來自 subagent，唯讀查 transcript（DB `mode=ro`），檢查空殼 compaction（`<template>`）或只有 `todowrite` 而無實際工具呼叫。
- **JUDGE**：證據不符 → 維持「未完成 / 待修正」，要求提出可驗證證據，不採信口頭回報。

**本技能特指：** LLM 生成的模擬腳本必須實際執行；物理結果須與解析解 / 權威模型（如 `heatload-coff-nist`）/ 原始量測檔交叉比對並貼出輸出；做量級 sanity check（如 10mK < 10 μW/ch）。`PASS` 須附原始儀器檔佐證。

**REQUIRED BACKGROUND:** `audit-worker-subagent`（完整 Audit Gate / rationalization table / red flags）
