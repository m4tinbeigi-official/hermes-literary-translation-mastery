---
name: telegram-content-bot-operations
description: "Use when configuring, operating, testing, or troubleshooting autonomous Telegram content curation & publishing bots, multi-source scraping (Hacker News, Reddit, Dev.to, GitHub), channel permission management, admin approval flows, and LLM tone rewriting pipelines."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [telegram-bot, content-curation, vibecoding, channel-publishing, approval-workflow, llm-rewriter]
---

# Telegram Content Bot Operations & Publishing Pipeline

## Overview
A comprehensive guide and operational pattern for developing, configuring, testing, and managing automated Telegram content bots that fetch technology/AI news across multiple platforms, rewrite content in customized Persian/English literary voices via LLM APIs (e.g. 9Router / Gemini 3.7 / Qwen), manage user approval workflows, and publish to channels.

---

## 1. Environment & Telegram API Architecture

### Essential Configuration (`.env`)
```bash
# Bot credentials from @BotFather
TELEGRAM_BOT_TOKEN=<TOKEN>

# Target channel (numerical -100xxx or public @username)
TELEGRAM_CHANNEL_ID=-1002101305073

# Admin user ID for interactive approvals & direct notifications
TELEGRAM_ADMIN_CHAT_ID=1414726588

# LLM backend for content rewriting (e.g. Local 9Router endpoint)
AI_API_BASE=http://localhost:20128/v1
AI_MODEL=ag/gemini-3.7-flash-medium
AI_API_KEY=dummy
```

### Channel Permissions & HTTP 403 Diagnostics
When publishing to a Telegram channel (`TELEGRAM_CHANNEL_ID`):
1. **Bot must be added as an Administrator** in the channel.
2. Bot must have the **"Post Messages"** permission explicitly granted.
3. If an HTTP `403 Forbidden` error occurs during `sendMessage`, verify channel membership:
   - Numerical channel IDs starting with `-100...` are required for private or supergroup channels.
   - Public channels can accept `@channel_username`, but numerical ID avoids DNS/lookup latency.

---

## 2. Admin Approval Flow Pattern
To ensure content quality and personal tone alignment before broadcasting:
1. **Scrape & Deduplicate:** Sources poll (RSS, APIs) -> filter keywords -> record in SQLite `posts.db`.
2. **Draft & Rewrite:** LLM rewrites content into concise, engaging Persian prose using target voice profiles.
3. **Interactive Approval:** Send draft to `TELEGRAM_ADMIN_CHAT_ID` with inline keyboard buttons (`[✅ Publish]` / `[❌ Reject]` / `[✏️ Edit]`).
4. **Publish on Action:** On callback query `approve_<post_id>`, broadcast to `TELEGRAM_CHANNEL_ID` and include channel signature/link.

---

## 3. Communication & User Identity Ethics
- **Strict Rule on User Naming:** Never infer or assume the user's real private name from Telegram usernames, channel titles, or bot IDs (e.g., handles like `m4tinbeigi` or titles do not mean the user wants to be called that name). Address the user politely, neutrally, or by their explicitly requested moniker.

---

## 4. Operational Troubleshooting

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `HTTP 403: Forbidden` to Channel | Bot not admin or lacks post permissions | Add bot as Channel Administrator with 'Post Messages' |
| Telegram web scrape returns 0 posts | Telegram blocks direct headless curl/requests to `/s/channel` | Use official Telegram Bot API or authenticated MTProto/Telethon client rather than HTML scraping |
| Rate limiting on GitHub Trending | GitHub API unauthenticated limit hit (60 req/hr) | Supply `GITHUB_TOKEN` in `.env` |
| Local LLM connection error | 9Router daemon not running on port 20128 | Verify `curl http://localhost:20128/v1/models` |
