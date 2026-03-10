import json
import logging
from typing import Any

from openai import AsyncOpenAI

from bot.config import config

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=config.openai_api_key)

SUMMARIZE_PROMPT = (
    "Ты — редактор новостного дайджеста. Тебе дан массив новостных постов.\n\n"
    "Задача: для каждого поста напиши краткое описание в 2-3 предложения. "
    "Сохрани ключевую суть и факты, убери воду и рекламу.\n\n"
    "Посты:\n{posts}\n\n"
    "Верни JSON-массив объектов с полями: \"id\", \"summary\", \"link\", \"source_channel\". "
    "Не добавляй пояснений, только JSON."
)

FILTER_PROMPT = (
    "Ты — фильтр новостей. Тебе дан список интересов пользователя и массив постов из Telegram-каналов.\n\n"
    "Задача: отобрать только те посты, которые соответствуют хотя бы одному интересу. "
    "Соответствие определяй по смыслу, а не по точному совпадению слов.\n\n"
    "Интересы:\n{interests}\n\n"
    "Посты:\n{posts}\n\n"
    "Верни JSON-массив подходящих постов. Каждый объект — точная копия исходного поста без изменений. "
    "Если ни один пост не подходит — верни пустой массив []. Не добавляй пояснений, только JSON."
)

GENERATE_PROMPT = (
    "Ты — копирайтер. Тебе даны тексты новостей и примеры постов пользователя (его стиль).\n\n"
    "Задача: напиши один пост на основе предоставленных новостей в стиле пользователя. "
    "Сохрани его манеру изложения, структуру и тон. Пост должен быть цельным и информативным.\n\n"
    "Новости:\n{news}\n\n"
    "Примеры стиля:\n{styles}\n\n"
    "Верни только текст готового поста, без пояснений."
)


async def summarize_news(posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prompt = SUMMARIZE_PROMPT.format(posts=json.dumps(posts, ensure_ascii=False))
    response = await client.chat.completions.create(
        model=config.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or ""
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        for key in ("items", "posts", "results"):
            if key in parsed:
                return parsed[key]
        return []
    except json.JSONDecodeError:
        logger.error("Failed to parse OpenAI summarization response: %s", raw[:200])
        return []


async def filter_by_interests(
    posts: list[dict[str, Any]],
    interests: list[str],
) -> list[dict[str, Any]]:
    prompt = FILTER_PROMPT.format(
        interests=json.dumps(interests, ensure_ascii=False),
        posts=json.dumps(posts, ensure_ascii=False),
    )
    response = await client.chat.completions.create(
        model=config.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or ""
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        for key in ("posts", "results", "items"):
            if key in parsed and isinstance(parsed[key], list):
                return parsed[key]
        return []
    except json.JSONDecodeError:
        logger.error("Failed to parse OpenAI filter response: %s", raw[:200])
        return []


async def generate_post_text(
    news: list[dict[str, Any]],
    styles: list[str],
) -> str:
    prompt = GENERATE_PROMPT.format(
        news=json.dumps(news, ensure_ascii=False),
        styles=json.dumps(styles, ensure_ascii=False),
    )
    response = await client.chat.completions.create(
        model=config.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content or "Не удалось сгенерировать пост."
