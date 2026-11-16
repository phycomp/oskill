---
name: social-media-suite
description: "Root architecture for all social media skills. Integrates content creation, publishing, analytics, and platform management across Facebook, Instagram, YouTube, TikTok, LinkedIn, Threads, X, and LINE."
version: "2.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# Social Media Suite — 社群媒體根架構

## 架構總覽

```
social-media-suite (根架構)
├── Content Layer (內容層)
│   ├── social              → 社群貼文創作 (LinkedIn/Twitter/IG/TikTok/FB)
│   ├── social-post         → 依真實貼文與成效寫文案 (FB/IG/YT/Threads/X)
│   └── remotion-social     → 社群媒體動態內容 (Remotion)
├── Publishing Layer (發布層)
│   ├── social-publish      → 社群發佈 (小紅書/FB/LINE/IG/TikTok)
│   ├── social-publisher    → 多平台發布自動化
│   ├── fb-app-post         → Facebook Graph API 發文
│   └── x-article-draft-uploader → X Article 草稿上傳
├── Video Layer (影音層)
│   ├── youtube-studio-browser-upload → YouTube Studio 瀏覽器上傳
│   ├── youtube-oauth-upload → YouTube OAuth API 上傳
│   └── shorts-pipeline     → Shorts 端到端 pipeline
├── Push Layer (推送層)
│   ├── push-streamlit      → Streamlit 網站推送 (GitHub/HF/Kaggle)
│   ├── push-repo           → Repo 推送
│   ├── git-push            → Git 推送到 GitHub
│   └── git-commit-and-push → 邏輯拆分 commit + push
└── Analytics Layer (分析層)
    └── (social-post data/ → 貼文成效學習)
```

## 子技能索引

### Content Layer (內容層)

| 技能 | 位置 | 功能 |
|------|------|------|
| `social` | `~/.agents/skills/social/` | LinkedIn/Twitter/Instagram/TikTok/Facebook 內容創作、排程、social listening |
| `social-post` | `~/.agents/skills/social-post/` | 依使用者真實貼文與成效寫 FB/IG/YT/Threads/X 文案 |
| `remotion-social` | `~/.opencode/skills/remotion-social/` | Remotion 社群媒體動態內容 |

### Publishing Layer (發布層)

| 技能 | 位置 | 功能 |
|------|------|------|
| `social-publish` | `~/.opencode/skills/social-publish/` | 社群發佈 (小紅書/FB/LINE/IG/TikTok)、成立群組、下載相簿 |
| `social-publisher` | `~/.agents/skills/social-publisher/` | 多平台社群媒體發布自動化 |
| `fb-app-post` | `~/.agents/skills/fb-app-post/` | Facebook Graph API 發文 |
| `x-article-draft-uploader` | `~/.agents/skills/x-article-draft-uploader/` | Markdown 上傳 X Article 草稿 |

### Video Layer (影音層)

| 技能 | 位置 | 功能 |
|------|------|------|
| `youtube-studio-browser-upload` | `~/.agents/skills/youtube-studio-browser-upload/` | YouTube Studio 瀏覽器上傳 |
| `youtube-oauth-upload` | `~/.agents/skills/youtube-oauth-upload/` | YouTube OAuth API 上傳 |
| `shorts-pipeline` | `~/.agents/skills/shorts-pipeline/` | Shorts 端到端 pipeline |

### Push Layer (推送層)

| 技能 | 位置 | 功能 |
|------|------|------|
| `push-streamlit` | `~/.opencode/skills/push-streamlit/` | Streamlit 網站推送 (GitHub/HF/Kaggle) |
| `push-repo` | `~/.agents/skills/push-repo/` | Repo 推送 |
| `git-push` | `~/.opencode/skills/git-push/` | Git 推送到 GitHub |
| `git-commit-and-push` | `~/.agents/skills/git-commit-and-push/` | 邏輯拆分 commit + push |

### Analytics Layer (分析層)

| 技能 | 位置 | 功能 |
|------|------|------|
| `social-post` (data/) | `~/.agents/skills/social-post/data/` | 貼文成效學習、規則註冊表 |
| `social` (references/) | `~/.agents/skills/social/references/` | 平台限制、模板、短影音框架 |

## 使用流程

### 1. 內容創作 → 發布
```
social (創作) → social-post (文案) → social-publish (發佈) → social-publisher (自動化)
```

### 2. 影音製作 → 上傳
```
shorts-production (製作) → shorts-acceptance (驗收) → youtube-studio-browser-upload (上傳)
```

### 3. 網站推送
```
push-streamlit (同步) → git-commit-and-push (提交) → push-repo (推送)
```

### 4. 臉書發布
```
fb-app-post (Graph API 發文) → social-post (文案優化)
```

### 5. X/Twitter 發布
```
x-article-draft-uploader (草稿上傳) → social-post (文案優化)
```

## 觸發條件
- 「社群媒體」「social media」「內容發布」「跨平台發佈」
- 「社群管理」「community management」「內容創作」
- 「push streamlit」「推送網站」「社群發文」

## 版本
- 2.0.0 (2026-11-16): 重構為根架構，整合所有社群技能