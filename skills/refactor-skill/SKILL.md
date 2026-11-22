---
name: refactor-skill
description: >
  Use when reviewing and refactoring a collection of skills into a
  non-redundant, modular hierarchy with parent-child chains and lower-level
  hooks. Triggers on "refactor skills", "modularize skills", or "skill audit".
---

# Refactor Skill

Refactor a set of skills into a clean, modular hierarchy.

## 1. Inventory

List all skills under review with name, description, triggers, core actions,
and dependencies.

## 2. Analyze usage scenarios

For each skill, determine when it is reached, what unique problem it solves,
and which skills are always co-invoked.

## 3. Remove redundancy

- Merge overlapping skills.
- Split skills mixing unrelated concerns.
- Keep one source of truth for shared reference.

## 4. Build parent-child chains

Design a hierarchy where parents orchestrate and children are atomic.
Document chains explicitly (e.g., `publish-to-github → audit-skill`).

## 5. Hook lower-level skills

Reference children in parents by name; do not duplicate child steps.

## 6. Archive redundant skills

Move redundant skills to an archive directory (e.g., `~/.agents/skills-archive/`)
and remove them from the active collection.

## 7. Visualize (optional)

Generate a mindmap SVG of the hierarchy (see `viz-dboard`).

## 8. Validate

- Unique, non-overlapping triggers.
- No duplicated guidance.
- Accurate, minimal hooks.
- Each skill still functional.

## 9. Update unified entry point

Add new skills to `skill-router` and remove archived ones.

## Common mistakes

- Merging skills with different triggers.
- Creating parents that just repeat child steps.
- Hooking unnecessary children.
- Leaving orphaned skills.
