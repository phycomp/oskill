---
name: rev-skill
description: >
  Use when converting or reviewing a skill into Traditional Chinese (繁體中文),
  while preserving code, commands, file paths, and technical identifiers.
  Triggers on "改成繁體中文", "translate skill to Chinese", or "rev-skill".
---

# Rev Skill

Convert a skill's prose into Traditional Chinese without breaking its
structure, code, or triggers.

## 1. Inspect the target skill

```bash
ls -la <skill-dir>
sed -n '1,40p' <skill-dir>/SKILL.md
```

Done when: you know the skill's files, frontmatter, and overall structure.

## 2. Preserve what must stay original

Do **not** translate:

- YAML keys (`name`, `description`, `license`, etc.)
- Code blocks, shell commands, file paths, URLs
- Identifiers, API names, product names
- Trigger keywords that users type in English (keep them, optionally add Chinese synonyms)

## 3. Translate prose to Traditional Chinese

- Translate headings, explanations, examples, and comments.
- Use Traditional Chinese (繁體中文) with Taiwan usage where applicable.
- Keep technical terms in English on first use, with Chinese in parentheses if helpful.
- Ensure `description` still starts with "Use when..." and remains searchable.

## 4. Validate

```bash
# Frontmatter check
head -20 <skill-dir>/SKILL.md

# No broken relative links
grep -oE '\]\([^)]+\)' <skill-dir>/SKILL.md
```

Done when: frontmatter is valid, links resolve, and content reads naturally in Traditional Chinese.

## 5. Test (optional but recommended)

- Read the converted skill end-to-end.
- Confirm code blocks are unchanged.
- Confirm triggers still match user intent.

## Common mistakes

- Translating code or commands (breaks usability).
- Dropping English trigger keywords (reduces discoverability).
- Mixing Simplified and Traditional Chinese.
- Changing the skill's `name` field (keep it stable).
EOF
echo "written"