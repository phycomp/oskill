#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate 2 RED/GREEN: quantum-llm 的 colibrì 來源與獨立 parent 規則。"""

from pathlib import Path
import re

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"

failures = []


def check(name, cond):
    if not cond:
        failures.append(name)


t = SKILL.read_text(encoding="utf-8")

check("source_path", "~/軟體/代理人/colibri/" in t)
check("model_path", "/mnt/d/sam/colibri/models/glm52_i4" in t)
check("hf_repo", "mastouri/GLM-5.2-colibri-int4-g64-with-int8-mtp" in t)
check("version", "1.12.1" in t)
check("cli_version", "coli --version" in t)
check("doctor", "coli doctor" in t)
check("test_suite", "tools/run_tests.py" in t)
check("test_result", "105/105 PASS" in t)
check("serve", "coli serve" in t)
check("api_models", "/v1/models" in t)
check("api_chat", "/v1/chat/completions" in t)
check("independent_parent", "共同 parent" in t and "llm-router" in t)
check("no_parent_child_claim", "parent of em-llm" not in t and "└── em-llm" not in t)
check("independent_child_of_router", "independent child" in t)
check("physics_sympy_hook", "`physics-sympy`" in t and "自然語言" in t)
check("not_owning_model_ids", "模型 id" in t and "physics-sympy" in t)
check("logic_check", "Logic check: 2026-11-26" in t)
check("no_plaintext_token", not re.search(r"hf_[A-Za-z0-9]{20,}", t))

if failures:
    print(f"RED: {len(failures)} check(s) failed")
    for f in failures:
        print(f"FAIL {f}")
    raise SystemExit(1)

print("GREEN: all checks passed")
