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
    r"(?i)\b(password|passwd|pwd|secret|api[ _-]?key|token|private[ _-]?key|"
    r"access[ _-]?key|client[ _-]?secret)\b\s*"
    r"(?::|(?<![=!<>])=(?![=>]))\s*(?P<value>\S{4,})"
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

# CRED_RE 只攔截「像真實字面值」的指派。技能文件、測試夾具與程式碼常出現
# 佔位符、變數名、函式呼叫、regex 字串；這些不是洩漏。TOKEN_RE 仍舊硬攔截
# ghp_/sk-/AKIA/PRIVATE KEY 等真實 token 格式，不受下列豁免影響。
CODE_EXPR_RE = re.compile(
    r"^[A-Za-z_$][\w$]*(?:\([^)]*\)|\[[^\]]*\]|\?\.[A-Za-z_$][\w$]*"
    r"|\.[A-Za-z_$][\w$]*)+$"
)
HYPHEN_WORD_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z][A-Za-z0-9]*)+$")
REGEX_LITERAL_RE = re.compile(r"\[[A-Za-z0-9_\-]|\{\d+(?:,\d*)?\}|\\|\|")
ALL_CAPS_VAR_RE = re.compile(r"[A-Z_][A-Z0-9_]*\Z")
PLACEHOLDER_PREFIX_RE = re.compile(
    r"(?i)^(?:your|my|the|dummy|placeholder|example|sample|fake|test|current|"
    r"newer|old|short|forged|previous)[_-][A-Za-z0-9_-]+$"
)
NON_SECRET_WORDS = {
    "true",
    "false",
    "none",
    "null",
    "undefined",
    "str",
    "int",
    "bool",
    "app_secret",
    "app_id",
    "token",
    "page_token",
    "short_token",
    "todo",
    "tbd",
    "unknown",
    "n/a",
    "na",
    "x",
}


def _looks_like_placeholder(value):
    """判定 CRED_RE 抓到的值是否只是示範/程式碼，而非真實憑證字面值。"""
    raw = value.strip()
    # shell/env 取值、f-string、模板字串、字串運算、regex 字元類別都不是字面 secret
    if (
        raw.startswith("$")
        or raw.startswith("`")
        or raw.startswith(('f"', "f'", 'F"', "F'"))
    ):
        return True
    if "${" in raw or "??" in raw or REGEX_LITERAL_RE.search(raw):
        return True
    # URL query string（client_secret=APP_SECRET&...）是文件示範，不是常值指派
    if "&" in raw and "=" in raw:
        return True
    # 先認出函式呼叫（保留結尾括号），其餘再把結構性尾綴去掉
    if CODE_EXPR_RE.fullmatch(raw.rstrip(",;")):
        return True
    raw = raw.rstrip(",;)]}")
    # 成對引號先解包，才能正確辨識 "newer-current-token" 之類測試夾具
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'`":
        raw = raw[1:-1].strip()
    elif raw.endswith(("`", "'", '"')):
        # Markdown 行內程式碼只剩結束引號，例如 `token=True`
        raw = raw[:-1]
    if CODE_EXPR_RE.fullmatch(raw):
        return True
    if not raw or len(raw) < 4:
        return True
    if raw.startswith("<") and raw.endswith(">"):
        return True
    low = raw.lower()
    if low in NON_SECRET_WORDS or ("_" in raw and ALL_CAPS_VAR_RE.fullmatch(raw)):
        return True
    if PLACEHOLDER_PREFIX_RE.fullmatch(raw):
        return True
    # newer-current-token / current-new 這類測試夾具：全小寫字詞以連字號串接
    if HYPHEN_WORD_RE.fullmatch(raw) and not any(c.isdigit() for c in raw):
        return True
    return False


def has_leak(text):
    """逐行檢查；TOKEN_RE 一律 FAIL，CRED_RE 只對真實字面值 FAIL。"""
    for line in text.splitlines():
        cleaned = SAFE_READ_RE.sub("", line)
        if TOKEN_RE.search(cleaned):
            return True
        for m in CRED_RE.finditer(cleaned):
            if not _looks_like_placeholder(m.group("value")):
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


def excluded_is_tracked(path, tracked_set):
    """帳本失效的定義：列出的路徑其實仍被 git 追蹤（與「不該進 repo」矛盾）。

    本機已清理的雜物、空目錄、斷鏈，clone 後本來就不存在，不算失效。
    """
    p = path.rstrip("/")
    if any(ch in p for ch in "*?["):
        return any(
            fnmatch.fnmatch(t, p) or fnmatch.fnmatch(os.path.basename(t), p)
            for t in tracked_set
        )
    return p in tracked_set or any(t.startswith(p + "/") for t in tracked_set)


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
            if r.get("path") and excluded_is_tracked(r["path"], tracked_set)
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
