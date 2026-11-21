---
name: skill-toolchain
description: >
  Use when you need a unified entry point to all self-developed skills.
  Triggers on "skill toolchain", "list my skills", or "what skills do I have".
---

# Skill Toolchain

A unified entry point to all self-developed skills. Delegate to the
appropriate child skill based on the task.

## Available skills

| Skill | Purpose | Hook |
|---|---|---|
| `paperclip-launch` | Install/start/auto-start Paperclip | `repo-pull` (optional) |
| `assign-maus` | Deploy/assign OpenMausBot bots and tasks | none |
| `audit-skill` | Security gate before install/publish | none |
| `repo-pull` | Clone/update a Git repository | none |
| `publish-to-github` | Publish a folder/skill to GitHub | `audit-skill` (before publish) |
| `quant-algo-auto` | Quant trading and channel operations | none |
| `viz-dboard` | Visualize skill hierarchies as mindmap SVG | none |
| `inspect-skill` | Review/refactor skill collections | none |

## Routing

- Installing Paperclip → `paperclip-launch`
- Deploying/assigning AI bots → `assign-maus`
- Security review before install/publish → `audit-skill`
- Cloning/updating a repo → `repo-pull`
- Translating a skill to Chinese → `inspect-skill` (Chinese conversion section)
- Publishing to GitHub → `publish-to-github`
- Quant/channel operations → `quant-algo-auto`
- Visualizing skill hierarchy → `viz-dboard`
- Reviewing/refactoring skills → `inspect-skill`

## Notes

- `audit-skill` is required before any local installation.
- `quant-algo-auto` is independent (no hooks).
- Hooks are explicit; do not duplicate child steps in this skill.
EOF
echo "written"