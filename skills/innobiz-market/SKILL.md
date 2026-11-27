---
name: innobiz-market
description: 蒸餾「創新商業模式與行銷渠道」主題：AI 寫作/內容工具定價分層、社群自動化發布通路（Meta Graph API/RPA/排程工具）、AI Agent 產品化與 AaaS 變現、企業/B2B/B2G 合作與第三方背書通路。Use when user asks about 創新商業模式, 行銷渠道, marketing channels, AI SaaS pricing, social media automation, Meta Graph API publishing, agent monetization, B2B GTM, 產學合作通路, 第三方量測背書, 護城河, moat, 競爭壁壘, defensibility, or topic-distill outputs from /home/sam/三目錄/10_軟體與工具鏈/.
version: 1.0.2
allowed-tools: Read, Grep, Glob
---

# Innovative Business Marketing — 創新商業模式與行銷渠道

本技能由 `topic-distill`（S1-S5）從 `/home/sam/三目錄/10_軟體與工具鏈/` 蒸餾產出，聚焦 AI 產品情境下的商業模式與行銷通路。蒸餾檔為路由與摘要，定量數字、合約條款、API 權限須回讀原始來源或官方文件。

## 快速路由

| 需求 | 讀這份 |
|------|--------|
| 子主題地圖、來源映射、跨主題結論 | `references/00_主題總覽.md` |
| AI 寫作/SEO/行銷/電商工具定價分層與變現設計 | `references/01_AI內容與寫作工具的商業模式.md` |
| Meta Graph API、RPA、自動化排程等社群發布通路 | `references/02_社群自動化與行銷渠道.md` |
| Agent 技能化、AaaS、usage/outcome/hybrid 定價 | `references/03_AI代理人產品化與創新服務模式.md` |
| 產學合作、第三方量測背書、IP/驗收的 B2B 通路 | `references/04_企業導入與B2B合作通路.md` |

## 使用須知（鐵律）

1. **溯源**：價格、權限、ARR、市場規模等數字回查原始檔/官方頁；本技能不把媒體估算當實績。
2. **合規**：社群自動化預設以官方 API + 權限審核為合規路線；RPA/UI 自動化需評估平台條款風險。
3. **爭議標註**：未經官方確認的數字或政策變動須標註檢索日期與來源性質。
4. **名稱校正**：來源目錄中 `Procuct Application and description(20260722).pptx` 依使用者指示記為 **Product Application PPTX**；該檔可抽取文字極少，未作核心證據。
5. **護城河檢核**：分析商業模式或行銷通路時，必須辨識護城河/競爭壁壘來源（資料飛輪、規模經濟、網路效應、切換成本、品牌信任、合規牌照、工作流嵌入、通路獨占等），並評估其可持續性與被侵蝕風險；無證據支撐時標註為「假說」，不得當定論。

## 來源範圍

- 主來源：`MoltBot工作原理.docx`（AI 寫作生態、FB 自動發佈技能設計）
- 輔來源：`Clawdbot 家庭版实现.docx`、`亞大AI算力平台.docx`、`AI寶萊*.docx`、`AI平台開發建置規劃書.docx`
- 弱關聯/排除：`0相關佈署.md`（ROS 訂閱誤中）、`Product Application PPTX`（文字抽取少）、`智能代理人.odp`、`作視頻.odp`
- 網路充實檢索日：2026-11-25（見各子主題「網路充實」段）

## 與其他技能的關係

- `topic-distill`：本技能的產製流程來源。
- `marketing-ideas` / `content-strategy` / `social`：若要把本主題轉為實際行銷方案，可接續這些技能。
- `cold-email` / `revops` / `sales-enablement`：B2B 通路與外展執行可接續。

## 版本

- 1.0.2（2026-11-25）：新增鐵律第 5 條「護城河檢核」（尋找護城河/競爭壁壘機制）；description 補充 moat/defensibility 觸發詞。
- 1.0.0（2026-11-25）：初版。由 topic-distill S1-S5 從 `/home/sam/三目錄/10_軟體與工具鏈/` 蒸餾，含 4 個子主題與 2026-11-25 網路充實。
