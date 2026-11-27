#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate 2 RED/GREEN: llm-router 新增 physics-sympy 路由與獨立 child 鏈。"""

from pathlib import Path
import re

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
failures = []


def check(name, cond):
    if not cond:
        failures.append(name)


t = SKILL.read_text(encoding="utf-8")

check("frontmatter_name", "name: llm-router" in t)
check("route_goal", "哈密頓量" in t and "SymPy" in t)
check("route_hook", "`physics-sympy`" in t)
check("child_inventory", "| `physics-sympy` | `.agents/skills` |" in t)
check("function_set", "自然語言 → 算符 → SymPy" in t)
check("independent_child", "physics-sympy" in t and "independent child" in t)
check("three_parallel_children", t.count("independent child") >= 2)
check("no_quantum_llm_parent_claim", "parent of em-llm" not in t)
check(
    "direct_child_physics_sympy",
    "  └── physics-sympy" in t and "      └── physics-sympy" not in t,
)
check("logic_check", "Logic check: 2026-11-26" in t)
check("no_plaintext_token", not re.search(r"hf_[A-Za-z0-9]{20,}", t))

if failures:
    print(f"RED: {len(failures)} check(s) failed")
    for f in failures:
        print(f"FAIL {f}")
    raise SystemExit(1)

print("GREEN: all checks passed")
