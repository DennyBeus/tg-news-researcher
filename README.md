# tg-news-researcher

Daily Telegram digest system based on n8n and a Python parser.

## What it does

- Parses Telegram channels on a schedule
- Filters news by your interests using AI (GPT-4o)
- Sends a daily digest with short summaries via Telegram bot
- Generates posts in your writing style based on selected news

## Stack

- **n8n** — orchestration, Telegram bot, AI calls, DB queries
- **Python** — Telegram channel parser only (kurigram)
- **PostgreSQL** — storage for news, channels, interests, styles, settings
- **OpenAI API** — filtering, summarization, post generation

## Structure

- `parser/` — Python parser (called by n8n via Execute Command)
- `n8n/` — workflow JSON files for import into n8n
- `sql/` — SQL scripts for creating database tables
- `PROJECT.md` — full project documentation and architecture

## Setup

See [PROJECT.md](PROJECT.md) for detailed setup instructions and architecture.

## Language

- [Русская версия (README.ru.md)](README.ru.md)
