---
name: skill-router
description: >
  Use when you need a unified entry point to all self-developed skills, or when
  updated self-developed skills must be committed and pushed to a repo (a personal
  remote or a shared repo such as phycomp/oskill). Triggers on "skill router",
  "list my skills", "what skills do I have", "push updated skills to repo",
  "sync skills to oskill", "skill 已更新 push", or "自行開發 push".
---

# Skill Router

A unified entry point to all self-developed skills. Delegate to the
appropriate child skill based on the task. This skill also owns the sync rule:
**when / where / how** updated self-developed skills reach a repo.

## Available skills

> **唯一來源宣告：** `~/.config/skill-timer/self-developed.list`（由 `skill-timer` 擁有）是「哪些 skill 算自行開發」的 single source of truth。下表**僅供路由索引**，不是判定依據。增刪 skill 時先改 allow-list，再同步下表。

| Skill | Purpose | Hook |
|---|---|---|
| `paperclip-launch` | Install/start/auto-start Paperclip | `repo-pull` (optional) |
| `assign-maus` | Deploy/assign OpenMausBot bots and tasks | none |
| `audit-skill` | Security gate before install/publish | none |
| `repo-pull` | Clone/update a Git repository | none |
| `publish-to-github` | Publish a new folder/skill as a repo | `audit-skill` (before publish) |
| `skill-timer` | Owns the self-developed allow-list | hook: read `~/.config/skill-timer/self-developed.list` |
| `quant-algo-auto` | Quant trading and channel operations | none |
| `viz-dboard` | Visualize skill hierarchies as mindmap SVG | none |
| `chain-skill` | Review/refactor skill collections into parent-child chains | none |
| `refactor-skill` | Refactor a skill collection into modular parent-child chains | `chain-skill` |
| `social-router` | Orchestrate social content loop (produce → publish → feedback) | platform skills (by goal) |

## Routing

- Installing Paperclip → `paperclip-launch`
- Deploying/assigning AI bots → `assign-maus`
- Security review before install/publish → `audit-skill`
- Cloning/updating a repo → `repo-pull`
- Translating a skill to Chinese → `chain-skill` (Chinese conversion section)
- Publishing a **new** folder/skill → `publish-to-github`
- Quant/channel operations → `quant-algo-auto`
- Visualizing skill hierarchy → `viz-dboard`
- Reviewing/refactoring skills → `chain-skill`
- Refactoring a skill collection → `refactor-skill`
- Social content loop (produce / publish / feedback) → `social-router`
- **Syncing updated skills to a repo → this skill (single source of truth)**
- Determining "self-developed" → `skill-timer` allow-list (do not duplicate here)

## Sync updated self-developed skills to repo

Single source of truth for the push rule. Do not scatter this across
`publish-to-github` (new repos only), `chain-skill` (refactor methodology), or
`skill-timer` (allow-list only).

### When to sync (REQUIRED triggers)

| Trigger | Evidence |
|---|---|
| User explicitly asks to push / sync skills to a repo | their words |
| A self-developed skill is `dirty` or `unpushed` | `git status --porcelain` + `git log @{u}..HEAD` |
| A skill was edited and writing-skills deployment requires commit + push | `dirty` after the edit |

### Target selection (do not guess)

| Condition | Target |
|---|---|
| Skill has its own `origin` remote | that `origin` (`git remote get-url origin`) |
| No remote, or user names a shared repo | `phycomp/oskill` → `skills/<name>/` |
| Destination ambiguous | ask before pushing; never pick a "reasonable" default |

### Procedure

1. Read the allow-list at `~/.config/skill-timer/self-developed.list`. This is
   the authoritative definition of "self-developed"; do not keep a second list.
2. Inventory every allowed skill: `git status --porcelain` and
   `git log @{u}..HEAD` → `dirty` / `unpushed` / `synced` / `NO-GIT`.
3. For each target, compare local against remote. Overwrite only when local is
   newer (e.g. local removed stray `EOF`/`echo`, or updated stale references).
4. Commit with a scoped message, push, then verify `dirty=0 / unpushed=0` on
   every repo involved.
5. Report the tally: total repos, synced, dirty, unpushed.

### Guardrails

- Never guess the remote; `git remote get-url origin` is authoritative.
- Never duplicate the self-developed list — hook `skill-timer`'s allow-list.
- Never push third-party skills (`using-superpowers`, `writing-skills`) or
  deprecated aliases (`inspect-skill`).
- `NO-GIT` is not an error: use oskill when the user says so.
- A push is complete only after the tally shows zero dirty and zero unpushed.

## Notes

- `audit-skill` is required before any local installation.
- `quant-algo-auto` is independent (no hooks).
- Hooks are explicit; do not duplicate child steps in this skill.
- `chain-skill` owns the refactor loop; this skill owns routing + sync. When a
  refactor changes the skill set, hook `chain-skill` — do not restate its rules.
- Logic check: 2026-11-22 — `inspect-skill` renamed to `chain-skill`; all references updated; stray `EOF`/`echo` removed.
- Logic check: 2026-11-23 — added **Sync updated self-developed skills to repo** as the single source of truth for when/where/how to push (RED evidence: local grep of 68 matches had zero rules for oskill or self-developed push; agent relied on ad-hoc user instruction). Added `skill-timer` allow-list row and hook so "self-developed" is not duplicated. Description extended with push/sync triggers; routing now separates `publish-to-github` (new repos) from this skill (updates). No push steps duplicated into `chain-skill` or `publish-to-github`.
- Logic check: 2026-11-23 (second pass) — declared `skill-timer`'s allow-list as the **single source of truth** for "self-developed"; the Available skills table is now explicitly **index-only**. The same declaration was added to `chain-skill`'s Inventory table so the three lists (allow-list + two index tables) cannot drift silently.
- Logic check: 2026-11-23 (rename) — renamed `skill-toolchain` → `skill-router` (directory, `name:`, description trigger, title). All references updated: `refactor-skill`, `skill-timer` allow-list, oskill `skills/<name>/`, audit manifest. No thin alias kept — single entry point for routing.
- Logic check: 2026-11-23 (social-router) — added the social content skill to allow-list first, then to this index table and routing. Follows the single-source declaration: allow-list is authoritative, table is index-only. Renamed `social-loop` → `social-router` before first push; references updated.
