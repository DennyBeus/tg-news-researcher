# Telegram News Researcher

[English](README.md) | [Русский](README.ru.md)

Система для сбора ежедневных дайджестов новостей из Telegram-каналов на базе Python Telegram-бота, n8n workflows и парсера каналов.

## Как это работает

1. **Парсинг** — Python userbot читает посты из настроенных Telegram-каналов (фоновая задача n8n)
2. **Фильтрация** — OpenAI отбирает посты по вашим интересам (n8n)
3. **Дайджест** — ежедневная сводка отправляется через Telegram-бота в настроенное время (бот)
4. **Генерация поста** — выберите новости из дайджеста и получите пост в вашем стиле (бот)

## Архитектура

- **bot/** — Python Telegram-бот (aiogram 3.x). Обрабатывает всё взаимодействие с пользователем, отправку дайджестов, уведомления об ошибках. Работает напрямую с PostgreSQL и OpenAI API
- **n8n/** — фоновый data pipeline. Парсинг + фильтрация, очистка БД, логирование ошибок в БД. Без Telegram-нод
- **parser/** — Python-парсер Telegram-каналов (kurigram). Вызывается из n8n через Execute Command
- **postgres/** — SQL-скрипты для схемы базы данных

## Стек технологий

- **Telegram-бот**: Python 3.10+, aiogram 3.x, asyncpg, openai SDK, APScheduler
- **n8n** (self-hosted) — оркестрация фоновых задач
- **Python-парсер**: [kurigram](https://github.com/KurimuzonAkuma/kurigram) (Pyrogram-совместимый)
- **OpenAI API** (gpt-4o) — фильтрация (n8n), суммаризация и генерация (бот)
- **PostgreSQL** — новости, каналы, интересы, стили, настройки, ошибки

## Структура проекта

```
tg-news-researcher/
├── bot/                     # Telegram-бот (Python, aiogram 3.x)
│   ├── main.py              # Точка входа
│   ├── config.py            # Конфигурация из .env
│   ├── db.py                # Пул подключений PostgreSQL (asyncpg)
│   ├── scheduler.py         # APScheduler: дайджест + опрос ошибок
│   ├── handlers/            # Обработчики команд
│   └── services/            # Бизнес-логика (OpenAI, дайджест)
├── n8n/                     # n8n workflow JSON (только БД + AI, без Telegram)
│   ├── parsing_and_filter.json
│   ├── cleanup.json
│   └── error_logger.json
├── parser/                  # Python-парсер (вызывается из n8n)
│   ├── core.py
│   ├── run.py
│   └── requirements.txt
├── postgres/                # Схема базы данных
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

## Установка

### 1. База данных

Выполните SQL-скрипты на вашем PostgreSQL сервере:

```bash
psql -U your_user -d your_db -f postgres/init.sql
```

### 2. Парсер

```bash
cd parser
pip install -r requirements.txt
```

Авторизуйте userbot (один раз):

```bash
python parser/run.py --auth
```

### 3. Бот

```bash
cd bot
pip install -r requirements.txt
```

Создайте `.env` в корне проекта (см. `.env.example`):

```env
TG_BOT_TOKEN=токен_бота
TG_CHAT_ID=id_чата
DB_HOST=localhost
DB_PORT=5432
DB_NAME=имя_бд
DB_USER=пользователь
DB_PASSWORD=пароль
OPENAI_API_KEY=ключ
API_ID=ваш_api_id
API_HASH=ваш_api_hash
PHONE_NUMBER=+79991234567
DATA_DIR=./data
```

Запуск бота:

```bash
python -m bot.main
```

### 4. n8n

1. Импортируйте все JSON файлы из `n8n/` в ваш n8n
2. Настройте credentials в n8n:
   - **OpenAI API** — API ключ
   - **PostgreSQL** — хост, порт, БД, пользователь, пароль
3. Обновите путь к парсеру в `parsing_and_filter.json` Code-ноде (`cd /path/to/tg-news-researcher`)
4. Назначьте `error_logger.json` как Error Workflow для всех рабочих воркфлоу в настройках n8n
5. Активируйте воркфлоу

## Команды бота

- `/start` — приветствие и справка
- `/set_channels` — управление каналами для парсинга
- `/set_interests` — управление интересами для фильтрации
- `/set_style` — управление примерами стиля (ваши посты)
- `/set_digest_time` — время отправки дайджеста (МСК)
- `/generate_post` — генерация поста из новостей дайджеста в вашем стиле
- `/cancel` — отмена текущего действия

## Лицензия

MIT
