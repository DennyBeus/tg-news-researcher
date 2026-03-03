# Telegram News Researcher

[English](README.md) | [Русский](README.ru.md)

Система для сбора ежедневных дайджестов новостей из Telegram-каналов на базе n8n workflows и Python-парсера.

## Как это работает

1. **Парсинг** — Python userbot читает посты из настроенных Telegram-каналов
2. **Фильтрация** — OpenAI отбирает посты по вашим интересам
3. **Дайджест** — ежедневная сводка отправляется через Telegram-бота в настроенное время
4. **Генерация поста** — выберите новости из дайджеста и получите пост в вашем стиле

## Стек технологий

- **n8n** (self-hosted) — оркестрация, Telegram-бот, AI-вызовы, работа с БД
- **Python 3.10+** — парсер Telegram-каналов ([kurigram](https://github.com/KurimuzonAkuma/kurigram))
- **OpenAI API** (gpt-4o) — фильтрация, суммаризация, генерация постов
- **PostgreSQL** — хранение новостей, каналов, интересов, стилей, настроек

## Структура проекта

```
tg-news-researcher/
├── parser/                  # Python-парсер (единственный не-n8n компонент)
│   ├── core.py              # Логика парсинга
│   ├── run.py               # CLI точка входа для n8n Execute Command
│   └── requirements.txt
├── n8n/                     # JSON воркфлоу для импорта в n8n
│   ├── bot.json             # Telegram-бот (команды, inline-кнопки, state)
│   ├── parsing_and_filter.json
│   ├── digest.json
│   ├── cleanup.json
│   └── error.json
├── sql/                     # Схема базы данных
│   ├── init.sql
│   ├── 001_news.sql
│   ├── 002_styles.sql
│   ├── 003_channels.sql
│   ├── 004_interests.sql
│   ├── 005_settings.sql
│   └── 006_user_state.sql
├── .env                     # Секреты парсера (не в git)
└── .gitignore
```

## Установка

### 1. База данных

Выполните SQL-скрипты на вашем PostgreSQL сервере:

```bash
psql -U your_user -d your_db -f sql/init.sql
```

### 2. Парсер

```bash
cd parser
pip install -r requirements.txt
```

Создайте `.env` в корне проекта:

```env
API_ID=your_api_id
API_HASH=your_api_hash
PHONE_NUMBER=+79991234567
DATA_DIR=./data
```

Авторизуйте userbot (один раз):

```bash
python parser/run.py --auth
```

### 3. n8n

1. Импортируйте все JSON файлы из `n8n/` в ваш n8n
2. Настройте credentials в n8n:
   - **Telegram Bot API** — токен бота
   - **OpenAI API** — API ключ
   - **PostgreSQL** — хост, порт, БД, пользователь, пароль
3. Установите переменную окружения n8n `TELEGRAM_BOT_TOKEN` (для динамических клавиатур)
4. Обновите путь к парсеру в `parsing_and_filter.json` Code-ноде (`cd /path/to/tg-news-researcher`)
5. Назначьте `error.json` как Error Workflow для всех рабочих воркфлоу в настройках n8n
6. Активируйте воркфлоу

## Команды бота

- `/start` — приветствие и справка
- `/set_channels` — управление каналами для парсинга
- `/set_interests` — управление интересами для фильтрации
- `/set_style` — управление примерами стиля (ваши посты)
- `/set_digest_time` — время отправки дайджеста (МСК)
- `/generate_post` — генерация поста из новостей дайджеста в вашем стиле

## Лицензия

MIT
