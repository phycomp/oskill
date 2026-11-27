# 2026-11-26 — em-llm 後端切換與 LLM 技能鏈建立

## em-llm 改連 OpenCode 本機 API、重算四截面並沉澱 v2；建立 LLM 技能鏈與治理規則更新

- **日期**：2026-11-26
- **類型**：feature + refactor + docs + chore
- **涉及技能/檔案**：
  - `/home/sam/em-llm/em_llm/llm_client.py` — 新增 `OpenCodeClient` + 保留 `OllamaClient`（修改）
  - `/home/sam/em-llm/em_llm/config.py` — 新增 `select_backend()`／`resolve_opencode_model()`／`BACKENDS`（修改）
  - `/home/sam/em-llm/em_llm/tool_use.py`、`cli.py` — backend 分派與 `--backend` 等參數（修改）
  - `/home/sam/em-llm/out/standard_section_IL_RL_v2/` — 新建沉澱目錄（報告 16414 B、summary.json、4 CSV、曲線圖、5 腳本、logs/00–10）
  - `/home/sam/.agents/skills/llm-router/SKILL.md` — 新建（v1.0.0）
  - `/home/sam/.agents/skills/quantum-llm/SKILL.md` — 新建（v1.0.0）
  - `/home/sam/.agents/skills/em-llm/SKILL.md` — 新增雙 backend 規則章（修改）
  - `/home/sam/.agents/skills/chain-skill/SKILL.md` — 技能表／parent-child 鏈／Logic check（修改）
  - `/home/sam/.agents/skills/quantum-router/SKILL.md` — v1.2.0（child 表＋跨家族引用）
  - `/home/sam/.agents/skills/skill-family/SKILL.md` — v1.1.9（§0 索引／Routing／Cross-family）
  - `/home/sam/.agents/skills/audit-skill/SKILL.md` — 「開發本機技能不需 hook」裁決（修改）
  - `/home/sam/.config/skill-timer/self-developed.list` — allow-list += `llm-router`／`quantum-llm`／`em-llm`

### 變更摘要
1. 背景 worker 因自身模型 Free usage limit 中斷，但計算產出已完整落地；主線依 `audit-worker-subagent` 紀律重新開檔獨立驗證，接手完成驗證／報告／沉澱，未信任任何「完成」宣告。
2. LLM 後端由 Ollama（`localhost:11434`，`qwen3:8b`）改連 OpenCode 本機 API（`127.0.0.1:49374`，`POST /api/experimental/generate/text`）；唯一可用模型 `opencode-go/deepseek-v4.1-flash`（`opencode/...` 與 `*-free` 實測回 429）。Basic auth 密碼執行期動態讀 `~/.config/opencode/service.json`，绝不寫入程式／文件／日誌。
3. 只換 LLM backend，數值核心不變；重算四截面（CPW／微帶／帶狀／同軸）Z₀ 全 50.000 Ω、DC–20 GHz IL／RL，沉澱至 `standard_section_IL_RL_v2/`，未覆蓋原目錄。
4. 以 `skill-family` 建立 `llm-router`（LLM 家族 parent）、以 `chain-skill` 建立 `quantum-llm`（parent gate）→ `em-llm`（child）鏈；parent 只做 goal→backend→hook→見證，不重述端點／模型 id／憑證，backend 規則由 em-llm owns。
5. 治理規則更新：開發本機技能不需 hook `audit-skill`（與 `rev-skill` 既有裁決一致），外部 install／publish／re-review baseline 強制閘門不變；同步 `audit-skill`／`chain-skill`／`skill-family` 並寫回 Logic check 形成閉環。

### 驗證結果
- OpenCode smoke test：OK（`logs/10_llm_usage.log` 原始回應 `{"data": {"text": "OpenCode smoke OK"}}`）
- `summary.json` 深層比對（float 容差 1e-12）：PASS（差異數 = 0）
- 四份 IL_RL CSV：PASS（`cmp` 逐位元組相同）
- 代表頻點：PASS（Z₀ 四截面 50.000 Ω；IL@10GHz CPW 35.814／微帶 5.534／帶狀 6.178／同軸 0.175 dB/10cm；RL@10GHz 25.17 dB，新舊一致）
- C1–C9 一致性（31 項）：PASS（`logs/08_verification.log` 全部通過）
- 自建 FD vs 內建 FEM：PASS（max 差異 1.110e-15）
- pytest：PASS（46 passed）
- 原報告 md5 錨定：PASS（`3d75895acbdc6fae361e92032bb3db31` 未變，v1 未被覆蓋）
- audit-skill 靜描＋semantic review：`llm-router` 0/100、`quantum-llm` 8/100（AS3 MEDIUM 判定為 chain hook 正規路徑引用之誤報），兩份 Verdict = APPROVE
- 憑證外洩掃描：PASS（無 password 字面值寫入 em_llm/）

### 上下級鏈影響
- 上級 ← `llm-router`（LLM 家族 parent）→ `quantum-llm`（parent gate）→ `em-llm`（child，owns backend 規則）
- 跨家族：`quantum-router` 加 `quantum-llm` child 與 `llm-router → quantum-llm → em-llm`；`skill-family` Index／Need-based predicate／Cross-family 表同步
- 雙向交叉引用：`chain-skill` 技能表與 parent-child chains、`quantum-router` child 表、`skill-family` §0／§1／§7 皆已雙向對帳

### 待辦／已知限制
- 背景 LLM CPW 場景（`llm_cpw/cpw.py`）兩版皆未完成獨立驗證，未納入主結果；不影響四截面主計算。
- RL 使用 SMA 典型 VSWR 估算（18–20 GHz 外推），非實測 S 參數。
- 本機無 `pymeep`，未跑 FDTD 全波驗證；主計算為自撰分析腳本 + SymPy + 內建 FD/FEM。
- OpenCode service 密碼為動態值，日誌／報告只記 providerID／model／base_url，不記 password。
