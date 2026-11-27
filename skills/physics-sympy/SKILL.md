---
name: physics-sympy
description: >
  自然語言 → 哈密頓量／物理運算算符 → SymPy 推導與實際驗算的 child skill。當使用者要把中文或英文物理描述轉成 Pauli／升降算符／自旋或玻色 Hamiltonian、交換子、對易關係、時間演化算符，並要求用 SymPy 算出結果時使用；依任務選 Qwen/Qwen2.5-Coder-7B-Instruct（產生程式）或 Qwen/Qwen2.5-Math-7B-Instruct（符號推導），本機以 Ollama 執行。所有回覆／文件使用繁體中文（正體中文）。
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Bash
---

# Physics SymPy — 自然語言到算符與 SymPy

> 2026-11-26 建立：本 skill 是 `llm-router` 的**獨立 child**，與 `quantum-llm`、`em-llm` 平行；不隸屬 `quantum-llm`，也不重述 `em-llm` 的電磁 backend／端點規則。共同 parent 是 `llm-router`。

## 1. 使用情境

| 情境 | 是否使用本 skill | 去向 |
|---|---|---|
| 「把這段物理描述寫成哈密頓量並用 SymPy 算」 | 是 | 本 skill 全流程 |
| Pauli／自旋算符交換子、升降算符、對易關係推導 | 是 | 本 skill 全流程 |
| 只要量子領域知識，不需 LLM 驅動計算 | 否 | `quantum-router` |
| 電磁模擬／Meep／阻抗／熱負載的 LLM 計算 | 否 | `quantum-llm` → `em-llm` |
| 純 LLM 部署／RAG／模型選型 | 否 | `llm-router` → `ai-ml-app-engineering` |

## 2. 模型選型（本 skill owns 這張表）

| 任務 | 上游模型 | 本機 Ollama model | 用途 |
|---|---|---|---|
| 產生可執行 SymPy 腳本 | `Qwen/Qwen2.5-Coder-7B-Instruct` | `qwen2.5-coder:7b` | 程式碼生成、矩陣建構 |
| 符號推導／CoT 代數 | `Qwen/Qwen2.5-Math-7B-Instruct` | `qwen2.5-math-7b`（由 `bartowski/Qwen2.5-Math-7B-Instruct-GGUF` 的 `Qwen2.5-Math-7B-Instruct-Q4_K_M.gguf` 以 `ollama create` 建立） | 交換子、指數映射、代數化簡 |

- Ollama 官方 library 沒有 `qwen2.5-math` tag；不要再用 `ollama pull qwen2.5-math:7b`，它會回 `file does not exist`。
- 兩顆模型都是 7B 等級，可在本機 CPU/8GB VRAM 跑；呼叫端點 `http://localhost:11434/api/generate`，`stream: false`，`temperature` 壓低（0.1 左右）。
- 模型 id 與端點屬本 skill 的領域規則；`quantum-llm` 只做 goal → hook，不重述本節。

## 3. 流程（自然語言 → 見證）

```
自然語言需求
  → 解析成結構規格：符號、Hilbert 空間維度、算符、 Hamiltonian 項、目標量
  → 依 §2 選模型
  → 要求模型「只輸出一個 ```python fenced block」的 SymPy 腳本
  → 取出程式碼，用 /home/sam/flex/bin/python 實際執行（sympy 1.14.0 已驗證）
  → 物理驗算：H†=H、[σx,σy]−2iσz=0、U†U=I、特徵值為實數
  → 失敗時把 stderr 回饋模型修正，最多 2 輪；仍失敗就手寫腳本並註記
  → 保存原始輸出／生成腳本／stdout/stderr，回報繁體中文
```

### 提示詞契約

- 明確要求：單一自我完足腳本、只輸出 fenced code、不要散文、符號先用 `sympy.symbols(..., real=True)` 宣告。
- 解析用 `re.search(r"```(?:python)?\s*\n(.*?)```", text, re.S)`；若沒有 fenced block 但含有 `import sympy`，從該行往後截取。
- 執行逾時 180 秒；模型呼叫逾時 600 秒。

### 物理驗算底線

- 不要把 LLM 的代數當事實。每一步都要由 SymPy 實際執行後印出。
- 么正性若留下 `sqrt(...)*conjugate(1/sqrt(...))`，代表符號正定性未宣告；補 `positive=True` 或 `refine()` 再化簡，如實記錄是否化到單位矩陣。
- 交換子／對易關係要印出化簡後的零矩陣，不是只印公式。

## 4. 見證格式

每次執行保存：

```
/home/sam/opencode-work/evidence/<kind>_raw.txt        # 模型原始輸出
/home/sam/opencode-work/evidence/<kind>_generated.py   # 取出的 SymPy 腳本
/home/sam/opencode-work/evidence/<kind>_stdout.txt     # 實際執行輸出
/home/sam/opencode-work/evidence/<kind>_stderr.txt     # 錯誤訊息（可能為空）
```

回報要包含：使用的模型 id、執行 return code、關鍵 stdout 行、Timestamp。不寫任何憑證值。

## 5. 本輪驗證（2026-11-26）

- `ollama pull qwen2.5-coder:7b` → `CODER_RC=0`，模型 `dae161e27b0e`，4.7 GB。
- 真實呼叫：`MODEL=qwen2.5-coder:7b`、`RAW_BYTES=811`、`CODE_BYTES=798`、`EXEC_RC=0`。
- 生成腳本輸出 `Matrix([[omega/2, g], [g, -omega/2]])` 作為 H，並印出特徵值／特徵向量；`simplify(sigma_x*sigma_y - I*sigma_z)` 為零矩陣，交換子驗證通過。
- 么正性輸出為 `sqrt(...)*conjugate(1/sqrt(...))` 未化到單位矩陣，屬符號正定性未宣告的限制，如實記錄。
- 重現指令：`python3 /home/sam/opencode-work/physics_sympy_validate.py coder`。

### Math 模型（Qwen2.5-Math-7B-Instruct）

- Ollama 官方 library 無 `qwen2.5-math` tag（`pull` 回 `file does not exist`）；`hf.co` 拉取遇 DNS timeout，Xet 下載遇 CAS error。最終用 `HF_HUB_DISABLE_XET=1` + `huggingface_hub.hf_hub_download` 取得 `bartowski/Qwen2.5-Math-7B-Instruct-GGUF/Qwen2.5-Math-7B-Instruct-Q4_K_M.gguf`（4.4 GiB），再 `ollama create qwen2.5-math-7b` → `CREATE_RC=0`，模型 id `a293a8d62529`。
- 真實呼叫：`MODEL=qwen2.5-math-7b`、`RAW_BYTES=2188`、`CODE_BYTES=933`、`EXEC_RC=1`（前導空格造成 `IndentationError`）。
- 依 §3 把 stderr 回饋重試 2 輪（`math_retry1/2_*.txt`），仍有 prose 混入程式碼或前導空格；**不標為模型直接生成可執行程式**。
- 依 §3 最終手段：以模型輸出中的數學內容手寫 `evidence/math_manual.py` 並實際執行，`MANUAL_RC=0`：`[σx,σy]=2iσz` 化簡為零矩陣、`H=[[ω/2,0],[0,-ω/2]]`、`U†U=I`。此事實如實註記於 `evidence/math_manual_note.txt`。
- Coder 與 Math 兩顆 7B 模型都已實際 pull／建立、實際呼叫，且都有 SymPy 執行輸出證據；差別在於 Math 需手寫清理。

## 6. 關係與治理

```
llm-router (parent / 單一入口)
  ├── quantum-llm   (independent child；LLM 驅動量子／EM 計算的閘門)
  ├── em-llm        (independent child；EM backend／solver 規則)
  └── physics-sympy (本 skill；自然語言 → 算符 → SymPy)
```

- `quantum-llm` 只把此 goal hook 到本 skill，不重述模型／SymPy 細節。
- 修改本 skill 需跑 `audit-skill`、清 `__pycache__`、re-audit 與 drift 比對。
- `Logic check: 2026-11-26` 建立：獨立 parent 關係、模型選型表、執行見證格式。
- 所有回覆／文件使用繁體中文（正體中文）。

---

## Verification Discipline

模型輸出是假設，不是證據。要重新開檔確認原始輸出與 stdout 屬於本輪，並重新執行生成腳本核對 return code；任何「通過」都要有實際執行輸出支持。
