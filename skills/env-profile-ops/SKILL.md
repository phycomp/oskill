---
name: env-profile-ops
description: >
  Use when setting up or updating the OpenCode environment profile kit
  (env-profile): clone, install, generate profile, and verify. Triggers on
  "env-profile", "environment profile", "generate profile", or "install profile".
---

# Env Profile Ops

Set up and maintain the OpenCode environment profile kit.

## 1. Clone or update

```bash
if [ -d "$HOME/env-profile/.git" ]; then
  git -C "$HOME/env-profile" pull --ff-only
else
  git clone https://github.com/phycomp/env-profile.git "$HOME/env-profile"
fi
```

## 2. Install

```bash
cd "$HOME/env-profile"
./install.sh
```

This installs `generate-profile.sh` and `portable.md` to `~/.config/opencode/`,
updates `opencode.jsonc` instructions, and generates `environment-profile.md`.

## 3. Verify

Open a new OpenCode session and confirm the profile is loaded.

## 4. Update flow

1. Edit `profile/portable.md`
2. Commit and push
3. On each host: `git pull` + re-run `./install.sh`

## Notes

- The profile is split into portable (version-controlled) and local snapshot (generated).
- Never commit `environment-profile.md` or credentials.
- install.sh backs up `opencode.jsonc` before modifying.
EOF
echo "written"