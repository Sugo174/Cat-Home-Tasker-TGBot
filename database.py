"""Работа с базой данных Telegram-бота.

Модуль содержит подключение к SQLite, миграции существующей базы,
работу с языком пользователя и генерацию кодов приглашения.

SQL-запросы отдельных экранов пока остаются в обработчиках. Позже
мы перенесём их сюда небольшими тематическими функциями.
"""

import logging
import secrets
import sqlite3
import string
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from contextlib import contextmanager
from collections.abc import Iterator
from config import DB_PATH
from localization import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
)


# =============================================================================
# Модели данных
# =============================================================================

@dataclass(
    frozen=True,
    slots=True,
)
class UserProfile:
    """Данные профиля пользователя.

    Attributes:
        name: Отображаемое имя.
        gender: Сохранённый пол пользователя.
        xp: Общее количество заработанного опыта.
    """

    name: str
    gender: str
    xp: int


@dataclass(
    frozen=True,
    slots=True,
)
class HouseMember:
    """Участник домашней группы.

    Attributes:
        user_id: Telegram ID участника.
        name: Отображаемое имя.
        xp: Общее количество опыта.
    """

    user_id: int
    name: str
    xp: int

    
@dataclass(
    frozen=True,
    slots=True,
)
class ActiveTask:
    """Активная задача домашней группы.

    Attributes:
        task_id: Идентификатор активной задачи.
        template_id: Идентификатор стандартного шаблона. Для
            пользовательской задачи содержит ``None``.
        name: Название стандартной или пользовательской задачи.
        xp: Награда за выполнение.
        assigned_by_name: Имя пользователя, добавившего задачу.
    """

    task_id: int
    template_id: int | None
    name: str
    xp: int
    assigned_by_name: str


@dataclass(
    frozen=True,
    slots=True,
)
class CompletedTaskResult:
    """Результат выполнения задачи.

    Attributes:
        name: Название выполненной задачи.
        xp: Количество начисленного опыта.
        is_standard: Показывает, была ли задача стандартной.
    """

    name: str
    xp: int
    is_standard: bool


@dataclass(
    frozen=True,
    slots=True,
)
class TaskTemplate:
    """Шаблон стандартной задачи.

    Attributes:
        template_id: Идентификатор шаблона.
        name: Внутреннее русское название задачи.
        xp: Награда за выполнение.
    """

    template_id: int
    name: str
    xp: int


@dataclass(
    frozen=True,
    slots=True,
)
class CompletedTaskEntry:
    """Запись истории выполненных задач.

    Attributes:
        completed_at: Дата и время выполнения.
        template_name: Название стандартной задачи или ``None``.
        custom_name: Название пользовательской задачи или ``None``.
        xp: Начисленный опыт.
        executor_name: Имя выполнившего задачу пользователя.
    """

    completed_at: datetime
    template_name: str | None
    custom_name: str | None
    xp: int
    executor_name: str


@dataclass(
    frozen=True,
    slots=True,
)
class ChangelogEntry:
    """Запись журнала обновлений.

    Attributes:
        entry_id: Идентификатор записи.
        message_ru: Русская версия текста.
        message_en: Английская версия или ``None``.
    """

    entry_id: int
    message_ru: str
    message_en: str | None


@dataclass(
    frozen=True,
    slots=True,
)
class AdminHouse:
    """Домашняя группа для административной панели.

    Attributes:
        house_id: Идентификатор домашней группы.
        invite_code: Код приглашения.
        member_count: Количество участников.
    """

    house_id: int
    invite_code: str
    member_count: int


@dataclass(
    frozen=True,
    slots=True,
)
class AdminHouseMember:
    """Участник дома для административной панели.

    Attributes:
        user_id: Telegram ID пользователя.
        name: Отображаемое имя.
        xp: Общее количество опыта.
    """

    user_id: int
    name: str
    xp: int


@dataclass(
    frozen=True,
    slots=True,
)
class AdminUser:
    """Пользователь для административной панели.

    Attributes:
        user_id: Telegram ID пользователя.
        name: Отображаемое имя.
        xp: Текущее количество опыта.
        house_id: Идентификатор домашней группы.
    """

    user_id: int
    name: str
    xp: int
    house_id: int


# =============================================================================
# Подключение к SQLite
# =============================================================================

@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Открывает управляемое соединение с SQLite.

    При успешном завершении выполняется ``commit()``. Если возникает
    ошибка, изменения откатываются. В любом случае соединение
    закрывается.

    Yields:
        Настроенное соединение SQLite.
    """
    connection = sqlite3.connect(DB_PATH)

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def table_exists(
    connection: sqlite3.Connection,
    table_name: str,
) -> bool:
    """Проверяет существование таблицы.

    Args:
        connection: Открытое соединение SQLite.
        table_name: Название проверяемой таблицы.

    Returns:
        ``True``, если таблица существует.
    """
    row = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (table_name,),
    ).fetchone()

    return row is not None


def get_table_columns(
    connection: sqlite3.Connection,
    table_name: str,
) -> set[str]:
    """Возвращает названия столбцов таблицы.

    Имя таблицы не принимается от пользователя. Функция вызывается
    только с названиями, заданными внутри приложения.

    Args:
        connection: Открытое соединение SQLite.
        table_name: Название таблицы.

    Returns:
        Множество названий столбцов.
    """
    rows = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return {
        row[1]
        for row in rows
    }


# =============================================================================
# Первоначальная настройка базы данных
# =============================================================================

def initialize_database() -> None:
    """Создаёт таблицы и добавляет стандартные задачи.

    SQL-схема загружается из файла ``schema.sql``, расположенного
    рядом с этим модулем. Команды ``CREATE TABLE IF NOT EXISTS`` и
    ``INSERT OR IGNORE`` позволяют безопасно вызывать функцию при
    каждом запуске бота.

    Raises:
        FileNotFoundError: Если файл ``schema.sql`` отсутствует.
    """
    schema_path = Path(__file__).with_name("schema.sql")

    if not schema_path.exists():
        raise FileNotFoundError(
            f"Файл схемы базы данных не найден: {schema_path}"
        )

    schema = schema_path.read_text(
        encoding="utf-8",
    )

    with get_connection() as connection:
        connection.executescript(schema)

    # Обновляем структуру базы, созданной старой версией бота.
    run_migrations()

    logging.info(
        "База данных подготовлена к работе"
    )


# =============================================================================
# Миграции существующей базы
# =============================================================================

def ensure_language_column() -> None:
    """Добавляет язык в существующую таблицу пользователей.

    Новые и существующие пользователи получают русский язык по
    умолчанию. Если столбец уже существует, функция ничего не меняет.
    """
    with get_connection() as connection:
        if not table_exists(connection, "users"):
            logging.warning(
                "Таблица users отсутствует: миграция языка пропущена"
            )
            return

        columns = get_table_columns(
            connection,
            "users",
        )

        if "language" in columns:
            return

        connection.execute(
            """
            ALTER TABLE users
            ADD COLUMN language TEXT NOT NULL DEFAULT 'ru'
            CHECK(language IN ('ru', 'en'))
            """
        )

        logging.info(
            "В таблицу users добавлен столбец language"
        )


def ensure_changelog_table() -> None:
    """Создаёт таблицу журнала, если она отсутствует.

    Поле ``message`` пока сохраняется для совместимости со старой
    версией приложения. Новые обработчики используют поля
    ``message_ru`` и ``message_en``.
    """
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS changelog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL DEFAULT '',
                message_ru TEXT,
                message_en TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def ensure_changelog_language_columns() -> None:
    """Добавляет русскую и английскую версии записей журнала.

    Старые записи переносятся в ``message_ru``. Английский текст
    остаётся пустым до ручного перевода через административную панель.
    """
    ensure_changelog_table()

    with get_connection() as connection:
        columns = get_table_columns(
            connection,
            "changelog",
        )

        if "message_ru" not in columns:
            connection.execute(
                """
                ALTER TABLE changelog
                ADD COLUMN message_ru TEXT
                """
            )

            # Старые записи журнала считаем русскими.
            if "message" in columns:
                connection.execute(
                    """
                    UPDATE changelog
                    SET message_ru = message
                    WHERE message_ru IS NULL
                    """
                )

            logging.info(
                "В таблицу changelog добавлен столбец message_ru"
            )

        if "message_en" not in columns:
            connection.execute(
                """
                ALTER TABLE changelog
                ADD COLUMN message_en TEXT
                """
            )

            logging.info(
                "В таблицу changelog добавлен столбец message_en"
            )


def run_migrations() -> None:
    """Запускает все безопасные миграции базы данных."""
    ensure_language_column()
    ensure_changelog_language_columns()


# =============================================================================
# Профиль пользователя
# =============================================================================

def get_user_profile(
    user_id: int,
) -> UserProfile | None:
    """Загружает данные профиля пользователя.

    Args:
        user_id: Telegram ID пользователя.

    Returns:
        Объект профиля. Если пользователь не найден, возвращается
        ``None``.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                name,
                gender,
                xp
            FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return UserProfile(
        name=str(row[0]),
        gender=str(row[1]),
        xp=int(row[2]),
    )


def update_user_name(
    user_id: int,
    new_name: str,
) -> bool:
    """Изменяет имя пользователя.

    Args:
        user_id: Telegram ID пользователя.
        new_name: Новое отображаемое имя.

    Returns:
        ``True``, если пользователь найден и обновлён.
    """
    normalized_name = new_name.strip()

    if len(normalized_name) < 2:
        return False

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE users
            SET name = ?
            WHERE tg_id = ?
            """,
            (
                normalized_name,
                user_id,
            ),
        )

        return cursor.rowcount > 0


def update_user_gender(
    user_id: int,
    gender: str,
) -> bool:
    """Изменяет пол пользователя.

    Args:
        user_id: Telegram ID пользователя.
        gender: Новое значение: ``male`` или ``female``.

    Returns:
        ``True``, если пользователь найден и обновлён.
    """
    if gender not in {"male", "female"}:
        return False

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE users
            SET gender = ?
            WHERE tg_id = ?
            """,
            (
                gender,
                user_id,
            ),
        )

        return cursor.rowcount > 0


# =============================================================================
# Язык пользователя
# =============================================================================

def get_user_language(user_id: int) -> str:
    """Возвращает выбранный пользователем язык.

    Args:
        user_id: Telegram ID пользователя.

    Returns:
        Код ``ru`` или ``en``. Если пользователь не найден или язык
        имеет неизвестное значение, возвращается русский.
    """
    with get_connection() as connection:
        if not table_exists(connection, "users"):
            return DEFAULT_LANGUAGE

        row = connection.execute(
            """
            SELECT language
            FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        ).fetchone()

    if row and row[0] in SUPPORTED_LANGUAGES:
        return row[0]

    return DEFAULT_LANGUAGE


def set_user_language(
    user_id: int,
    language: str,
) -> bool:
    """Сохраняет выбранный язык пользователя.

    Args:
        user_id: Telegram ID пользователя.
        language: Новый код языка.

    Returns:
        ``True``, если пользователь найден и обновлён. Для неизвестного
        пользователя или неподдерживаемого языка возвращается
        ``False``.
    """
    if language not in SUPPORTED_LANGUAGES:
        return False

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE users
            SET language = ?
            WHERE tg_id = ?
            """,
            (language, user_id),
        )

        return cursor.rowcount > 0


# =============================================================================
# Коды приглашения
# =============================================================================

def generate_invite_code(length: int = 6) -> str:
    """Генерирует случайный код приглашения.

    Для кода используются латинские заглавные буквы и цифры.
    Проверка уникальности выполняется отдельно при создании дома.

    Args:
        length: Требуемая длина кода.

    Returns:
        Строка вида ``A1B2C3``.

    Raises:
        ValueError: Если передана неположительная длина.
    """
    if length <= 0:
        raise ValueError(
            "Длина кода должна быть положительным числом"
        )

    alphabet = (
        string.ascii_uppercase
        + string.digits
    )

    return "".join(
        secrets.choice(alphabet)
        for _ in range(length)
    )


# =============================================================================
# Регистрация пользователя
# =============================================================================

def create_house_with_user(
    user_id: int,
    name: str,
    gender: str,
    language: str,
) -> str:
    """Создаёт домашнюю группу и добавляет в неё пользователя.

    Код приглашения генерируется автоматически. В маловероятном случае
    совпадения с существующим кодом создаётся новый.

    Args:
        user_id: Telegram ID пользователя.
        name: Имя пользователя.
        gender: Пол пользователя: ``male`` или ``female``.
        language: Выбранный язык: ``ru`` или ``en``.

    Returns:
        Новый код приглашения.

    Raises:
        RuntimeError: Если не удалось создать уникальный код.
        sqlite3.IntegrityError: Если данные пользователя некорректны
            или пользователь уже зарегистрирован.
    """
    with get_connection() as connection:
        house_id: int | None = None
        invite_code = ""

        # Обычно достаточно одной попытки. Ограничение защищает
        # функцию от бесконечного цикла.
        for _ in range(100):
            invite_code = generate_invite_code()

            try:
                cursor = connection.execute(
                    """
                    INSERT INTO houses (invite_code)
                    VALUES (?)
                    """,
                    (invite_code,),
                )

                house_id = cursor.lastrowid
                break

            except sqlite3.IntegrityError:
                # Такой код уже существует — генерируем другой.
                continue

        if house_id is None:
            raise RuntimeError(
                "Не удалось создать уникальный код приглашения"
            )

        connection.execute(
            """
            INSERT INTO users (
                tg_id,
                name,
                gender,
                house_id,
                language
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                name,
                gender,
                house_id,
                language,
            ),
        )

    return invite_code


def join_house_by_invite_code(
    user_id: int,
    name: str,
    gender: str,
    language: str,
    invite_code: str,
) -> bool:
    """Добавляет пользователя в дом по коду приглашения.

    Args:
        user_id: Telegram ID пользователя.
        name: Имя пользователя.
        gender: Пол пользователя.
        language: Выбранный язык.
        invite_code: Введённый код домашней группы.

    Returns:
        ``True``, если домашняя группа найдена и пользователь добавлен.
        Если код не существует, возвращается ``False``.

    Raises:
        sqlite3.IntegrityError: Если данные пользователя некорректны
            или пользователь уже зарегистрирован.
    """
    normalized_code = invite_code.strip().upper()

    with get_connection() as connection:
        house = connection.execute(
            """
            SELECT id
            FROM houses
            WHERE invite_code = ?
            """,
            (normalized_code,),
        ).fetchone()

        if house is None:
            return False

        connection.execute(
            """
            INSERT INTO users (
                tg_id,
                name,
                gender,
                house_id,
                language
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                name,
                gender,
                house[0],
                language,
            ),
        )

    return True


# =============================================================================
# Активные задачи
# =============================================================================

def get_task_templates_page(
    page: int = 1,
    page_size: int = 7,
) -> tuple[list[TaskTemplate], int, int]:
    """Возвращает одну страницу стандартных задач.

    Задачи сортируются по XP, а при одинаковой награде — по ID.

    Args:
        page: Запрошенный номер страницы.
        page_size: Количество задач на одной странице.

    Returns:
        Кортеж из списка задач, фактического номера страницы и общего
        количества страниц.

    Raises:
        ValueError: Если размер страницы неположительный.
    """
    if page_size <= 0:
        raise ValueError(
            "Размер страницы должен быть положительным"
        )

    with get_connection() as connection:
        total_tasks = int(
            connection.execute(
                """
                SELECT COUNT(*)
                FROM task_templates
                """
            ).fetchone()[0]
        )

        total_pages = max(
            1,
            (
                total_tasks
                + page_size
                - 1
            )
            // page_size,
        )

        current_page = min(
            max(page, 1),
            total_pages,
        )

        offset = (
            current_page - 1
        ) * page_size

        rows = connection.execute(
            """
            SELECT
                id,
                name,
                xp
            FROM task_templates
            ORDER BY
                xp DESC,
                id
            LIMIT ?
            OFFSET ?
            """,
            (
                page_size,
                offset,
            ),
        ).fetchall()

    templates = [
        TaskTemplate(
            template_id=int(row[0]),
            name=str(row[1]),
            xp=int(row[2]),
        )
        for row in rows
    ]

    return (
        templates,
        current_page,
        total_pages,
    )


def get_task_template(
    template_id: int,
) -> TaskTemplate | None:
    """Возвращает стандартную задачу по её ID.

    Args:
        template_id: Идентификатор шаблона задачи.

    Returns:
        Данные шаблона. Если задача не найдена, возвращается ``None``.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                name,
                xp
            FROM task_templates
            WHERE id = ?
            """,
            (template_id,),
        ).fetchone()

    if row is None:
        return None

    return TaskTemplate(
        template_id=int(row[0]),
        name=str(row[1]),
        xp=int(row[2]),
    )


def add_template_task_to_active(
    user_id: int,
    template_id: int,
) -> TaskTemplate | None:
    """Добавляет стандартную задачу в активный список дома.

    Args:
        user_id: Telegram ID пользователя, добавляющего задачу.
        template_id: Идентификатор стандартного шаблона.

    Returns:
        Добавленный шаблон задачи. Если пользователь, дом или шаблон
        не найдены, возвращается ``None``.
    """
    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT house_id
            FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        ).fetchone()

        if user is None:
            return None

        template = connection.execute(
            """
            SELECT
                id,
                name,
                xp
            FROM task_templates
            WHERE id = ?
            """,
            (template_id,),
        ).fetchone()

        if template is None:
            return None

        connection.execute(
            """
            INSERT INTO active_tasks (
                template_id,
                house_id,
                assigned_by
            )
            VALUES (?, ?, ?)
            """,
            (
                template_id,
                user[0],
                user_id,
            ),
        )

    return TaskTemplate(
        template_id=int(template[0]),
        name=str(template[1]),
        xp=int(template[2]),
    )


def add_custom_task_to_active(
    user_id: int,
    description: str,
    xp: int,
) -> int | None:
    """Добавляет пользовательскую задачу в активный список.

    Args:
        user_id: Telegram ID пользователя, создающего задачу.
        description: Описание пользовательской задачи.
        xp: Награда за выполнение.

    Returns:
        ID созданной активной задачи. Если пользователь или его
        домашняя группа не найдены, возвращается ``None``.

    Raises:
        ValueError: Если описание слишком короткое или XP имеет
            недопустимое значение.
    """
    normalized_description = description.strip()

    if len(normalized_description) < 3:
        raise ValueError(
            "Описание должно содержать не менее трёх символов"
        )

    if xp not in {
        5,
        10,
        15,
        20,
    }:
        raise ValueError(
            "Недопустимое количество XP"
        )

    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT house_id
            FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        ).fetchone()

        if user is None:
            return None

        cursor = connection.execute(
            """
            INSERT INTO active_tasks (
                template_id,
                custom_name,
                custom_xp,
                house_id,
                assigned_by
            )
            VALUES (NULL, ?, ?, ?, ?)
            """,
            (
                normalized_description,
                xp,
                user[0],
                user_id,
            ),
        )

        task_id = cursor.lastrowid

    if task_id is None:
        return None

    return int(task_id)


def update_custom_task_description(
    user_id: int,
    task_id: int,
    description: str,
) -> bool:
    """Изменяет описание пользовательской активной задачи.

    Args:
        user_id: Telegram ID пользователя.
        task_id: Идентификатор активной задачи.
        description: Новое описание.

    Returns:
        ``True``, если пользовательская задача найдена и обновлена.

    Raises:
        ValueError: Если описание слишком короткое.
    """
    normalized_description = description.strip()

    if len(normalized_description) < 3:
        raise ValueError(
            "Описание должно содержать не менее трёх символов"
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE active_tasks
            SET custom_name = ?
            WHERE id = ?
              AND template_id IS NULL
              AND house_id = (
                  SELECT house_id
                  FROM users
                  WHERE tg_id = ?
              )
            """,
            (
                normalized_description,
                task_id,
                user_id,
            ),
        )

        return cursor.rowcount > 0


def update_custom_task_xp(
    user_id: int,
    task_id: int,
    xp: int,
) -> bool:
    """Изменяет XP пользовательской активной задачи.

    Args:
        user_id: Telegram ID пользователя.
        task_id: Идентификатор активной задачи.
        xp: Новая награда.

    Returns:
        ``True``, если пользовательская задача найдена и обновлена.

    Raises:
        ValueError: Если передано недопустимое количество XP.
    """
    if xp not in {
        5,
        10,
        15,
        20,
    }:
        raise ValueError(
            "Недопустимое количество XP"
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE active_tasks
            SET custom_xp = ?
            WHERE id = ?
              AND template_id IS NULL
              AND house_id = (
                  SELECT house_id
                  FROM users
                  WHERE tg_id = ?
              )
            """,
            (
                xp,
                task_id,
                user_id,
            ),
        )

        return cursor.rowcount > 0


def update_custom_task(
    user_id: int,
    task_id: int,
    description: str,
    xp: int,
) -> bool:
    """Сохраняет описание и XP пользовательской задачи.

    Оба поля обновляются одним SQL-запросом, поэтому задача не может
    остаться частично изменённой.

    Args:
        user_id: Telegram ID создателя задачи.
        task_id: Идентификатор активной задачи.
        description: Новое описание.
        xp: Новая награда.

    Returns:
        ``True``, если задача найдена и обновлена.

    Raises:
        ValueError: Если описание или XP имеют неверное значение.
    """
    normalized_description = description.strip()

    if len(normalized_description) < 3:
        raise ValueError(
            "Описание должно содержать не менее трёх символов"
        )

    if xp not in {
        5,
        10,
        15,
        20,
    }:
        raise ValueError(
            "Недопустимое количество XP"
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE active_tasks
            SET
                custom_name = ?,
                custom_xp = ?
            WHERE id = ?
              AND assigned_by = ?
              AND template_id IS NULL
            """,
            (
                normalized_description,
                xp,
                task_id,
                user_id,
            ),
        )

        return cursor.rowcount > 0


def complete_template_task_now(
    user_id: int,
    template_id: int,
    history_limit: int = 50,
) -> CompletedTaskResult | None:
    """Сразу выполняет стандартную задачу.

    Задача записывается в историю, а пользователю начисляется XP.
    Добавление в таблицу активных задач не требуется.

    Args:
        user_id: Telegram ID пользователя.
        template_id: Идентификатор стандартного шаблона.
        history_limit: Максимальное количество записей истории дома.

    Returns:
        Результат выполнения. Если пользователь, дом или шаблон
        не найдены, возвращается ``None``.

    Raises:
        ValueError: Если передан неположительный лимит истории.
    """
    if history_limit <= 0:
        raise ValueError(
            "Лимит истории должен быть положительным"
        )

    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT house_id
            FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        ).fetchone()

        if user is None:
            return None

        template = connection.execute(
            """
            SELECT
                name,
                xp
            FROM task_templates
            WHERE id = ?
            """,
            (template_id,),
        ).fetchone()

        if template is None:
            return None

        house_id = int(user[0])
        task_name = str(template[0])
        task_xp = int(template[1])

        connection.execute(
            """
            INSERT INTO completed_tasks (
                template_id,
                custom_name,
                custom_xp,
                completed_by,
                house_id
            )
            VALUES (?, NULL, NULL, ?, ?)
            """,
            (
                template_id,
                user_id,
                house_id,
            ),
        )

        connection.execute(
            """
            DELETE FROM completed_tasks
            WHERE house_id = ?
              AND id NOT IN (
                  SELECT id
                  FROM completed_tasks
                  WHERE house_id = ?
                  ORDER BY
                      completed_at DESC,
                      id DESC
                  LIMIT ?
              )
            """,
            (
                house_id,
                house_id,
                history_limit,
            ),
        )

        connection.execute(
            """
            UPDATE users
            SET xp = xp + ?
            WHERE tg_id = ?
            """,
            (
                task_xp,
                user_id,
            ),
        )

    return CompletedTaskResult(
        name=task_name,
        xp=task_xp,
        is_standard=True,
    )


def get_active_tasks(
    user_id: int,
) -> list[ActiveTask] | None:
    """Возвращает активные задачи домашней группы пользователя.

    Args:
        user_id: Telegram ID пользователя.

    Returns:
        Список активных задач. Если пользователь не зарегистрирован
        или не состоит в домашней группе, возвращается ``None``.
    """
    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT house_id
            FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        ).fetchone()

        if user is None:
            return None

        rows = connection.execute(
            """
            SELECT
                active_tasks.id,
                active_tasks.template_id,
                COALESCE(
                    task_templates.name,
                    active_tasks.custom_name
                ),
                COALESCE(
                    task_templates.xp,
                    active_tasks.custom_xp
                ),
                users.name
            FROM active_tasks
            LEFT JOIN task_templates
              ON task_templates.id = active_tasks.template_id
            JOIN users
              ON users.tg_id = active_tasks.assigned_by
            WHERE active_tasks.house_id = ?
            ORDER BY
                active_tasks.assigned_at,
                active_tasks.id
            """,
            (user[0],),
        ).fetchall()

    return [
        ActiveTask(
            task_id=int(row[0]),
            template_id=(
                int(row[1])
                if row[1] is not None
                else None
            ),
            name=str(row[2]),
            xp=int(row[3]),
            assigned_by_name=str(row[4]),
        )
        for row in rows
    ]


def get_active_task(
    user_id: int,
    task_id: int,
) -> ActiveTask | None:
    """Возвращает активную задачу из дома пользователя.

    Задача ищется одновременно по её ID и домашней группе текущего
    пользователя. Поэтому пользователь не сможет открыть задачу
    другой группы, подставив чужой ID.

    Args:
        user_id: Telegram ID пользователя.
        task_id: Идентификатор активной задачи.

    Returns:
        Данные задачи. Если задача недоступна или не существует,
        возвращается ``None``.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                active_tasks.id,
                active_tasks.template_id,
                COALESCE(
                    task_templates.name,
                    active_tasks.custom_name
                ),
                COALESCE(
                    task_templates.xp,
                    active_tasks.custom_xp
                ),
                users.name
            FROM active_tasks
            LEFT JOIN task_templates
              ON task_templates.id = active_tasks.template_id
            JOIN users
              ON users.tg_id = active_tasks.assigned_by
            WHERE active_tasks.id = ?
              AND active_tasks.house_id = (
                  SELECT house_id
                  FROM users
                  WHERE tg_id = ?
              )
            """,
            (
                task_id,
                user_id,
            ),
        ).fetchone()

    if row is None:
        return None

    return ActiveTask(
        task_id=int(row[0]),
        template_id=(
            int(row[1])
            if row[1] is not None
            else None
        ),
        name=str(row[2]),
        xp=int(row[3]),
        assigned_by_name=str(row[4]),
    )


def get_owned_custom_task(
    user_id: int,
    task_id: int,
) -> ActiveTask | None:
    """Возвращает пользовательскую задачу, созданную пользователем.

    Args:
        user_id: Telegram ID создателя задачи.
        task_id: Идентификатор активной задачи.

    Returns:
        Данные задачи, если она пользовательская и создана текущим
        пользователем. В остальных случаях возвращается ``None``.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                active_tasks.id,
                active_tasks.template_id,
                active_tasks.custom_name,
                active_tasks.custom_xp,
                users.name
            FROM active_tasks
            JOIN users
              ON users.tg_id = active_tasks.assigned_by
            WHERE active_tasks.id = ?
              AND active_tasks.assigned_by = ?
              AND active_tasks.template_id IS NULL
            """,
            (
                task_id,
                user_id,
            ),
        ).fetchone()

    if row is None:
        return None

    return ActiveTask(
        task_id=int(row[0]),
        template_id=None,
        name=str(row[2]),
        xp=int(row[3]),
        assigned_by_name=str(row[4]),
    )


def delete_active_task(
    user_id: int,
    task_id: int,
) -> bool:
    """Удаляет активную задачу из дома пользователя.

    Args:
        user_id: Telegram ID пользователя.
        task_id: Идентификатор удаляемой задачи.

    Returns:
        ``True``, если задача найдена и удалена. Если задача не
        существует или принадлежит другому дому, возвращается
        ``False``.
    """
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM active_tasks
            WHERE id = ?
              AND house_id = (
                  SELECT house_id
                  FROM users
                  WHERE tg_id = ?
              )
            """,
            (
                task_id,
                user_id,
            ),
        )

        return cursor.rowcount > 0


def complete_active_task(
    user_id: int,
    task_id: int,
    history_limit: int = 50,
) -> CompletedTaskResult | None:
    """Выполняет задачу и начисляет пользователю опыт.

    Операция удаляет задачу из активных, сохраняет её в истории,
    ограничивает историю дома и начисляет XP. Все изменения
    выполняются в одной транзакции.

    Args:
        user_id: Telegram ID пользователя, выполнившего задачу.
        task_id: Идентификатор активной задачи.
        history_limit: Максимальное количество записей истории дома.

    Returns:
        Сведения о выполненной задаче. Если задача не существует,
        принадлежит другому дому или пользователь не зарегистрирован,
        возвращается ``None``.

    Raises:
        ValueError: Если передан неположительный лимит истории.
    """
    if history_limit <= 0:
        raise ValueError(
            "Лимит истории должен быть положительным"
        )

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                active_tasks.house_id,
                active_tasks.template_id,
                active_tasks.custom_name,
                active_tasks.custom_xp,
                COALESCE(
                    task_templates.name,
                    active_tasks.custom_name
                ),
                COALESCE(
                    task_templates.xp,
                    active_tasks.custom_xp
                )
            FROM active_tasks
            LEFT JOIN task_templates
              ON task_templates.id = active_tasks.template_id
            WHERE active_tasks.id = ?
              AND active_tasks.house_id = (
                  SELECT house_id
                  FROM users
                  WHERE tg_id = ?
              )
            """,
            (
                task_id,
                user_id,
            ),
        ).fetchone()

        if row is None:
            return None

        house_id = int(row[0])
        template_id = (
            int(row[1])
            if row[1] is not None
            else None
        )
        custom_name = row[2]
        custom_xp = row[3]
        task_name = str(row[4])
        task_xp = int(row[5])

        deleted = connection.execute(
            """
            DELETE FROM active_tasks
            WHERE id = ?
              AND house_id = ?
            """,
            (
                task_id,
                house_id,
            ),
        )

        if deleted.rowcount == 0:
            return None

        connection.execute(
            """
            INSERT INTO completed_tasks (
                template_id,
                custom_name,
                custom_xp,
                completed_by,
                house_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                template_id,
                custom_name,
                custom_xp,
                user_id,
                house_id,
            ),
        )

        connection.execute(
            """
            DELETE FROM completed_tasks
            WHERE house_id = ?
              AND id NOT IN (
                  SELECT id
                  FROM completed_tasks
                  WHERE house_id = ?
                  ORDER BY
                      completed_at DESC,
                      id DESC
                  LIMIT ?
              )
            """,
            (
                house_id,
                house_id,
                history_limit,
            ),
        )

        connection.execute(
            """
            UPDATE users
            SET xp = xp + ?
            WHERE tg_id = ?
            """,
            (
                task_xp,
                user_id,
            ),
        )

    return CompletedTaskResult(
        name=task_name,
        xp=task_xp,
        is_standard=template_id is not None,
    )


# =============================================================================
# Административное управление домами
# =============================================================================

def get_admin_houses_page(
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[AdminHouse], int, int]:
    """Возвращает страницу домашних групп для админки.

    Args:
        page: Запрошенный номер страницы.
        page_size: Количество домов на странице.

    Returns:
        Кортеж из домов, фактической страницы и общего количества
        страниц.

    Raises:
        ValueError: Если размер страницы неположительный.
    """
    if page_size <= 0:
        raise ValueError(
            "Размер страницы должен быть положительным"
        )

    with get_connection() as connection:
        total_houses = int(
            connection.execute(
                """
                SELECT COUNT(*)
                FROM houses
                """
            ).fetchone()[0]
        )

        total_pages = max(
            1,
            (
                total_houses
                + page_size
                - 1
            )
            // page_size,
        )

        current_page = max(
            1,
            min(page, total_pages),
        )

        offset = (
            current_page - 1
        ) * page_size

        rows = connection.execute(
            """
            SELECT
                houses.id,
                houses.invite_code,
                COUNT(users.tg_id)
            FROM houses
            LEFT JOIN users
              ON users.house_id = houses.id
            GROUP BY
                houses.id,
                houses.invite_code
            ORDER BY houses.id
            LIMIT ? OFFSET ?
            """,
            (
                page_size,
                offset,
            ),
        ).fetchall()

    houses = [
        AdminHouse(
            house_id=int(row[0]),
            invite_code=str(row[1]),
            member_count=int(row[2]),
        )
        for row in rows
    ]

    return (
        houses,
        current_page,
        total_pages,
    )


def get_admin_house_members(
    house_id: int,
) -> list[AdminHouseMember] | None:
    """Возвращает участников выбранного дома.

    Args:
        house_id: Идентификатор домашней группы.

    Returns:
        Список участников. Для существующего пустого дома возвращается
        пустой список. Если дом не существует, возвращается ``None``.
    """
    with get_connection() as connection:
        house_exists = connection.execute(
            """
            SELECT 1
            FROM houses
            WHERE id = ?
            """,
            (house_id,),
        ).fetchone()

        if house_exists is None:
            return None

        rows = connection.execute(
            """
            SELECT
                tg_id,
                name,
                xp
            FROM users
            WHERE house_id = ?
            ORDER BY
                xp DESC,
                name COLLATE NOCASE,
                tg_id
            """,
            (house_id,),
        ).fetchall()

    return [
        AdminHouseMember(
            user_id=int(row[0]),
            name=str(row[1]),
            xp=int(row[2]),
        )
        for row in rows
    ]


def get_admin_user(
    user_id: int,
) -> AdminUser | None:
    """Возвращает пользователя для административного управления.

    Args:
        user_id: Telegram ID выбранного пользователя.

    Returns:
        Данные пользователя. Если он не найден, возвращается ``None``.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                tg_id,
                name,
                xp,
                house_id
            FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return AdminUser(
        user_id=int(row[0]),
        name=str(row[1]),
        xp=int(row[2]),
        house_id=int(row[3]),
    )


def set_admin_user_xp(
    user_id: int,
    xp: int,
) -> bool:
    """Устанавливает точное количество XP пользователя.

    Args:
        user_id: Telegram ID выбранного пользователя.
        xp: Новое неотрицательное значение опыта.

    Returns:
        ``True``, если пользователь найден и обновлён.

    Raises:
        ValueError: Если передано отрицательное значение XP.
    """
    if xp < 0:
        raise ValueError(
            "Количество XP не может быть отрицательным"
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE users
            SET xp = ?
            WHERE tg_id = ?
            """,
            (
                xp,
                user_id,
            ),
        )

        return cursor.rowcount > 0


def delete_admin_user(
    user_id: int,
) -> int | None:
    """Удаляет пользователя и возвращает ID его дома.

    Связанные активные задачи и записи истории обрабатываются правилами
    внешних ключей SQLite.

    Args:
        user_id: Telegram ID удаляемого пользователя.

    Returns:
        ID домашней группы удалённого пользователя. Если пользователь
        не найден, возвращается ``None``.
    """
    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT house_id
            FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        ).fetchone()

        if user is None:
            return None

        house_id = int(user[0])

        cursor = connection.execute(
            """
            DELETE FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        )

        if cursor.rowcount == 0:
            return None

    return house_id


def clear_admin_house_history(
    house_id: int,
) -> bool:
    """Удаляет всю историю выполненных задач выбранного дома.

    Args:
        house_id: Идентификатор домашней группы.

    Returns:
        ``True``, если дом существует. Если дом не найден,
        возвращается ``False``.
    """
    with get_connection() as connection:
        house = connection.execute(
            """
            SELECT 1
            FROM houses
            WHERE id = ?
            """,
            (house_id,),
        ).fetchone()

        if house is None:
            return False

        connection.execute(
            """
            DELETE FROM completed_tasks
            WHERE house_id = ?
            """,
            (house_id,),
        )

    return True


def delete_admin_house(
    house_id: int,
) -> bool:
    """Удаляет домашнюю группу со связанными данными.

    Участники, активные задачи и история удаляются автоматически
    согласно внешним ключам из ``schema.sql``.

    Args:
        house_id: Идентификатор удаляемого дома.

    Returns:
        ``True``, если дом найден и удалён.
    """
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM houses
            WHERE id = ?
            """,
            (house_id,),
        )

        return cursor.rowcount > 0


# =============================================================================
# Журнал обновлений
# =============================================================================

def get_changelog_page(
    page: int = 1,
    page_size: int = 3,
) -> tuple[list[ChangelogEntry], int, int]:
    """Возвращает страницу журнала обновлений.

    Для старых записей русским текстом считается прежнее поле
    ``message``, если поле ``message_ru`` ещё не заполнено.

    Args:
        page: Запрошенный номер страницы.
        page_size: Количество записей на странице.

    Returns:
        Кортеж из записей, фактической страницы и общего количества
        страниц.

    Raises:
        ValueError: Если размер страницы неположительный.
    """
    if page_size <= 0:
        raise ValueError(
            "Размер страницы должен быть положительным"
        )

    with get_connection() as connection:
        total_records = int(
            connection.execute(
                """
                SELECT COUNT(*)
                FROM changelog
                """
            ).fetchone()[0]
        )

        total_pages = max(
            1,
            (
                total_records
                + page_size
                - 1
            )
            // page_size,
        )

        current_page = max(
            1,
            min(page, total_pages),
        )

        offset = (
            current_page - 1
        ) * page_size

        rows = connection.execute(
            """
            SELECT
                id,
                COALESCE(
                    message_ru,
                    message
                ),
                message_en
            FROM changelog
            ORDER BY
                created_at DESC,
                id DESC
            LIMIT ? OFFSET ?
            """,
            (
                page_size,
                offset,
            ),
        ).fetchall()

    entries = [
        ChangelogEntry(
            entry_id=int(row[0]),
            message_ru=str(row[1]),
            message_en=(
                str(row[2])
                if row[2] is not None
                else None
            ),
        )
        for row in rows
    ]

    return (
        entries,
        current_page,
        total_pages,
    )


def add_changelog_entry(
    message_ru: str,
    message_en: str,
) -> int:
    """Добавляет двуязычную запись журнала.

    Старое поле ``message`` заполняется русским текстом для
    совместимости с предыдущей версией приложения.

    Args:
        message_ru: Русская версия записи.
        message_en: Английская версия записи.

    Returns:
        ID созданной записи.

    Raises:
        ValueError: Если один из вариантов текста пустой.
        RuntimeError: Если SQLite не вернул ID новой записи.
    """
    normalized_ru = message_ru.strip()
    normalized_en = message_en.strip()

    if not normalized_ru:
        raise ValueError(
            "Русский текст записи не может быть пустым"
        )

    if not normalized_en:
        raise ValueError(
            "Английский текст записи не может быть пустым"
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO changelog (
                message,
                message_ru,
                message_en
            )
            VALUES (?, ?, ?)
            """,
            (
                normalized_ru,
                normalized_ru,
                normalized_en,
            ),
        )

        entry_id = cursor.lastrowid

    if entry_id is None:
        raise RuntimeError(
            "SQLite не вернул ID записи журнала"
        )

    return int(entry_id)


def get_changelog_entry(
    entry_id: int,
) -> ChangelogEntry | None:
    """Возвращает одну запись журнала по ID.

    Args:
        entry_id: Идентификатор записи.

    Returns:
        Двуязычная запись или ``None``, если она не найдена.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                COALESCE(
                    message_ru,
                    message
                ),
                message_en
            FROM changelog
            WHERE id = ?
            """,
            (entry_id,),
        ).fetchone()

    if row is None:
        return None

    return ChangelogEntry(
        entry_id=int(row[0]),
        message_ru=str(row[1]),
        message_en=(
            str(row[2])
            if row[2] is not None
            else None
        ),
    )


def update_changelog_entry(
    entry_id: int,
    message_ru: str,
    message_en: str,
) -> bool:
    """Обновляет обе языковые версии записи журнала.

    Старое поле ``message`` также обновляется русским текстом для
    совместимости с предыдущей версией бота.

    Args:
        entry_id: Идентификатор редактируемой записи.
        message_ru: Новый русский текст.
        message_en: Новый английский текст.

    Returns:
        ``True``, если запись найдена и обновлена.

    Raises:
        ValueError: Если один из вариантов текста пустой.
    """
    normalized_ru = message_ru.strip()
    normalized_en = message_en.strip()

    if not normalized_ru:
        raise ValueError(
            "Русский текст записи не может быть пустым"
        )

    if not normalized_en:
        raise ValueError(
            "Английский текст записи не может быть пустым"
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE changelog
            SET
                message = ?,
                message_ru = ?,
                message_en = ?
            WHERE id = ?
            """,
            (
                normalized_ru,
                normalized_ru,
                normalized_en,
                entry_id,
            ),
        )

        return cursor.rowcount > 0


def delete_changelog_entry(
    entry_id: int,
) -> bool:
    """Удаляет запись журнала обновлений.

    Args:
        entry_id: Идентификатор удаляемой записи.

    Returns:
        ``True``, если запись найдена и удалена.
    """
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM changelog
            WHERE id = ?
            """,
            (entry_id,),
        )

        return cursor.rowcount > 0


# =============================================================================
# История выполненных задач
# =============================================================================

def get_completed_tasks_page(
    user_id: int,
    page: int = 1,
    page_size: int = 5,
) -> tuple[list[CompletedTaskEntry], int, int] | None:
    """Возвращает страницу истории домашней группы.

    Args:
        user_id: Telegram ID пользователя.
        page: Запрошенный номер страницы.
        page_size: Количество записей на странице.

    Returns:
        Кортеж из записей, фактической страницы и общего количества
        страниц. Если пользователь не состоит в доме, возвращается
        ``None``.

    Raises:
        ValueError: Если размер страницы неположительный.
    """
    if page_size <= 0:
        raise ValueError(
            "Размер страницы должен быть положительным"
        )

    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT house_id
            FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        ).fetchone()

        if user is None:
            return None

        house_id = int(user[0])

        total_records = int(
            connection.execute(
                """
                SELECT COUNT(*)
                FROM completed_tasks
                WHERE house_id = ?
                """,
                (house_id,),
            ).fetchone()[0]
        )

        total_pages = max(
            1,
            (
                total_records
                + page_size
                - 1
            )
            // page_size,
        )

        current_page = max(
            1,
            min(page, total_pages),
        )

        offset = (
            current_page - 1
        ) * page_size

        rows = connection.execute(
            """
            SELECT
                completed_tasks.completed_at,
                task_templates.name,
                completed_tasks.custom_name,
                COALESCE(
                    task_templates.xp,
                    completed_tasks.custom_xp
                ),
                users.name
            FROM completed_tasks
            LEFT JOIN task_templates
              ON task_templates.id = completed_tasks.template_id
            JOIN users
              ON users.tg_id = completed_tasks.completed_by
            WHERE completed_tasks.house_id = ?
            ORDER BY
                completed_tasks.completed_at DESC,
                completed_tasks.id DESC
            LIMIT ? OFFSET ?
            """,
            (
                house_id,
                page_size,
                offset,
            ),
        ).fetchall()

    records = [
        CompletedTaskEntry(
            completed_at=datetime.fromisoformat(
                str(row[0]),
            ),
            template_name=(
                str(row[1])
                if row[1] is not None
                else None
            ),
            custom_name=(
                str(row[2])
                if row[2] is not None
                else None
            ),
            xp=int(row[3]),
            executor_name=str(row[4]),
        )
        for row in rows
    ]

    return (
        records,
        current_page,
        total_pages,
    )


# =============================================================================
# Домашняя группа пользователя
# =============================================================================

def get_house_members(
    user_id: int,
) -> list[HouseMember] | None:
    """Возвращает участников домашней группы пользователя.

    Участники располагаются по количеству опыта: сначала пользователь
    с наибольшим XP.

    Args:
        user_id: Telegram ID пользователя, открывшего экран.

    Returns:
        Список участников. Если пользователь не зарегистрирован или
        не состоит в домашней группе, возвращается ``None``.
    """
    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT house_id
            FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        ).fetchone()

        if user is None:
            return None

        rows = connection.execute(
            """
            SELECT
                tg_id,
                name,
                xp
            FROM users
            WHERE house_id = ?
            ORDER BY
                xp DESC,
                name COLLATE NOCASE,
                tg_id
            """,
            (user[0],),
        ).fetchall()

    return [
        HouseMember(
            user_id=int(row[0]),
            name=str(row[1]),
            xp=int(row[2]),
        )
        for row in rows
    ]


def get_house_invite_code(
    user_id: int,
) -> str | None:
    """Возвращает код приглашения домашней группы пользователя.

    Args:
        user_id: Telegram ID пользователя.

    Returns:
        Код приглашения. Если пользователь или его домашняя группа
        не найдены, возвращается ``None``.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT houses.invite_code
            FROM users
            JOIN houses
              ON houses.id = users.house_id
            WHERE users.tg_id = ?
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return str(row[0])


# =============================================================================
# Служебная информация
# =============================================================================

def get_database_path() -> Path:
    """Возвращает абсолютный путь к файлу базы данных.

    Returns:
        Путь к ``household.db``.
    """
    return Path(DB_PATH)
