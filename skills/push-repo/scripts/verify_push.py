#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""push-repo phase 6：推送後驗證。只讀，不改 repo。

用法：
    python3 scripts/verify_push.py <DIR> <REMOTE_URL> [--branch main]
                                  [--excluded _repo_excluded.tsv]

檢查（任何一項 FAIL 就以 exit 1 結束）：
  1. 遠端 HEAD 與本機 HEAD 一致
  2. fresh clone 可取得、git fsck 無錯
  3. clone 內每個追蹤檔的 md5 與來源相同（不是只看 git 自己說成功）
  4. 執行權限一致、符號連結目標一致
  5. 對帳：磁碟上每個檔案 = 已追蹤 ∪ 已列在排除清單，沒有第三類
  6. clone 出來的工作區沒有機密樣式

排除清單格式（TSV，第一列標頭）：
    path    size    reason    backup
  path 以 `/` 結尾代表整個目錄；含 `*` 視為 glob；其餘為單一檔案。
  backup 寫「原件的唯一副本在哪」，沒有就寫 `本機唯一，勿刪`。
"""

import argparse
import fnmatch
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

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
SKIP_DIRS = {".git"}
ERE_CRED = (
    r"(password|passwd|pwd|secret|api[ _-]?key|token|private[ _-]?key"
    r"|access[ _-]?key|client[ _-]?secret)[[:space:]]*[:=]"
)
ERE_TOKEN = (
    r"(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|gho_[A-Za-z0-9]{30,}"
    r"|github_pat_[A-Za-z0-9_]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}"
    r"|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|hf_[A-Za-z0-9]{30,})"
)
# 安全讀取豁免：技能文件會示範「從本機憑證檔讀入變數」，這是安全做法，
# 不是把 token 字面值寫進檔案。只移除該片段，真正的 token 格式仍由 TOKEN_RE 攔截。
SAFE_READ_RE = re.compile(r"[A-Z_][A-Z0-9_]*=\$\(cat\s+[^\n]*credentials\)")


def has_leak(text):
    """逐行檢查；先剔除安全讀取片段，其餘命中照常視為洩漏。"""
    for line in text.splitlines():
        cleaned = SAFE_READ_RE.sub("", line)
        if TOKEN_RE.search(cleaned) or CRED_RE.search(cleaned):
            return True
    return False


def sh(*args, cwd=None):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=300)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except (OSError, subprocess.SubprocessError) as e:
        return 1, "", str(e)


def blob_md5(repo, rel):
    """取 HEAD 裡該路徑的內容雜湊（工作區可能被改過，不能拿它比）。"""
    try:
        p = subprocess.run(
            ["git", "-C", repo, "show", f"HEAD:{rel}"], capture_output=True, timeout=300
        )
        return hashlib.md5(p.stdout).hexdigest() if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def collect(root):
    files = {}
    for cur, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            full = os.path.join(cur, n)
            rel = os.path.relpath(full, root)
            if os.path.islink(full):
                files[rel] = ("link", os.readlink(full))
            else:
                files[rel] = ("file", full)
    return files


def load_excluded(path):
    rows = []
    if not path or not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            if not line.strip():
                continue
            cells = line.rstrip("\n").split("\t")
            cells += [""] * (4 - len(cells))
            rows.append(
                dict(
                    zip(head + ["path", "size", "reason", "backup"][len(head) :], cells)
                )
            )
    return rows


def covered(rel, rows):
    for r in rows:
        p = r.get("path", "")
        if not p:
            continue
        if p.endswith("/"):
            if rel.startswith(p.rstrip("/") + "/"):
                return p
        elif any(ch in p for ch in "*?["):
            if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(os.path.basename(rel), p):
                return p
        elif rel == p:
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("remote")
    ap.add_argument("--branch", default=None)
    ap.add_argument("--excluded", default=None)
    a = ap.parse_args()

    root = os.path.abspath(a.path)
    branch = a.branch or sh("git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD")[1]
    excluded = a.excluded or os.path.join(root, "_repo_excluded.tsv")
    rows = load_excluded(excluded)
    results, fails = [], []

    def check(name, ok, detail=""):
        results.append((name, ok, detail))
        if not ok:
            fails.append(f"{name}：{detail}")

    rc, local_head, _ = sh("git", "-C", root, "rev-parse", "HEAD")
    check("本機有 HEAD", rc == 0 and bool(local_head), local_head or "找不到 HEAD")

    rc, dirty, _ = sh("git", "-C", root, "status", "--porcelain")
    check(
        "工作區沒有未提交變更（推上去的就是你看到的）",
        not dirty.strip(),
        f"{len(dirty.splitlines())} 項未提交",
    )

    rc, ls, err = sh("git", "ls-remote", a.remote, f"refs/heads/{branch}")
    remote_head = ls.split()[0] if rc == 0 and ls else ""
    check(
        "遠端分支存在且指向同一個 commit",
        remote_head == local_head,
        f"local={local_head[:12] or '?'} remote={remote_head[:12] or '（無）'} {err}",
    )

    tmp = tempfile.mkdtemp(prefix="verify_push_")
    clone = os.path.join(tmp, "clone")
    try:
        rc, out, err = sh(
            "git",
            "clone",
            "--quiet",
            "--no-hardlinks",
            "--branch",
            branch,
            a.remote,
            clone,
        )
        check("fresh clone 成功", rc == 0, err or out)
        if rc != 0:
            raise RuntimeError("clone failed")

        rc, out, err = sh("git", "-C", clone, "fsck", "--no-progress")
        check("clone 的 git fsck 無錯", rc == 0, err or out)

        rc, out, _ = sh("git", "-c", "core.quotepath=false", "-C", clone, "ls-files")
        tracked = [x for x in out.splitlines() if x]
        rc, out2, _ = sh("git", "-c", "core.quotepath=false", "-C", root, "ls-files")
        source_tracked = [x for x in out2.splitlines() if x]
        check(
            "追蹤檔數一致",
            len(tracked) == len(source_tracked),
            f"clone={len(tracked)} source={len(source_tracked)}",
        )

        # 逐檔內容比對
        bad, checked, exec_bad, link_bad = [], 0, [], []
        for relp in tracked:
            src = os.path.join(root, relp)
            dst = os.path.join(clone, relp)
            if os.path.islink(src) or os.path.islink(dst):
                if os.readlink(src) != os.readlink(dst):
                    link_bad.append(relp)
                checked += 1
                continue
            if not os.path.exists(src):
                bad.append(f"{relp}（來源不存在）")
                continue
            if not os.path.exists(dst):
                bad.append(f"{relp}（clone 缺檔）")
                continue
            want = blob_md5(root, relp)
            if want is None or want != md5(dst):
                bad.append(f"{relp}（commit 內容與 clone 不同）")
            src_x = bool(os.stat(src).st_mode & 0o100)
            dst_x = bool(os.stat(dst).st_mode & 0o100)
            if src_x != dst_x:
                exec_bad.append(relp)
            checked += 1
        check("clone 內每個追蹤檔與來源 md5 相同", not bad, "；".join(bad[:8]))
        check("執行權限一致", not exec_bad, "、".join(exec_bad[:8]))
        check("符號連結目標一致", not link_bad, "、".join(link_bad[:8]))

        # 機密掃描（clone 工作區）
        leaks = []
        for cur, dirs, names in os.walk(clone):
            dirs[:] = [d for d in dirs if d != ".git"]
            for n in names:
                full = os.path.join(cur, n)
                if re.search(r"(?i)(example|sample|template|\.dist)", n):
                    continue
                try:
                    if os.path.getsize(full) > 1_000_000:
                        continue
                    text = open(full, encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                if has_leak(text):
                    leaks.append(os.path.relpath(full, clone))
        check("clone 工作區無機密樣式", not leaks, "、".join(leaks[:8]))

        # 歷史也要乾淨：加了 .gitignore 不會讓舊 commit 裡的字串消失
        hist = set()
        _, revlist, _ = sh("git", "-C", clone, "rev-list", "--all")
        revs = revlist.splitlines()[:50]
        if revs:
            for pat in (ERE_CRED, ERE_TOKEN):
                _, out, _ = sh("git", "-C", clone, "grep", "-I", "-l", "-E", pat, *revs)
                for line in out.splitlines():
                    if ":" not in line:
                        continue
                    rev, path = line.split(":", 1)
                    # git grep 是快速篩選，會誤判「安全讀取示範」；
                    # 取實際 blob 逐行複查，避免 false positive，也不放過真 token。
                    _, blob, _ = sh("git", "-C", clone, "show", f"{rev}:{path}")
                    if has_leak(blob):
                        hist.add(path)
        check("clone 歷史提交無機密樣式", not hist, "、".join(sorted(hist)[:8]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 對帳：磁碟 = 追蹤 ∪ 排除清單
    disk = collect(root)
    tracked_set = set(source_tracked)
    orphans = sorted(p for p in disk if p not in tracked_set and not covered(p, rows))
    stale = sorted(
        {
            r["path"]
            for r in rows
            if r.get("path")
            and not os.path.exists(os.path.join(root, r["path"].rstrip("/")))
        }
    )
    check(
        "每個未追蹤檔案都列在排除清單（沒有第三類）",
        not orphans,
        "、".join(orphans[:10]) + (f" …共 {len(orphans)}" if len(orphans) > 10 else ""),
    )
    check("排除清單沒有失效條目", not stale, "、".join(stale[:10]))

    # 「不知道」「N/A」也是空白：backup 要能被人實際找到那份原件
    VAGUE = {
        "無",
        "沒有",
        "未知",
        "不知道",
        "待確認",
        "待補",
        "之後再說",
        "n/a",
        "na",
        "none",
        "null",
        "?",
        "-",
        "--",
        "todo",
        "tbd",
        "unknown",
        "x",
        "推",
        "稍後",
    }

    def vague(val):
        v = val.strip().strip("。.").strip()
        return not v or v.lower() in VAGUE or len(v) < 2

    unresolved = [r for r in rows if vague(r.get("backup", ""))]
    check(
        "排除清單每列都寫了原件去處（不能寫「無」或「不知道」）",
        not unresolved,
        "、".join(r["path"] for r in unresolved[:8]),
    )

    print(f"== verify_push {root} → {a.remote} ({branch}) ==")
    for name, ok, detail in results:
        print(
            f"[{'PASS' if ok else 'FAIL'}] {name}"
            + (f" — {detail}" if detail and not ok else "")
        )
    print(
        f"tracked={len(source_tracked)} disk={len(disk)} excluded_rows={len(rows)} "
        f"fail={len(fails)}"
    )
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
