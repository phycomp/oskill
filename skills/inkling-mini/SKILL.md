---
name: inkling-mini
description: 部署與驗證 unsloth/Inkling-2-Mini-GGUF（UD-Q4_K_M）本機推論。Use when 使用者提到 Inkling-2-Mini、Inkling 2 Mini GGUF、inkling2_loop、inkling2v、Ollama 不支援此架構、llama.cpp b12803、llama-server OpenAI 相容 API，或要檢查本機 Inkling 模型/端點狀態。所有回覆與文件使用繁體中文（正體中文）。
---

# inkling-mini

把 `hf.co/unsloth/Inkling-2-Mini-GGUF:UD-Q4_K_M` 跑成可驗證的 OpenAI 相容端點，並清楚記錄本機（WSL2 + RTX 5060 Laptop 8GB）的可行邊界。

## 快速結論（先讀這個）

- **Ollama 不能跑這個模型。** Ollama 0.40.14 內建 llama.cpp `b11963`，0.40.17 也只到 `b12257`；Inkling 需要 `b12600+` 才認得架構、`b12611+` 才有正確輸出、`b12641+` 才有 tokenizer 修正。
- **可行路線是 llama.cpp `b12803` 官方 CUDA 12.8 預編譯檔 + 已下載的 GGUF blob**。2026-11-27 已在本機實際驗證：模型載入成功、`/health` OK、`/v1/models` 200、`/v1/chat/completions` 200 且輸出 `OK`。
- 本機速度約 **2.65 tok/s**，模型載入約 **141–144 秒**；這是「可正確推論」不是「流暢對話」。
- OpenCode 可列出 `inkling/inkling-mini`，但 **agent 會話（`opencode run`）目前不可用**：system prompt + skills 清單高達 92k tokens，4096 ctx 仍會被 compaction／取消。可直接用 curl 打 `/v1`。

## 何時使用

1. 要確認 Inkling-2-Mini 在本機能不能跑、用什麼執行器。
2. 要啟動／停止 `llama-server` 並做 API 冒煙測試。
3. 要排查 Ollama pull 成功但 `ollama run` 報 `unknown model architecture`。
4. 要查 OpenCode 接法與其失效邊界。

## 本機已驗證事實（勿重複猜測）

| 項目 | 值 |
| --- | --- |
| 模型 blob | `/mnt/d/ollama/models/blobs/sha256-78fcedcf93c5d1bfe83e225513b71392bb52259be0eaa5f8899c856a2e5834ae`（16,610,544,608 bytes） |
| mmproj blob | `/mnt/d/ollama/models/blobs/sha256-2c165c78790e78a3f45a2d1e9e931083e52ee69d45ff2a0dc9c281fdf1a666e7`（641,805,760 bytes） |
| GGUF 架構 | `inkling2_loop`；mmproj 為 `inkling2v`；quant `Q4_K - Medium` |
| 模型規模 | 26.2B 總參數（本機回報 `n_params=26070390272`）、3.4B active、約 5.4B effective/token；訓練 context 1,048,576 |
| 執行器 | `/mnt/d/llama-b12803/llama-b12803/llama-server`；`version: 1.1.0-dev (build 12803, commit 492d23cc9)` |
| CUDA libs | `/mnt/d/llama-b12803/cudart-llama-b12803-bin-ubuntu-cuda-12.8-x64`（必須放進 `LD_LIBRARY_PATH`） |
| 硬體 | RTX 5060 Laptop GPU 8151 MiB；`-ngl 8` 時用到約 7.6 GiB；RAM 15Gi + Swap 4Gi |
| 端點 | `http://127.0.0.1:8001/v1`，model id `inkling-mini` |
| 速度 | prompt 約 2.77 tok/s，generate 約 2.65 tok/s（`Say OK.` 共 20.3 秒 wall） |
| 載入時間 | 約 141–144 秒（含 mmproj） |

## 啟動（可直接執行）

詳見 `scripts/serve.sh`；核心指令：

```bash
LLAMA_DIR=/mnt/d/llama-b12803/llama-b12803
CUDART_DIR=/mnt/d/llama-b12803/cudart-llama-b12803-bin-ubuntu-cuda-12.8-x64
LD_LIBRARY_PATH="$LLAMA_DIR:$CUDART_DIR:${LD_LIBRARY_PATH:-}" \
  "$LLAMA_DIR/llama-server" \
  -m /mnt/d/ollama/models/blobs/sha256-78fcedcf93c5d1bfe83e225513b71392bb52259be0eaa5f8899c856a2e5834ae \
  --mmproj /mnt/d/ollama/models/blobs/sha256-2c165c78790e78a3f45a2d1e9e931083e52ee69d45ff2a0dc9c281fdf1a666e7 \
  --alias inkling-mini -c 4096 \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --no-repack --no-warmup -np 1 -ngl 4 \
  --host 127.0.0.1 --port 8001
```

注意事項：

- `cudart-llama-b12803-bin-ubuntu-cuda-12.8-x64.tar.gz` **只含 CUDA runtime libs，沒有 llama-server**；必須另外下載 `llama-b12803-bin-ubuntu-cuda-12.8-x64.tar.gz`。
- `-c 1024` 也能啟動，但只適合直接 curl 短提示；OpenCode 需要更大 context。
- `--no-repack --no-warmup -np 1` 是在 8GB 等等級環境降低啟動壓力的必要參數。
- 若用 `-ngl 8`，VRAM 逼近上限（約 7.6/8.1 GiB）；`-ngl 4` 較安全且已驗證。
- 模型 chat template 會保留 reasoning 到 `reasoning_content`，**它會吃掉 `max_tokens`**。`max_tokens=32` 時 `content` 是空的；至少用 160。

## 驗證（照順序做，保留證據）

```bash
curl -sS http://127.0.0.1:8001/health
curl -sS http://127.0.0.1:8001/v1/models
time curl -sS -H 'Content-Type: application/json' \
  -d '{"model":"inkling-mini","messages":[{"role":"user","content":"Say OK."}],"max_tokens":160,"temperature":0}' \
  http://127.0.0.1:8001/v1/chat/completions
```

通過條件：`/health` 回 `{"status":"ok"}`；`/v1/models` 含 id `inkling-mini` 且 `HTTP=200`；chat 回 `message.content` 為 `OK`、`finish_reason=stop`、`HTTP=200`。完整成功輸出保存在 `/home/sam/opencode-work/inkling-chat-test-160.json` 與 `inkling-v1-models.json`。

## OpenCode 接法與已知失效邊界

`~/.config/opencode/opencode.jsonc` 已加 provider（備份：`~/.config/opencode/opencode.jsonc.bak.pre-inkling-20261127104044`）：

```jsonc
"inkling": {
  "name": "inkling（本機 llama.cpp b12803）",
  "package": "@opencode/ai/providers/openai-compatible",
  "settings": { "baseURL": "http://127.0.0.1:8001/v1", "encoding": "none",
                "headerTimeout": 1800000, "chunkTimeout": false },
  "models": { "inkling-mini": {
    "modelID": "inkling-mini", "name": "inkling-mini", "family": "inkling2",
    "capabilities": { "tools": false, "input": ["text"], "output": ["text"] },
    "limit": { "context": 4096, "output": 512 },
    "compatibility": { "maxTokensField": "max_tokens" }
  }}
}
```

- `opencode models` 已列出 `inkling/inkling-mini`。
- `opencode run --model inkling/inkling-mini '...'` 失敗：server log 記錄 `request (92884 tokens) exceeds the available context size`；即使換成極短 system prompt 的測試 agent 也有 3483 tokens，1024 ctx 仍然 compaction 失敗。
- 提到 4096 ctx 後 request 會進到 server，但 OpenCode 在 300 秒內取消、沒有產出。**不要宣稱 OpenCode agent 已可用**；目前可用的是 OpenAI 相容 HTTP API。
- 若要讓 agent 真正可用，需要大幅提升 server context（並接受更大 KV cache／更慢速度）或更強硬體。

## 常見錯誤與處置

| 現象 | 原因 | 處置 |
| --- | --- | --- |
| `unknown model architecture: 'inkling2_loop'` | Ollama / 舊 llama.cpp | 改用 llama.cpp b12803，不要期待 Ollama |
| Ollama pull 最後 `chmod ... operation not permitted` | `/mnt/d` 是 WSL 9p 掛載，Ollama 無法 chmod 暂存擋 | blob 已完整（sha256 符合），直接用 llama-server 讀 blob |
| chat 回 `content: ""`、`reasoning_content` 很長 | `max_tokens` 被思考吃掉 | 提到至少 160；必要時 `--no-reasoning-preserve` |
| `failed to fit params to free device memory` | 明確指定了 `-ngl` | 降低 `-ngl` 或接受警告；本機 `-ngl 4` 已驗證 |
| `Flash Attention not supported, set to disabled` | b12803 CUDA build 限制 | 不影響正確性，只影響速度 |
| 載入很久、沒有回應 | 16.6GB 模型需 offload | 等 141–144 秒；CPU-only 路線極慢（參考 28-token prompt 13 分鐘無回覆） |

## 邊界與未驗證

- 已驗證：文字生成、`mmproj` 成功載入、`/v1/models` 回報 `completion` 與 `multimodal` capabilities。
- 未驗證：實際圖片／影片輸入的輸出品質；工具呼叫（provider 已設 `tools: false`）；長 context（>4096）穩定性；OpenCode agent 會話。
- 不要抄錄或提交 `USAGE_TEST_EXAMPLES.md` 內的明文 HF token；本機 token 只以「有憑嫌疑人」記錄。

## 來源

- Unsloth README（已下載）：`/home/sam/opencode-work/inkling-mini-README.md`
- llama.cpp release b12803：`https://github.com/ggml-org/llama.cpp/releases/tag/b12803`
- vLLM GGUF 官方文件（對照用）：`https://docs.vllm.ai/en/latest/features/quantization/gguf/`
- Ollama 版本 pin：`https://raw.githubusercontent.com/ollama/ollama/v0.40.14/LLAMA_CPP_VERSION`、`v0.40.17/LLAMA_CPP_VERSION`
- 本機證據：`/home/sam/opencode-work/inkling-llama-server-4096.log`、`inkling-v1-models.json`、`inkling-chat-test-160.json`
