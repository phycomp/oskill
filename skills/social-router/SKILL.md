---
name: social-router
description: >
  Use when the user wants social content handled as a closed loop — plan a post,
  produce copy and assets, publish to one or more platforms, verify delivery,
  and feed results back into the next post. Triggers on "social post workflow",
  "social router", "社群貼文 製作 發布", "社群製作發布",
  "cross-platform posting loop", or "social content loop". Not for a single
  platform's API details (use the platform skill).
---

# Social Router — 社群製作與發布閉環

Orchestrate social content from idea to published post to feedback. This skill
owns the **loop and the hook decisions**; it does not duplicate platform details.

## Core invariant — 引用 `chain-skill`

The closed loop is owned by `chain-skill`. **Do not duplicate its rules here** —
load `chain-skill` when changing this skill:

```
寫什麼(製作) → 發到哪(發布) → 效果如何(回饋) → 學到什麼(沉澱)
     ↑                                            │
     └────────── need-based hook ←────────────────┘
```

Closing the loop means writing the learning back into the content calendar,
re-running audit + drift verify for skill changes, and recording the date in
`Logic check:`. Reporting a problem without writing it back is an open loop.

> **唯一來源宣告：** `~/.config/skill-timer/self-developed.list`（由 `skill-timer` 擁有）是「哪些 skill 算自行開發」的 single source of truth。本 skill 的各種表僅供索引，不是判定依據。

## Need-based hooks — 需要時才 hook

Hook by **workflow goal**, not by skill name. Do not invoke every platform skill on every post.

| Goal | Hook | Skip when |
|---|---|---|
| Cross-platform scheduling / publishing | `social-publisher` | Single platform |
| WeChat Official Account (微信公眾號) | `baoyu-post-to-wechat` | Non-WeChat target |
| RedNote (小紅書) | `xiaohongshu` | Non-RedNote target |
| Video script / storyboard for the post | `yt-vid` | Text-only post |
| Analytics after publish | platform analytics skill | Before publishing |
| Push updated skill to repo | `skill-router` (sync rule), `audit-skill` (gate) | No local changes |

A hook without a matching goal is a violation — it adds cost and blurs ownership.
Platform skills are third-party: **hook them, never modify them**.

## Doc + delivery + feedback compliance

A tool success message is not evidence. Verify all three layers:

| Layer | Check | Failure example (RED baseline) |
|---|---|---|
| Doc | Copy matches assets; platform format respected (aspect ratio, character limit, hashtags) | Copy says "nine-image carousel" but only one image attached |
| Delivery | After publish, confirm the post exists and is visible on the platform | Tool returned success but post never appeared |
| Feedback | Record reach/engagement back into the content calendar | Published and forgotten; no learning captured |

If delivery contradicts the tool response, re-check the platform — never paper
over it with an unchecked item or a `legacy` label.

## When to use

- Planning a post across platforms (not just one platform's API)
- Producing copy + assets, then publishing and verifying
- Closing the loop: results → next post's plan
- Deciding which platform skill to call for a given goal

## Workflow

1. **Scenario** — audience, goal, platforms, and what makes this post unique.
2. **Produce** — copy + assets; check Doc compliance before publishing.
3. **Hook by goal** — call only the platform skills the target requires.
4. **Publish** — require explicit user consent for anything public or irreversible.
5. **Verify** — confirm the post is live (Delivery compliance).
6. **Feedback** — record results; write the learning back into the calendar.
7. **Distill** — for skill changes, write into this SKILL.md, re-audit, update `Logic check:`.

## Common mistakes

- Calling every platform skill "just in case" (unnecessary hook).
- Editing a third-party platform skill to fit this loop (hook it instead).
- Treating a tool's success message as proof of delivery.
- Publishing without explicit user consent.
- Reporting a learning without writing it back (open loop).
- Duplicate `chain-skill`'s loop rules here instead of referencing them.

## Guardrails

1. Never publish public or irreversible content without clear user consent.
2. Do not guess platform accounts or credentials — read them from the hooked tool's config.
3. Never modify third-party platform skills; hook them only.
4. Do not restate platform-specific rules here — the platform skill owns them.
5. Close the loop: write the learning back, or do not call it done.

## References

- `chain-skill` — owns the closed loop; load it when changing this skill (do not duplicate)
- `skill-router` — owns the sync rule when updated skills must be pushed to a repo
- `audit-skill` — security gate before publish/install
- `social-publisher` — cross-platform scheduling and publishing (hook)
- `baoyu-post-to-wechat` — WeChat Official Account (hook)
- `xiaohongshu` — RedNote content and publishing (hook)
- `yt-vid` — video script / storyboard (hook)
- Logic check: 2026-11-23 — created with the closed-loop rule by reference (user request: 「引用閉環規則 開發社群製作、發佈技能」). Core invariant references `chain-skill` without duplicating it; need-based hook table, doc/delivery/feedback compliance, guardrails, and allow-list single-source declaration added. RED evidence reused from prior observations (stale doc vs reality, unnecessary hooks, tool-success-as-evidence, open loop). New skill — no existing self-developed social skill to refactor; platform skills remain third-party and are hooked, not modified.
- Logic check: 2026-11-23 (rename) — renamed `social-loop` → `social-router` (directory, `name:`, description trigger, title) before the first push. All references updated: `skill-timer` allow-list, `skill-router` index + routing, `chain-skill` index, audit manifest. No thin alias kept.
