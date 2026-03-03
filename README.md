# Telegram News Researcher

[English](README.md) | [Русский](README.ru.md)

A system for collecting daily news digests from Telegram channels, powered by n8n workflows and a Python parser.

## How it works

1. **Parsing** — a Python userbot reads posts from configured Telegram channels
2. **Filtering** — OpenAI filters posts by your interests
3. **Digest** — daily summary sent via Telegram bot at a configured time
4. **Post generation** — select news from the digest and generate a post in your writing style

## Tech stack

- **n8n** (self-hosted) — orchestration, Telegram bot, AI calls, database queries
- **Python 3.10+** — Telegram channel parser ([kurigram](https://github.com/KurimuzonAkuma/kurigram))
- **OpenAI API** (gpt-4o) — filtering, summarization, post generation
- **PostgreSQL** — storage for news, channels, interests, styles, settings

## Project structure

```
tg-news-researcher/
├── parser/                  # Python parser (only non-n8n component)
│   ├── core.py              # Parsing logic
│   ├── run.py               # CLI entry point for n8n Execute Command
│   └── requirements.txt
├── n8n/                     # n8n workflow JSONs (import into n8n)
│   ├── bot.json             # Telegram bot (commands, inline buttons, state)
│   ├── parsing_and_filter.json
│   ├── digest.json
│   ├── cleanup.json
│   └── error.json
├── sql/                     # Database schema
│   ├── init.sql
│   ├── 001_news.sql
│   ├── 002_styles.sql
│   ├── 003_channels.sql
│   ├── 004_interests.sql
│   ├── 005_settings.sql
│   └── 006_user_state.sql
├── .env                     # Parser secrets (not in git)
└── .gitignore
```

## Setup

### 1. Database

Run SQL scripts on your PostgreSQL server:

```bash
psql -U your_user -d your_db -f sql/init.sql
```

### 2. Parser

```bash
cd parser
pip install -r requirements.txt
```

Create `.env` in the project root:

```env
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+79991234567
DATA_DIR=./data
```

Authorize the userbot (one-time):

```bash
python parser/run.py --auth
```

### 3. n8n

1. Import all JSON files from `n8n/` into your n8n instance
2. Configure credentials in n8n:
   - **Telegram Bot API** — your bot token
   - **OpenAI API** — your API key
   - **PostgreSQL** — host, port, database, user, password
3. Set n8n environment variable `TELEGRAM_BOT_TOKEN` (used for dynamic keyboard messages)
4. Update the parser path in `parsing_and_filter.json` Code node (`cd /path/to/tg-news-researcher`)
5. Set `error.json` as the Error Workflow for all other workflows in n8n Settings
6. Activate the workflows

## Bot commands

- `/start` — welcome and help
- `/set_channels` — manage channels for parsing
- `/set_interests` — manage interests for filtering
- `/set_style` — manage style examples (your posts)
- `/set_digest_time` — set digest delivery time (MSK)
- `/generate_post` — generate a post from digest news in your style

## License

MIT
