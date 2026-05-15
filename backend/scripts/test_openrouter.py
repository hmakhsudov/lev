"""
Utility script to quickly verify OpenRouter API connectivity.

Usage:
    source ../.venv/bin/activate  # (если используете виртуальное окружение)
    export OPENROUTER_TOKEN=sk-or-...  # или заполните в .env
    python backend/scripts/test_openrouter.py
"""

from __future__ import annotations

import json
import os
import sys
from textwrap import indent

import requests
from dotenv import load_dotenv


def main() -> int:
    # Пытаемся подхватить переменные из .env рядом с проектом
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(project_root, ".env"))

    api_key = os.getenv("OPENROUTER_TOKEN") or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_TOKEN не найден. Укажите токен в .env или переменной окружения.")
        return 1
    api_url = (os.getenv("OPENROUTER_API") or "https://openrouter.ai/api/v1/chat/completions").rstrip("/")
    if not api_url.endswith("/chat/completions"):
        api_url = f"{api_url}/chat/completions"
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    timeout = int(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "30"))

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a health-check probe."},
            {"role": "user", "content": "Ответь коротко: работает ли соединение?"},
        ],
        "temperature": 0,
        "max_tokens": 16,
    }

    print("➡️  Отправляем тестовый запрос к OpenRouter...")
    try:
        response = requests.post(
            api_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        print(f"❌ Сетевая ошибка: {exc}")
        return 1

    print(f"⬅️  HTTP {response.status_code}")
    if response.ok:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        print("✅ Соединение установлено. Ответ модели:")
        print(indent(content, "    "))
        return 0

    try:
        error_payload = response.json()
        pretty = json.dumps(error_payload, ensure_ascii=False, indent=2)
    except ValueError:
        pretty = response.text
    print("❌ OpenRouter вернул ошибку:")
    print(indent(pretty, "    "))
    return 1


if __name__ == "__main__":
    sys.exit(main())
