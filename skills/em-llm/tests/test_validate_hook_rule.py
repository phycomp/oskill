#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate 2 RED/GREEN: em-llm 的 EM 驗證觸發與 hook 規則。"""

from pathlib import Path
import re

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"

failures = []


def check(name, cond):
    if not cond:
        failures.append(name)


t = SKILL.read_text(encoding="utf-8")

check("trigger_validate_em_llm", "驗證電磁LLM" in t)
check("trigger_validate_em_model", "驗證電磁模型" in t)
check(
    "description_has_triggers",
    "Use when" in t and "驗證電磁LLM" in t and "驗證電磁模型" in t,
)
check("version_bump", 'version: "1.1.0"' in t)
check("hook_executes", "hook 執行" in t and "em 驗證" in t)
check("pytest_suite", "/home/sam/flex/bin/python -m pytest -q tests/" in t)
check("cli_info", "/home/sam/flex/bin/python -m em_llm.cli info" in t)
check("cli_scenarios", "/home/sam/flex/bin/python -m em_llm.cli scenarios" in t)
check("mesh_example", "/home/sam/flex/bin/python examples/run_mesh_em.py" in t)
check("optional_env_gate", "Ollama" in t and "pymeep" in t and "skipped" in t)
check(
    "credential_discipline",
    "~/.config/opencode/service.json" in t and "password" in t and "绝不寫入" in t,
)
check("no_false_success", "PASS" in t and "不等於物理正確" in t)
check("chinese_output", "繁體中文" in t)
check("no_plaintext_token", not re.search(r"hf_[A-Za-z0-9]{20,}", t))

if failures:
    print(f"RED: {len(failures)} check(s) failed")
    for f in failures:
        print(f"FAIL {f}")
    raise SystemExit(1)

print("GREEN: all checks passed")
