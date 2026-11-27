---
name: quantum-llm
description: >
  LLM 驅動量子／電磁計算的 parent skill：當使用者要把 LLM 用於量子模擬、電磁模擬、Meep/FDTD 腳本生成、阻抗／熱負載／傳輸線計算時，載入本 skill 並 hook `em-llm` 執行；自然語言 → 哈密頓量／算符 → SymPy 則 hook `physics-sympy`。本身只做 goal→backend→hook→見證的閘門，不重複 child 的 solver／CLI／模型 id 細節。本地 source 為 `~/軟體/代理人/colibri/`。Use when the user asks to use an LLM for quantum/EM simulation, LLM-driven science computation, or to chain quantum + em-llm. Triggers include "驗證量子LLM" and "驗證量子模型" to run the local engine verification hook. 所有回覆／文件使用繁體中文（正體中文）。
version: "1.1.0"
user-invocable: true
allowed-tools: Read, Write, Bash
---

# Quantum LLM — LLM 驅動量子／電磁計算 parent

> 2026-11-26 建立／更新：`llm-router` 的 **independent child**，與 `em-llm`、`physics-sympy` 平行。本 skill 只做「需求 → backend → hook → 見證」的閘門；實際 solver／CLI／模型選型由 child owns。

## 1. 使用情境（Usage scenario）

| 情境 | 是否載入本 skill | 去向 |
|---|---|---|
| 用 LLM 產生／驗證量子或電磁模擬腳本 | 是 | hook `em-llm` |
| 使用者說「驗證量子LLM」或「驗證量子模型」 | 是 | hook 執行本地 `verify.py`；不轉介 `em-llm` |
| 阻抗／IL／RL／熱負載／傳輸線計算，且要 LLM 參與 | 是 | hook `em-llm`（領域計算由 child owns） |
| 自然語言 → 哈密頓量／物理運算算符 → SymPy 推導與實際驗算 | 本 skill 只做路由 | hook `physics-sympy`（模型 id／SymPy 細節由它 owns） |
| 純量子知識（QKD／PQC／qubit 架構），無 LLM 驅動 | 否 | `quantum-router` |
| 純 LLM 基礎設施（部署／RAG／agent／模型選型） | 否 | `llm-router` → 對應 child |

## 2. 嚴格邏輯（Strict logic）— 暴力等比映射閘門

```
需求 → 若命中驗證觸發（「驗證量子LLM」／「驗證量子模型」）
     → hook 執行本地 verify.py（先檢查 Ollama 與 8002 endpoint）
     → 收集 verification.json / serve.log 見證並回報
需求 → 判別是否 LLM 驅動的量子／EM 計算
     → 選 backend（規則由 em-llm owns）
     → hook em-llm 執行；若為自然語言轉算符＋SymPy 則 hook physics-sympy
     → 收集見證（原始輸出 + 交叉核對 + 本輪時間戳）
     → 回報（繁體中文）
```

- 除第 2A 節的本地引擎驗證 hook 外，本 skill **不**重述量子／EM 計算的端點、模型 id、CLI 指令、solver 名稱——那些在 `em-llm/SKILL.md`；7B 模型選型與 SymPy 提示詞契約在 `physics-sympy/SKILL.md`。
- backend 切換只轉述 goal（「用 OpenCode 本機 API」），具體實現在 child。
- 本 skill 的本地 source 是 `~/軟體/代理人/colibri/`（實際展開 `/home/sam/軟體/代理人/colibri/`），不要用文件或範例中的舊路徑。

## 2A. 本地引擎驗證 hook（2026-11-27）

命中「驗證量子LLM」或「驗證量子模型」時，這是**直接執行**規則，不可只提出建議或描述指令。

1. 以 Bash 檢查 Ollama 沒有常駐模型：

   ```bash
   curl -sS http://127.0.0.1:11434/api/ps
   ```

   輸出必須是 `{"models":[]}`。若不是，停止並如實回報 VRAM 競爭風險；未經授權不要自行 kill 服務或卸載別人的模型。

2. 檢查本機 llama.cpp 端點：`curl -fsS http://127.0.0.1:8002/health`。若失敗，停止並提示以 `~/opencode-work/quantum-llm/serve.sh` 背景啟動服務，不要在skill 內偷偷啟動或修改的模型／port。

3. 執行驗證：

   ```bash
   python3 ~/opencode-work/quantum-llm/verify.py
   ```

4. 讀取 `~/opencode-work/quantum-llm/verification.json` 與 `~/opencode-work/quantum-llm/serve.log`，回報 `all_passed`、各 case 耗時、`finish_reason`、GPU 用量與任何失敗。`PASS` 只代表端點、模板與基本生成可用，**不代表答案正確**；幻覺與舊 Qiskit API 仍須 RAG／Aer 驗證。

5. 若重新生成驗證證據且要提交，必須同步更新 `skill-reports/manifests/quantum-llm-20261127.sha256`；push／設 remote 仍需另行明確授權。

## 3. Parent-child 鏈（2026-11-26 裁決）

```
llm-router                         (共同 parent / 單一入口；只路由)
  ├── quantum-llm                  (本 skill；independent child)
  ├── em-llm                       (independent child；EM backend／solver 規則)
  └── physics-sympy                (independent child；自然語言 → 算符 → SymPy)
```

- `quantum-llm` **不是** `em-llm` 的 parent；兩者皆直接隸屬 `llm-router`。`em-llm/SKILL.md` 內舊的「parent of」宣稱因未獲授權修改而保留，屬已知不一致，以本節為準。
- need-based hook：只有「LLM 驅動的量子／EM 計算」才 hook `em-llm`；「自然語言 → 算符 → SymPy」hook `physics-sympy`；純計算若已明確指定 `em-llm` 可由 `llm-router` 直接 hook，跳過本層。

## 4. 本地 source 與本輪驗證（colibrì）

| 項目 | 值／證據 | 狀態 |
|---|---|---|
| source path | `~/軟體/代理人/colibri/` → `/home/sam/軟體/代理人/colibri/`；CLI 為 `c/coli`（可執行 Python script） | 已核對 |
| 模型路徑 | `/mnt/d/sam/colibri/models/glm52_i4`（舊文件寫 `/mnt/sde/...`，不存在） | 已核對 |
| HF repo | `mastouri/GLM-5.2-colibri-int4-g64-with-int8-mtp`（public、ungated、149 檔、429276220139 bytes ≈ 399.8 GiB） | 已核對 |
| 版本 | `coli --version` → `colibri 1.12.1` | 已驗證 |
| 無模型診斷 | `coli doctor` → `result error`、RC=2（代表模型尚未就緒） | 已驗證 |
| 測試套件 | `cd c && python3 tools/run_tests.py $(find tests -maxdepth 1 -type f -executable -name 'test_*' \| sort)` → 105 支、**105/105 PASS**、`FAILED:` 0 個 | 已驗證 |
| 模型下載 | 149/149 檔、約 404 GiB；`coli doctor --deep` 的 model.path/config/family/tokenizer/shards/container/shard_sequence/required 皆 ok | 已驗證（2026-11-27） |
| `coli doctor --deep`（模型就緒後） | `result error`：engine CPU-only（warn）＋`memory.ram` fail（13 GB budget 容納不了每層一個 expert slot，peak 19–20 GB > 可用 14 GB）；這是本機 RAM 限制，不是模型檔缺失 | 已驗證（硬體限制） |
| serve／API | `COLI_RAM_OVERCOMMIT=1 KVB_FLASH_MB=512 KVB_TILE_MB=256 coli serve --ram 13 --ctx 256` 啟動；`/v1/models` → HTTP 200、id `glm-5.2-colibri`；`/v1/chat/completions` → HTTP 200、`finish_reason=stop`（prompt 7 tokens / completion 1 token，約 100 s）；25-token 中文提問在 900 s 客戶端 timeout 內未完成，如實列為限制 | 已驗證（overcommit，非生產安全宣告） |

- HF 下載快取仍有 2 個 `.incomplete`（共約 4.1 GB），位於 `.cache/huggingface/download/`；不屬模型 shard，serving 已實際成功，保留不影響服務。
- 憑證政策：`USAGE_TEST_EXAMPLES.md` 含明文 HF token；本 skill 只記「有憑嫌疑人」，不下抄值、不進 manifest、不進報告。下載用 `token=True` 讀本機憑證。
- 模型 id／推導細節不寫在本節；量子／EM 的 backend 規則在 `em-llm`，7B 模型選型在 `physics-sympy`。

## 5. 文件／程式一致性（Doc + Code compliance）

- 本 skill 無程式碼；一致性指 hook 目標存在且可達：`/home/sam/.agents/skills/em-llm/SKILL.md`、`/home/sam/.agents/skills/physics-sympy/SKILL.md` 存在，兩者皆在 allow-list 內；本地驗證 hook 的 `~/opencode-work/quantum-llm/verify.py`、`granite-chat.jinja`、`serve.sh` 亦須存在且指向同一端點。
- 任何修改需回寫本檔並 re-audit（`chain-skill` stage 6 distill）。

## 6. 進化（darwin-skill）

- 路由／hook 規則變更要走 chain-skill 閉環；無效修改回退。
- 定期核對 `em-llm`／`physics-sympy` 是否仍在本機、allow-list 是否同步。

## 7. 治理

- publish 前跑 `audit-skill`；完成宣告依 `audit-worker-subagent` 獨立驗證。
- **Logic check: 2026-11-26**：colibrì source、105/105 PASS、版本 1.12.1、模型路徑、獨立 child 關係、`physics-sympy` hook 已建立；serve/API 如實標記待驗證。
- **Logic check: 2026-11-27**：GLM-5.2 完整下載；`coli serve` + `/v1/models` + `/v1/chat/completions` 在 RAM overcommit 條件下實際驗證回 200；RAM 不足與長提示詞 timeout 如實記載，不標為生產可用。
- **Logic check: 2026-11-27（驗證 hook）**：新增「驗證量子LLM／驗證量子模型」觸發，hook 執行 `verify.py`；RED 12 項失敗、GREEN 全過後才寫入本檔；`PASS` 如實標記為端點／模板／生成煙測，不作答案正確性宣告。
- 所有回覆／文件使用繁體中文（正體中文）。

---

## Verification Discipline

**Required background:** `audit-worker-subagent`。hook `em-llm` 或 `physics-sympy` 後不可直接轉述其成功宣告，要重新讀取輸出檔／重跑指令，確認證據屬於本輪。本地引擎驗證 hook 後必須重新讀取 `verification.json`／`serve.log`，不可把 3/3 `PASS` 當作答案正確性。模型輸出是假設，不是證據；「通過」必須有實際執行輸出支持。
