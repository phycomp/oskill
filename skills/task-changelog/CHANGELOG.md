# Changelog — 變更彙總

task-changelog 的人類可讀入口。最新變更置頂；完整索引見 [references/log-index.md](references/log-index.md)，條目本體見 [logs/](logs/)。

## 2026-11-27

- **toolkit-viz 新增演示graphify觸發與 skillrule-viz UI 載入修正** (`fix + docs + test`)
  toolkit-viz 觸發規則新增「演示graphify工具、演示graphify」並同步 §E 路由；skillrule-viz Streamlit 視圖修正輸出目錄偵測/fallback 與 radio 選擇器。驗證：py_compile PASS、toolkit-viz 相關測試 4 passed、skillrule-viz demo 重建（nodes=43, edges=40）；Streamlit 互動 UI 自動化已執行，restart 後截圖證據未保留。→ [完整日誌](logs/2026-11-27-toolkit-viz-graphify-trigger-ui.md)

- **skillrule-viz 擴充 manifest/drift 解析與 Graphify 原生 HTML Streamlit 整合** (`feature + docs`)
  擴充 `skillrule-viz`：新增 `--manifest-target`/manifest drift 比對（ok/changed/missing/extra）、audit report/JSON verdict-risk-finding 解析、`graphify export html` 原生 HTML 輸出；`toolkit-viz` 新增「🕸 技能規則視覺化」模式，載入 skillrule-viz 輸出並以 `components.html` 內嵌本機 `graph.html`。opencode/agents 兩端同步。驗證：py_compile PASS、toolkit-viz 既有測試 4 passed、manifest+report+HTML 煙測產出 `nodes=41, edges=38, native_html=.../graph.html`。→ [完整日誌](logs/2026-11-27-skillrule-viz-manifest-drift-graphify-html.md)

- **skill-gvnor 壓力情境 TDD：baseline 3/3 違規 → with-skill 3/3 遵守 → REFACTOR 4 反制 → meta-test「技能已清楚」** (`refactor + fix + docs`)
  跑 3 個複合壓力情境（A 時間/權威/沉沒成本；B 疲憊/社交/務實；C 權威/經濟/沉沒成本）× baseline／with-skill：baseline 3/3 違規（直接改、shell grep 硬做、保留重複全文），with-skill 3/3 遵守且逐字引用章節。baseline 逐字暴露 4 個未覆蓋藉口 → REFACTOR 補 4 條 rationalization＋Red Flags 章節＋修正過時索引規則（v1.0.0→v1.1.0）。Gate 2 RED 4/4 失敗→Gate 3 GREEN 4/4＋contract 12/12＋index 7/7；Gate 5 drift 僅 `CHANGED SKILL.md`＋`NEW tests/test_refactor.py`。重測情境 C 引用新條目仍遵守，meta-test 回答「技能已經很清楚」→ 達 bulletproof 判準。限制：每情境只 1 rep，未達 micro-test 5+ reps，如實揭露。→ [完整日誌](logs/2026-11-27-skill-gvnor-pressure-test.md)

- **skill-gvnor description 微測 6/6；allow-list SSOT → chain-skill → skill-family 索引同步** (`docs + chore + refactor`)
  派 fresh-context subagent 只看 frontmatter description 對 6 個提示判斷 → 6/6 正確（3 should-trigger 全 YES、3 near-miss 全 NO）；微測只驗證 wording，完整壓力情境仍列待辦。索引同步依 SSOT 順序：allow-list 先補 `skill-gvnor`（33→34），再同步 `chain-skill` Inventory 兩列＋Logic check、`skill-family` Index／Routing／Version 1.3.0＋Logic check；別名指向未改，維持文件化。Gate 1 pre 皆 APPROVE（chain-skill 7/100 LOW SAFE、skill-family 0/100）；Gate 2 RED 6/7 失敗→Gate 3 GREEN 7/7＋contract 12/12；Gate 5 drift 皆僅 `CHANGED SKILL.md`、allow-list diff 僅 `skill-gvnor` 一列。→ [完整日誌](logs/2026-11-27-skill-gvnor-index-sync.md)

## 2026-11-26

- **建立 skill-gvnor：整合 audit／inspect／revised／CRUD 四能力治理 router，skill-crud R/U 改 hook 消除全文 drift** (`feature + refactor + docs`)
  比較 `writing-plans`（傳達決策）／`writing-skills`（遵守決策）／`using-superpowers`（載入決策）後，建立 `skill-gvnor` 為 skill 治理家族 parent：只做 goal→hook 與證據組裝，不重複 child 規則。audit→`audit-skill`、inspect→`inspec-skill`＋`using-superpowers`、revised→`rev-skill` Gate 0–6、CRUD→`skill-crud`。`skill-crud` 的 R 章節移除 L1–L8 全文、U 章節移除 Gate 0–5 全文，改 hook 本技能，消除與 `rev-skill`／`audit-skill` 的兩份全文 drift。別名（`inspect-skill`→`chain-skill`／`inspec-skill` 現行／`skill-router`→`skill-family`）僅文件化，索引同步下一輪。Gate 0 explicit consent；Gate 1 pre CAUTION 27/100→APPROVE；Gate 2 RED 12/12 失敗→Gate 3 GREEN 12/12；Gate 5 post CAUTION 35/100→APPROVE、drift 僅 `CHANGED SKILL.md`。完整壓力情境（3+ 複合壓力＋控制組）因 subagent 配額耗盡未跑，列為已知限制。→ [完整日誌](logs/2026-11-26-skill-gvnor-integration.md)

- **沉澱 dev-skill：把「skill-family 建 parent + chain-skill 建 parent-child 鏈」封裝為技能開發編排 SOP** (`feature + docs`)
  新建 `dev-skill` v1.0.0（D0–D6 編排：拆解→命名→建 parent→建鏈→allow-list／交叉索引同步→治理→changelog→核對），定位為 orchestrator，只 hook `skill-family`／`chain-skill`／`skill-timer`／`task-changelog`，不重述其規則；明確與 `impl-skill`／`skill-crud`／`refactor-skill` 邊界。allow-list SSOT 先補 `dev-skill` 再同步 `skill-family`（v1.2.0）Index／`chain-skill` inventory。→ [完整日誌](logs/2026-11-26-dev-skill-sedimentation.md)

- **em-llm 改連 OpenCode 本機 API、重算四截面並沉澱 v2；建立 LLM 技能鏈與治理規則更新** (`feature + refactor + docs + chore`)
  後端由 Ollama 改連 OpenCode 本機 API（`opencode-go/deepseek-v4.1-flash`，密碼執行期動態讀取不入檔），只換 LLM backend、數值核心不變；重算四截面 Z₀／IL／RL 沉澱至 `standard_section_IL_RL_v2/`，`summary.json` 差異 0、四份 CSV 逐位元組相同、C1–C9 31 項全 PASS、pytest 46 passed、原報告 md5 未變。建立 `llm-router` → `quantum-llm` → `em-llm` 鏈並同步 chain-skill／quantum-router／skill-family／allow-list；治理裁決「開發本機技能不 hook audit-skill」寫回三技能形成閉環。背景 worker 因自身模型額度中斷，主線依 `audit-worker-subagent` 重新開檔獨立驗證接手完成。→ [完整日誌](logs/2026-11-26-em-llm-opencode-skill-chain.md)

## 2026-11-25

- **修正 chain-skill 對 viz-router 的 doc/code compliance 歸屬矛盾** (`fix + docs`)
  依前筆稽核 #6 與使用者裁決「是改 chain-skill 的歸屬句」（Gate 0），最小修正 4 處歸屬句 + 1 行 Logic check：改為「`viz-router` 僅 goal→hook 路由；hooked child 執行 SVG／demo 驗證；`rev-skill` 管 Logic L6 文件↔實作一致」。rev-skill Gate 0–5：pre 0/100 LOW SAFE → RED 8/9 → GREEN 8/8 → post 7/100 LOW SAFE（LP3 僅測試檔 file_read，降 Low）→ drift 僅 SKILL.md + 新測試（皆預期），post manifest 自比對 OK。原稽核報告 #5/#6/#8 已更新為「修正後 PASS」；未新增 hook。→ [完整日誌](logs/2026-11-25-chain-skill-viz-router-attribution.md)

- **核實 audit-skill-chain ↔ chain-skill：八段契約稽核報告** (`docs`)
  依 `audit-skill-chain`「先建表、後查證」契約產出 127 行報告（八段全填、無占位）。核心發現：兩技能**雙向皆無引用**（唯一相關是 `topic-router:38` 的單向跨家族引用），判定「無引用／此鏈不存在」；`chain-skill:240` 宣稱「viz-router owns demo-code compliance」與 `viz-router:11,27,50` 的 route-only 自述矛盾，標「須澄清」。其餘如實揭露：無 `version:`、未收錄 allow-list、git 未追蹤、`~/薦家/布球/` 為不存在的設計常數、無 scripts/MANIFEST 故 N/A。判定 #1/#2/#4/#5 PASS、#3 N/A、#6/#7 FAIL。→ [完整報告](../../../skill-reports/audit-skill-chain-vs-chain-skill.md)／[日誌](logs/2026-11-25-audit-skill-chain-vs-chain-skill.md)


- **toolkit-viz 去除 4 處冗餘規則** (`refactor + docs`)
  核實後區分「定義+引用型合理重複」（GIT_ASKPASS／sync_topics／同源快照／Logic check 歷史，保留）與真冗餘，移除：(1) `sync_topics.py` 指令在使用方式段與 SSOT.D2 完整重複 → 改引用；(2) 裸 `git commit && git push` 繞過 D3 GIT_ASKPASS／D4 push.sh → 改 hook；(3) 整合進來的 `__init__.py` docstring 重述 SSOT 規則 → 改「見 SKILL.md 不重複」；(4) `data.py` 舊 showcase 路徑註解 → 改新路徑。SSOT A–E 本體未動。Gate 0–5：pre `toolkit-viz-dedup-pre.sha256`(62/100) → RED 4/4 → GREEN 4/4 → post 62/100（findings 與 pre 同，無新增）、drift 僅 4 預期檔；既有整合測試 4/4、B2 測試 all checks 仍 GREEN。→ [完整日誌](logs/2026-11-25-toolkit-viz-dedup.md)


- **整併 push-streamlit 合併與「更新演示工具」並行變更、最終稽核** (`refactor + docs + fix`)
  另一 session 完成的 skill_inventory 整合（`src/views/skill_inventory/` + 快照 + app.py 路由）與 §E「更新演示工具」直接實作例外，與本輪 push-streamlit D1–D7 合併核實為不衝突。修正 `test_b2_direct_render.py` 的字面字串掃描（排除 tests/ 與 SKILL.md 歷史 Logic check）。四支測試全 GREEN；最終稽核 raw 62/100 HIGH 的 40 個 findings 全在唯讀盤點快照（惰性 skill description 文字），降級 `APPROVE / Low`；drift 全為兩階段預期檔。→ [完整日誌](logs/2026-11-25-toolkit-viz-parallel-merge.md)


- **整合 skill_inventory_showcase 入 toolkit-viz，原 showcase 標 deprecated** (`feature + refactor + docs`)
  把 `~/skill-inventory-viz/skill_inventory_showcase/` 整合入 toolkit-viz skill。來源取已去折疊、相對 import 已修復的 `quantum_website/src/views/skill_inventory/` 移植版（非含 9 處 expander 的原 showcase），落點 `src/views/skill_inventory/` + `data/skill_inventory_viz_data.json`；`app.py` 頂層加「展示模式」radio（SSOT.B.1）分派蒸餾主題／技能盤點。`skill_inventory_showcase` 非 skill，deprecated 以 thin pointer（`DEPRECATED.md`）+ spec 註記處理，不碰 self-developed.list；原程式保留供追溯。SSOT A–E 規則文字不改（只引用）。rev-skill Gate 0–5：pre manifest `toolkit-viz-pre.sha256`、RED 4/4、GREEN 4/4、post audit + drift（僅預期檔）、py_compile／0 expander／同源一致性通過。→ [完整日誌](logs/2026-11-25-skill-inventory-into-toolkit-viz.md)


- **合併 push-streamlit 入 toolkit-viz D 節並降為 deprecated alias** (`refactor + docs`)
  `toolkit-viz` D 節由 2 條擴為 D1–D7（repo 事實卡／origin 推導鐵律、sync_topics 閘門、hook `push-repo` GIT_ASKPASS、push.sh、Cloud/HF/Kaggle 三目標含免費層硬限制、health+內容驗證、除錯預防合併）；既有 Known Issues／預防措施移除併入 D7，未重新引入 `__init__.py` 同步規則。`push-streamlit` 降為 `deprecated_keep` thin alias（`replaced_by: toolkit-viz`），5 支 scripts 保留原路徑供 D 節引用。13 份技能交叉引用同步（push-router／topic-post／viz-router／skill-family／skill-seek／skill-dependency-hook／chain-skill／social-media-suite／stock-market／sci-router／audit-credential／topic-distill／ai-ml-app-engineering）；allow-list 保留 deprecated_keep。rev-skill Gate 0–5：RED 7+4 FAIL → GREEN 8+4 PASS → post4 9/100 LOW 與 raw 59/100 HIGH（6 findings 與 pre4 全同、逐條舉證降級）皆 `APPROVE / Low`、drift 僅預期檔。→ [完整日誌](logs/2026-11-25-push-streamlit-merge.md)


- **移除 toolkit-viz SSOT A4「__init__.py 保持與 app.py 一致」** (`refactor + docs`)
  skill-seek 核實：全 SKILL.md／docs／changelog 無「`__init__.py` symlink 指向 `app.py`」規則；最接近的 A4 與 `push-streamlit:36` 是內容同步的 Streamlit 規則、未要求 symlink。依使用者明確裁決移除 A4（本機 repo 已無 `app.py`，`__init__.py` 為唯一入口；`push-streamlit` 打包明確排除 `__init__.py`），A5「相對路徑」遞補為 A4。rev-skill Gate 0–5：pre3 9/100 LOW → RED 4 FAIL → GREEN 4 PASS → post3 9/100 LOW `APPROVE / Low`、drift 僅預期檔。`topic-distill:35` 同類字串未改（需另裁決）。→ [完整日誌](logs/2026-11-25-toolkit-viz-a4-removal.md)


- **移植 viz 演示工具、全站去除折疊區塊、修正 src.data 絕對 import** (`feature + refactor + fix`)
  將 `~/skill-inventory-viz/skill_inventory_showcase/` 移植為 `quantum_website/src/views/skill_inventory/`，快照複製到 `data/`，入口以 `skill_inventory_sidebar()`／`render_skill_inventory()` 接入 `__init__.py` 新分段（不新增 pages/）。全 repo 6 處 `st.expander` 改為直接呈現，遵循 toolkit-viz SSOT B2。使用者回報 `ModuleNotFoundError: No module named 'src.data'` — 查證根因是移植後 view 仍用絕對 `from src.data import ...`，改為相對 `from ..data import ...` 修復（**不是** `__init__.py` 未 symlink 至 `app.py`）。skill-seek 核實：所有 SKILL.md／docs／changelog 均無「`__init__.py` symlink 指向 `app.py`」規則；最接近的 toolkit-viz A4 與 push-streamlit:36 是內容同步的 Streamlit 規則，未要求 symlink。驗證：expander／selectbox／use_container_width 零命中、py_compile PASS、venv import 煙霧測試 PASS、兩入口 SECTIONS 同步。→ [完整日誌](logs/2026-11-25-quantum-website-viz-streamlit.md)


- **合併 sci-sediment／sci-research-distill 並將 sci-router 收斂為純 router** (`refactor + docs`)
  重疊分析結論：共享證據紀律、骨架互補 → `sci-sediment` v2.0.0 抽出 C1–C4 共用核心（no-invention／estimate·`[待查]`／claim verbs／evidence levels／EN-ZH／common mistakes）為唯一來源，Branch A 保留四區塊科學結果＋概念驗證，Branch B 承接 11 步驟市場研究／商業計畫；`sci-research-distill` 降為 deprecated_keep thin alias（`replaced_by: sci-sediment`）；`sci-router` v2.0.0 移除 S1–S7 全文改為 Goal→Hook 路由（hook `topic-distill`＋`arxiv-search`／`sci-sediment`／`viz-router`／`push-*`）。rev-skill Gate 0–5 全數通過：pre audit 8/0/10 → RED 5/3/3 FAIL → GREEN 5/3/3 PASS → post audit 15/15/14 LOW（findings 全判定惰性／良性）→ drift 僅預期檔；三份 verdict `APPROVE / Low`。chain-skill 三列＋Logic check、skill-family 兩列同步；allow-list 無增刪。無 commit/publish/push。
  → [完整日誌](logs/2026-11-25-science-family-merge.md)


- **建立 skill-crud：合併 skill-creator／writing-skills／writing-plans 為 C/R/U/D 單一全文** (`feature + refactor + docs`)
  依使用者裁決採「獨立合併全文」（非 parent router）、完整 C/R/U/D、裝於 `~/.agents/skills/` 並入 allow-list。`skill-creator` 提供草稿／eval／viewer／description 優化；`writing-skills` 提供 TDD Iron Law、依類型測試、rationalization／micro-test／anti-patterns；`writing-plans` 提供規格→任務切分→self-review→handoff；另補 R（audit-skill + rev-skill Logic L1–L8）、U（Gate 0–5）、D（去留／SSOT／索引同步／task-changelog 三契約）與衝突裁決。稽核 27/100 MEDIUM，2 findings 皆判定為惰性文件文字（grep 路徑範例／本機 viewer `nohup`），verdict `APPROVE / Low`；繁體硬規則掃描修正 4 處。allow-list（SSOT）、chain-skill 盤點＋Logic check、skill-family 路由索引均同步。無 eval 實跑、無 commit/publish/push。
  → [完整日誌](logs/2026-11-25-skill-crud-merge.md)


- **整合 toolkit-viz 舊副本為單一 Streamlit 規則 SSOT + 同步 allow-list／chain-skill 盤點** (`refactor + docs`)
  比對確認舊副本（`~/軟體/代理人/.agents/skills/toolkit-viz/`）5 條鐵律全為主版 SSOT 子集、無獨特規則後刪除；主版 `SKILL.md` 精簡架構註解與重複鐵律並追加 Logic check。稽核首掃 100/100 CRITICAL（bytecode）→ 清 `__pycache__` 後 9/100 LOW，AST3 `__import__('datetime')` 判定良性誤報，報告 `APPROVE / Low`、manifest drift `OK: 10 files match`。治理同步：`self-developed.list`（SSOT）先補 `toolkit-viz`，再同步 chain-skill 盤點列與 Logic check；`skill-router` 已 deprecated、`skill-family` 為 family-parent 索引，故不同步。驗證：舊副本不存在、編輯落地、規則無第二份表述、allow-list／盤點欄位一致。
  → [完整日誌](logs/2026-11-25-toolkit-viz-rule-consolidation.md)

## 2026-11-24

- **topic-router 達爾文 E1/E2 驗收：4 勝 0 負、keep、總分 88.1** (`docs + chore`)
  完成 E0 之後的 E1 讀評 + E2 實跑盲評（darwin 盲評唯一例外派 3 位獨立評委，其餘 native）。8/8 執行者完成、隔離污染的 dev-1 裸跑並乾淨重跑、A/B Jaccard 全 0；`tally` 4 勝 0 平 0 負、檢查項 17 vs 11、體積 +0%、裁決 keep。9 條 fact_claim 逐條核實：勝者 s0 的 4 條全不成立（`e0-check.txt` 為盲評人為移除、`quota-mnpl` 確實存在）、敗者裸跑 5 條成立（`topic-post` 已 deprecated、symlink 底層應 `paperclip-router`），事实與票數同向。9 維總分 88.1（dim8=10，dev 9/9 全過）；新建 `darwin-skill/results.tsv`。E3 真機涉及 Obsidian 不可逆改寫待 human checkpoint；全程 no commit/publish/push。
  → [完整日誌](logs/2026-11-24-topic-router-darwin-e2.md)

- **topic-router 建立：topic 主題家族 + Obsidian 知識庫家族父節點** (`feature + refactor + docs`)
  第四個家族重構（native，no worker）。新建 `topic-router`（v1.0.0）收斂 topic-xxx/xxx-topic 命名技能 + Obsidian 知識庫技能；語意分層避免雙父：`topic-distill` 主父 distill-router、`topic-viz` 主父 viz-router，本 router 僅命名入口轉介；`skill-seek`（承接 topic-seek 舊名）＋obsidian-automation/obsidian-markdown/para-memory-files 直接 hook 為主父；topic-post/topic-workflow-auto deprecated 不 hook。同步 allow-list（26 筆）/chain-skill Inventory/skill-family（version→1.1.4）。驗證：darwin E0 topic-router 0 錯誤 0 警告 1 提示、hook 目標 12/12 存在（含 symlink）、26/26 SSOT 一致、雙父標註正確。
  → [完整日誌](logs/2026-11-24-topic-router-obsidian-family.md)

- **家族 router 批次重構：quant-algo-auto 拆解 + vid-router + paperclip-router + 索引同步** (`refactor + feature + docs`)
  延續 chain-skill 六階段 + darwin-skill E0-E3，把本機家族逐一收斂到單一 router（native，no worker）。(1) `quant-algo-auto` 拆解 deprecated：交易面 100% 重複於 `quant-risk-bt`、新建 `quant-channel` 承接唯一獨有 12 週 content plan、通用影片導向 `yt-vid`；(2) 新建 `vid-router` 收斂 vid/video-autopilot/remotion-* 30+ child，`video-agent-jianying-editor` deprecated；(3) 新建 `paperclip-router` 收斂 paperclip-* 平台治理 + market-*/marketing-* 行銷職能，`video-market-analysis` 主父標 vid-router 避免雙父；(4) allow-list SSOT += quant-channel/vid-router/paperclip-router，chain-skill／skill-family 索引同步，`topic-workflow-auto` 補 deprecated frontmatter。驗證：darwin E0 六 skill 全 0 錯誤、hook 目標 20/20 存在、allow-list 25/25 一致；全程 no commit/publish/push。
  → [完整日誌](logs/2026-11-24-family-routers-quant-vid-paperclip.md)

- **skill-family 閉環 router + mindmap-viz 抽離（draw/push/social/mindmap/svg）** (`feature + refactor + docs`)
  新建 `skill-family`（v1.0.0）閉環 router parent：父節點導向 → hook 下級 → hook 本機既有（14/14 驗證存在，不另開發）→ 功能集合（draw/push/social/mindmap/svg）→ 沉澱；含 darwin-skill 風格 S1-S6 進化機制與跨家族明確父節點對照表。同時將 viz-router 的 SVG render/validate 抽離成 `mindmap-viz` demo tool（V2 Logic check 寫回）。兩份 plan + changelog 落地；allow-list 納入待裁決，本次無排程/发布/commit。
  → [完整日誌](logs/2026-11-24-skill-family-mindmap-viz.md)

- **distill-showcase --> toolkit-viz 改名殘留清理 + 視頻展示線收斂（含網站 module 改名）** (`refactor + docs`)
  依 chain-skill 維護節奏完成 `distill-showcase` → `toolkit-viz` 改名殘留清理：主 skill 目錄/副本/venv/網站 module 改名、跨專案殘留引用批量替換；14 檔 py_compile 全數 PASS、舊名掃描排除 runtime/git 後殘留清零（module 已改名）。視頻展示線（toolkit-viz / distill_paper / floquet / 9coeff / temperature-zone）改名收斂。
  → [完整日誌](logs/2026-11-24-toolkit-viz-rename-cleanup.md)

- **五家族技能鏈閉環 GREEN 批次交付（topic/sci/social/push/viz）+ viz rename** (`refactor + docs`)
  五家族（topic/sci/social/push/viz）依 chain-skill 六階段閉環落地 GREEN：topic（R1–R6，含 version 漂移修、空殼刪除、rename、deprecation 用語）、sci（S1–S4 合併）、social（SO1–SO5）、push（P2/P3 token 安全）、viz（V1/V5）。同時完成 `viz-dboard` → `viz-router` rename（Gate 0：全改＋舊 trigger 保留，不發布）。驗證：GREEN baseline manifest 20 檔、post audit（多數 APPROVE/LEANING）、drift 僅預期 CHANGED、殘留掃描通過、token-in-URL 清零。→ [完整日誌](logs/2026-11-24-family-green-batch.md)

- **撰寫「每月一次、星期五 22:00」家族鏈合規排程計畫** (`docs`)
  依 `writing-plans` 格式撰出 implementation plan（`/home/sam/docs/superpowers/plans/2026-11-24-family-chain-scheduler.md）：排程規格（每月一次、星期五 22:00；chain sequence topic→sci→push）、Global Constraints（report-only、timer 不撞週日 weekly）、Review Focus（時鐘對／report-only 邊界／頻率解讀）、Tasks 1–3。→ [完整日誌](logs/2026-11-24-family-chain-scheduler-plan.md)

## 2026-11-18

- **新建 sssn-output 技能：列舉 session + 對話匯出 Markdown（TDD 全流程）** (`feature`)
  依 `@writing-skills` 需求（列舉 session／內建方法 A／沉澱成 skill）以完整 RED→GREEN→REFACTOR 開發。3 個無 skill baseline subagent 擷出 6 個失敗模式（CLI list 70≠DB 188、DB 表格陷阱、目前 id 找不到、export 不含 child/有損、最近更新是移動標靶、不知有現成工具）。form matching 判定為 how-to 缺口 → positive recipe + decision table 而非 prohibition。bundled `session-export-to-md.py` 新增 `--list`/`--current`（DB 唯讀）；SKILL.md 含 Quick Reference 決策表 + Step 2.5「最近更新 id 映射規則」。3 GREEN 對照全過並指出 7 個缺口（路徑、映射規則、limit 截斷、快照標註等），REFACTOR 補齊後重測全過。audit-skill APPROVE（24/MEDIUM，3 issues 全溯源到必要的官方 CLI subprocess、良性）、manifest 無 drift。
  → [完整日誌](logs/2026-11-18-sssn-output.md)

- **推廣 audit-worker-subagent 驗證紀律到 35 個技能（軟體 10 + 電磁 19 + QA 6）** (`refactor + docs`)
  以 `audit-worker-subagent` 的真實 RED baseline 為唯一來源，把「Iron Law：宣稱≠證據」+ 六要素（VERIFY／ATTRIBUTE／CROSS-CHECK／JUDGE／REQUIRED BACKGROUND）逐字注入 35 個 SKILL.md 檔尾，只新增不改既有。3 個 worker 並行（software 10／電磁 19／QA 6），hub 用總則標題省力覆蓋家族，verification-before-completion 走 cross-ref 例外。驗證 PASS：35/35 結構檢查、audit-skill 全量 35 檔掃描（高分 finding 全在既有內容）、2 個高優先壓力測試皆 GREEN（空 diff 拒絕派 reviewer／合併；50 μW 無輸出拒絕寫報告，交叉比對 + 量級 sanity check 抓出物理不可能）。索引列 + CHANGELOG 已同步。
  → [完整日誌](logs/2026-11-18-audit-discipline-promotion.md)

- **新建 audit-worker-subagent 技能：派工後獨立驗收 + 模型對接審查** (`feature`)
  依真實 RED baseline（worker 四次空轉誤報完成、router 盲信三次）沉澱 Iron Law「無獨立 VCS/FS 證據不接受完成宣稱」+ Audit Gate 五步（RECEIVE/VERIFY/ATTRIBUTE/CROSS-CHECK/JUDGE）+ 模型對接審查 6 步 + 8 條 rationalization + 6 條 red flags。以 writing-skills 完整 RED→GREEN→REFACTOR 開發：3 without-skill + 2 with-skill + 1 誘餌重測全數通過（重測抓出「檔案確實存在但属舊成果」且未矯枉過正）。audit-skill 掃描 0/100 LOW SAFE、APPROVE、manifest 無 drift。
  → [完整日誌](logs/2026-11-18-audit-worker-subagent.md)

- **新建 audit-skill-chain 技能：技能鏈稽核契約與雙向證據表** (`feature`)
  依真實 RED baseline 的 7 個偏差，以 writing-skills 的 form matching 決策建立「逐邊×雙向×證據表」稽核契約：REQUIRED 八段報告模板 + 7 步 recipe + 常見藉口對照表 + red flags；表格是查證驅動結構而非事後整理。worked example 如實呈現熱負載鏈 4 個真實缺陷（語意不閉合、MANIFEST 漏檔、功能.xlsx 矛盾、溯源路徑不可解析），並標註 heatload-sop 刻意重複。驗證 PASS（REFACTOR 3 路對照：control 無技能仍零散/事後補表，2 treatment 有技能皆先建表/逐邊雙向/正反向 MANIFEST/內容對帳/語意質疑，並在壓力下抓出真缺陷拒絕簽核；據此補入 checklist 與 red flags 的 3 點強化）。
  → [完整日誌](logs/2026-11-18-audit-skill-chain.md)

- **heatload-coff-nist 蒸餾展示整合（論文出處/資料庫/計算 Excel）** (`feature`)
  於 `references/` 產出下游計算 Excel（`Thermal Calculator` 21×8）與展示總覽 md；`toolkit-viz/app.py` 加法式新增 Excel/CSV 下載區；重建索引後 heatload-coff-nist 為 3 個 md。streamlit 1.57.0 可用（flex python）。驗證 PASS（reviewer 四面向核實 + router AppTest 複核：3 下載按鈕、0 exception、health 200）。
  → [完整日誌](logs/2026-11-18-heatload-showcase.md)

- **thermal-* 技能重命名為 heatload-* + 全引用同步** (`refactor`)
  9 個目錄重命名（主目錄 5 + 副本 4）：`thermal-coff-nist`→`heatload-coff-nist`、`thermal-load-*`→`heatload-*`；48 檔共 180 處技能名引用同步；版本號 +1 minor；MANIFEST 重算；歷史日志加更名註記。驗證 PASS（reviewer 實跑 8 項全數 OK）。
  → [完整日誌](logs/2026-11-18-heatload-rename.md)

- **已停業素食餐廳不列入總覽卡與 contact sheet** (`fix + docs`)
  已停業的「三個傻瓜 印度蔬食」從 card / overview 兩張展示卡（素食 4→3 間）與 contact sheet（15→14 格）移除；資料與 15 張原始 SVG 保留。渲染時過濾，`contact_sheet.py` 新增 `--exclude`。三套數值驗證全 PASS，色差 3.34 / 3.19 /255。
  → [完整日誌](logs/2026-11-18-poi-closed-restaurant.md)

- **熱負載技能上下級鏈重構 + 新建 heatload-coff-nist + 建立 task-changelog 常態日誌機制** (`refactor + feature`)
  熱負載技能鏈重構為「出處 → 計算 → 產出/量測」linked list；新增 `heatload-coff-nist`（54 材料 9 係數對照表 + 計算引擎）；建立本常態日誌機制並寫下第一筆。
  → [完整日誌](logs/2026-11-18-thermal-load-chain.md)
