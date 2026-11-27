#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate 2 RED/GREEN: quantum-llm 的本地驗證觸發與 hook 規則。"""

from pathlib import Path
import re

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"

failures = []


def check(name, cond):
    if not cond:
        failures.append(name)


t = SKILL.read_text(encoding="utf-8")

check("trigger_validate_quantum_llm", "驗證量子LLM" in t)
check("trigger_validate_quantum_model", "驗證量子模型" in t)
check(
    "description_has_triggers",
    "Use when" in t and "驗證量子LLM" in t and "驗證量子模型" in t,
)
check("version_bump", 'version: "1.1.0"' in t)
check("usage_row", "驗證量子LLM" in t and "驗證量子模型" in t and "verify.py" in t)
check("logic_branch", "驗證觸發" in t and "verify.py" in t)
check(
    "hook_executes",
    "hook 執行" in t and "python3 ~/opencode-work/quantum-llm/verify.py" in t,
)
check(
    "ollama_guard", "curl -sS http://127.0.0.1:11434/api/ps" in t and '"models":[]' in t
)
check("endpoint_check", "http://127.0.0.1:8002/health" in t)
check("report_fields", "all_passed" in t and "finish_reason" in t)
check("no_false_success", "PASS" in t and "不代表答案正確" in t)
check("manifest_reminder", "quantum-llm-20261127.sha256" in t)
check("chinese_output", "繁體中文" in t)
check("no_plaintext_token", not re.search(r"hf_[A-Za-z0-9]{20,}", t))

if failures:
    print(f"RED: {len(failures)} check(s) failed")
    for f in failures:
        print(f"FAIL {f}")
    raise SystemExit(1)

print("GREEN: all checks passed")
