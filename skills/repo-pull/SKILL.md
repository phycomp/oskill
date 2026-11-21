---
name: repo-pull
description: >
  Use when cloning or updating a Git repository locally, especially
  environment-profile repos. Triggers on "git pull", "clone repo",
  "update env-profile", or "pull latest".
---

# Repo Pull

Clone or update a Git repository and, when present, run its install script.

## Inputs

- `REPO_URL`: repository URL (default: `https://github.com/phycomp/env-profile.git`)
- `DEST`: destination directory (default: `~/env-profile`)

## 1. Check existing clone

```bash
if [ -d "$DEST/.git" ]; then
  git -C "$DEST" pull --ff-only
else
  git clone "$REPO_URL" "$DEST"
fi
```

Done when: the command exits 0 and `git -C "$DEST" status` shows a clean working tree.

## 2. Inspect changes (optional)

```bash
git -C "$DEST" log --oneline -5
git -C "$DEST" diff --stat HEAD~1
```

## 3. Run install script (if present)

```bash
if [ -x "$DEST/install.sh" ]; then
  "$DEST/install.sh"
fi
```

Only run install scripts from repositories you trust.

## 4. Verify (env-profile example)

```bash
test -f "$HOME/.config/opencode/environment-profile.md" && echo "profile generated"
```

## Common mistakes

- Running `git pull` in a directory that is not a Git repository.
- Forgetting to run the install script after updating `profile/portable.md`.
- Assuming `git pull` merges; use `--ff-only` to avoid unexpected merge commits.
EOF
echo "written"