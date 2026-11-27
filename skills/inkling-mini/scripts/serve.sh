#!/usr/bin/env bash
# 啟動 Inkling-2-Mini 的 llama.cpp b12803 llama-server（OpenAI 相容 /v1）。
# 本機已驗證：RTX 5060 Laptop 8GB + 15GB RAM，約 141–144 秒載入，約 2.65 tok/s。
set -euo pipefail

LLAMA_DIR="${LLAMA_DIR:-/mnt/d/llama-b12803/llama-b12803}"
CUDART_DIR="${CUDART_DIR:-/mnt/d/llama-b12803/cudart-llama-b12803-bin-ubuntu-cuda-12.8-x64}"
MODEL="${MODEL:-/mnt/d/ollama/models/blobs/sha256-78fcedcf93c5d1bfe83e225513b71392bb52259be0eaa5f8899c856a2e5834ae}"
MMPROJ="${MMPROJ:-/mnt/d/ollama/models/blobs/sha256-2c165c78790e78a3f45a2d1e9e931083e52ee69d45ff2a0dc9c281fdf1a666e7}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8001}"
CTX="${CTX:-4096}"
NGL="${NGL:-4}"
LOG="${LOG:-/home/sam/opencode-work/inkling-llama-server-4096.log}"

for f in "$LLAMA_DIR/llama-server" "$MODEL" "$MMPROJ"; do
  [[ -e "$f" ]] || { echo "缺少檔案：$f" >&2; exit 1; }
done

export LD_LIBRARY_PATH="$LLAMA_DIR:$CUDART_DIR:${LD_LIBRARY_PATH:-}"

echo "啟動 llama-server：$HOST:$PORT ctx=$CTX ngl=$NGL log=$LOG"
nohup "$LLAMA_DIR/llama-server" \
  -m "$MODEL" \
  --mmproj "$MMPROJ" \
  --alias inkling-mini \
  -c "$CTX" \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --no-repack --no-warmup \
  -np 1 -ngl "$NGL" \
  --host "$HOST" --port "$PORT" \
  > "$LOG" 2>&1 &

PID=$!
echo "PID=$PID"
for i in $(seq 1 240); do
  if curl -fsS --max-time 2 "http://$HOST:$PORT/health" >/dev/null 2>&1; then
    echo "READY after ${i}s"
    exit 0
  fi
  if ! kill -0 "$PID" 2>/dev/null; then
    echo "SERVER_DIED" >&2
    tail -50 "$LOG" >&2
    exit 1
  fi
  sleep 1
done
echo "TIMEOUT：240 秒內未 ready" >&2
exit 1
