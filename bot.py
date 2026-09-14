"""Запуск Telegram-бота для совместного ведения домашних дел.

Модуль создаёт подключение к Telegram через SOCKS5-прокси, готовит
базу данных, подключает пользовательские и административные
обработчики и запускает получение обновлений.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from config import (
    BOT_TOKEN,
    PROXY_URL,
)
from database import initialize_database
from handlers.admin import router as admin_router
from handlers.user import router as user_router


# =============================================================================
# Логирование
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)


# =============================================================================
# Обработка устаревших нажатий
# =============================================================================

class IgnoreOldQueryMiddleware(BaseMiddleware):
    """Игнорирует кнопки, срок действия которых истёк.

    Telegram отклоняет ответ на callback, если пользователь нажал
    слишком старую кнопку. Такая ошибка не должна останавливать
    обработку следующих обновлений.
    """

    async def __call__(
        self,
        handler: Callable[
            [Any, dict[str, Any]],
            Awaitable[Any],
        ],
        event: Any,
        data: dict[str, Any],
    ) -> Any:
        """Запускает обработчик и перехватывает старый callback.

        Args:
            handler: Следующий обработчик в цепочке.
            event: Полученное событие Telegram.
            data: Данные зависимостей aiogram.

        Returns:
            Результат следующего обработчика или ``None`` для
            устаревшего callback.
        """
        try:
            return await handler(
                event,
                data,
            )

        except TelegramBadRequest as error:
            if "query is too old" in str(error):
                logger.debug(
                    "Проигнорирован устаревший callback"
                )
                return None

            raise


# =============================================================================
# Создание приложения
# =============================================================================

def create_dispatcher() -> Dispatcher:
    """Создаёт диспетчер и подключает обработчики.

    Returns:
        Настроенный диспетчер aiogram.
    """
    dispatcher = Dispatcher()

    dispatcher.callback_query.middleware(
        IgnoreOldQueryMiddleware()
    )

    # Административный роутер подключается первым, чтобы его
    # специальные действия проверялись раньше пользовательских.
    dispatcher.include_router(
        admin_router,
    )
    dispatcher.include_router(
        user_router,
    )

    return dispatcher


def create_bot() -> Bot:
    """Создаёт Telegram-бота с подключением через прокси.

    Returns:
        Настроенный экземпляр Telegram-бота.
    """
    session = AiohttpSession(
        proxy=PROXY_URL,
    )

    return Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )


# =============================================================================
# Запуск
# =============================================================================

async def main() -> None:
    """Подготавливает базу и запускает получение обновлений."""
    initialize_database()

    bot = create_bot()
    dispatcher = create_dispatcher()

    logger.info(
        "Бот запускается..."
    )

    await dispatcher.start_polling(
        bot,
    )


if __name__ == "__main__":
    try:
        asyncio.run(
            main()
        )
    except KeyboardInterrupt:
        logger.info(
            "Бот остановлен пользователем"
        )