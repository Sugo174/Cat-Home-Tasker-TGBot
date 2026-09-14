"""Административные обработчики Telegram-бота.

Модуль содержит вход в административную панель, управление домашними
группами и пользователями, а также управление журналом обновлений.
"""

from html import escape
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.filters import StateFilter
from handlers.user import (
    delete_message_safely,
    show_interface,
    remember_interface_message,
)
from localization import (
    calculate_level,
    t,
)
from states import (
    AdminChangelog,
    AdminChangelogEdit,
    AdminEditXP,
    AdminState,
)
from config import ADMIN_PASSWORD
from database import (
    add_changelog_entry,
    clear_admin_house_history,
    delete_admin_house,
    delete_admin_user,
    delete_changelog_entry,
    get_admin_house_members,
    get_admin_houses_page,
    get_admin_user,
    get_changelog_entry,
    get_changelog_page,
    get_user_language,
    set_admin_user_xp,
    update_changelog_entry,
)
from keyboards import (
    get_admin_houses_menu,
    get_main_menu,
    get_admin_house_menu,
    get_admin_user_menu,
    get_admin_delete_house_confirmation_menu,
    get_admin_changelog_menu,
    get_changelog_delete_confirmation_menu,
)

# =============================================================================
# Роутер административных обработчиков
# =============================================================================

router = Router(
    name="admin",
)


# =============================================================================
# Вход в административную панель
# =============================================================================

@router.message(F.text == "/admin")
async def cmd_admin(
    message: Message,
    state: FSMContext,
) -> None:
    """Открывает экран ввода административного пароля.

    Команда пользователя удаляется, а существующее сообщение обычного
    интерфейса превращается в запрос пароля.

    Args:
        message: Сообщение с командой ``/admin``.
        state: Текущее состояние пользователя.
    """
    if message.from_user is None:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    language = get_user_language(user_id)

    await delete_message_safely(
        bot=message.bot,
        chat_id=chat_id,
        message_id=message.message_id,
    )

    await state.clear()

    admin_message_id = await show_interface(
        bot=message.bot,
        chat_id=chat_id,
        user_id=user_id,
        text=t(
            language,
            "admin_password_prompt",
        ),
    )

    await state.update_data(
        admin_message_id=admin_message_id,
        chat_id=chat_id,
        admin_user_id=user_id,
        admin_language=language,
    )

    await state.set_state(
        AdminState.waiting_for_password,
    )


# =============================================================================
# Список домашних групп
# =============================================================================

def build_admin_houses_screen(
    language: str,
    page: int = 1,
) -> tuple[str, InlineKeyboardMarkup]:
    """Формирует страницу домашних групп.

    Args:
        language: Код языка администратора.
        page: Запрошенная страница.

    Returns:
        Текст страницы и административная клавиатура.
    """
    houses, current_page, total_pages = (
        get_admin_houses_page(
            page=page,
            page_size=10,
        )
    )

    if houses:
        screen_text = t(
            language,
            "admin_houses_title",
            page=current_page,
            total_pages=total_pages,
        )
    else:
        screen_text = t(
            language,
            "admin_no_houses",
        )

    keyboard_houses = [
        (
            house.house_id,
            house.invite_code,
        )
        for house in houses
    ]

    return (
        screen_text,
        get_admin_houses_menu(
            language=language,
            houses=keyboard_houses,
            current_page=current_page,
            total_pages=total_pages,
        ),
    )


async def show_admin_houses(
    bot: Bot,
    chat_id: int,
    user_id: int,
    language: str,
    page: int = 1,
) -> None:
    """Показывает страницу домашних групп в одном сообщении.

    Args:
        bot: Экземпляр Telegram-бота.
        chat_id: ID административного чата.
        user_id: Telegram ID администратора.
        language: Код языка интерфейса.
        page: Отображаемая страница.
    """
    screen_text, keyboard = build_admin_houses_screen(
        language=language,
        page=page,
    )

    await show_interface(
        bot=bot,
        chat_id=chat_id,
        user_id=user_id,
        text=screen_text,
        reply_markup=keyboard,
    )


# =============================================================================
# Проверка административного пароля
# =============================================================================

@router.message(
    AdminState.waiting_for_password,
    ~F.text.startswith("/"),
)
async def admin_password_check(
    message: Message,
    state: FSMContext,
) -> None:
    """Проверяет пароль и открывает список домов.

    Args:
        message: Сообщение с введённым паролем.
        state: Состояние административной авторизации.
    """
    if message.from_user is None:
        return

    user_id = message.from_user.id
    language = get_user_language(user_id)

    entered_password = message.text or ""

    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    if entered_password != ADMIN_PASSWORD:
        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=user_id,
            text=t(
                language,
                "admin_wrong_password",
            ),
        )
        return

    await state.set_state(
        AdminState.browsing_houses,
    )

    await state.update_data(
        admin_language=language,
        current_houses_page=1,
    )

    await show_admin_houses(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=user_id,
        language=language,
        page=1,
    )


# =============================================================================
# Навигация административной панели
# =============================================================================

@router.callback_query(
    F.data.startswith("admin:houses_page:"),
    AdminState.browsing_houses,
)
async def handle_admin_houses_pagination(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Переключает страницы домашних групп.

    Args:
        callback: Нажатие кнопки предыдущей или следующей страницы.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        page = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        page = 1

    user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(user_id),
    )

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await state.update_data(
        current_houses_page=page,
    )

    await show_admin_houses(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        language=language,
        page=page,
    )

    await callback.answer()


@router.callback_query(
    F.data == "admin:exit",
)
async def exit_admin_panel(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Закрывает админку и возвращает обычное меню.

    Args:
        callback: Нажатие кнопки выхода.
        state: Текущее состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(user_id),
    )

    await state.clear()

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=t(
            language,
            "main_title",
        ),
        reply_markup=get_main_menu(language),
    )

    await callback.answer(
        t(
            language,
            "admin_exited",
        )
    )


# =============================================================================
# Управление выбранным домом
# =============================================================================

def build_admin_house_screen(
    house_id: int,
    language: str,
) -> tuple[str, InlineKeyboardMarkup] | None:
    """Формирует экран участников выбранного дома.

    Args:
        house_id: Идентификатор домашней группы.
        language: Код языка администратора.

    Returns:
        Текст и клавиатура дома. Если дом не существует,
        возвращается ``None``.
    """
    members = get_admin_house_members(
        house_id,
    )

    if members is None:
        return None

    if not members:
        screen_text = t(
            language,
            "admin_house_empty",
            house_id=house_id,
        )
    else:
        lines = [
            t(
                language,
                "admin_house_members",
                house_id=house_id,
            ),
            "",
        ]

        for member in members:
            level_info = calculate_level(
                member.xp,
                language,
            )

            lines.append(
                t(
                    language,
                    "admin_member_line",
                    name=escape(member.name),
                    user_id=member.user_id,
                    level=level_info["level"],
                )
            )

        screen_text = "\n".join(lines)

    keyboard_members = [
        (
            member.user_id,
            member.name,
        )
        for member in members
    ]

    return (
        screen_text,
        get_admin_house_menu(
            language=language,
            house_id=house_id,
            members=keyboard_members,
        ),
    )


@router.callback_query(
    F.data.startswith("admin:house:"),
    StateFilter(
        AdminState.browsing_houses,
        AdminState.managing_house,
    ),
)
async def show_admin_house(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Открывает выбранную домашнюю группу.

    Args:
        callback: Нажатие кнопки дома.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        house_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid house ID",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(user_id),
    )

    screen = build_admin_house_screen(
        house_id=house_id,
        language=language,
    )

    if screen is None:
        await callback.answer(
            t(
                language,
                "admin_house_not_found",
            ),
            show_alert=True,
        )

        await show_admin_houses(
            bot=callback.bot,
            chat_id=callback.message.chat.id,
            user_id=user_id,
            language=language,
            page=1,
        )
        return

    screen_text, keyboard = screen

    await state.update_data(
        current_house_id=house_id,
    )

    await state.set_state(
        AdminState.managing_house,
    )

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=screen_text,
        reply_markup=keyboard,
    )

    await callback.answer()


@router.callback_query(
    F.data == "admin:back_to_houses",
    StateFilter(
        AdminState.browsing_houses,
        AdminState.managing_house,
    ),
)


async def back_to_admin_houses(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Возвращает администратора к списку домов.

    Args:
        callback: Нажатие кнопки возврата.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(user_id),
    )
    page = int(
        state_data.get(
            "current_houses_page",
            1,
        )
    )

    await state.set_state(
        AdminState.browsing_houses,
    )

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await show_admin_houses(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        language=language,
        page=page,
    )

    await callback.answer()


# =============================================================================
# Управление участником
# =============================================================================

@router.callback_query(
    F.data.startswith("admin:user:"),
    AdminState.managing_house,
)
async def show_admin_user(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Открывает административную карточку пользователя.

    Args:
        callback: Нажатие кнопки участника.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        target_user_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid user ID",
            show_alert=True,
        )
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    target_user = get_admin_user(
        target_user_id,
    )

    if target_user is None:
        await callback.answer(
            t(
                language,
                "admin_user_not_found",
            ),
            show_alert=True,
        )

        current_house_id = state_data.get(
            "current_house_id",
        )

        if current_house_id is not None:
            screen = build_admin_house_screen(
                house_id=int(current_house_id),
                language=language,
            )

            if screen is not None:
                screen_text, keyboard = screen

                await show_interface(
                    bot=callback.bot,
                    chat_id=callback.message.chat.id,
                    user_id=admin_user_id,
                    text=screen_text,
                    reply_markup=keyboard,
                )

        return

    await state.update_data(
        target_user_id=target_user.user_id,
        current_house_id=target_user.house_id,
    )

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        text=t(
            language,
            "admin_user_management",
            name=escape(target_user.name),
            xp=target_user.xp,
        ),
        reply_markup=get_admin_user_menu(
            language=language,
            user_id=target_user.user_id,
            house_id=target_user.house_id,
        ),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:reset_xp:"),
    AdminState.managing_house,
)
async def reset_admin_user_xp(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Сбрасывает XP выбранного пользователя до нуля.

    Args:
        callback: Нажатие кнопки сброса XP.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        target_user_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid user ID",
            show_alert=True,
        )
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    updated = set_admin_user_xp(
        user_id=target_user_id,
        xp=0,
    )

    if not updated:
        await callback.answer(
            t(
                language,
                "admin_user_not_found",
            ),
            show_alert=True,
        )
        return

    target_user = get_admin_user(
        target_user_id,
    )

    if target_user is None:
        await callback.answer(
            t(
                language,
                "admin_user_not_found",
            ),
            show_alert=True,
        )
        return

    await state.update_data(
        target_user_id=target_user.user_id,
        current_house_id=target_user.house_id,
    )

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        text=t(
            language,
            "admin_user_management",
            name=escape(target_user.name),
            xp=target_user.xp,
        ),
        reply_markup=get_admin_user_menu(
            language=language,
            user_id=target_user.user_id,
            house_id=target_user.house_id,
        ),
    )

    await callback.answer(
        t(
            language,
            "admin_xp_reset",
        )
    )


@router.callback_query(
    F.data.startswith("admin:set_xp:"),
    AdminState.managing_house,
)
async def start_admin_user_xp_edit(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Начинает ручное изменение XP пользователя.

    Args:
        callback: Нажатие кнопки установки XP.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        target_user_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid user ID",
            show_alert=True,
        )
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    if get_admin_user(target_user_id) is None:
        await callback.answer(
            t(
                language,
                "admin_user_not_found",
            ),
            show_alert=True,
        )
        return

    await state.update_data(
        target_user_id=target_user_id,
        admin_message_id=callback.message.message_id,
        chat_id=callback.message.chat.id,
    )

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        text=t(
            language,
            "admin_enter_xp",
        ),
    )

    await state.set_state(
        AdminEditXP.waiting_for_xp,
    )

    await callback.answer()


@router.message(
    AdminEditXP.waiting_for_xp,
    ~F.text.startswith("/"),
)
async def save_admin_user_xp(
    message: Message,
    state: FSMContext,
) -> None:
    """Проверяет и сохраняет введённое значение XP.

    Args:
        message: Сообщение с новым количеством XP.
        state: Данные административного редактирования.
    """
    if message.from_user is None:
        return

    admin_user_id = message.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )
    target_user_id = state_data.get(
        "target_user_id",
    )

    entered_value = (
        message.text or ""
    ).strip()

    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    try:
        new_xp = int(entered_value)

        if new_xp < 0:
            raise ValueError

    except ValueError:
        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=admin_user_id,
            text=t(
                language,
                "admin_invalid_xp",
            ),
        )
        return

    if target_user_id is None:
        await state.set_state(
            AdminState.managing_house,
        )

        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=admin_user_id,
            text=t(
                language,
                "admin_user_not_found",
            ),
        )
        return

    updated = set_admin_user_xp(
        user_id=int(target_user_id),
        xp=new_xp,
    )

    await state.set_state(
        AdminState.managing_house,
    )

    target_user = get_admin_user(
        int(target_user_id),
    )

    if not updated or target_user is None:
        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=admin_user_id,
            text=t(
                language,
                "admin_user_not_found",
            ),
        )
        return

    await state.update_data(
        current_house_id=target_user.house_id,
    )

    screen_text = t(
        language,
        "admin_user_management",
        name=escape(target_user.name),
        xp=target_user.xp,
    )

    await show_interface(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=admin_user_id,
        text=screen_text,
        reply_markup=get_admin_user_menu(
            language=language,
            user_id=target_user.user_id,
            house_id=target_user.house_id,
        ),
    )


@router.callback_query(
    F.data.startswith("admin:delete_user:"),
    AdminState.managing_house,
)
async def delete_selected_user(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Удаляет выбранного пользователя и возвращает экран дома.

    Args:
        callback: Нажатие кнопки удаления пользователя.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        target_user_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid user ID",
            show_alert=True,
        )
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    house_id = delete_admin_user(
        target_user_id,
    )

    if house_id is None:
        await callback.answer(
            t(
                language,
                "admin_user_not_found",
            ),
            show_alert=True,
        )
        return

    await state.update_data(
        current_house_id=house_id,
        target_user_id=None,
    )

    screen = build_admin_house_screen(
        house_id=house_id,
        language=language,
    )

    if screen is None:
        await callback.answer(
            t(
                language,
                "admin_house_not_found",
            ),
            show_alert=True,
        )

        await state.set_state(
            AdminState.browsing_houses,
        )

        await show_admin_houses(
            bot=callback.bot,
            chat_id=callback.message.chat.id,
            user_id=admin_user_id,
            language=language,
            page=1,
        )
        return

    screen_text, keyboard = screen

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        text=screen_text,
        reply_markup=keyboard,
    )

    await callback.answer(
        t(
            language,
            "admin_user_deleted",
        )
    )


@router.callback_query(
    F.data.startswith("admin:clear_history:"),
    AdminState.managing_house,
)
async def clear_selected_house_history(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Очищает историю выполненных задач выбранного дома.

    Args:
        callback: Нажатие кнопки очистки истории.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        house_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid house ID",
            show_alert=True,
        )
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    cleared = clear_admin_house_history(
        house_id,
    )

    if not cleared:
        await callback.answer(
            t(
                language,
                "admin_house_not_found",
            ),
            show_alert=True,
        )
        return

    screen = build_admin_house_screen(
        house_id=house_id,
        language=language,
    )

    if screen is None:
        await callback.answer(
            t(
                language,
                "admin_house_not_found",
            ),
            show_alert=True,
        )
        return

    screen_text, keyboard = screen

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        text=screen_text,
        reply_markup=keyboard,
    )

    await callback.answer(
        t(
            language,
            "admin_history_cleared",
        )
    )


# =============================================================================
# Удаление домашней группы
# =============================================================================

@router.callback_query(
    F.data.startswith("admin:delete_house:"),
    AdminState.managing_house,
)
async def confirm_admin_house_deletion(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Показывает подтверждение удаления дома.

    На этом этапе данные в базе ещё не изменяются.

    Args:
        callback: Нажатие кнопки удаления дома.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        house_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid house ID",
            show_alert=True,
        )
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        text=t(
            language,
            "admin_confirm_delete_house",
            house_id=house_id,
        ),
        reply_markup=(
            get_admin_delete_house_confirmation_menu(
                language=language,
                house_id=house_id,
            )
        ),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:confirm_delete_house:"),
    AdminState.managing_house,
)
async def delete_selected_house(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Окончательно удаляет выбранный дом.

    Args:
        callback: Нажатие кнопки подтверждения.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        house_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid house ID",
            show_alert=True,
        )
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    deleted = delete_admin_house(
        house_id,
    )

    await state.update_data(
        current_house_id=None,
        target_user_id=None,
        current_houses_page=1,
    )

    await state.set_state(
        AdminState.browsing_houses,
    )

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await show_admin_houses(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        language=language,
        page=1,
    )

    if deleted:
        await callback.answer(
            t(
                language,
                "admin_house_deleted",
                house_id=house_id,
            )
        )
    else:
        await callback.answer(
            t(
                language,
                "admin_house_not_found",
            ),
            show_alert=True,
        )


# =============================================================================
# Административный журнал обновлений
# =============================================================================

def build_admin_changelog_screen(
    language: str,
    page: int = 1,
) -> tuple[str, InlineKeyboardMarkup]:
    """Формирует административную страницу журнала.

    Args:
        language: Код языка администратора.
        page: Запрошенная страница.

    Returns:
        Текст журнала и административная клавиатура.
    """
    entries, current_page, total_pages = (
        get_changelog_page(
            page=page,
            page_size=3,
        )
    )

    if not entries:
        screen_text = t(
            language,
            "admin_changelog_empty",
        )
    else:
        lines = [
            t(
                language,
                "admin_changelog_title",
                page=current_page,
                total_pages=total_pages,
            ),
            "",
        ]

        for entry in entries:
            english_text = (
                entry.message_en
                or t(
                    language,
                    "admin_translation_missing",
                )
            )

            lines.extend(
                [
                    f"🇷🇺 {entry.message_ru}",
                    f"🇬🇧 {english_text}",
                    "",
                ]
            )

        screen_text = "\n".join(lines).rstrip()

    return (
        screen_text,
        get_admin_changelog_menu(
            language=language,
            entry_ids=[
                entry.entry_id
                for entry in entries
            ],
            current_page=current_page,
            total_pages=total_pages,
        ),
    )


async def show_admin_changelog_page(
    bot: Bot,
    chat_id: int,
    user_id: int,
    language: str,
    page: int = 1,
) -> None:
    """Показывает административную страницу журнала.

    Args:
        bot: Экземпляр Telegram-бота.
        chat_id: ID чата администратора.
        user_id: Telegram ID администратора.
        language: Код языка интерфейса.
        page: Отображаемая страница.
    """
    screen_text, keyboard = build_admin_changelog_screen(
        language=language,
        page=page,
    )

    await show_interface(
        bot=bot,
        chat_id=chat_id,
        user_id=user_id,
        text=screen_text,
        reply_markup=keyboard,
    )


@router.callback_query(
    F.data == "admin:changelog",
    AdminState.browsing_houses,
)
async def show_admin_changelog(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Открывает административный журнал.

    Args:
        callback: Нажатие кнопки управления журналом.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await state.update_data(
        current_changelog_page=1,
    )

    await show_admin_changelog_page(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        language=language,
        page=1,
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("changelog:page:"),
    F.data.endswith(":admin"),
    AdminState.browsing_houses,
)
async def handle_admin_changelog_pagination(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Переключает страницы административного журнала.

    Args:
        callback: Нажатие кнопки страницы.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""
    parts = callback_data.split(":")

    try:
        page = int(parts[2])
    except (
        IndexError,
        ValueError,
    ):
        page = 1

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await state.update_data(
        current_changelog_page=page,
    )

    await show_admin_changelog_page(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        language=language,
        page=page,
    )

    await callback.answer()


# =============================================================================
# Добавление записи журнала
# =============================================================================

@router.callback_query(
    F.data == "admin:changelog_add",
    AdminState.browsing_houses,
)
async def start_changelog_add(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Начинает добавление двуязычной записи журнала.

    Args:
        callback: Нажатие кнопки добавления записи.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await state.update_data(
        admin_language=language,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        text=t(
            language,
            "admin_enter_changelog_ru",
        ),
    )

    await state.set_state(
        AdminChangelog.waiting_for_russian,
    )

    await callback.answer()


@router.message(
    AdminChangelog.waiting_for_russian,
    ~F.text.startswith("/"),
)
async def add_changelog_russian(
    message: Message,
    state: FSMContext,
) -> None:
    """Сохраняет русский текст и запрашивает английский.

    Args:
        message: Сообщение с русской версией.
        state: Данные создаваемой записи.
    """
    if message.from_user is None:
        return

    admin_user_id = message.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    message_ru = (
        message.text or ""
    ).strip()

    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    if not message_ru:
        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=admin_user_id,
            text=t(
                language,
                "admin_changelog_ru_empty",
            ),
        )
        return

    await state.update_data(
        changelog_message_ru=message_ru,
    )

    await show_interface(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=admin_user_id,
        text=t(
            language,
            "admin_enter_changelog_en",
        ),
    )

    await state.set_state(
        AdminChangelog.waiting_for_english,
    )


@router.message(
    AdminChangelog.waiting_for_english,
    ~F.text.startswith("/"),
)
async def add_changelog_english(
    message: Message,
    state: FSMContext,
) -> None:
    """Сохраняет английский текст и создаёт запись.

    Args:
        message: Сообщение с английской версией.
        state: Данные создаваемой записи.
    """
    if message.from_user is None:
        return

    admin_user_id = message.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )
    message_ru = str(
        state_data.get(
            "changelog_message_ru",
            "",
        )
    )
    message_en = (
        message.text or ""
    ).strip()

    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    if not message_en:
        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=admin_user_id,
            text=t(
                language,
                "admin_changelog_en_empty",
            ),
        )
        return

    if not message_ru:
        await state.set_state(
            AdminChangelog.waiting_for_russian,
        )

        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=admin_user_id,
            text=t(
                language,
                "admin_enter_changelog_ru",
            ),
        )
        return

    add_changelog_entry(
        message_ru=message_ru,
        message_en=message_en,
    )

    await state.clear()

    await state.set_state(
        AdminState.browsing_houses,
    )

    await state.update_data(
        admin_language=language,
        current_changelog_page=1,
    )

    await show_admin_changelog_page(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=admin_user_id,
        language=language,
        page=1,
    )


# =============================================================================
# Редактирование записи журнала
# =============================================================================

@router.callback_query(
    F.data.startswith("changelog:edit:"),
    AdminState.browsing_houses,
)
async def start_changelog_edit(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Начинает редактирование двуязычной записи.

    Args:
        callback: Нажатие кнопки редактирования.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        entry_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid changelog ID",
            show_alert=True,
        )
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    entry = get_changelog_entry(
        entry_id,
    )

    if entry is None:
        await callback.answer(
            t(
                language,
                "admin_changelog_not_found",
            ),
            show_alert=True,
        )
        return

    await state.update_data(
        editing_changelog_id=entry.entry_id,
        editing_changelog_ru=entry.message_ru,
        editing_changelog_en=entry.message_en or "",
    )

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        text=t(
            language,
            "admin_edit_changelog_ru",
        ),
    )

    await state.set_state(
        AdminChangelogEdit.waiting_for_russian,
    )

    await callback.answer()


@router.message(
    AdminChangelogEdit.waiting_for_russian,
    ~F.text.startswith("/"),
)
async def edit_changelog_russian(
    message: Message,
    state: FSMContext,
) -> None:
    """Сохраняет новый русский текст во временном состоянии.

    Args:
        message: Сообщение с русской версией.
        state: Данные редактируемой записи.
    """
    if message.from_user is None:
        return

    admin_user_id = message.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    message_ru = (
        message.text or ""
    ).strip()

    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    if not message_ru:
        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=admin_user_id,
            text=t(
                language,
                "admin_edit_changelog_ru_empty",
            ),
        )
        return

    await state.update_data(
        editing_changelog_ru=message_ru,
    )

    await show_interface(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=admin_user_id,
        text=t(
            language,
            "admin_edit_changelog_en",
        ),
    )

    await state.set_state(
        AdminChangelogEdit.waiting_for_english,
    )


@router.message(
    AdminChangelogEdit.waiting_for_english,
    ~F.text.startswith("/"),
)
async def edit_changelog_english(
    message: Message,
    state: FSMContext,
) -> None:
    """Сохраняет английский текст и обновляет запись.

    Args:
        message: Сообщение с английской версией.
        state: Данные редактируемой записи.
    """
    if message.from_user is None:
        return

    admin_user_id = message.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )
    entry_id = state_data.get(
        "editing_changelog_id",
    )
    message_ru = str(
        state_data.get(
            "editing_changelog_ru",
            "",
        )
    )
    message_en = (
        message.text or ""
    ).strip()

    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    if not message_en:
        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=admin_user_id,
            text=t(
                language,
                "admin_edit_changelog_en_empty",
            ),
        )
        return

    if entry_id is None or not message_ru:
        await state.clear()

        await state.set_state(
            AdminState.browsing_houses,
        )

        await state.update_data(
            admin_language=language,
        )

        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=admin_user_id,
            text=t(
                language,
                "admin_changelog_not_found",
            ),
        )
        return

    updated = update_changelog_entry(
        entry_id=int(entry_id),
        message_ru=message_ru,
        message_en=message_en,
    )

    current_page = int(
        state_data.get(
            "current_changelog_page",
            1,
        )
    )

    await state.clear()

    await state.set_state(
        AdminState.browsing_houses,
    )

    await state.update_data(
        admin_language=language,
        current_changelog_page=current_page,
    )

    await show_admin_changelog_page(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=admin_user_id,
        language=language,
        page=current_page,
    )

    if not updated:
        # Экран журнала уже восстановлен; отдельное сообщение
        # создавать не требуется.
        return


# =============================================================================
# Удаление записи журнала
# =============================================================================

@router.callback_query(
    F.data.startswith("changelog:delete:"),
    AdminState.browsing_houses,
)
async def confirm_changelog_deletion(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Показывает подтверждение удаления записи.

    Args:
        callback: Нажатие кнопки удаления.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        entry_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid changelog ID",
            show_alert=True,
        )
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )

    if get_changelog_entry(entry_id) is None:
        await callback.answer(
            t(
                language,
                "admin_changelog_not_found",
            ),
            show_alert=True,
        )
        return

    await state.update_data(
        deleting_changelog_id=entry_id,
    )

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        text=t(
            language,
            "admin_confirm_delete_changelog",
        ),
        reply_markup=(
            get_changelog_delete_confirmation_menu(
                language,
            )
        ),
    )

    await callback.answer()


@router.callback_query(
    F.data == "changelog:confirm_delete",
    AdminState.browsing_houses,
)
async def delete_selected_changelog_entry(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Удаляет запись после подтверждения.

    Args:
        callback: Нажатие кнопки подтверждения.
        state: Состояние административной панели.
    """
    if callback.message is None:
        await callback.answer()
        return

    admin_user_id = callback.from_user.id
    state_data = await state.get_data()

    language = state_data.get(
        "admin_language",
        get_user_language(admin_user_id),
    )
    entry_id = state_data.get(
        "deleting_changelog_id",
    )
    current_page = int(
        state_data.get(
            "current_changelog_page",
            1,
        )
    )

    if entry_id is None:
        await callback.answer(
            t(
                language,
                "admin_changelog_not_found",
            ),
            show_alert=True,
        )
        return

    deleted = delete_changelog_entry(
        int(entry_id),
    )

    await state.update_data(
        deleting_changelog_id=None,
    )

    remember_interface_message(
        user_id=admin_user_id,
        message_id=callback.message.message_id,
    )

    await show_admin_changelog_page(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=admin_user_id,
        language=language,
        page=current_page,
    )

    if deleted:
        await callback.answer(
            t(
                language,
                "admin_changelog_deleted",
            )
        )
    else:
        await callback.answer(
            t(
                language,
                "admin_changelog_not_found",
            ),
            show_alert=True,
        )