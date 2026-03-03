# Telegram News Researcher

[English](README.md) | [Русский](README.ru.md)

A system for collecting daily news digests from Telegram channels, powered by a Python Telegram bot, n8n workflows and a channel parser.

## How it works

1. **Parsing** — a Python userbot reads posts from configured Telegram channels (n8n scheduled task)
2. **Filtering** — OpenAI filters posts by your interests (n8n)
3. **Digest** — daily summary sent via Telegram bot at a configured time (bot)
4. **Post generation** — select news from the digest and generate a post in your writing style (bot)

## Architecture

- **bot/** — Python Telegram bot (aiogram 3.x). Handles all user interaction, digest sending, error notifications. Works directly with PostgreSQL and OpenAI API
- **n8n/** — background data pipeline. Parsing + filtering, DB cleanup, error logging to DB. No Telegram nodes
- **parser/** — Python Telegram channel parser (kurigram). Called by n8n via Execute Command
- **postgres/** — SQL scripts for database schema

## Tech stack

- **Telegram bot**: Python 3.10+, aiogram 3.x, asyncpg, openai SDK, APScheduler
- **n8n** (self-hosted) — orchestration of background tasks
- **Python parser**: [kurigram](https://github.com/KurimuzonAkuma/kurigram) (Pyrogram-compatible)
- **OpenAI API** (gpt-4o) — filtering (n8n), summarization & generation (bot)
- **PostgreSQL** — news, channels, interests, styles, settings, errors

## Project structure

```
tg-news-researcher/
├── bot/                     # Telegram bot (Python, aiogram 3.x)
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration from .env
│   ├── db.py                # PostgreSQL connection pool (asyncpg)
│   ├── scheduler.py         # APScheduler: digest + error polling
│   ├── handlers/            # Command handlers
│   └── services/            # Business logic (OpenAI, digest)
├── n8n/                     # n8n workflow JSONs (DB + AI only, no Telegram)
│   ├── parsing_and_filter.json
│   ├── cleanup.json
│   └── error_logger.json
├── parser/                  # Python parser (called by n8n)
│   ├── core.py
│   ├── run.py
│   └── requirements.txt
├── postgres/                # Database schema
│   ├── init.sql
│   ├── 001_news.sql
│   ├── 002_styles.sql
│   ├── 003_channels.sql
│   ├── 004_interests.sql
│   ├── 005_settings.sql
│   ├── 006_user_state.sql
│   └── 007_errors.sql
├── .env.example
└── .gitignore
```

## Setup

### 1. Database

Run SQL scripts on your PostgreSQL server:

```bash
psql -U your_user -d your_db -f postgres/init.sql
```

### 2. Parser

```bash
cd parser
pip install -r requirements.txt
```

Authorize the userbot (one-time):

```bash
python parser/run.py --auth
```

### 3. Bot

```bash
cd bot
pip install -r requirements.txt
```

Create `.env` in the project root (see `.env.example`):

```env
TG_BOT_TOKEN=your_bot_token
TG_CHAT_ID=your_chat_id
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
OPENAI_API_KEY=your_key
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+79991234567
DATA_DIR=./data
```

Run the bot:

```bash
python -m bot.main
```

### 4. n8n

1. Import all JSON files from `n8n/` into your n8n instance
2. Configure credentials in n8n:
   - **OpenAI API** — your API key
   - **PostgreSQL** — host, port, database, user, password
3. Update the parser path in `parsing_and_filter.json` Code node (`cd /path/to/tg-news-researcher`)
4. Set `error_logger.json` as the Error Workflow for all other workflows in n8n Settings
5. Activate the workflows

## Bot commands

- `/start` — welcome and help
- `/set_channels` — manage channels for parsing
- `/set_interests` — manage interests for filtering
- `/set_style` — manage style examples (your posts)
- `/set_digest_time` — set digest delivery time (MSK)
- `/generate_post` — generate a post from digest news in your style
- `/cancel` — cancel current action

## License

MIT
