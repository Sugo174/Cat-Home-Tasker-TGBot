"""Клавиатуры Telegram-бота.

Модуль отвечает только за создание кнопок. Он не обращается к базе
данных, не отправляет сообщения и не обрабатывает нажатия пользователя.
"""

from collections.abc import Sequence
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from localization import (
    DEFAULT_LANGUAGE,
    normalize_language,
    t,
)


# =============================================================================
# Главное меню
# =============================================================================

def get_main_menu(language: str) -> InlineKeyboardMarkup:
    """Создаёт главное меню пользователя.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура главного меню.
    """
    language = normalize_language(language)

    buttons = [
        [
            InlineKeyboardButton(
                text=t(language, "menu_tasks"),
                callback_data="menu:tasks",
            )
        ],
        [
            InlineKeyboardButton(
                text=t(language, "menu_add_task"),
                callback_data="menu:addtask",
            )
        ],
        [
            InlineKeyboardButton(
                text=t(language, "menu_invite"),
                callback_data="menu:invite",
            )
        ],
        [
            InlineKeyboardButton(
                text=t(language, "menu_history"),
                callback_data="menu:history",
            )
        ],
        [
            InlineKeyboardButton(
                text=t(language, "menu_profile"),
                callback_data="menu:profile",
            )
        ],
        [
            InlineKeyboardButton(
                text=t(language, "menu_house"),
                callback_data="menu:house",
            )
        ],
        [
            InlineKeyboardButton(
                text=t(language, "menu_changelog"),
                callback_data="menu:changelog",
            )
        ],
        [
            InlineKeyboardButton(
                text=t(language, "menu_language"),
                callback_data="menu:language",
            )
        ],
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )


# =============================================================================
# Выбор языка
# =============================================================================

def get_language_menu() -> InlineKeyboardMarkup:
    """Создаёт меню изменения языка.

    Returns:
        Клавиатура с русским и английским языками.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇷🇺 Русский",
                    callback_data="language:set:ru",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇬🇧 English",
                    callback_data="language:set:en",
                )
            ],
        ]
    )


def get_registration_language_menu() -> InlineKeyboardMarkup:
    """Создаёт выбор языка во время регистрации.

    Returns:
        Клавиатура выбора первоначального языка.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇷🇺 Русский",
                    callback_data="registration:language:ru",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇬🇧 English",
                    callback_data="registration:language:en",
                )
            ],
        ]
    )


# =============================================================================
# Общая навигация
# =============================================================================

def get_back_button(
    language: str = DEFAULT_LANGUAGE,
) -> InlineKeyboardMarkup:
    """Создаёт кнопку возврата в главное меню.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура с кнопкой возврата.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "back_to_menu"),
                    callback_data="menu:main",
                )
            ]
        ]
    )


# =============================================================================
# Регистрация пользователя
# =============================================================================

def get_gender_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт меню выбора пола при регистрации.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура с вариантами пола.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "gender_male"),
                    callback_data="gender:male",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "gender_female"),
                    callback_data="gender:female",
                )
            ],
        ]
    )


# =============================================================================
# Профиль
# =============================================================================

def get_profile_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру профиля пользователя.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура с редактированием профиля и возвратом в меню.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(language, "profile_edit"),
                    callback_data="profile:edit",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(language, "back_to_menu"),
                    callback_data="menu:main",
                )
            ],
        ]
    )


# =============================================================================
# Редактирование профиля
# =============================================================================

def get_profile_edit_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт меню редактирования профиля.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура выбора изменяемого поля.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "profile_change_name",
                    ),
                    callback_data="profile:edit_name",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "profile_change_gender",
                    ),
                    callback_data="profile:edit_gender",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "back",
                    ),
                    callback_data="menu:profile",
                )
            ],
        ]
    )


def get_profile_gender_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт выбор нового пола в настройках профиля.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура с вариантами пола.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "gender_male",
                    ),
                    callback_data="profile:set_gender:male",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "gender_female",
                    ),
                    callback_data="profile:set_gender:female",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "back",
                    ),
                    callback_data="menu:profile",
                )
            ],
        ]
    )


# =============================================================================
# Активные задачи
# =============================================================================

def get_active_tasks_menu(
    language: str,
    tasks: Sequence[tuple[int, str]],
) -> InlineKeyboardMarkup:
    """Создаёт кнопки активных задач.

    Args:
        language: Код языка пользователя.
        tasks: Последовательность пар из ID и отображаемого названия
            задачи.

    Returns:
        Клавиатура со списком задач и кнопкой возврата.
    """
    language = normalize_language(language)

    buttons = [
        [
            InlineKeyboardButton(
                text=f"🔧 {task_name}",
                callback_data=f"task:detail:{task_id}",
            )
        ]
        for task_id, task_name in tasks
    ]

    buttons.append(
        [
            InlineKeyboardButton(
                text=t(
                    language,
                    "back_to_menu",
                ),
                callback_data="menu:main",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )


def get_task_detail_menu(
    language: str,
    task_id: int,
    is_custom: bool,
) -> InlineKeyboardMarkup:
    """Создаёт кнопки управления активной задачей.

    Args:
        language: Код языка пользователя.
        task_id: Идентификатор активной задачи.
        is_custom: ``True`` для пользовательской задачи.

    Returns:
        Клавиатура выполнения, редактирования и удаления задачи.
    """
    language = normalize_language(language)

    buttons = [
        [
            InlineKeyboardButton(
                text=t(
                    language,
                    "complete_task",
                ),
                callback_data=f"complete_task:{task_id}",
            )
        ]
    ]

    if is_custom:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "edit_task",
                    ),
                    callback_data=f"edit_custom_task:{task_id}",
                )
            ]
        )

    buttons.extend(
        [
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "delete_task",
                    ),
                    callback_data=f"delete_task:{task_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "back_to_tasks",
                    ),
                    callback_data="menu:tasks",
                )
            ],
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )


# =============================================================================
# Добавление задач
# =============================================================================

def get_add_task_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт меню выбора типа новой задачи.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура выбора стандартной или пользовательской задачи.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "choose_standard_task",
                    ),
                    callback_data="addtask:standard:1",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "create_custom_task",
                    ),
                    callback_data="addtask:custom",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "back_to_menu",
                    ),
                    callback_data="menu:main",
                )
            ],
        ]
    )


def get_standard_tasks_menu(
    language: str,
    tasks: Sequence[tuple[int, str, int]],
    current_page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    """Создаёт страницу кнопок стандартных задач.

    Args:
        language: Код языка пользователя.
        tasks: Последовательность из ID, названия и XP задачи.
        current_page: Текущий номер страницы.
        total_pages: Общее количество страниц.

    Returns:
        Клавиатура выбора задачи и переключения страниц.
    """
    language = normalize_language(language)

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{task_name} (+{xp} XP)",
                callback_data=f"add_task:{task_id}",
            )
        ]
        for task_id, task_name, xp in tasks
    ]

    navigation_buttons = []

    if current_page > 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text=t(
                    language,
                    "previous_page",
                ),
                callback_data=(
                    "addtask:standard:"
                    f"{current_page - 1}"
                ),
            )
        )

    if current_page < total_pages:
        navigation_buttons.append(
            InlineKeyboardButton(
                text=t(
                    language,
                    "next_page",
                ),
                callback_data=(
                    "addtask:standard:"
                    f"{current_page + 1}"
                ),
            )
        )

    if navigation_buttons:
        buttons.append(
            navigation_buttons,
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=t(
                    language,
                    "back",
                ),
                callback_data="menu:addtask",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )


def get_standard_task_actions_menu(
    language: str,
    template_id: int,
) -> InlineKeyboardMarkup:
    """Создаёт действия для выбранной стандартной задачи.

    Args:
        language: Код языка пользователя.
        template_id: Идентификатор шаблона задачи.

    Returns:
        Клавиатура выполнения или добавления задачи.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "complete_task",
                    ),
                    callback_data=(
                        f"complete_now:{template_id}"
                    ),
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "add_to_active",
                    ),
                    callback_data=(
                        f"add_to_active:{template_id}"
                    ),
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "back_to_task_selection",
                    ),
                    callback_data="menu:addtask",
                )
            ],
        ]
    )


# =============================================================================
# Пользовательские задачи
# =============================================================================

def get_custom_task_preview_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт кнопки предварительного просмотра задачи.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура продолжения, изменения или отмены.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "continue",
                    ),
                    callback_data="custom_task:choose_xp",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "edit",
                    ),
                    callback_data="custom_task:edit_desc",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "cancel",
                    ),
                    callback_data="menu:addtask",
                )
            ],
        ]
    )


def get_custom_task_xp_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт кнопки выбора награды за задачу.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура выбора XP, возврата и отмены.
    """
    language = normalize_language(language)

    xp_buttons = [
        [
            InlineKeyboardButton(
                text=f"{xp} XP",
                callback_data=f"custom_xp:{xp}",
            )
        ]
        for xp in (
            5,
            10,
            15,
            20,
        )
    ]

    xp_buttons.extend(
        [
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "back",
                    ),
                    callback_data="custom_task:back_to_desc",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "cancel",
                    ),
                    callback_data="menu:addtask",
                )
            ],
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=xp_buttons,
    )


def get_custom_task_added_menu(
    language: str,
    task_id: int,
) -> InlineKeyboardMarkup:
    """Создаёт действия после добавления пользовательской задачи.

    Args:
        language: Код языка пользователя.
        task_id: ID созданной активной задачи.

    Returns:
        Клавиатура выполнения задачи или возврата.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "complete_task",
                    ),
                    callback_data=f"complete_task:{task_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "edit_task",
                    ),
                    callback_data=f"edit_custom_task:{task_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "back_to_add_tasks",
                    ),
                    callback_data="menu:addtask",
                )
            ],
        ]
    )


# =============================================================================
# Редактирование пользовательской задачи
# =============================================================================

def get_custom_task_edit_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт основное меню редактирования задачи.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура изменения описания или XP.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "edit_description",
                    ),
                    callback_data="edit_desc",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "change_xp",
                    ),
                    callback_data="edit_xp",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "cancel",
                    ),
                    callback_data="menu:tasks",
                )
            ],
        ]
    )


def get_edited_description_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт действия после изменения описания.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура сохранения или продолжения редактирования.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "save",
                    ),
                    callback_data="save_edited_task",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "change_xp",
                    ),
                    callback_data="edit_xp",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "cancel",
                    ),
                    callback_data="menu:tasks",
                )
            ],
        ]
    )


def get_custom_task_edit_xp_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт выбор нового XP при редактировании.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура выбора XP и отмены.
    """
    language = normalize_language(language)

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{xp} XP",
                callback_data=f"set_xp:{xp}",
            )
        ]
        for xp in (
            5,
            10,
            15,
            20,
        )
    ]

    buttons.append(
        [
            InlineKeyboardButton(
                text=t(
                    language,
                    "cancel",
                ),
                callback_data="menu:tasks",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )


def get_edited_xp_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт действия после изменения XP.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура сохранения или изменения описания.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "save",
                    ),
                    callback_data="save_edited_task",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "change_description",
                    ),
                    callback_data="edit_desc",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "cancel",
                    ),
                    callback_data="menu:tasks",
                )
            ],
        ]
    )


def get_back_to_tasks_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт кнопку возврата к активным задачам.

    Args:
        language: Код языка пользователя.

    Returns:
        Клавиатура с кнопкой возврата к списку задач.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "back_to_tasks",
                    ),
                    callback_data="menu:tasks",
                )
            ]
        ]
    )


# =============================================================================
# История выполненных задач
# =============================================================================

def get_history_menu(
    language: str,
    current_page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    """Создаёт навигацию по истории задач.

    Args:
        language: Код языка пользователя.
        current_page: Текущая страница.
        total_pages: Общее количество страниц.

    Returns:
        Клавиатура переключения страниц и возврата в меню.
    """
    language = normalize_language(language)

    buttons: list[list[InlineKeyboardButton]] = []
    navigation_buttons: list[InlineKeyboardButton] = []

    if current_page > 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text=t(
                    language,
                    "previous_page",
                ),
                callback_data=(
                    f"history:page:{current_page - 1}"
                ),
            )
        )

    if current_page < total_pages:
        navigation_buttons.append(
            InlineKeyboardButton(
                text=t(
                    language,
                    "next_page",
                ),
                callback_data=(
                    f"history:page:{current_page + 1}"
                ),
            )
        )

    if navigation_buttons:
        buttons.append(
            navigation_buttons,
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=t(
                    language,
                    "back_to_menu",
                ),
                callback_data="menu:main",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )


# =============================================================================
# Журнал обновлений
# =============================================================================

def get_changelog_menu(
    language: str,
    current_page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    """Создаёт пользовательскую навигацию журнала.

    Args:
        language: Код языка пользователя.
        current_page: Текущая страница.
        total_pages: Общее количество страниц.

    Returns:
        Клавиатура листания журнала и возврата в меню.
    """
    language = normalize_language(language)

    buttons: list[list[InlineKeyboardButton]] = []
    navigation_buttons: list[InlineKeyboardButton] = []

    if current_page > 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text=t(
                    language,
                    "previous_page",
                ),
                callback_data=(
                    "changelog:page:"
                    f"{current_page - 1}:user"
                ),
            )
        )

    if current_page < total_pages:
        navigation_buttons.append(
            InlineKeyboardButton(
                text=t(
                    language,
                    "next_page",
                ),
                callback_data=(
                    "changelog:page:"
                    f"{current_page + 1}:user"
                ),
            )
        )

    if navigation_buttons:
        buttons.append(
            navigation_buttons,
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=t(
                    language,
                    "back_to_menu",
                ),
                callback_data="menu:main",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )


# =============================================================================
# Административная панель
# =============================================================================

def get_admin_houses_menu(
    language: str,
    houses: Sequence[tuple[int, str]],
    current_page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    """Создаёт список домов и навигацию админки.

    Args:
        language: Код языка администратора.
        houses: Последовательность пар из ID дома и кода приглашения.
        current_page: Текущая страница.
        total_pages: Общее количество страниц.

    Returns:
        Клавиатура выбора дома, журнала и выхода.
    """
    language = normalize_language(language)

    buttons = [
        [
            InlineKeyboardButton(
                text=t(
                    language,
                    "admin_house_button",
                    house_id=house_id,
                    invite_code=invite_code,
                ),
                callback_data=f"admin:house:{house_id}",
            )
        ]
        for house_id, invite_code in houses
    ]

    navigation_buttons: list[InlineKeyboardButton] = []

    if current_page > 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text=t(
                    language,
                    "previous_page",
                ),
                callback_data=(
                    f"admin:houses_page:{current_page - 1}"
                ),
            )
        )

    if current_page < total_pages:
        navigation_buttons.append(
            InlineKeyboardButton(
                text=t(
                    language,
                    "next_page",
                ),
                callback_data=(
                    f"admin:houses_page:{current_page + 1}"
                ),
            )
        )

    if navigation_buttons:
        buttons.append(
            navigation_buttons,
        )

    buttons.extend(
        [
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_manage_changelog",
                    ),
                    callback_data="admin:changelog",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_exit",
                    ),
                    callback_data="admin:exit",
                )
            ],
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )


def get_admin_house_menu(
    language: str,
    house_id: int,
    members: Sequence[tuple[int, str]],
) -> InlineKeyboardMarkup:
    """Создаёт кнопки управления домом и его участниками.

    Args:
        language: Код языка администратора.
        house_id: Идентификатор выбранного дома.
        members: Последовательность пар из ID и имени участника.

    Returns:
        Клавиатура участников и действий с домом.
    """
    language = normalize_language(language)

    buttons = [
        [
            InlineKeyboardButton(
                text=t(
                    language,
                    "admin_manage_user",
                    name=member_name,
                ),
                callback_data=f"admin:user:{member_id}",
            )
        ]
        for member_id, member_name in members
    ]

    buttons.extend(
        [
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_clear_history",
                    ),
                    callback_data=(
                        f"admin:clear_history:{house_id}"
                    ),
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_delete_house",
                    ),
                    callback_data=(
                        f"admin:delete_house:{house_id}"
                    ),
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_back_to_houses",
                    ),
                    callback_data="admin:back_to_houses",
                )
            ],
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )


def get_admin_user_menu(
    language: str,
    user_id: int,
    house_id: int,
) -> InlineKeyboardMarkup:
    """Создаёт административные действия с пользователем.

    Args:
        language: Код языка администратора.
        user_id: Telegram ID выбранного пользователя.
        house_id: ID дома для кнопки возврата.

    Returns:
        Клавиатура изменения XP, удаления и возврата.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_set_xp",
                    ),
                    callback_data=f"admin:set_xp:{user_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_reset_xp",
                    ),
                    callback_data=f"admin:reset_xp:{user_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_delete_user",
                    ),
                    callback_data=f"admin:delete_user:{user_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_back_to_house",
                    ),
                    callback_data=f"admin:house:{house_id}",
                )
            ],
        ]
    )


def get_admin_delete_house_confirmation_menu(
    language: str,
    house_id: int,
) -> InlineKeyboardMarkup:
    """Создаёт подтверждение удаления домашней группы.

    Args:
        language: Код языка администратора.
        house_id: Идентификатор удаляемого дома.

    Returns:
        Клавиатура подтверждения и отмены.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_confirm_delete",
                    ),
                    callback_data=(
                        f"admin:confirm_delete_house:{house_id}"
                    ),
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "cancel",
                    ),
                    callback_data=f"admin:house:{house_id}",
                )
            ],
        ]
    )


def get_admin_changelog_menu(
    language: str,
    entry_ids: Sequence[int],
    current_page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру управления журналом обновлений.

    Args:
        language: Код языка администратора.
        entry_ids: ID записей текущей страницы.
        current_page: Текущая страница.
        total_pages: Общее количество страниц.

    Returns:
        Клавиатура редактирования, удаления и навигации.
    """
    language = normalize_language(language)

    buttons: list[list[InlineKeyboardButton]] = []

    for entry_id in entry_ids:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_edit_changelog",
                    ),
                    callback_data=(
                        f"changelog:edit:{entry_id}"
                    ),
                ),
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_delete_changelog",
                    ),
                    callback_data=(
                        f"changelog:delete:{entry_id}"
                    ),
                ),
            ]
        )

    navigation_buttons: list[InlineKeyboardButton] = []

    if current_page > 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text=t(
                    language,
                    "previous_page",
                ),
                callback_data=(
                    "changelog:page:"
                    f"{current_page - 1}:admin"
                ),
            )
        )

    if current_page < total_pages:
        navigation_buttons.append(
            InlineKeyboardButton(
                text=t(
                    language,
                    "next_page",
                ),
                callback_data=(
                    "changelog:page:"
                    f"{current_page + 1}:admin"
                ),
            )
        )

    if navigation_buttons:
        buttons.append(
            navigation_buttons,
        )

    buttons.extend(
        [
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_add_changelog",
                    ),
                    callback_data="admin:changelog_add",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_back_to_houses",
                    ),
                    callback_data="admin:back_to_houses",
                )
            ],
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )


def get_changelog_delete_confirmation_menu(
    language: str,
) -> InlineKeyboardMarkup:
    """Создаёт подтверждение удаления записи журнала.

    Args:
        language: Код языка администратора.

    Returns:
        Клавиатура подтверждения и отмены удаления.
    """
    language = normalize_language(language)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "admin_confirm_delete",
                    ),
                    callback_data="changelog:confirm_delete",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(
                        language,
                        "cancel",
                    ),
                    callback_data="admin:changelog",
                )
            ],
        ]
    )