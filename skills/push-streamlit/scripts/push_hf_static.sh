#!/usr/bin/env bash
# push_hf_static.sh — 把 markdown references 轉成靜態 HTML 站並上傳 Hugging Face Static Space
#
# HF 免費層只能跑 Static Space（Streamlit/Gradio/Docker 需 PRO，實測 402/配額 0）。
# 本腳本：md → 自帶深色 CSS 的靜態站（index + 各文檔頁、側欄導覽、表格樣式）→ hf upload。
#
# 用法:
#   bash push_hf_static.sh <source_dir> [space_name] [--title "站名"] [--public|--private] [--dry-run] [--wait]
#
# 依賴：/home/sam/flex/bin/python（markdown 套件；缺則自動 pip install，失敗則用內建 fallback 轉換器）
#       hf CLI（/usr/sbin/hf），curl。token 不印出。

set -euo pipefail

PY="${PY:-/home/sam/flex/bin/python}"
PIP="${PIP:-/home/sam/flex/bin/pip}"
HF="${HF:-hf}"
STAGE="${STAGE_DIR:-/tmp/opencode/hf-static}"

usage() {
  echo "用法: $0 <source_dir> [space_name] [--title \"站名\"] [--public|--private] [--dry-run] [--wait]" >&2
  exit 2
}

[[ $# -ge 1 ]] || usage
SOURCE_DIR="$1"; shift
[[ -d "$SOURCE_DIR" ]] || { echo "[FAIL] source_dir 不存在：$SOURCE_DIR" >&2; exit 1; }

SPACE_NAME="topic-notes"
SITE_TITLE=""
VISIBILITY="private"
DRY_RUN=0
WAIT_FLAG=0
for arg in "$@"; do
  case "$arg" in
    --title) SITE_TITLE="__NEXT__" ;;
    --public) VISIBILITY="public" ;;
    --private) VISIBILITY="private" ;;
    --dry-run) DRY_RUN=1 ;;
    --wait) WAIT_FLAG=1 ;;
    -*) echo "[FAIL] 未知旗標：$arg" >&2; exit 2 ;;
    *)
      if [[ "$SITE_TITLE" == "__NEXT__" ]]; then SITE_TITLE="$arg"
      elif [[ "$SPACE_NAME" == "topic-notes" && "$arg" != "topic-notes" ]]; then SPACE_NAME="$arg"
      else SPACE_NAME="$arg"; fi
      ;;
  esac
done
[[ "$SITE_TITLE" == "__NEXT__" ]] && { echo "[FAIL] --title 需要值" >&2; exit 2; }
[[ -z "$SITE_TITLE" ]] && SITE_TITLE="$SPACE_NAME"

slug_space() { echo "$1" | tr '[:upper:]_' '[:lower:]-'; }

echo "=== [1/5] 參數與依賴 ==="
echo "[OK] source = $SOURCE_DIR"
echo "[OK] space  = $SPACE_NAME | title = $SITE_TITLE | visibility = $VISIBILITY | dry-run = $DRY_RUN"

# markdown 套件
if "$PY" -c "import markdown" >/dev/null 2>&1; then
  echo "[OK] python-markdown 可用"
else
  echo "[INFO] 安裝 markdown 套件…"
  "$PIP" install markdown >/dev/null 2>&1 || echo "[WARN] pip install markdown 失敗，將使用 fallback 轉換器"
fi

# owner/token
OWNER=""
TOKEN=""
if [[ "$DRY_RUN" == "1" ]]; then
  echo "[WARN] --dry-run：略過登入檢查（owner=dryrun-user）"
  OWNER="dryrun-user"
else
  TOKEN=$("$HF" auth token 2>/dev/null || true)
  WHO=$("$HF" auth whoami 2>&1 || true)
  OWNER=$(echo "$WHO" | sed -n 's/^user=\([^ ]*\).*/\1/p' | head -1)
  if [[ -z "$OWNER" && -n "$TOKEN" ]]; then
    OWNER=$(curl -s -H "Authorization: Bearer $TOKEN" https://huggingface.co/api/whoami-v2 | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('name',''))" 2>/dev/null || true)
  fi
  [[ -n "$OWNER" ]] || { echo "[FAIL] 無法取得 HF 帳號（請先 hf auth login）" >&2; exit 1; }
  [[ -n "$TOKEN" ]] || { echo "[FAIL] 無法取得 HF token" >&2; exit 1; }
  echo "[OK] 帳號 = $OWNER"
fi
SPACE_ID="$OWNER/$SPACE_NAME"
RUN_URL="https://$(slug_space "$OWNER")-$(slug_space "$SPACE_NAME").static.hf.space"
echo "[OK] 目標 Space = $SPACE_ID"
echo "[OK] 預期網址  = $RUN_URL"

echo "=== [2/5] 建 staging（$STAGE）==="
rm -rf "$STAGE"; mkdir -p "$STAGE"

"$PY" - "$SOURCE_DIR" "$STAGE" "$SITE_TITLE" <<'PYTHON'
import sys, os, re, html, json
from pathlib import Path

src = Path(sys.argv[1])
stage = Path(sys.argv[2])
site_title = sys.argv[3]

# collect md files
md_files = sorted([p for p in src.iterdir() if p.suffix.lower() == '.md'])
if not md_files:
    print('[FAIL] source_dir 無 .md 檔', file=sys.stderr); sys.exit(1)

# converter
use_md = False
try:
    import markdown as mdlib
    use_md = True
except Exception:
    pass

def md_to_html(text):
    if use_md:
        return mdlib.markdown(text, extensions=['tables','fenced_code','toc','sane_lists','attr_list'])
    # minimal fallback: headings, code fences, inline code, bold, links, lists, tables
    lines = text.splitlines()
    out=[]; in_code=False; in_ul=False; in_ol=False; in_table=False
    def close_lists():
        nonlocal in_ul,in_ol,in_table
        tags=[]
        if in_ul: tags.append('</ul>'); in_ul=False
        if in_ol: tags.append('</ol>'); in_ol=False
        if in_table: tags.append('</tbody></table></div>'); in_table=False
        return ''.join(tags)
    def esc(s): return html.escape(s)
    def inline(s):
        s=esc(s)
        s=re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        s=re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
        s=re.sub(r'\*([^*]+)\*', r'<em>\1</em>', s)
        s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
        return s
    i=0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('```'):
            if not in_code:
                out.append(close_lists()); out.append('<pre><code>'); in_code=True
            else:
                out.append('</code></pre>'); in_code=False
            i+=1; continue
        if in_code:
            out.append(esc(ln)); i+=1; continue
        m = re.match(r'^(#{1,6})\s+(.*)', ln)
        if m:
            out.append(close_lists()); lvl=len(m.group(1)); out.append(f'<h{lvl}>{inline(m.group(2))}</h{lvl}>'); i+=1; continue
        if re.match(r'^\|', ln):
            # table
            if not in_table:
                out.append(close_lists())
                out.append('<div class="table-wrap"><table>')
                # header
                cells=[c.strip() for c in ln.strip().strip('|').split('|')]
                out.append('<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cells) + '</tr></thead><tbody>')
                in_table=True
                # skip separator if present
                if i+1 < len(lines) and re.match(r'^\|\s*[-: ]+\|', lines[i+1]):
                    i+=2; continue
                i+=1; continue
            else:
                if re.match(r'^\|\s*[-: ]+\|', ln):
                    i+=1; continue
                cells=[c.strip() for c in ln.strip().strip('|').split('|')]
                out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells) + '</tr>')
                i+=1; continue
        else:
            if in_table:
                out.append('</tbody></table></div>'); in_table=False
        if re.match(r'^\s*[-*]\s+', ln):
            if not in_ul: out.append(close_lists()); out.append('<ul>'); in_ul=True
            out.append('<li>'+inline(re.sub(r'^\s*[-*]\s+','',ln))+'</li>'); i+=1; continue
        if re.match(r'^\s*\d+\.\s+', ln):
            if not in_ol: out.append(close_lists()); out.append('<ol>'); in_ol=True
            out.append('<li>'+inline(re.sub(r'^\s*\d+\.\s+','',ln))+'</li>'); i+=1; continue
        if in_ul or in_ol:
            out.append(close_lists())
        if ln.strip()=='':
            out.append(''); i+=1; continue
        if ln.startswith('> '):
            out.append(f'<blockquote>{inline(ln[2:])}</blockquote>'); i+=1; continue
        out.append(f'<p>{inline(ln)}</p>'); i+=1
    out.append(close_lists())
    if in_code: out.append('</code></pre>')
    return '\n'.join(out)

def extract_title(path, text):
    for ln in text.splitlines():
        if ln.startswith('# '): return ln[2:].strip()
    return path.stem

def extract_summary(text):
    # first non-empty non-heading non-blockquote paragraph-like line
    for ln in text.splitlines():
        s=ln.strip()
        if not s: continue
        if s.startswith('#') or s.startswith('>') or s.startswith('|') or s.startswith('-') or s.startswith('*') or s.startswith('```'):
            continue
        s=re.sub(r'[`*_\[\]()]','',s)
        return (s[:160] + '…') if len(s)>160 else s
    return ''

pages=[]
for p in md_files:
    text = p.read_text(encoding='utf-8', errors='replace')
    title = extract_title(p, text)
    body = md_to_html(text)
    slug = p.stem + '.html'
    pages.append({'file': slug, 'src': p.name, 'title': title, 'body': body, 'summary': extract_summary(text)})

CSS = r'''
:root{--bg:#0b1020;--panel:#121a2e;--panel2:#0f1628;--text:#e6edf7;--muted:#9fb0c8;--accent:#7aa2ff;--accent2:#4fd1c5;--border:#22304d;--code:#0a1222}
*{box-sizing:border-box} html,body{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif;line-height:1.7}
a{color:var(--accent);text-decoration:none} a:hover{text-decoration:underline}
.layout{display:flex;min-height:100vh}
nav{width:290px;min-width:240px;background:var(--panel2);border-right:1px solid var(--border);padding:18px 14px;position:sticky;top:0;height:100vh;overflow:auto}
nav h2{font-size:15px;margin:0 0 10px 0;color:var(--muted);font-weight:600;letter-spacing:.02em}
nav .brand{font-size:17px;font-weight:700;color:var(--text);margin-bottom:14px;display:block}
nav ul{list-style:none;padding:0;margin:0}
nav li{margin:4px 0}
nav a{display:block;padding:6px 8px;border-radius:8px;color:var(--text);font-size:14px}
nav a:hover{background:rgba(122,162,255,.12);text-decoration:none}
nav a.active{background:rgba(122,162,255,.18);color:#fff}
main{flex:1;max-width:1100px;padding:28px 34px 60px}
h1{font-size:30px;margin:0 0 8px} h2{font-size:22px;margin:28px 0 10px;border-bottom:1px solid var(--border);padding-bottom:4px}
h3{font-size:18px;margin:22px 0 8px} p{margin:10px 0}
blockquote{margin:10px 0;padding:8px 14px;border-left:4px solid var(--accent);background:rgba(122,162,255,.08);color:var(--muted);border-radius:6px}
code{background:var(--code);padding:1px 6px;border-radius:5px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.92em}
pre{background:var(--code);border:1px solid var(--border);border-radius:10px;padding:14px;overflow:auto}
pre code{background:none;padding:0}
.table-wrap{overflow-x:auto;margin:14px 0;border:1px solid var(--border);border-radius:10px}
table{border-collapse:collapse;width:100%;min-width:520px;font-size:14px}
th,td{border-bottom:1px solid var(--border);padding:9px 12px;text-align:left;vertical-align:top}
th{background:#16223a;color:#dfe8f5;font-weight:600;position:sticky;top:0}
tr:nth-child(even) td{background:rgba(255,255,255,.02)}
tr:hover td{background:rgba(122,162,255,.06)}
ul,ol{padding-left:22px} li{margin:4px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin-top:18px}
.card{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:14px}
.card h3{margin:0 0 6px;font-size:16px;border:0} .card p{margin:0;color:var(--muted);font-size:14px}
.badge{display:inline-block;background:rgba(79,209,197,.15);color:var(--accent2);padding:2px 8px;border-radius:999px;font-size:12px;margin-bottom:14px}
@media(max-width:900px){.layout{flex-direction:column} nav{position:relative;width:auto;height:auto;border-right:0;border-bottom:1px solid var(--border)} main{padding:18px}}
'''

def nav_html(active_file):
    items = [f'<li><a href="index.html" class="{"active" if active_file=="index.html" else ""}">首頁</a></li>']
    for pg in pages:
        cls = 'active' if pg['file']==active_file else ''
        t = html.escape(pg['title'])
        items.append(f'<li><a href="{pg["file"]}" class="{cls}">{t}</a></li>')
    return '<nav><a class="brand" href="index.html">'+html.escape(site_title)+'</a><h2>文檔導覽</h2><ul>'+''.join(items)+'</ul></nav>'

def page_wrap(active, title, content, extra_head=''):
    return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — {html.escape(site_title)}</title>
<style>{CSS}</style>{extra_head}</head><body><div class="layout">{nav_html(active)}<main>{content}</main></div></body></html>'''

# index
cards=[]
for pg in pages:
    cards.append(f'<div class="card"><h3><a href="{pg["file"]}">{html.escape(pg["title"])}</a></h3><p>{html.escape(pg["summary"])}</p></div>')
index_body = f'<span class="badge">Static 知識庫 · {len(pages)} 節</span><h1>{html.escape(site_title)}</h1><p>由 Markdown 蒸餾文檔自動轉為靜態站（深色主題、可離線閱讀）。左側導覽可切換各子主題。</p><div class="cards">{"".join(cards)}</div>'
(stage / 'index.html').write_text(page_wrap('index.html', '首頁', index_body), encoding='utf-8')

for pg in pages:
    content = f'<article>{pg["body"]}</article><p style="margin-top:28px;color:var(--muted);font-size:13px"><a href="index.html">← 回首頁</a></p>'
    (stage / pg['file']).write_text(page_wrap(pg['file'], pg['title'], content), encoding='utf-8')

print(f"[OK] 產生 index.html + {len(pages)} 頁（共 {len(pages)+1} 個 HTML）")
for pg in pages:
    print(f"   - {pg['file']}  ({len(pg['body'])} chars body)")
PYTHON

echo "=== [3/5] README frontmatter（sdk: static）==="
cat > "$STAGE/README.md" <<EOF
---
title: ${SITE_TITLE}
emoji: 📚
colorFrom: indigo
colorTo: blue
sdk: static
pinned: false
---

# ${SITE_TITLE}

靜態知識庫（由 Markdown 自動轉換；免費 Static Space）。
EOF

echo "=== [4/5] 打包結果 ==="
du -sh "$STAGE" || true
find "$STAGE" -maxdepth 1 -type f | sed 's|.*/|   + |' | sort

if [[ "$DRY_RUN" == "1" ]]; then
  echo "[DRY-RUN] 略過建立/上傳。staging 保留於 $STAGE"
  echo "[HINT] 可本機預覽：cd $STAGE && $PY -m http.server 8765"
  echo "[HINT] private Space 匿名會 404；驗證內容請用 --public 或帶 cookie"
  exit 0
fi

echo "=== [5/5] 建立/上傳 Space ==="
PRIVATE_JSON="true"; [[ "$VISIBILITY" == "public" ]] && PRIVATE_JSON="false"
CREATE_RESP=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"name\":\"$SPACE_NAME\",\"type\":\"space\",\"sdk\":\"static\",\"private\":$PRIVATE_JSON}" \
  https://huggingface.co/api/repos/create)
CREATE_CODE=$(echo "$CREATE_RESP" | tail -1)
CREATE_BODY=$(echo "$CREATE_RESP" | sed '$d')
if [[ "$CREATE_CODE" == "200" || "$CREATE_CODE" == "201" ]]; then
  echo "[OK] Space 已建立（HTTP $CREATE_CODE）"
elif echo "$CREATE_BODY" | grep -qi "exist"; then
  echo "[OK] Space 已存在，改為更新上傳"
else
  echo "[WARN] 建立 Space 回應 HTTP $CREATE_CODE（將嘗試直接上傳）：$(echo "$CREATE_BODY" | head -c 180)"
fi

"$HF" upload "$SPACE_ID" "$STAGE" . --type space \
  --commit-message "deploy: ${SITE_TITLE} ($(date '+%Y-%m-%d %H:%M'))" 2>&1 | tail -6

echo "[OK] Space 頁面：https://huggingface.co/spaces/$SPACE_ID"
echo "[OK] 執行網址：$RUN_URL"
if [[ "$VISIBILITY" == "private" ]]; then
  echo "[INFO] private Space 匿名存取會 404；驗證請登入或改 --public"
fi

if [[ "$WAIT_FLAG" == "1" ]]; then
  echo "=== 等待 RUNNING ==="
  for i in $(seq 1 24); do
    INFO_JSON=$("$HF" spaces info "$SPACE_ID" --format json 2>/dev/null || echo "{}")
    STAGE_RT=$(echo "$INFO_JSON" | "$PY" -c "import json,sys; d=json.load(sys.stdin); print((d.get('runtime') or {}).get('stage',''))" 2>/dev/null || echo "")
    HOST_RT=$(echo "$INFO_JSON" | "$PY" -c "import json,sys; d=json.load(sys.stdin); print(d.get('host',''))" 2>/dev/null || echo "")
    echo "  t=${i}0s stage=$STAGE_RT"
    [[ -n "$HOST_RT" ]] && RUN_URL="$HOST_RT"
    [[ "$STAGE_RT" == "RUNNING" ]] && break
    sleep 10
  done
  HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 "$RUN_URL/index.html" || echo "000")
  echo "[CHECK] $RUN_URL/index.html → HTTP $HTTP"
  if [[ "$HTTP" == "200" ]]; then
    curl -s --max-time 20 "$RUN_URL/index.html" | grep -o "<title>[^<]*" | head -1 || true
  else
    HTTP2=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 "$RUN_URL/" || echo "000")
    echo "[CHECK] $RUN_URL/ → HTTP $HTTP2（Static Space 根路徑可能 302 到 index.html）"
  fi
fi
