#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""push-repo phase 1：唯讀偵察。不改任何檔案。

用法：
    python3 scripts/preflight.py <DIR> [--out <DIR>]

產出（預設寫到 <DIR>/../<dirname>_preflight/，避免污染待推送目錄）：
    preflight.md     給人看的摘要
    preflight.json   給後續步驟用的機器可讀結果

只回答事實，不做決定：哪些是機密、哪些超過上限、哪些已經被既有 .gitignore 吃掉。
"""

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys

CRED_RE = re.compile(
    r"(?i)(password|passwd|pwd|secret|api[ _-]?key|token|private[ _-]?key|"
    r"access[ _-]?key|client[ _-]?secret)\s*[:=]\s*\S{4,}"
)
TOKEN_RE = re.compile(
    r"(sk-[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{30,}|gho_[A-Za-z0-9]{30,}"
    r"|github_pat_[A-Za-z0-9_]{30,}|xox[baprs]-[A-Za-z0-9\-]{10,}"
    r"|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_\-]{30,}|hf_[A-Za-z0-9]{30,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)

JUNK_PATTERNS = [
    ("__pycache__", "Python bytecode 快取"),
    ("*.pyc", "Python bytecode"),
    ("*.pyo", "Python bytecode"),
    ("node_modules", "npm 相依套件"),
    (".DS_Store", "macOS 中繼資料"),
    (".venv", "Python 虛擬環境"),
    ("*.log", "日誌"),
    ("*.tmp", "暫存"),
    (".pytest_cache", "測試快取"),
    ("*.egg-info", "套件中繼資料"),
    ("dist", "建置產物"),
    ("build", "建置產物"),
]

TEXT_EXT = {
    ".md",
    ".txt",
    ".py",
    ".js",
    ".mjs",
    ".ts",
    ".sh",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".env",
    ".example",
    ".csv",
    ".html",
}

WARN_MB, HARD_MB = 50, 100


def sh(cwd, *args):
    try:
        return subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, timeout=120
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def rel(root, path):
    return os.path.relpath(path, root)


def scan_tree(root):
    files, links, empty_dirs, nested = [], [], [], []
    for cur, dirs, names in os.walk(root):
        has_own_git = ".git" in dirs or os.path.exists(os.path.join(cur, ".git"))
        dirs[:] = [d for d in dirs if d != ".git"]
        if has_own_git and os.path.abspath(cur) != root:
            nested.append(rel(root, cur))
        for d in sorted(dirs):
            full = os.path.join(cur, d)
            if not os.listdir(full):
                empty_dirs.append(rel(root, full))
        for n in sorted(names):
            full = os.path.join(cur, n)
            if os.path.islink(full):
                tgt = os.readlink(full)
                links.append(
                    {
                        "path": rel(root, full),
                        "target": tgt,
                        "broken": not os.path.exists(full),
                    }
                )
                continue
            try:
                st = os.lstat(full)
            except OSError:
                continue
            files.append(
                {
                    "path": rel(root, full),
                    "size": st.st_size,
                    "mode": st.st_mode & 0o777,
                    "exec": bool(st.st_mode & 0o100),
                }
            )
    return files, links, empty_dirs, nested


SAMPLE_RE = re.compile(
    r"(?i)(\.(example|sample|template|dist|tpl)$|^(example|sample)[._-])"
)


def read_head(p, size, limit=512_000):
    """大檔只讀頭尾，不要整檔吞進記憶體，也不要直接跳過。"""
    try:
        with open(p, "rb") as fh:
            if size <= limit * 4:
                return fh.read().decode("utf-8", "ignore")
            head = fh.read(limit)
            fh.seek(max(0, size - limit))
            return (head + b"\n" + fh.read(limit)).decode("utf-8", "ignore")
    except OSError:
        return ""


def scan_secrets(root, files):
    hits, skipped = [], []
    for f in files:
        p = os.path.join(root, f["path"])
        ext = os.path.splitext(f["path"])[1].lower()
        head = os.path.basename(f["path"]).lower()
        looks_text = ext in TEXT_EXT or head.startswith(".env") or "." not in head
        if not looks_text:
            continue
        if SAMPLE_RE.search(head):
            skipped.append(f["path"])
            continue
        text = read_head(p, f["size"])
        if not text:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            m = TOKEN_RE.search(line)
            c = None if m else CRED_RE.search(line)
            if m or c:
                val = line.split(":", 1)[-1].split("=", 1)[-1].strip().strip("\"'")
                if (
                    c
                    and not m
                    and re.search(
                        r"(?i)^(x+|\*+|change|your|example|"
                        r"placeholder|dummy|todo|<|\.\.\.)",
                        val,
                    )
                ):
                    continue
                key = (m.group(1)[:12] + "…") if m else c.group(1)
                hits.append({"path": f["path"], "line": i, "kind": key})
    # 呼叫端要的是 (hits, skipped)：skipped 是被判定為範本檔而「沒掃」的清單，
    # 必須回報給使用者自行確認，不能靜靜吞掉。
    return hits, skipped


def ignored_by_gitignore(root, files):
    """用既有 .gitignore 的常見語法近似比對（無 repo 時）。"""
    rules = []
    gi = os.path.join(root, ".gitignore")
    if os.path.exists(gi):
        for raw in open(gi, encoding="utf-8", errors="ignore").read().splitlines():
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            neg = s.startswith("!")
            rules.append((s[1:] if neg else s, neg))
    out = []
    for f in files:
        p = f["path"]
        parts = p.split(os.sep)
        verdict = False
        for pat, neg in rules:
            base = pat.rstrip("/")
            hit = (
                fnmatch.fnmatch(p, pat)
                or fnmatch.fnmatch(os.path.basename(p), pat)
                or any(fnmatch.fnmatch(part, base) for part in parts)
            )
            if hit:
                verdict = not neg
        if verdict:
            out.append(p)
    return out


def junk_hits(files):
    buckets = {}
    for label, desc in JUNK_PATTERNS:
        hit = [
            f["path"]
            for f in files
            if fnmatch.fnmatch(os.path.basename(f["path"]), label)
            or any(fnmatch.fnmatch(part, label) for part in f["path"].split(os.sep))
        ]
        if hit:
            buckets.setdefault(f"{label}（{desc}）", hit)
    return buckets


ERE_CRED = (
    r"(password|passwd|pwd|secret|api[ _-]?key|token|private[ _-]?key"
    r"|access[ _-]?key|client[ _-]?secret)[[:space:]]*[:=]"
)
ERE_TOKEN = (
    r"(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|gho_[A-Za-z0-9]{30,}"
    r"|github_pat_[A-Za-z0-9_]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}"
    r"|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|hf_[A-Za-z0-9]{30,})"
)


def history_secrets(root, limit=300):
    """掃歷史。git 的 -G/-E 是 POSIX ERE，不支援 \\s 與 (?i)，所以樣式另寫。"""
    if not os.path.isdir(os.path.join(root, ".git")):
        return []
    commits = set()
    for pat in (ERE_CRED, ERE_TOKEN):
        out = sh(
            root,
            "git",
            "log",
            "--all",
            "-i",
            "-G",
            pat,
            "--format=%H",
            f"--max-count={limit}",
        )
        commits.update(c for c in out.splitlines() if re.fullmatch(r"[0-9a-f]{40}", c))
    hits = set()
    for c in sorted(commits)[:50]:
        for pat in (ERE_CRED, ERE_TOKEN):
            out = sh(
                root,
                "git",
                "-c",
                "core.quotepath=false",
                "grep",
                "-I",
                "-l",
                "-E",
                pat,
                c,
                "--",
            )
            for line in out.splitlines():
                if ":" in line:
                    hits.add(line.split(":", 1)[1])
    return sorted(hits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    root = os.path.abspath(a.path)
    if not os.path.isdir(root):
        print(f"!! 不是目錄：{root}", file=sys.stderr)
        return 2
    out = os.path.abspath(
        a.out
        or os.path.join(os.path.dirname(root), os.path.basename(root) + "_preflight")
    )
    os.makedirs(out, exist_ok=True)

    files, links, empty_dirs, nested = scan_tree(root)
    total = sum(f["size"] for f in files)
    large = sorted(
        [f for f in files if f["size"] >= WARN_MB * 1024 * 1024],
        key=lambda f: -f["size"],
    )
    secrets, skipped_samples = scan_secrets(root, files)
    hist = history_secrets(root)

    top = sh(root, "git", "rev-parse", "--show-toplevel")
    is_repo = bool(top) and os.path.abspath(top) == root
    parent_repo = bool(top) and os.path.abspath(top) != root
    repo = {}
    if is_repo:
        repo = {
            "branch": sh(root, "git", "rev-parse", "--abbrev-ref", "HEAD")
            or "(no commit)",
            "commits": int(sh(root, "git", "rev-list", "--all", "--count") or 0),
            "dirty": len(
                [x for x in sh(root, "git", "status", "--porcelain").splitlines() if x]
            ),
            "remotes": [x for x in sh(root, "git", "remote").splitlines() if x],
            "tracked": len([x for x in sh(root, "git", "ls-files").splitlines() if x]),
        }

    gi_ignored = (
        ignored_by_gitignore(root, files)
        if not is_repo
        else [
            ln[3:]
            for ln in sh(
                root,
                "git",
                "-c",
                "core.quotepath=false",
                "status",
                "--ignored=matching",
                "--porcelain",
            ).splitlines()
            if ln.startswith("!! ")
        ]
    )

    expanded = []
    for pth in gi_ignored:
        full = os.path.join(root, pth)
        if os.path.isdir(full):
            expanded += [
                f["path"]
                for f in files
                if f["path"].startswith(pth.rstrip("/") + os.sep)
            ]
        else:
            expanded.append(pth)
    gi_ignored = expanded

    def is_junk(pth):
        parts = pth.split(os.sep)
        return any(
            fnmatch.fnmatch(part, pat) for pat, _ in JUNK_PATTERNS for part in parts
        )

    # 不再只認文字副檔名：被目錄規則吃掉的 *.jpg／*.mp4 也要看得見
    suspicious_ignored = [pth for pth in dict.fromkeys(gi_ignored) if not is_junk(pth)]

    data = {
        "root": root,
        "files": len(files),
        "bytes": total,
        "is_repo": is_repo,
        "parent_repo": top if parent_repo else None,
        "repo": repo,
        "secrets_worktree": secrets,
        "secrets_history": hist,
        "large": [
            {
                "path": f["path"],
                "mb": round(f["size"] / 1048576, 1),
                "hard_limit": f["size"] >= HARD_MB * 1024 * 1024,
            }
            for f in large
        ],
        "junk": junk_hits(files),
        "nested_repos": nested,
        "symlinks": links,
        "empty_dirs": empty_dirs,
        "secret_samples_skipped": skipped_samples,
        "gitignore_paths": gi_ignored,
        "gitignore_suspicious": suspicious_ignored,
        "exec_files": sum(1 for f in files if f["exec"]),
    }
    json.dump(
        data,
        open(os.path.join(out, "preflight.json"), "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )

    # 排除清單草稿：只填路徑與理由，backup 留空等人工補（空 = 未交代，驗證會 FAIL）
    draft, seen = [], set()

    def add(p, size, reason, backup=""):
        if p in seen:
            return
        bare = p.rstrip("/")
        for q in seen:
            if q.endswith("/") and (bare == q.rstrip("/") or bare.startswith(q)):
                return
        seen.add(p)
        draft.append((p, size, reason, backup))

    def prefix_for(relp, pattern):
        """找出真正該排除的那一層（project/__pycache__/x.pyc → project/__pycache__）。"""
        acc = []
        for part in relp.split(os.sep):
            acc.append(part)
            if fnmatch.fnmatch(part, pattern):
                return os.sep.join(acc)
        return relp

    for label, paths in data["junk"].items():
        pattern = label.split("（")[0]
        for pref in sorted({prefix_for(x, pattern) for x in paths}):
            full = os.path.join(root, pref)
            if os.path.isdir(full):
                size = sum(
                    f["size"]
                    for f in files
                    if f["path"] == pref or f["path"].startswith(pref + os.sep)
                )
                add(pref + "/", size, f"雜物：{label}", "由工具重建")
            else:
                size = next((f["size"] for f in files if f["path"] == pref), 0)
                add(pref, size, f"雜物：{label}", "由工具重建")
    for h in secrets:
        add(
            h["path"],
            next((f["size"] for f in files if f["path"] == h["path"]), 0),
            f"機密：疑似 {h['kind']}",
            "",
        )
    for f in large:
        add(
            f["path"],
            f["size"],
            f"大檔 {f['size'] / 1048576:.1f} MB"
            + (
                "（≥100 MB，GitHub 硬擋）"
                if f["size"] >= HARD_MB * 1024 * 1024
                else "（≥50 MB，push 會警告）"
            ),
        )
    for pth in nested:
        add(
            pth + "/",
            sum(f["size"] for f in files if f["path"].startswith(pth + os.sep)),
            "巢狀 repo，需選擇攤平／submodule／排除",
        )
    for pth in empty_dirs:
        add(pth + "/", 0, "空目錄：git 不追蹤，clone 後消失", "不適用（無內容）")

    with open(os.path.join(out, "excluded_draft.tsv"), "w", encoding="utf-8") as f:
        f.write("path\tsize\treason\tbackup\n")
        for pth, size, reason, backup in draft:
            f.write(f"{pth}\t{size}\t{reason}\t{backup}\n")

    L = [
        "# push-repo 偵察報告",
        "",
        f"- 目錄：`{root}`",
        f"- 檔案 {len(files)} 個、符號連結 {len(links)} 個"
        f"（合計 disk={len(files) + len(links)}，與 verify_push 同口徑）、"
        f"{total / 1048576:.1f} MB、可執行 {data['exec_files']} 個",
        f"- 已是 git repo：{'是' if is_repo else '否'}"
        + (f"（父層 repo：`{top}`，**init 前必須確認**）" if parent_repo else ""),
        "",
    ]
    if is_repo:
        L += [
            f"- 分支 `{repo['branch']}`、提交 {repo['commits']} 筆、未提交 {repo['dirty']} 項、"
            f"已追蹤 {repo['tracked']} 檔、remote {len(repo['remotes'])} 個",
            "",
            "> 既有 repo：**不要重新 init**，沿用歷史。",
            "",
        ]
    L += ["## 機密（工作區）", ""]
    L += [f"- `{h['path']}:{h['line']}` — 疑似 {h['kind']}" for h in secrets] or [
        "（無）"
    ]
    if skipped_samples:
        L += [
            "",
            f"**視為範本檔而略過（{len(skipped_samples)} 個，請自行確認內容真的只是 placeholder）**",
            "",
        ]
        L += [f"- `{p}`" for p in skipped_samples[:20]]
    L += ["", "## 機密（歷史）", ""]
    L += [f"- `{p}`（曾在歷史提交中出現）" for p in hist] or ["（無歷史，或無命中）"]
    L += ["", "## 大檔", ""]
    L += [
        f"- `{f['path']}` — {f['mb']} MB"
        + (
            "　**≥100 MB，GitHub 硬擋**"
            if f["hard_limit"]
            else "　（≥50 MB，push 會警告）"
        )
        for f in data["large"]
    ] or ["（無 ≥50 MB 檔案）"]
    L += ["", "## 雜物", ""]
    L += [f"- `{k}`：{len(v)} 檔（例：`{v[0]}`）" for k, v in data["junk"].items()] or [
        "（無）"
    ]
    L += ["", "## 巢狀 repo（會變成 gitlink，clone 後是空目錄）", ""]
    L += [f"- `{p}`" for p in nested] or ["（無）"]
    L += ["", "## 既有 .gitignore 已排除的檔案", ""]
    L += [f"- `{p}`" for p in gi_ignored[:40]] or ["（無）"]
    if suspicious_ignored:
        L += [
            "",
            "**注意：以下看起來是需要版控的內容，卻已被既有 .gitignore 排除**",
            "",
        ]
        L += [f"- `{p}`" for p in suspicious_ignored[:20]]
    L += ["", "## 其他", ""]
    L += [
        f"- 符號連結 {len(links)} 個"
        + (f"（含 {sum(1 for x in links if x['broken'])} 個斷鏈）" if links else ""),
        f"- 空目錄 {len(empty_dirs)} 個（git 不追蹤空目錄）",
        "",
        f"機器可讀結果：`{os.path.join(out, 'preflight.json')}`",
        "",
    ]
    open(os.path.join(out, "preflight.md"), "w", encoding="utf-8").write("\n".join(L))

    print(
        f"preflight: disk={len(files) + len(links)} (files={len(files)} "
        f"links={len(links)}) bytes={total} repo={is_repo} "
        f"secrets={len(secrets)}+{len(hist)} large={len(large)} "
        f"junk={sum(len(v) for v in data['junk'].values())} nested={len(nested)}"
    )
    print(f"報告：{os.path.join(out, 'preflight.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
