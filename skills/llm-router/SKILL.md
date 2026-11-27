---
name: llm-router
description: >
  LLM 家族 parent / 單一入口：依目標把 request route 到既有 LLM 相關 child skill（本機 LLM backend、雲端免費 LLM API 資源、LLM 驅動電磁／量子計算、agent 框架、RAG／embedding、自然語言解析），本身不重複 child 的領域規則；chain-skill 六階段閉環 + darwin-skill 進化規則（E0-E3 / 9 維 rubric / keep-revert 棘輪）。Use when the user asks about local LLM backend（Ollama／OpenCode API）、free LLM API providers（Groq/OpenRouter/Gemini/Cloudflare Workers AI 等）、LLM-driven computation, LLM tool-use pipeline, model selection, RAG, LLM agents, or which LLM skill to use. 所有回覆／文件使用繁體中文（正體中文）。
version: "1.0.1"
user-invocable: true
allowed-tools: Read
---

# LLM Router — LLM 家族父節點 / 單一入口

> 2026-11-26 建立：以 chain-skill 六階段閉環 + darwin-skill 進化規則建立。`llm-router` **只做「目標 → hook child」決策**，不重複 child 的領域規則；實際運算／解釋由 hooked child skill 承接。

## 1. Parent Node — 目標 → hook 決策（need-based predicate）

`llm-router` 是 LLM 家族的 **parent / 單一入口**：使用者提出 LLM 相關需求時先載本 skill，再依目標 hook 既有 child。判定依 **goal，不是 skill 名稱**；parent 不 inline child 步驟。

| Goal | Hook（既有 child） | Skip when |
|---|---|---|
| LLM 驅動量子／電磁計算／模擬／Meep 腳本生成／EM RAG | `quantum-llm`（independent child）→ `em-llm`（independent child，見 §4 鏈） | 僅問量子領域知識（非 LLM 驅動）→ `quantum-router`；自然語言轉算符＋SymPy → `physics-sympy` |
| 自然語言 → 哈密頓量／物理運算算符 → SymPy 推導與實際驗算 | `physics-sympy`（independent child） | 純量子知識 → `quantum-router`；EM 模擬 → `em-llm` |
| 電磁模擬具體操作（CPW／天線／PCB／FDTD／FEM／阻抗／IL／RL） | `em-llm`（直接 hook，由 `quantum-llm` 承接時同上） | 問 general LLM backend → 看下行 |
| 本機 LLM 部署／推理優化／模型選型／RAG／向量資料庫／微調／上線成本 | `ai-ml-app-engineering` | 僅需 EM 領域 RAG → `em-llm` |
| 免費 LLM API 資源／雲端免費 provider 設定（Groq/OpenRouter `:free`/Gemini/Cloudflare Workers AI/Cerebras 等）／限額與資料使用條款／OpenCode `opencode.jsonc` provider 設定 | `free-llm` | 本機 Ollama/llama.cpp 免費 fallback → `opencode-free-fallback`；一般模型選型/成本工程 → `ai-ml-app-engineering` |
| 自然語言轉結構化參數（解析器／啟發式 fallback） | `llm-parser` | 參數已是 struct → 直接用 child |
| Voice／tool-use agent 建置（ElevenLabs agents） | `agents` | Cloudflare Agents SDK → `agents-sdk` |
| Cloudflare Agents SDK 建置／除錯／審查 | `agents-sdk` | 一般 agent 框架 → `ai-agent-builder` |
| Markdown 知識庫語意搜尋（QMD／embedding） | `qmd-skill` | 僅關鍵字 grep → `skill-seek` |

### Need-based predicate 細則
- 一個 request 命中單一 goal → 只 hook 該 child，不廣播。
- 跨 goal（例：LLM 部署 + EM 模擬）→ 依序 hook，parent 只處理順序與銜接，不重複解釋。
- parent 不自行產出領域內容；children own their rules。
- backend 切換（Ollama／OpenCode API）屬 `em-llm` 的領域規則，`llm-router` 不重述端點／模型 id／憑證。

## 2. 既有本機 child 盤點（不另開發）

| Child | 位置 | 角色 |
|---|---|---|
| `quantum-llm` | `.agents/skills` | LLM 驅動量子／電磁計算 parent；hook `em-llm` |
| `em-llm` | `.agents/skills` | 本機 LLM tool-use 電磁模擬管線（backend：Ollama／OpenCode API） |
| `ai-ml-app-engineering` | `.agents/skills` | 本地 LLM 部署／推理優化／RAG／微調／上線 |
| `free-llm` | `.agents/skills` | 雲端免費 LLM API 資源盤點／OpenCode provider 設定／限額與資料使用條款／最小驗證腳本 |
| `llm-parser` | `.opencode/skills` | 中文自然語言 → 傳輸線參數解析 |
| `agents` | `.agents/skills` | ElevenLabs voice agent |
| `agents-sdk` | `.agents/skills` | Cloudflare Agents SDK |
| `qmd-skill` | `.agents/skills` | QMD markdown 語意搜尋 |
| `physics-sympy` | `.agents/skills` | 自然語言 → Pauli／升降算符／Hamiltonian → SymPy 實際驗算；模型選型與見證格式由其 owns |

- **不另開發**：既有 child 全部為本機技能；`llm-router` 僅維護路由與整合，不重複領域內容。
- 跨家族：量子領域本體（QKD／PQC／qubit／拓撲）屬 `quantum-router`，本家族只處理「LLM 作為驅動工具」的部分。

## 3. 功能集合（Function Set）

1. **LLM 驅動計算** — `quantum-llm` → `em-llm`（tool-use 管線、腳本生成／執行／驗證迴圈）。
2. **LLM 基礎設施** — `ai-ml-app-engineering`（部署、推理、RAG、成本）。
3. **免費／低門檻雲端 API 資源** — `free-llm`（免費 tier 盤點、OpenCode provider 設定、限額/資料使用條款、最小驗證）；本機 Ollama fallback 屬 `opencode-free-fallback`，不重複。
4. **LLM 介面層** — `llm-parser`（自然語言解析）、`agents` / `agents-sdk`（agent 框架）、`qmd-skill`（語意搜尋）。
5. **自然語言 → 算符 → SymPy** — `physics-sympy`（模型選型、提示詞契約、SymPy 實際執行與見證）。

## 4. Parent-child 鏈（由 `chain-skill` 建立／維護）

```
llm-router                     (parent / 單一入口；只路由)
  ├── quantum-llm              (independent child；LLM 驅動量子／EM 計算閘門 → hook em-llm)
  ├── em-llm                   (independent child；EM backend／solver 規則)
  ├── free-llm                 (independent child；雲端免費 LLM API 資源／provider 設定)
  └── physics-sympy            (independent child；自然語言 → 算符 → SymPy)
```

- 2026-11-26 裁決：`em-llm` 為 `llm-router` 的**獨立 child**，與 `quantum-llm`、`physics-sympy` 平行；`quantum-llm` 不再是 `em-llm` 的 parent。
- 2026-11-27 補充：`free-llm` 為 `llm-router` 的**獨立 child**，負責雲端免費 LLM API 資源與 OpenCode provider 設定；本機 Ollama fallback 仍由 `opencode-free-fallback` owns，避免重複。
- `em-llm` owns backend／端點／模型 id 規則；`physics-sympy` owns 7B 模型選型與 SymPy 見證；`free-llm` owns 免費 provider 盤點、限額/條款查證與最小驗證；parent 不重述。
- 若使用者只問「跑 EM 模擬」，`llm-router` 直接 hook `em-llm`；若問「量子／LLM 整合架構」則走 `quantum-llm`；若問「把物理描述寫成哈密頓量並用 SymPy 算」則走 `physics-sympy`；若問「設定免費 LLM API / Groq/OpenRouter/Gemini 免費額度」則走 `free-llm`。

## 5. 進化規則（darwin-skill）

E0–E3／9 維 rubric／keep-revert 棘輪的規則單一來源為 `darwin-skill`。本 router 不重複其實作；需要進化時 hook `darwin-skill`，依它的流程執行。路由表修改仍須經 `chain-skill` 六階段閉環並同步 allow-list SSOT；stale hook 視為 open loop。

## 6. 治理與驗證

- **Iron Law**：任何「完成／PASS／已更新」都是 claim，不是 evidence；以 `audit-worker-subagent` 的 Audit Gate 獨立驗證。
- publish 前跑 `audit-skill` 安全閘（manifest + verdict）。
- **Logic check: 2026-11-26**：新增 `physics-sympy` 路由；`quantum-llm`／`em-llm`／`physics-sympy` 三者皆為 `llm-router` 獨立 child。
- **Logic check: 2026-11-27**：新增 `free-llm` 路由（雲端免費 LLM API 資源／provider 設定）；與 `opencode-free-fallback`（本機 Ollama fallback）邊界明確；`quantum-llm`／`em-llm`／`free-llm`／`physics-sympy` 為 `llm-router` 獨立 child。
- 所有回覆／文件使用繁體中文（正體中文）。

---

## Verification Discipline

**Required background:** `audit-worker-subagent`（Audit Gate / rationalization table / red flags）。任何 child 回報的成功都要重新開檔／重跑指令核對，並確認證據屬於本輪（mtime／commit hash），不看既有 ✓。
