#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_topics.py — push 前必跑：同步本機主題 md 到 quantum_website repo。

同步規則（repo ⊇ 來源，同名一律覆蓋）：
  ~/量子/PQC/topics/*.md  -> quantum_website/data/topics/       （15 檔）
  ~/量化/topics/0*.md     -> quantum_website/data/quant_topics/ （9 檔）
  ~/.opencode/skills/topological-insulator/references/*.md
                          -> quantum_website/data/ti_topics/     （7 檔）
  ~/.opencode/skills/stock-market/references/*.md
                          -> quantum_website/data/stock_topics/  （9 檔）
  只取來源「頂層」檔案 — fb_posts/ 等子目錄自動排除；
  repo 內既有的合併檔（PQC_QKD_topics.md、quant_trading_topics.md）保留不動。

驗證規則（exit 1 = 禁止 push）：
  同步後每個來源檔都必須存在於 repo 且內容一致（md5）。

為何需要此腳本（2026-11-11 事故根因）：
  1. commit 4c44911 加入 quant 支援時，只把合併檔 quant_trading_topics.md
     放進 data/quant_topics/，9 個獨立主題檔（00_索引～08）從未進 repo。
  2. content_loader / 頁面載入器「家目錄優先、repo 為 fallback」：
     本機永遠讀到 ~/量化/topics 的 9 檔（看起來正常），雲端 fallback 只剩
     1 個合併檔 → 「quant 主題無法上線」，但本機測試永遠看不到。
  3. push-streamlit 原本只有 health check 驗證（只證明 app 活著，
     不證明內容完整），缺檔跨多次 push 未被發現。

用法：
  python sync_topics.py [--dry-run]
"""

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

HOME = Path.home()
REPO = Path("/home/sam/quantum_website")

# (來源目錄, repo 目標目錄, glob 模式)
SYNC_PAIRS = [
    (HOME / "量子" / "PQC" / "topics", REPO / "data" / "topics", "*.md"),
    (HOME / "量化" / "topics", REPO / "data" / "quant_topics", "0*.md"),
    # TI 蒸餾主題：技能 references 即唯一真源（同步覆蓋 repo，日後更新技能=網站同步）
    (
        HOME / ".opencode" / "skills" / "topological-insulator" / "references",
        REPO / "data" / "ti_topics",
        "*.md",
    ),
    # 股市蒸餾主題：同 TI 模式 — stock-market 技能 references 為唯一真源
    (
        HOME / ".opencode" / "skills" / "stock-market" / "references",
        REPO / "data" / "stock_topics",
        "*.md",
    ),
    # 2D 超導體/石墨烯蒸餾主題
    (
        HOME / ".opencode" / "skills" / "2d-superconductor" / "references",
        REPO / "data" / "2d_superconductor_topics",
        "*.md",
    ),
    # Quantum algorithms & QKD & ECC (qalgo) 蒸餾主題
    (
        HOME / "qalgo",
        REPO / "data" / "qalgo_topics",
        "*.md",
    ),
]


def md5(path: Path) -> str:
    h = hashlib.md5()
    h.update(path.read_bytes())
    return h.hexdigest()


def top_level_files(directory: Path, pattern: str):
    """只取頂層符合的檔案（排除子目錄，如 fb_posts/）。"""
    return sorted(p for p in directory.glob(pattern) if p.is_file())


def main(dry_run: bool = False) -> int:
    if not REPO.is_dir():
        print(f"[FAIL] repo 不存在：{REPO}", file=sys.stderr)
        return 1

    failures = []
    for src, dst, pattern in SYNC_PAIRS:
        if not src.is_dir():
            print(f"[FAIL] 來源不存在：{src}", file=sys.stderr)
            failures.append(src)
            continue

        src_files = top_level_files(src, pattern)
        if not src_files:
            print(f"[FAIL] 來源沒有任何符合 {pattern} 的檔案：{src}", file=sys.stderr)
            failures.append(src)
            continue

        dst.mkdir(parents=True, exist_ok=True)
        copied = skipped = 0
        for f in src_files:
            target = dst / f.name
            if target.is_file() and md5(target) == md5(f):
                skipped += 1
                if dry_run:
                    print(f"[DRY] 一致免複製: {f.name}")
                continue
            if dry_run:
                print(f"[DRY] 需複製: {f} -> {target}")
                continue
            shutil.copy2(f, target)
            copied += 1

        # 驗證：來源每檔都必須在 repo 且 md5 一致
        dst_files = {p.name for p in top_level_files(dst, pattern)}
        missing = [f.name for f in src_files if f.name not in dst_files]
        mismatched = [
            f.name
            for f in src_files
            if f.name in dst_files and md5(dst / f.name) != md5(f)
        ]
        status = "OK" if not missing and not mismatched else "FAIL"
        print(
            f"[{status}] {src} -> {dst}\n"
            f"      來源 {len(src_files)} 檔；本次複製 {copied}、一致 {skipped}；"
            f"repo {pattern} 檔數 {len(dst_files)}"
        )
        if missing:
            print(f"      缺少: {missing}", file=sys.stderr)
        if mismatched:
            print(f"      內容不一致: {mismatched}", file=sys.stderr)
        if missing or mismatched:
            failures.append(src)

    if failures:
        print(
            "\n同步驗證失敗 — 來源與 repo 不一致，禁止 push！",
            file=sys.stderr,
        )
        return 1
    print("\n同步完成：來源與 repo 內容一致，可以 push。")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="push 前同步主題 md 到 repo 並驗證一致性")
    ap.add_argument("--dry-run", action="store_true", help="只顯示將做什麼，不實際複製")
    args = ap.parse_args()
    sys.exit(main(args.dry_run))
