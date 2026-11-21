---
name: inspect-skill
description: >
  Use when reviewing, refactoring, or modularizing a set of skills: analyze
  usage scenarios, remove redundancy, build parent-child skill chains, and hook
  lower-level skills. Triggers on "inspect skills", "refactor skills",
  "modularize skills", or "skill audit".
---

# Inspect Skill

Review a collection of skills and refactor it into a non-redundant, modular
hierarchy with clear parent-child relationships.

## 1. Inventory

List the skills under review and capture for each:

- `name` and `description`
- Trigger conditions
- Core actions (what it does)
- Inputs/outputs
- Dependencies on other skills or tools

### Self-developed skills

Example inventory (self-developed skills):

| Skill | Triggers | Core actions | Lower-level hooks |
|---|---|---|---|
| `paperclip-launch` | install/launch Paperclip | managed CLI, service, health, repairs | `repo-pull` (for env-profile) |
| `assign-maus` | deploy/assign OpenMausBot | create bots/channels, kickoff, assign tasks | `paperclip-launch` (if Paperclip needed) |
| `audit-skill` | any skill work | security scan, manifest, verdict | none |
| `repo-pull` | clone/update repo | git clone/pull, install script | none |
| `rev-skill` | convert skill to Chinese | translate prose, preserve code | none |
| `publish-to-github` | publish to GitHub | git init, create repo, push, release | `audit-skill` (before publish) |
| `quant-algo-auto` | quant trading/channel ops | strategy, backtest, risk, content | none |

### External (installed) skills

| Skill | Source | Role | Hooked by |
|---|---|---|---|
| `grill-me` | `vinvcn/mattpocock-skills-zh-cn` | 持續追问式計畫壓力測試（wrapper → `grilling`） | `assign-maus`（指派任務前可選） |
| `grilling` | `vinvcn/mattpocock-skills-zh-cn` | 實際執行 grill 流程 | `grill-me` |

## 2. Analyze usage scenarios

For each skill, answer:

- When does a user or agent reach for it?
- What problem does it solve that no other skill covers?
- Which skills are always used together?

Group skills that share triggers or are always co-invoked.

## 3. Remove redundancy

- Merge skills whose descriptions overlap and whose bodies duplicate guidance.
- Split skills that mix unrelated concerns (e.g., install + publish).
- Keep one source of truth for shared reference (e.g., GitHub publishing steps).

## 4. Build parent-child chains

Design a hierarchy where:

- **Parent skills** orchestrate a workflow and delegate to children.
- **Child skills** are atomic, single-purpose capabilities.

Example chains:

```
paperclip-launch
  └── repo-pull          (pull env-profile before install)

publish-to-github
  └── audit-skill        (security gate before publish)

assign-maus
  └── paperclip-launch   (only if Paperclip must be running)
```

## 5. Hook lower-level skills

When a parent needs a child's capability, reference it explicitly:

- In prose: "Run the `audit-skill` skill before publishing."
- In a checklist: "Prerequisite: `repo-pull` completed."
- In code: invoke the child skill by name.

Do not duplicate the child's steps in the parent; hook instead.

## 6. Validate

- Every skill has a unique, non-overlapping trigger.
- No skill contains duplicated guidance from another.
- Parent-child references are accurate and minimal.
- Each skill still passes its own tests (if any).

## Common mistakes

- Merging skills that have different trigger conditions.
- Creating parent skills that just repeat child steps.
- Hooking a child that is not actually needed.
- Leaving orphaned skills with no clear owner.

## Notes

- This skill is a reference process, not an automated refactor tool.
- Apply changes incrementally: refactor one chain at a time.
- Keep `audit-skill` as a gate before publishing or installing any skill.
EOF
echo "written"