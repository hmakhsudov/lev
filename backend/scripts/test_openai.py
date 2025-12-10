"""
Utility script to quickly verify OpenAI API connectivity.

Usage:
    source ../.venv/bin/activate  # (если используете виртуальное окружение)
    export OPENAI_API_KEY=sk-...  # или заполните в .env и загрузите через dotenv
    python backend/scripts/test_openai.py
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

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY не найден. Укажите ключ в .env или переменной окружения.")
        return 1

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a health-check probe."},
            {"role": "user", "content": "Ответь коротко: работает ли соединение?"},
        ],
        "temperature": 0,
        "max_tokens": 16,
    }

    print("➡️  Отправляем тестовый запрос к OpenAI...")
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
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
    print("❌ OpenAI вернул ошибку:")
    print(indent(pretty, "    "))
    return 1


if __name__ == "__main__":
    sys.exit(main())

