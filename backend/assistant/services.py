import ast
import json
import logging
from typing import Any, Dict

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Ты — помощник риелтора. Отвечай строго JSON без комментариев."
    " Формат:"
    " {"
    '  "summary": "<краткий вывод на русском>",'
    '  "filters": {'
    '     "rooms": <int|null>,'
    '     "price_max": <int|null>,'
    '     "area_min": <number|null>,'
    '     "area_max": <number|null>,'
    '     "district": "<строка|null>",'
    '     "city": "<строка|null>",'
    '     "property_type": "<apartment|room|house|commercial|null>"'
    "  }"
    " }."
    " Если данных нет — ставь null. Не добавляй текст вне JSON."
)


class AssistantClientError(Exception):
    pass


def parse_query_with_openrouter(query: str) -> Dict[str, Any]:
    api_key = settings.OPENROUTER_TOKEN
    if not api_key:
        raise AssistantClientError("OPENROUTER_TOKEN is not configured")

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        "temperature": 0.2,
    }
    try:
        response = requests.post(
            _chat_completions_url(settings.OPENROUTER_API),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=settings.OPENROUTER_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        logger.exception(
            "OpenRouter returned HTTP %s: %s",
            exc.response.status_code if exc.response else "unknown",
            exc.response.text if exc.response else "no body",
        )
        raise AssistantClientError("OpenRouter request failed") from exc
    except requests.RequestException as exc:
        logger.exception("OpenRouter network error: %s", exc)
        raise AssistantClientError("OpenRouter request failed") from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.exception("Failed to decode OpenRouter JSON: %s", response.text)
        raise AssistantClientError("Invalid OpenRouter response") from exc

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        logger.exception("Unexpected OpenRouter payload: %s", data)
        raise AssistantClientError("Invalid OpenRouter response") from exc
    cleaned_content = content.strip()
    if cleaned_content.startswith("```"):
        lines = cleaned_content.splitlines()
        # удаляем открывающий и закрывающий маркеры ``` или ```json
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned_content = "\n".join(lines).strip()

    for parser in (_parse_json, _parse_literal):
        parsed = parser(cleaned_content)
        if parsed is not None:
            return parsed

    logger.exception("OpenRouter returned non-JSON content: %s", content)
    raise AssistantClientError("Invalid JSON from OpenRouter")


# Старое имя оставлено как совместимость для импортов в коде/тестах.
parse_query_with_openai = parse_query_with_openrouter


def _chat_completions_url(api_url: str) -> str:
    normalized = (api_url or "").rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"


def _parse_json(payload: str) -> Dict[str, Any] | None:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None


def _parse_literal(payload: str) -> Dict[str, Any] | None:
    try:
        result = ast.literal_eval(payload)
    except (ValueError, SyntaxError):
        return None
    if isinstance(result, dict):
        return result
    return None
