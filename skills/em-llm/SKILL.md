---
name: em-llm
description: Use when the user wants to run local LLM-driven electromagnetic simulation, computation, Meep/FDTD script generation, SymPy EM derivations, or EM RAG/KeplerAgent workflows per /home/sam/em-simulation-llm (01-06). Triggers include "EM simulation with LLM", "Meep script", "electromagnetic calculation", "CPW/antenna/PCB simulation", "Maxwell derivation", "em-llm 使用者 本機 首頁 生成 驗證", or requests to generate/verify EM solver scripts locally with Ollama or OpenCode 本機 API. Triggers include "驗證電磁LLM" and "驗證電磁模型" to run the EM verification hook. 此 skill 為 `llm-router` → `quantum-llm` 鏈的 child，擁有 EM 計算的 backend 規則。
version: "1.1.0"
---

# em-llm

Local LLM tool-use pipeline for electromagnetic simulation, computation, and Meep script generation.

Project: `/home/sam/em-llm` (Python, run with `/home/sam/flex/bin/python`).

## What it does
- 雙 LLM backend：`OllamaClient`（預設，Ollama 本機）與 `OpenCodeClient`（OpenCode 本機 API，`--backend opencode`）；見下方「LLM backend 規則」
- VRAM-based local model selection (Ollama): `em_llm.cli info`
- Tool-use pipeline: classify request -> generate Meep/SymPy script -> run -> verify -> LLM correction loop
- Scenarios (spec 06): `cpw`, `antenna`, `pcb`, `motor`, `formula`
- SymPy derivations: CPW effective permittivity, wave impedance, skin depth
- Built-in mesh EM solvers (no Meep required): 2D FDTD TMz on Yee grid (`em_llm.solvers.fdtd.fdtd_tmz`), 2D FEM Poisson/electrostatics on triangular mesh (`em_llm.solvers.fem.fem_poisson_2d`, `em_llm.solvers.mesh`)
- RAG: keyword + embedding retriever (hash fallback; HF embedder; PEFT/LoRA helpers `load_peft_embedding_model`/`make_peft_embedder`/`make_embeddinggemma_ir_embedder`)
- Data/model pipeline: `em_llm.data` (synthetic/real import, grid/frequency/component alignment) and `em_llm.models` (DeepONet + `MaxwellPipeline`)
- KeplerAgent-style: symmetry inference + sparse symbolic regression (`em_llm.cli kepler`)

## Quick usage
```bash
cd /home/sam/em-llm
PY=/home/sam/flex/bin/python

$PY -m em_llm.cli info
$PY -m em_llm.cli scenarios
$PY -m em_llm.cli run "derive cpw effective permittivity for er=11.7" -o ./out --scenario formula
$PY -m em_llm.cli run "derive cpw effective permittivity for er=11.7" -o ./out --scenario formula --backend opencode   # OpenCode 本機 API
$PY -m em_llm.cli run "simulate a coplanar waveguide resonator at 2 GHz" -o ./out --scenario cpw
$PY -m em_llm.cli rag --roots /home/sam/em-simulation-llm --query "Meep CPW resonator"
$PY -m em_llm.cli kepler "time-invariant Maxwell field"
$PY examples/run_mesh_em.py
$PY -m pytest -q tests/
```

## EM 驗證 hook（2026-11-27）

命中「驗證電磁LLM」或「驗證電磁模型」時，這是**直接執行**規則：hook 執行 em 驗證，不可只描述指令或引用舊報告。

1. 以 Bash 執行不依賴 LLM／Meep 的核心驗證：

   ```bash
   cd /home/sam/em-llm && /home/sam/flex/bin/python -m pytest -q tests/
   /home/sam/flex/bin/python -m em_llm.cli info
   /home/sam/flex/bin/python -m em_llm.cli scenarios
   /home/sam/flex/bin/python examples/run_mesh_em.py
   ```

2. 需 Ollama backend 或 pymeep 的 LLM／Meep 場景，只在服務與模型／套件實際可用時執行；不可用時如實標記 `skipped` 或預期失敗，不得改寫成 PASS。

3. 回報必須貼出原始輸出、pytest 通過數、CLI 摘要、mesh FDTD/FEM 結果與環境狀態。`PASS` **不等於物理正確**；仍需以解析解、權威模型或原始量測檔交叉核對。

4. OpenCode 本機 API 的 password 只在執行期由 `~/.config/opencode/service.json` 讀取，绝不寫入程式、輸出、報告或日誌。

5. 所有回覆／文件使用繁體中文（正體中文）。

## Development workflow (安裝電磁軟體 / 佈署本地端 LLM / MEEP / 實作 / 測試)
- **安裝電磁軟體**：優先用內建 mesh FDTD/FEM（numpy/scipy）。真實 Meep 需 **pymeep**（conda-forge：`conda install -c conda-forge pymeep`），勿用 PyPI `meep==1.0.6`（非 FDTD）。其他 FEM/FDTD 工具與本機狀態見 `docs/FEM_FDTD_自由軟體.md`。
- **佈署本地端 LLM**：兩條路徑二選一。① Ollama：安裝/啟動 Ollama、`ollama pull` 依 VRAM 選型（`$PY -m em_llm.cli info`，8GB 常用 `qwen3:8b`），確認 `http://localhost:11434`。② OpenCode 本機 API：確認 service 已啟動（`http://127.0.0.1:49374`），用 `--backend opencode`；模型唯一可用 `opencode-go/deepseek-v4.1-flash`（`opencode/...` 與 `*-free` 變體實測回 429）。密碼由程式執行期動態讀取 `~/.config/opencode/service.json`，**勿寫入程式／文件／日誌**。完整規則見下方。
- **MEEP**：`meep_generator` 產生場景腳本，`tool_use`+`verify` 執行並回饋 stderr 修正；無 pymeep 時 Meep 場景僅生成/驗證失敗屬預期，formula/motor/內建 FDTD-FEM 可直接跑。
- **實作**：依 specs 01–06 擴充 `config/llm_client/solvers(tool_use, meep/sympy/kepler/mesh/fdtd/fem)/rag/data/models/cli`，同步範例與 docs。
- **測試**：新增/更新 `tests/test_*.py` → `$PY -m pytest -q tests/`；並做 CLI 煙囪與 `examples/run_mesh_em.py`（需 LLM/Meep 的場景分別在對應環境驗證）。完整流程見 `docs/DEV_WORKFLOW.md`。

## LLM backend 規則（2026-11-26，doc ↔ code 一致）

`em-llm` 為 `llm-router → quantum-llm` 鏈的 child，**擁有 EM 計算的 backend 規則**，parent 不重述本節細節。

| 項目 | Ollama（預設） | OpenCode 本機 API |
|---|---|---|
| 啟用 | `--backend ollama`（預設） | `--backend opencode` |
| Client 類別 | `em_llm.llm_client.OllamaClient` | `em_llm.llm_client.OpenCodeClient` |
| 位址 | `http://localhost:11434` | `http://127.0.0.1:49374` |
| 端點 | `/api/generate`、`/api/chat`、`/api/tags` | `POST /api/experimental/generate/text` |
| 模型 | `qwen3:8b`（依 VRAM 選型） | `opencode-go/deepseek-v4.1-flash`（唯一可用；`opencode/...` 與 `*-free` 皆 429） |
| 認證 | 無 | HTTP Basic `opencode:<password>`，密碼執行期動態讀 `~/.config/opencode/service.json` |

- **request body（OpenCode）**：`{"prompt":"...","model":{"providerID":"opencode-go","id":"deepseek-v4.1-flash"}}`；回應 `{"data":{"text":"..."}}`。
- **憑證紀律**：Basic auth 密碼只在執行期讀取，绝不寫入程式碼、產出、報告或日誌；`llm_usage.log` 等紀錄只記 providerID／model／base_url，不記 password。
- **後端切換不改數值**：只換 LLM backend，自撰分析腳本／SymPy／FD/FEM 數值核心不變（v1↔v2 逐項比對見 `/home/sam/em-llm/out/standard_section_IL_RL_v2/報告.md` 第 12 節：summary.json 差異 0、四份 CSV 逐位元組相同、C1–C9 全 PASS）。

## Notes / constraints
- 需要至少一個可用後端：Ollama（含已安裝模型，如 8GB 的 `qwen3:8b`）或 OpenCode 本機 API service。Client 分別為 `http://localhost:11434` 與 `http://127.0.0.1:49374`。
- **Meep (real FDTD)**: install via conda-forge `pymeep` or system build; without it, Meep scripts are generated but `verify` fails with `ModuleNotFoundError: meep`.
- Embedding RAG: hash fallback works offline; HF/PEFT paths need local weights (e.g. `/mnt/d/models/unsloth-embeddinggemma-300m`, `/mnt/d/models/electrical-embeddinggemma-ir_lora`) and `transformers`/`torch` (`peft` for LoRA).
- Generated scripts/physics results should be inspected before use.

## References
- Workflow: `/home/sam/em-llm/docs/DEV_WORKFLOW.md`
- Specs: `/home/sam/em-simulation-llm/00_索引.md`–`06_Meep_Scenarios.md`
- EM software: `/home/sam/em-llm/docs/FEM_FDTD_自由軟體.md`
- RAG: `/home/sam/em-llm/docs/RAG.md`
- README: `/home/sam/em-llm/README.md`

---

## Verification Discipline (don't trust reports — `audit-worker-subagent`)

**Iron Law (from `audit-worker-subagent`):** Any "done / PASS / updated / verified ✓ / agent reports success" is a **claim, not evidence**. Independently verify before trusting or acting on it.

- **VERIFY**: Re-open the file / re-run the command / check VCS (`git status --porcelain`, `git log <base>..HEAD --stat`) / read the source artifact — never relay someone's report or an existing ✓.
- **ATTRIBUTE**: Confirm evidence belongs to *this round*: compare commit hash / file mtime / timestamps; stale artifacts ≠ this round's output.
- **CROSS-CHECK**: If the completion claim came from a subagent, read its transcript read-only (DB `mode=ro`); check for hollow compaction (`<template>`) or only `todowrite` calls with no real tool use.
- **JUDGE**: Evidence missing → keep status "not done / needs correction"; demand verifiable evidence, don't accept verbal claims.

**Specific to this skill:** Actually run LLM-generated simulation scripts; cross-check physical results against analytic solutions / authoritative models (e.g. `heatload-coff-nist`) / raw measurement files and paste output; do order-of-magnitude sanity checks (e.g. 10mK < 10 μW/ch). A `PASS` must be backed by raw instrument files.

**REQUIRED BACKGROUND:** `audit-worker-subagent` (full Audit Gate / rationalization table / red flags)

