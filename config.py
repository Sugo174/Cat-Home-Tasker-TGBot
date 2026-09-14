"""Конфигурация Telegram-бота.

Модуль загружает переменные окружения из файла ``.env`` и хранит
основные пути проекта. Остальные модули импортируют готовые настройки
отсюда и не работают с ``os.getenv()`` напрямую.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# =============================================================================
# Пути проекта
# =============================================================================

# __file__ — путь к текущему файлу config.py.
# resolve().parent получает абсолютный путь к папке проекта.
BASE_DIR = Path(__file__).resolve().parent

ENV_PATH = BASE_DIR / ".env"
DB_PATH = BASE_DIR / "household.db"


# =============================================================================
# Загрузка переменных окружения
# =============================================================================

load_dotenv(ENV_PATH)


def get_required_environment_variable(name: str) -> str:
    """Возвращает обязательную переменную окружения.

    Args:
        name: Название переменной в файле ``.env``.

    Returns:
        Значение найденной переменной.

    Raises:
        RuntimeError: Если переменная отсутствует или имеет пустое
            значение.
    """
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Переменная {name} не найдена в файле .env"
        )

    return value


# =============================================================================
# Настройки приложения
# =============================================================================

BOT_TOKEN = get_required_environment_variable(
    "BOT_TOKEN"
)

ADMIN_PASSWORD = get_required_environment_variable(
    "ADMIN_PASSWORD"
)

PROXY_URL = get_required_environment_variable(
    "PROXY_URL"
)
