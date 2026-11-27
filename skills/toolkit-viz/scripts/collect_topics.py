#!/usr/bin/env python3
"""Collect all distilled topics from local + skills + deployed sources."""

import json, os, sys, hashlib
from pathlib import Path

SOURCES = [
    ("local", Path("/tmp/opencode")),
    ("skills", Path("/home/sam/.opencode/skills")),
    ("project", Path("/home/sam/軟體/代理人/.agents/skills")),
]


def find_distill_dirs(base):
    """Find distill_* directories."""
    results = []
    if base.exists():
        for d in base.iterdir():
            if d.is_dir() and d.name.startswith("distill_"):
                results.append(d)
    return results


def find_skill_refs(base):
    """Find skill references directories."""
    results = []
    if base.exists():
        for d in base.iterdir():
            if d.is_dir() and (d / "references").exists():
                results.append(d)
    return results


def collect():
    topics = {}
    # 1. Local distill dirs
    for label, base in SOURCES[:1]:
        for d in find_distill_dirs(base):
            name = d.name.replace("distill_", "")
            md_files = sorted(d.glob("*.md"))
            topics[name] = {
                "source": "local",
                "path": str(d),
                "md_files": [str(f) for f in md_files],
                "count": len(md_files),
            }
    # 2. Skill references
    for label, base in SOURCES[1:]:
        for d in find_skill_refs(base):
            name = d.name
            refs = sorted((d / "references").glob("*.md"))
            if refs:
                topics[name] = {
                    "source": "skill",
                    "path": str(d / "references"),
                    "md_files": [str(f) for f in refs],
                    "count": len(refs),
                }
    # Save index
    out = Path("/home/sam/.opencode/skills/toolkit-viz/data/topics_index.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(topics, ensure_ascii=False, indent=2))
    print(f"Collected {len(topics)} topics")
    for name, info in topics.items():
        print(f"  {name}: {info['count']} files ({info['source']})")
    return topics


if __name__ == "__main__":
    collect()
