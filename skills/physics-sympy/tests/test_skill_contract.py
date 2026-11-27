#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""physics-sympy 技能契約測試：模型選型、流程、見證、獨立 child、繁體。"""

from pathlib import Path
import re

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
failures = []


def check(name, cond):
    if not cond:
        failures.append(name)


t = SKILL.read_text(encoding="utf-8")

check("frontmatter_name", "name: physics-sympy" in t)
check("parent_is_llm_router", "llm-router (parent / 單一入口)" in t)
check("independent_of_quantum_llm", "不隸屬 `quantum-llm`" in t)
check("independent_of_em_llm", "不重述 `em-llm`" in t)
check("coder_model", "qwen2.5-coder:7b" in t and "Qwen2.5-Coder-7B-Instruct" in t)
check("math_model", "qwen2.5-math-7b" in t and "Qwen2.5-Math-7B-Instruct" in t)
check("gguf_source", "bartowski/Qwen2.5-Math-7B-Instruct-GGUF" in t)
check("no_official_tag", "file does not exist" in t)
check("sympy_executor", "/home/sam/flex/bin/python" in t)
check(
    "commutator_check", "sigma_x*sigma_y" in t and ("2iσz" in t or "2*I*sigma_z" in t)
)
check("unitarity_check", "U.H*U" in t or "U†U" in t)
check("evidence_paths", "_raw.txt" in t and "_stdout.txt" in t and "_stderr.txt" in t)
check("retry_limit", "最多 2 輪" in t)
check("coder_verified", "CODER_RC=0" in t and "EXEC_RC=0" in t)
check("math_verified", "CREATE_RC=0" in t and "MANUAL_RC=0" in t)
check("math_limitation_honest", "不標為模型直接生成可執行程式" in t)
check("logic_check", "Logic check: 2026-11-26" in t)
check("no_plaintext_token", not re.search(r"hf_[A-Za-z0-9]{20,}", t))
check(
    "traditional_chinese",
    not re.search(
        r"[确时换简关证对误执编译进说话们这来个为与从当发过还结给经统设计]", t
    ),
)

if failures:
    print(f"RED: {len(failures)} check(s) failed")
    for f in failures:
        print(f"FAIL {f}")
    raise SystemExit(1)

print("GREEN: all checks passed")
