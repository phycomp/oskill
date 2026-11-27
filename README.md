# oskill

A collection of self-developed agent skills.

## Skills

### Social media suite

Root architecture and its 14 sub-skills. Start from `social-media-suite` — it maps every
sub-skill to a layer (content → publishing → video → push → analytics).

| Skill | Description |
| --- | --- |
| `skill-toolchain` | Unified entry point to all self-developed skills |
| `social-media-suite` | Root architecture: routes any social request to the right sub-skill across Facebook, Instagram, YouTube, TikTok, LinkedIn, Threads, X and LINE |
| `social` | Social content creation, scheduling, and social listening for LinkedIn, X, Instagram, TikTok and Facebook |
| `social-post` | Write FB/IG/YT/Threads/X copy from your own past posts and their performance; local workbench, publish-after-confirm, comment replies, outcome learning |
| `remotion-social` | Record platform flows with Playwright and compose them into Remotion video projects |
| `social-publish` | Publish posts, create groups and download albums on Xiaohongshu / Facebook / LINE / Instagram / TikTok |
| `social-publisher` | Multi-platform publishing automation: schedule, post and track across TikTok, Instagram, YouTube and LinkedIn |
| `fb-app-post` | Post to a Facebook Page via Graph API: app setup, Page Access Token, `pages_manage_posts` troubleshooting |
| `x-article-draft-uploader` | Upload local Markdown to X/Twitter Articles drafts, including Markdown pipe tables and 5:2 cover images |
| `youtube-studio-browser-upload` | Upload to YouTube Studio through browser automation, with UI-state verification and evidence-based stop rules |
| `youtube-oauth-upload` | Upload or schedule via the YouTube Data API with an OAuth desktop client, including consent and channel checks |
| `shorts-pipeline` | End-to-end Short-form pipeline: topic selection, production, acceptance, caption/upload packages, scheduling |
| `push-streamlit` | Push a Streamlit site to GitHub and deploy to Streamlit Cloud / Hugging Face Spaces / Kaggle |
| `push-repo` | Turn a directory into its own repo and push it: read-only preflight, exclusion ledger, post-push fresh-clone verification |
| `git-push` | Git push to GitHub: PAT scopes, remote setup, large-file and workflow-scope troubleshooting |
| `git-commit-and-push` | Split uncommitted changes into a few logical, single-concern commits, then push |

### Other

| Skill | Description |
| --- | --- |
| `paperclip-launch` | Install, start, and auto-start a local Paperclip instance, including health checks and startup repairs |
| `refactor-skill` | Refactor a skill collection into modular parent-child chains |
| `viz-dboard` | Visualize skill hierarchies as a mindmap SVG |
| `inspect-skill` | Review and refactor a set of skills into a modular parent-child hierarchy |
| `repo-pull` | Clone or update a Git repository locally, with optional install script execution |
| `assign-maus` | Deploy and assign work through OpenMausBot MCP: role-based bots, channels, kickoff messages, task assignment |
| `publish-to-github` | Publish a local folder or skill to GitHub end-to-end |
| `quant-algo-auto` | Quantitative investing, algorithmic trading, and automation skill |
| `audit-skill` | Security-first workflow for developing or installing agent skills |

## Install a skill

Copy the desired skill folder into your skills directory:

```bash
cp -r skills/paperclip-launch ~/.agents/skills/
```

Skills live under `~/.agents/skills/` or `~/.opencode/skills/` depending on which agent
runtime reads them; both layouts work, the folder content is the same.

### 本機自建技能（2026-11-27 彙入）

| Skill | 來源 |
| --- | --- |
| `inkling-mini` | `.agents/skills/inkling-mini` |
| `llm-router` | `.agents/skills/llm-router` |
| `physics-sympy` | `.agents/skills/physics-sympy` |
| `push-repo` | `.agents/skills/push-repo` |
| `push-router` | `.agents/skills/push-router` |
| `quantum-llm` | `.agents/skills/quantum-llm` |
| `em-llm` | `.agents/skills/em-llm` |
| `skillrule-viz` | `.opencode/skills/skillrule-viz` |
| `innobiz-market` | `.opencode/skills/innobiz-market` |
| `physim-topics` | `.opencode/skills/physim-topics` |
| `qc-skill` | `.opencode/skills/quantum-website` |
| `task-changelog` | `.opencode/skills/task-changelog` |
| `toolkit-viz` | `.opencode/skills/toolkit-viz` |
