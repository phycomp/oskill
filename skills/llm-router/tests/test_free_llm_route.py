#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RED/GREEN: llm-router 應路由免費/雲端 LLM API 資源到 free-llm。"""

from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
failures = []


def check(name, cond):
    if not cond:
        failures.append(name)


t = SKILL.read_text(encoding="utf-8")
tl = t.lower()

check("route_free_llm_hook", "`free-llm`" in t)
check("route_free_api_goal", "免費 llm api" in tl or "免費llm api" in tl or "free llm api" in tl)
check("route_cloud_provider", "groq" in tl or "openrouter" in tl or "gemini" in tl)
check("child_inventory_free_llm", "| `free-llm` | `.agents/skills` |" in t)
check("boundary_opencode_free_fallback", "opencode-free-fallback" in t)
check("no_secret_inline", "sk-" not in t and "gsk_" not in t)

if failures:
    print(f"RED: {len(failures)} check(s) failed")
    for f in failures:
        print(f"FAIL {f}")
    raise SystemExit(1)

print("GREEN: all checks passed")
