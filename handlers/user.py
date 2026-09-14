"""Пользовательские обработчики Telegram-бота.

Модуль содержит регистрацию, главное меню, профиль, домашнюю группу,
задачи, историю и пользовательский просмотр журнала обновлений.
"""

from html import escape
from aiogram import F, Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)

from database import (
    create_house_with_user,
    get_connection,
    get_house_invite_code,
    get_user_language,
    get_user_profile,
    join_house_by_invite_code,
    set_user_language,
    update_user_name,
    update_user_gender,
    get_house_members,
    get_active_tasks,
    get_active_task,
    delete_active_task,
    complete_active_task,
    get_task_templates_page,
    get_task_template,
    add_template_task_to_active,
    complete_template_task_now,
    add_custom_task_to_active,
    get_owned_custom_task,
    update_custom_task,
    get_completed_tasks_page,
    get_changelog_page,
)

from keyboards import (
    get_back_button,
    get_gender_menu,
    get_language_menu,
    get_main_menu,
    get_profile_edit_menu,
    get_profile_gender_menu,
    get_profile_menu,
    get_registration_language_menu,
    get_active_tasks_menu,
    get_task_detail_menu,
    get_add_task_menu,
    get_standard_tasks_menu,
    get_standard_task_actions_menu,
    get_custom_task_added_menu,
    get_custom_task_preview_menu,
    get_custom_task_xp_menu,
    get_custom_task_edit_menu,
    get_edited_description_menu,
    get_custom_task_edit_xp_menu,
    get_edited_xp_menu,
    get_back_to_tasks_menu,
    get_history_menu,
    get_changelog_menu,

)

from localization import (
    SUPPORTED_LANGUAGES,
    calculate_level,
    make_progress_bar,
    t,
    translate_task_name,
)

from states import (
    CustomTaskCreation,
    CustomTaskEditing,
    ProfileEdit,
    UserRegistration,
)


# =============================================================================
# Роутер пользовательских обработчиков
# =============================================================================

router = Router(
    name="user",
)


# =============================================================================
# Активные сообщения интерфейса
# =============================================================================

# Для каждого пользователя запоминаем ID текущего сообщения с меню.
# Благодаря этому новый экран может заменить или удалить старый.
ACTIVE_INTERFACE_MESSAGES: dict[int, int] = {}


def remember_interface_message(
    user_id: int,
    message_id: int,
) -> None:
    """Запоминает текущее сообщение интерфейса пользователя.

    Args:
        user_id: Telegram ID пользователя.
        message_id: Telegram ID сообщения с текущим экраном.
    """
    ACTIVE_INTERFACE_MESSAGES[user_id] = message_id


def get_interface_message_id(
    user_id: int,
) -> int | None:
    """Возвращает ID текущего интерфейсного сообщения.

    Args:
        user_id: Telegram ID пользователя.

    Returns:
        ID сообщения или ``None``, если оно ещё не было сохранено.
    """
    return ACTIVE_INTERFACE_MESSAGES.get(user_id)


def forget_interface_message(
    user_id: int,
) -> None:
    """Удаляет сохранённый ID интерфейсного сообщения.

    Args:
        user_id: Telegram ID пользователя.
    """
    ACTIVE_INTERFACE_MESSAGES.pop(
        user_id,
        None,
    )


# =============================================================================
# Безопасное удаление сообщений
# =============================================================================

async def delete_message_safely(
    bot: Bot,
    chat_id: int,
    message_id: int,
) -> bool:
    """Пытается удалить сообщение без остановки работы бота.

    Telegram может отказать в удалении, если сообщение уже удалено,
    слишком старое или недоступно боту. Такая ситуация не должна
    приводить к ошибке всего обработчика.

    Args:
        bot: Экземпляр Telegram-бота.
        chat_id: ID чата.
        message_id: ID удаляемого сообщения.

    Returns:
        ``True``, если сообщение удалено. В противном случае ``False``.
    """
    try:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
        return True

    except TelegramBadRequest:
        return False


async def clear_previous_interface(
    bot: Bot,
    chat_id: int,
    user_id: int,
    last_message_id: int,
    limit: int = 100,
) -> None:
    """Удаляет прежний интерфейс и следующие за ним сообщения.

    Функция используется при вводе ``/start``. Она удаляет старое меню,
    сообщения после него и саму команду пользователя.

    Args:
        bot: Экземпляр Telegram-бота.
        chat_id: ID чата.
        user_id: Telegram ID пользователя.
        last_message_id: ID последнего сообщения, которое нужно удалить.
        limit: Максимальное количество проверяемых сообщений.
    """
    old_interface_id = get_interface_message_id(
        user_id,
    )

    if old_interface_id is None:
        await delete_message_safely(
            bot=bot,
            chat_id=chat_id,
            message_id=last_message_id,
        )
        return

    first_message_id = max(
        old_interface_id,
        last_message_id - limit + 1,
    )

    for message_id in range(
        first_message_id,
        last_message_id + 1,
    ):
        await delete_message_safely(
            bot=bot,
            chat_id=chat_id,
            message_id=message_id,
        )

    forget_interface_message(user_id)


async def show_interface(
    bot: Bot,
    chat_id: int,
    user_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> int:
    """Редактирует текущий экран или отправляет новый.

    Если ID активного сообщения известен, функция пытается изменить
    это сообщение. Если редактирование невозможно, отправляется новое.

    Args:
        bot: Экземпляр Telegram-бота.
        chat_id: ID чата.
        user_id: Telegram ID пользователя.
        text: Новый текст экрана.
        reply_markup: Клавиатура нового экрана.

    Returns:
        ID отображаемого интерфейсного сообщения.
    """
    interface_message_id = get_interface_message_id(
        user_id,
    )

    if interface_message_id is not None:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=interface_message_id,
                text=text,
                reply_markup=reply_markup,
            )
            return interface_message_id

        except TelegramBadRequest as error:
            # Telegram возвращает ошибку, если экран уже содержит
            # точно такой же текст и такую же клавиатуру.
            if "message is not modified" in str(error):
                return interface_message_id

    sent_message = await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=reply_markup,
    )

    remember_interface_message(
        user_id=user_id,
        message_id=sent_message.message_id,
    )

    return sent_message.message_id


# =============================================================================
# Проверка регистрации
# =============================================================================

def user_exists(user_id: int) -> bool:
    """Проверяет наличие пользователя в базе данных.

    Args:
        user_id: Telegram ID пользователя.

    Returns:
        ``True``, если пользователь уже зарегистрирован.
    """
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM users
            WHERE tg_id = ?
            """,
            (user_id,),
        ).fetchone()

    return row is not None


# =============================================================================
# Команда /start
# =============================================================================

@router.message(F.text == "/start")
async def cmd_start(
    message: Message,
    state: FSMContext,
) -> None:
    """Очищает старый интерфейс и запускает меню или регистрацию.

    Для зарегистрированного пользователя показывается главное меню.
    Новый пользователь сначала выбирает язык интерфейса.

    Args:
        message: Сообщение с командой ``/start``.
        state: Текущее состояние диалога пользователя.
    """
    if message.from_user is None:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    await clear_previous_interface(
        bot=message.bot,
        chat_id=chat_id,
        user_id=user_id,
        last_message_id=message.message_id,
    )

    if user_exists(user_id):
        # Старое состояние могло сохраниться после незавершённого
        # действия, поэтому при новом запуске очищаем его.
        await state.clear()

        language = get_user_language(user_id)

        sent_message = await message.answer(
            t(language, "welcome_back"),
            reply_markup=get_main_menu(language),
        )

    else:
        await state.clear()

        sent_message = await message.answer(
            "🌐 Выберите язык / Select a language:",
            reply_markup=get_registration_language_menu(),
        )

        await state.set_state(
            UserRegistration.waiting_for_language,
        )

    remember_interface_message(
        user_id=user_id,
        message_id=sent_message.message_id,
    )


# =============================================================================
# Регистрация: выбор языка
# =============================================================================

@router.callback_query(
    F.data.startswith("registration:language:"),
    UserRegistration.waiting_for_language,
)
async def process_registration_language(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Сохраняет язык, выбранный в начале регистрации.

    Язык пока записывается во временное состояние FSM. В базу данных
    он попадёт после завершения всей регистрации пользователя.

    Args:
        callback: Нажатие кнопки выбора языка.
        state: Текущее состояние регистрации.
    """
    callback_data = callback.data or ""
    language = callback_data.rsplit(":", maxsplit=1)[-1]

    if language not in SUPPORTED_LANGUAGES:
        await callback.answer(
            "Unsupported language",
            show_alert=True,
        )
        return

    await state.update_data(
        language=language,
    )

    if callback.message is not None:
        await callback.message.edit_text(
            t(language, "registration_name_prompt"),
        )

    await state.set_state(
        UserRegistration.waiting_for_name,
    )

    await callback.answer()


# =============================================================================
# Регистрация: ввод имени
# =============================================================================

@router.message(
    UserRegistration.waiting_for_name,
)
async def process_name(
    message: Message,
    state: FSMContext,
) -> None:
    """Сохраняет имя и показывает выбор пола.

    Сообщение пользователя удаляется, а существующий экран регистрации
    редактируется. Благодаря этому регистрация остаётся в одном
    интерфейсном сообщении.

    Args:
        message: Сообщение пользователя с именем.
        state: Текущее состояние регистрации.
    """
    if message.from_user is None:
        return

    user_id = message.from_user.id

    state_data = await state.get_data()
    language = state_data.get(
        "language",
        "ru",
    )

    user_name = (
        message.text or ""
    ).strip()

    if len(user_name) < 2:
        await delete_message_safely(
            bot=message.bot,
            chat_id=message.chat.id,
            message_id=message.message_id,
        )

        interface_message_id = get_interface_message_id(
            user_id,
        )

        if interface_message_id is not None:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=interface_message_id,
                    text=t(language, "name_too_short"),
                )
            except TelegramBadRequest:
                pass

        return

    await state.update_data(
        name=user_name,
    )

    # Убираем сообщение, в котором пользователь написал имя.
    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    interface_message_id = get_interface_message_id(
        user_id,
    )

    if interface_message_id is not None:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=interface_message_id,
                text=t(language, "gender_prompt"),
                reply_markup=get_gender_menu(language),
            )

        except TelegramBadRequest:
            sent_message = await message.answer(
                t(language, "gender_prompt"),
                reply_markup=get_gender_menu(language),
            )

            remember_interface_message(
                user_id=user_id,
                message_id=sent_message.message_id,
            )

    else:
        sent_message = await message.answer(
            t(language, "gender_prompt"),
            reply_markup=get_gender_menu(language),
        )

        remember_interface_message(
            user_id=user_id,
            message_id=sent_message.message_id,
        )

    await state.set_state(
        UserRegistration.waiting_for_gender,
    )


# =============================================================================
# Регистрация: выбор пола
# =============================================================================

@router.callback_query(
    F.data.startswith("gender:"),
    UserRegistration.waiting_for_gender,
)
async def process_gender(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Сохраняет пол и переходит к выбору домашней группы.

    Args:
        callback: Нажатие кнопки выбора пола.
        state: Текущее состояние регистрации.
    """
    callback_data = callback.data or ""
    gender = callback_data.rsplit(":", maxsplit=1)[-1]

    if gender not in {"male", "female"}:
        await callback.answer(
            "Unknown gender",
            show_alert=True,
        )
        return

    await state.update_data(
        gender=gender,
    )

    state_data = await state.get_data()
    language = state_data.get(
        "language",
        "ru",
    )

    if callback.message is not None:
        await callback.message.edit_text(
            t(language, "house_choice"),
        )

    await state.set_state(
        UserRegistration.waiting_for_invite_code,
    )

    await callback.answer()


# =============================================================================
# Регистрация: создание дома или присоединение
# =============================================================================

@router.message(
    UserRegistration.waiting_for_invite_code,
)
async def process_invite_or_create(
    message: Message,
    state: FSMContext,
) -> None:
    """Завершает регистрацию пользователя.

    Пользователь может создать новую домашнюю группу словом
    ``создать`` или ``create`` либо ввести код существующей группы.

    Args:
        message: Сообщение со словом создания или кодом приглашения.
        state: Данные, собранные во время регистрации.
    """
    if message.from_user is None:
        return

    user_id = message.from_user.id
    entered_text = (
        message.text or ""
    ).strip()

    normalized_text = entered_text.lower()

    state_data = await state.get_data()

    user_name = state_data["name"]
    user_gender = state_data.get(
        "gender",
        "male",
    )
    language = state_data.get(
        "language",
        "ru",
    )

    # Убираем сообщение пользователя с командой или кодом.
    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    if normalized_text in {"создать", "create"}:
        invite_code = create_house_with_user(
            user_id=user_id,
            name=user_name,
            gender=user_gender,
            language=language,
        )

        result_text = t(
            language,
            "house_created",
            code=invite_code,
        )

    else:
        joined = join_house_by_invite_code(
            user_id=user_id,
            name=user_name,
            gender=user_gender,
            language=language,
            invite_code=entered_text,
        )

        if not joined:
            interface_message_id = get_interface_message_id(
                user_id,
            )

            if interface_message_id is not None:
                try:
                    await message.bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=interface_message_id,
                        text=t(language, "invalid_house_code"),
                    )
                except TelegramBadRequest:
                    pass

            return

        result_text = t(
            language,
            "joined_house",
        )

    await state.clear()

    interface_message_id = get_interface_message_id(
        user_id,
    )

    if interface_message_id is not None:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=interface_message_id,
                text=result_text,
                reply_markup=get_main_menu(language),
            )
            return

        except TelegramBadRequest:
            pass

    sent_message = await message.answer(
        result_text,
        reply_markup=get_main_menu(language),
    )

    remember_interface_message(
        user_id=user_id,
        message_id=sent_message.message_id,
    )


# =============================================================================
# Главное меню
# =============================================================================

@router.message(F.text == "/menu")
async def cmd_menu(
    message: Message,
    state: FSMContext,
) -> None:
    """Открывает главное меню и удаляет введённую команду.

    Args:
        message: Сообщение с командой ``/menu``.
        state: Текущее состояние пользователя.
    """
    if message.from_user is None:
        return

    user_id = message.from_user.id

    if not user_exists(user_id):
        # Незарегистрированного пользователя направляем в обычный
        # процесс регистрации.
        await cmd_start(
            message=message,
            state=state,
        )
        return

    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    await state.clear()

    language = get_user_language(user_id)

    await show_interface(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=user_id,
        text=t(language, "main_title"),
        reply_markup=get_main_menu(language),
    )


@router.callback_query(
    F.data == "menu:main",
)
async def back_to_menu(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Возвращает пользователя в главное меню.

    Args:
        callback: Нажатие кнопки возврата.
        state: Текущее состояние пользователя.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id

    await state.clear()

    # После перезапуска словарь может не помнить старое меню.
    # Нажатая кнопка сообщает нам его актуальный ID.
    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    language = get_user_language(user_id)

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=t(language, "main_title"),
        reply_markup=get_main_menu(language),
    )

    await callback.answer()


# =============================================================================
# Настройки языка
# =============================================================================

@router.callback_query(
    F.data == "menu:language",
)
async def show_language_menu(
    callback: CallbackQuery,
) -> None:
    """Показывает меню выбора языка.

    Args:
        callback: Нажатие пункта языка в главном меню.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=t(language, "language_title"),
        reply_markup=get_language_menu(),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("language:set:"),
)
async def change_language(
    callback: CallbackQuery,
) -> None:
    """Сохраняет новый язык и возвращает главное меню.

    Args:
        callback: Нажатие кнопки русского или английского языка.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""
    language = callback_data.rsplit(":", maxsplit=1)[-1]

    if language not in SUPPORTED_LANGUAGES:
        await callback.answer(
            "Unsupported language",
            show_alert=True,
        )
        return

    language_changed = set_user_language(
        user_id=callback.from_user.id,
        language=language,
    )

    if not language_changed:
        await callback.answer(
            t(language, "register_first"),
            show_alert=True,
        )
        return

    user_id = callback.from_user.id

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=(
            t(language, "language_changed")
            + "\n\n"
            + t(language, "main_title")
        ),
        reply_markup=get_main_menu(language),
    )

    await callback.answer()


# =============================================================================
# Код приглашения
# =============================================================================

@router.callback_query(
    F.data == "menu:invite",
)
async def show_invite_code(
    callback: CallbackQuery,
) -> None:
    """Показывает код приглашения домашней группы.

    Args:
        callback: Нажатие пункта с кодом приглашения.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    invite_code = get_house_invite_code(
        user_id,
    )

    if invite_code is None:
        screen_text = t(
            language,
            "not_in_house",
        )
    else:
        screen_text = t(
            language,
            "invite_code_message",
            code=invite_code,
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
        reply_markup=get_back_button(language),
    )

    await callback.answer()    


# =============================================================================
# Профиль пользователя
# =============================================================================

def build_user_profile_screen(
    user_id: int,
    language: str,
) -> tuple[str, InlineKeyboardMarkup]:
    """Формирует текст и клавиатуру профиля.

    Args:
        user_id: Telegram ID пользователя.
        language: Код языка интерфейса.

    Returns:
        Текст профиля и соответствующая клавиатура.
    """
    profile = get_user_profile(
        user_id,
    )

    if profile is None:
        return (
            t(language, "profile_not_found"),
            get_back_button(language),
        )

    gender_text = t(
        language,
        f"gender_{profile.gender}",
    )

    level_info = calculate_level(
        profile.xp,
        language,
    )

    progress_bar = make_progress_bar(
        level_info["xp_current"],
        level_info["xp_for_next"],
    )

    profile_level_text = t(
        language,
        "profile_level",
        level=level_info["level"],
        emoji=level_info["emoji"],
        title=level_info["title"],
    )

    screen_text = (
        f"👤 <b>{escape(profile.name)}</b>\n"
        f"{t(language, 'profile_gender', gender=gender_text)}\n\n"
        f"{profile_level_text}\n"
        f"XP: {level_info['xp_current']} / "
        f"{level_info['xp_for_next']}\n"
        f"{progress_bar}"
    )

    return (
        screen_text,
        get_profile_menu(language),
    )


@router.callback_query(
    F.data == "menu:profile",
)
async def show_user_profile(
    callback: CallbackQuery,
) -> None:
    """Показывает имя, пол, уровень и опыт пользователя.

    Args:
        callback: Нажатие пункта профиля в главном меню.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    screen_text, keyboard = build_user_profile_screen(
        user_id=user_id,
        language=language,
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


# =============================================================================
# Редактирование профиля
# =============================================================================

@router.callback_query(
    F.data == "profile:edit",
)
async def show_profile_edit_menu(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Показывает выбор поля для редактирования.

    Args:
        callback: Нажатие кнопки редактирования профиля.
        state: Текущее состояние пользователя.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await state.update_data(
        profile_message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=t(language, "profile_edit_title"),
        reply_markup=get_profile_edit_menu(language),
    )

    await callback.answer()


@router.callback_query(
    F.data == "profile:edit_name",
)
async def edit_name_start(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Просит пользователя ввести новое имя.

    Args:
        callback: Нажатие кнопки изменения имени.
        state: Текущее состояние пользователя.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await state.update_data(
        profile_message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=t(language, "enter_new_name"),
    )

    await state.set_state(
        ProfileEdit.editing_name,
    )

    await callback.answer()
    

@router.message(
    ProfileEdit.editing_name,
)
async def edit_name_save(
    message: Message,
    state: FSMContext,
) -> None:
    """Проверяет и сохраняет новое имя пользователя.

    Args:
        message: Сообщение с новым именем.
        state: Текущее состояние редактирования профиля.
    """
    if message.from_user is None:
        return

    user_id = message.from_user.id
    language = get_user_language(user_id)

    new_name = (
        message.text or ""
    ).strip()

    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    if len(new_name) < 2:
        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=user_id,
            text=t(language, "edit_name_too_short"),
        )
        return

    name_updated = update_user_name(
        user_id=user_id,
        new_name=new_name,
    )

    if not name_updated:
        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=user_id,
            text=t(language, "profile_not_found"),
            reply_markup=get_back_button(language),
        )

        await state.clear()
        return

    await state.clear()

    screen_text, keyboard = build_user_profile_screen(
        user_id=user_id,
        language=language,
    )

    await show_interface(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=user_id,
        text=screen_text,
        reply_markup=keyboard,
    )


@router.callback_query(
    F.data == "profile:edit_gender",
)
async def edit_gender_start(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Показывает выбор нового пола.

    Args:
        callback: Нажатие кнопки изменения пола.
        state: Текущее состояние пользователя.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await state.update_data(
        profile_message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=t(language, "select_new_gender"),
        reply_markup=get_profile_gender_menu(language),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("profile:set_gender:"),
)
async def edit_gender_save(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Сохраняет новый пол и возвращает профиль.

    Args:
        callback: Нажатие кнопки с новым значением пола.
        state: Текущее состояние пользователя.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""
    gender = callback_data.rsplit(":", maxsplit=1)[-1]

    if gender not in {"male", "female"}:
        await callback.answer(
            "Invalid gender",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    gender_updated = update_user_gender(
        user_id=user_id,
        gender=gender,
    )

    if not gender_updated:
        await callback.answer(
            t(language, "profile_not_found"),
            show_alert=True,
        )
        return

    await state.clear()

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    screen_text, keyboard = build_user_profile_screen(
        user_id=user_id,
        language=language,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=screen_text,
        reply_markup=keyboard,
    )

    await callback.answer()


# =============================================================================
# Домашняя группа
# =============================================================================

def build_house_screen(
    user_id: int,
    language: str,
) -> tuple[str, InlineKeyboardMarkup]:
    """Формирует список участников домашней группы.

    Args:
        user_id: Telegram ID пользователя, открывшего экран.
        language: Код языка интерфейса.

    Returns:
        Текст со списком участников и клавиатура возврата.
    """
    members = get_house_members(
        user_id,
    )

    if members is None:
        return (
            t(language, "not_in_house"),
            get_back_button(language),
        )

    if not members:
        return (
            t(language, "house_empty"),
            get_back_button(language),
        )

    lines = [
        t(language, "house_title"),
        "",
    ]

    for position, member in enumerate(
        members,
        start=1,
    ):
        level_info = calculate_level(
            member.xp,
            language,
        )

        progress_bar = make_progress_bar(
            level_info["xp_current"],
            level_info["xp_for_next"],
        )

        marker = (
            t(language, "you_marker")
            if member.user_id == user_id
            else ""
        )

        level_text = t(
            language,
            "member_level",
            level=level_info["level"],
            emoji=level_info["emoji"],
            title=level_info["title"],
        )

        lines.extend(
            [
                (
                    f"{position}. "
                    f"<b>{escape(member.name)}</b>"
                    f"{marker}"
                ),
                f"   {level_text}",
                (
                    f"   XP: {level_info['xp_current']} / "
                    f"{level_info['xp_for_next']}"
                ),
                f"   {progress_bar}",
                "",
            ]
        )

    return (
        "\n".join(lines).rstrip(),
        get_back_button(language),
    )


@router.callback_query(
    F.data == "menu:house",
)
async def show_house(
    callback: CallbackQuery,
) -> None:
    """Показывает участников домашней группы.

    Args:
        callback: Нажатие пункта «Мой дом».
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    screen_text, keyboard = build_house_screen(
        user_id=user_id,
        language=language,
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


# =============================================================================
# Активные задачи
# =============================================================================

def build_active_tasks_screen(
    user_id: int,
    language: str,
) -> tuple[str, InlineKeyboardMarkup]:
    """Формирует экран активных задач.

    Args:
        user_id: Telegram ID пользователя.
        language: Код языка интерфейса.

    Returns:
        Текст списка задач и клавиатура.
    """
    tasks = get_active_tasks(
        user_id,
    )

    if tasks is None:
        return (
            t(language, "not_in_house"),
            get_back_button(language),
        )

    if not tasks:
        return (
            t(language, "active_tasks_empty"),
            get_back_button(language),
        )

    lines = [
        t(language, "active_tasks_title"),
        "",
    ]

    keyboard_tasks: list[tuple[int, str]] = []

    for task in tasks:
        translated_name = translate_task_name(
            task.name,
            language,
        )

        lines.append(
            t(
                language,
                "task_added_by",
                name=escape(translated_name),
                xp=task.xp,
                assigned_by=escape(
                    task.assigned_by_name,
                ),
            )
        )

        keyboard_tasks.append(
            (
                task.task_id,
                translated_name,
            )
        )

    return (
        "\n".join(lines),
        get_active_tasks_menu(
            language=language,
            tasks=keyboard_tasks,
        ),
    )


@router.callback_query(
    F.data == "menu:tasks",
)
async def show_active_tasks(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Показывает активные задачи домашней группы.

    Args:
        callback: Нажатие пункта активных задач.
        state: Текущее состояние пользователя.
    """
    if callback.message is None:
        await callback.answer()
        return
    # Переход к списку задач отменяет незавершённое создание
    # или редактирование пользовательской задачи.
    await state.clear()

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    screen_text, keyboard = build_active_tasks_screen(
        user_id=user_id,
        language=language,
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
    F.data.startswith("task:detail:"),
)
async def show_task_detail(
    callback: CallbackQuery,
) -> None:
    """Показывает карточку выбранной активной задачи.

    Args:
        callback: Нажатие кнопки активной задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        task_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid task ID",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    task = get_active_task(
        user_id=user_id,
        task_id=task_id,
    )

    if task is None:
        await callback.answer(
            t(language, "task_not_found"),
            show_alert=True,
        )
        return

    translated_name = translate_task_name(
        task.name,
        language,
    )

    screen_text = t(
        language,
        "active_task_card",
        name=escape(translated_name),
        xp=task.xp,
        assigned_by=escape(
            task.assigned_by_name,
        ),
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
        reply_markup=get_task_detail_menu(
            language=language,
            task_id=task.task_id,
            is_custom=task.template_id is None,
        ),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("delete_task:"),
)
async def handle_delete_task(
    callback: CallbackQuery,
) -> None:
    """Удаляет задачу и обновляет список активных задач.

    Args:
        callback: Нажатие кнопки удаления задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        task_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid task ID",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    deleted = delete_active_task(
        user_id=user_id,
        task_id=task_id,
    )

    if deleted:
        await callback.answer(
            t(language, "task_deleted"),
        )
    else:
        await callback.answer(
            t(language, "task_no_longer_active"),
            show_alert=True,
        )

    screen_text, keyboard = build_active_tasks_screen(
        user_id=user_id,
        language=language,
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


@router.callback_query(
    F.data.startswith("complete_task:"),
)
async def handle_complete_task(
    callback: CallbackQuery,
) -> None:
    """Выполняет задачу, начисляет XP и обновляет список.

    Args:
        callback: Нажатие кнопки выполнения задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        task_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid task ID",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    result = complete_active_task(
        user_id=user_id,
        task_id=task_id,
    )

    tasks_text, keyboard = build_active_tasks_screen(
        user_id=user_id,
        language=language,
    )

    if result is None:
        screen_text = tasks_text

        await callback.answer(
            t(language, "task_no_longer_active"),
            show_alert=True,
        )

    else:
        task_name = (
            translate_task_name(
                result.name,
                language,
            )
            if result.is_standard
            else result.name
        )

        completion_text = t(
            language,
            "task_completed_now",
            name=escape(task_name),
            xp=result.xp,
        )

        screen_text = (
            completion_text
            + tasks_text
        )

        await callback.answer()

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


@router.callback_query(
    F.data == "menu:addtask",
)
async def show_add_task_menu(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Показывает выбор типа новой задачи.

    Args:
        callback: Нажатие пункта добавления задачи.
        state: Текущее состояние пользователя.
    """
    if callback.message is None:
        await callback.answer()
        return
    # Возврат к выбору типа задачи отменяет предыдущий
    # незавершённый сценарий.
    await state.clear()

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    if not user_exists(user_id):
        await callback.answer(
            t(language, "register_first"),
            show_alert=True,
        )
        return

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=t(language, "add_task_title"),
        reply_markup=get_add_task_menu(language),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("addtask:standard:"),
)
async def show_standard_tasks(
    callback: CallbackQuery,
) -> None:
    """Показывает страницу стандартных задач.

    Args:
        callback: Нажатие кнопки открытия или смены страницы.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        requested_page = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        requested_page = 1

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    if not user_exists(user_id):
        await callback.answer(
            t(language, "register_first"),
            show_alert=True,
        )
        return

    templates, current_page, total_pages = (
        get_task_templates_page(
            page=requested_page,
            page_size=7,
        )
    )

    if templates:
        screen_text = t(
            language,
            "standard_tasks_page",
            page=current_page,
            total_pages=total_pages,
        )
    else:
        screen_text = t(
            language,
            "standard_tasks_empty",
        )

    keyboard_tasks = [
        (
            template.template_id,
            translate_task_name(
                template.name,
                language,
            ),
            template.xp,
        )
        for template in templates
    ]

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=screen_text,
        reply_markup=get_standard_tasks_menu(
            language=language,
            tasks=keyboard_tasks,
            current_page=current_page,
            total_pages=total_pages,
        ),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("add_task:"),
)
async def show_standard_task_actions(
    callback: CallbackQuery,
) -> None:
    """Показывает действия для стандартной задачи.

    Args:
        callback: Нажатие кнопки стандартной задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        template_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid task ID",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    if not user_exists(user_id):
        await callback.answer(
            t(language, "not_in_house"),
            show_alert=True,
        )
        return

    template = get_task_template(
        template_id,
    )

    if template is None:
        await callback.answer(
            t(language, "task_not_found"),
            show_alert=True,
        )
        return

    translated_name = translate_task_name(
        template.name,
        language,
    )

    screen_text = t(
        language,
        "task_card",
        name=escape(translated_name),
        xp=template.xp,
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
        reply_markup=get_standard_task_actions_menu(
            language=language,
            template_id=template.template_id,
        ),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("add_to_active:"),
)
async def add_standard_task_to_active(
    callback: CallbackQuery,
) -> None:
    """Добавляет стандартную задачу в активный список.

    Args:
        callback: Нажатие кнопки добавления задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        template_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid task ID",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    if not user_exists(user_id):
        await callback.answer(
            t(language, "not_in_house"),
            show_alert=True,
        )
        return

    template = add_template_task_to_active(
        user_id=user_id,
        template_id=template_id,
    )

    if template is None:
        await callback.answer(
            t(language, "task_not_found"),
            show_alert=True,
        )
        return

    translated_name = translate_task_name(
        template.name,
        language,
    )

    screen_text = (
        t(
            language,
            "task_added_to_active",
            name=escape(translated_name),
        )
        + t(language, "add_task_title")
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
        reply_markup=get_add_task_menu(language),
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("complete_now:"),
)
async def complete_standard_task_now(
    callback: CallbackQuery,
) -> None:
    """Сразу выполняет стандартную задачу и начисляет XP.

    Args:
        callback: Нажатие кнопки немедленного выполнения.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        template_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid task ID",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    if not user_exists(user_id):
        await callback.answer(
            t(language, "not_in_house"),
            show_alert=True,
        )
        return

    result = complete_template_task_now(
        user_id=user_id,
        template_id=template_id,
    )

    if result is None:
        await callback.answer(
            t(language, "task_not_found"),
            show_alert=True,
        )
        return

    translated_name = translate_task_name(
        result.name,
        language,
    )

    screen_text = (
        t(
            language,
            "task_completed_now",
            name=escape(translated_name),
            xp=result.xp,
        )
        + t(language, "add_task_title")
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
        reply_markup=get_add_task_menu(language),
    )

    await callback.answer()


# =============================================================================
# Создание пользовательской задачи
# =============================================================================

@router.callback_query(
    F.data == "addtask:custom",
)
async def start_custom_task(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Начинает создание пользовательской задачи.

    Args:
        callback: Нажатие кнопки создания своей задачи.
        state: Текущее состояние пользователя.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    if not user_exists(user_id):
        await callback.answer(
            t(language, "not_in_house"),
            show_alert=True,
        )
        return

    remember_interface_message(
        user_id=user_id,
        message_id=callback.message.message_id,
    )

    await state.clear()

    await show_interface(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        text=t(
            language,
            "custom_description_prompt",
        ),
    )

    await state.set_state(
        CustomTaskCreation.waiting_for_description,
    )

    await callback.answer()


@router.message(
    CustomTaskCreation.waiting_for_description,
)
async def process_custom_task_description(
    message: Message,
    state: FSMContext,
) -> None:
    """Проверяет описание и показывает предварительный просмотр.

    Args:
        message: Сообщение с описанием задачи.
        state: Текущее состояние создания задачи.
    """
    if message.from_user is None:
        return

    user_id = message.from_user.id
    language = get_user_language(user_id)

    description = (
        message.text or ""
    ).strip()

    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    if len(description) < 3:
        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=user_id,
            text=t(
                language,
                "description_too_short",
            ),
        )
        return

    await state.update_data(
        task_description=description,
    )

    await show_interface(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=user_id,
        text=t(
            language,
            "task_preview",
            description=escape(description),
        ),
        reply_markup=get_custom_task_preview_menu(
            language,
        ),
    )


@router.callback_query(
    F.data == "custom_task:edit_desc",
)
async def edit_custom_task_description(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Возвращает пользователя к вводу описания.

    Args:
        callback: Нажатие кнопки изменения описания.
        state: Текущее состояние создания задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

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
            "custom_new_description",
        ),
    )

    await state.set_state(
        CustomTaskCreation.waiting_for_description,
    )

    await callback.answer()


@router.callback_query(
    F.data == "custom_task:choose_xp",
)
async def choose_custom_task_xp(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Показывает выбор награды за пользовательскую задачу.

    Args:
        callback: Нажатие кнопки продолжения.
        state: Текущее состояние создания задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    state_data = await state.get_data()
    description = state_data.get(
        "task_description",
    )

    if not description:
        await callback.answer(
            t(language, "description_too_short"),
            show_alert=True,
        )

        await state.set_state(
            CustomTaskCreation.waiting_for_description,
        )
        return

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
            "custom_choose_xp",
        ),
        reply_markup=get_custom_task_xp_menu(
            language,
        ),
    )

    await state.set_state(
        CustomTaskCreation.waiting_for_xp,
    )

    await callback.answer()


@router.callback_query(
    F.data == "custom_task:back_to_desc",
)
async def back_to_custom_task_preview(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Возвращает предварительный просмотр описания.

    Args:
        callback: Нажатие кнопки возврата от выбора XP.
        state: Текущее состояние создания задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    state_data = await state.get_data()
    description = state_data.get(
        "task_description",
    )

    if not description:
        await show_interface(
            bot=callback.bot,
            chat_id=callback.message.chat.id,
            user_id=user_id,
            text=t(
                language,
                "custom_description_prompt",
            ),
        )

        await state.set_state(
            CustomTaskCreation.waiting_for_description,
        )

        await callback.answer()
        return

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
            "task_preview",
            description=escape(description),
        ),
        reply_markup=get_custom_task_preview_menu(
            language,
        ),
    )

    await state.set_state(
        CustomTaskCreation.waiting_for_description,
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("custom_xp:"),
    CustomTaskCreation.waiting_for_xp,
)
async def save_custom_task(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Сохраняет пользовательскую задачу с выбранным XP.

    Args:
        callback: Нажатие кнопки с наградой.
        state: Данные создаваемой задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        xp = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid XP value",
            show_alert=True,
        )
        return

    if xp not in {
        5,
        10,
        15,
        20,
    }:
        await callback.answer(
            "Invalid XP value",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    state_data = await state.get_data()
    description = state_data.get(
        "task_description",
    )

    if not description:
        await callback.answer(
            t(language, "description_not_found"),
            show_alert=True,
        )
        return

    task_id = add_custom_task_to_active(
        user_id=user_id,
        description=description,
        xp=xp,
    )

    if task_id is None:
        await callback.answer(
            t(language, "not_in_house"),
            show_alert=True,
        )
        return

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
            "custom_task_added",
            description=escape(description),
            xp=xp,
        ),
        reply_markup=get_custom_task_added_menu(
            language=language,
            task_id=task_id,
        ),
    )

    await callback.answer()


# =============================================================================
# Редактирование пользовательской задачи
# =============================================================================

@router.callback_query(
    F.data.startswith("edit_custom_task:"),
)
async def edit_custom_task_start(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Открывает меню редактирования пользовательской задачи.

    Args:
        callback: Нажатие кнопки редактирования задачи.
        state: Текущее состояние пользователя.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        task_id = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid task ID",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    task = get_owned_custom_task(
        user_id=user_id,
        task_id=task_id,
    )

    if task is None:
        await callback.answer(
            t(language, "task_not_found"),
            show_alert=True,
        )

        screen_text, keyboard = build_active_tasks_screen(
            user_id=user_id,
            language=language,
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
        return

    await state.update_data(
        editing_task_id=task.task_id,
        task_description=task.name,
        task_xp=task.xp,
    )

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
            "edit_task_menu",
            description=escape(task.name),
            xp=task.xp,
        ),
        reply_markup=get_custom_task_edit_menu(
            language,
        ),
    )

    await callback.answer()


@router.callback_query(
    F.data == "edit_desc",
)
async def edit_custom_description_start(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Просит ввести новое описание задачи.

    Args:
        callback: Нажатие кнопки изменения описания.
        state: Данные редактируемой задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    state_data = await state.get_data()

    if state_data.get("editing_task_id") is None:
        await callback.answer(
            t(language, "task_not_found"),
            show_alert=True,
        )
        return

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
            "enter_new_description",
        ),
    )

    await state.set_state(
        CustomTaskEditing.waiting_for_description,
    )

    await callback.answer()


@router.message(
    CustomTaskEditing.waiting_for_description,
)
async def process_edited_description(
    message: Message,
    state: FSMContext,
) -> None:
    """Проверяет и временно сохраняет новое описание.

    Args:
        message: Сообщение с новым описанием.
        state: Данные редактируемой задачи.
    """
    if message.from_user is None:
        return

    user_id = message.from_user.id
    language = get_user_language(user_id)

    description = (
        message.text or ""
    ).strip()

    await delete_message_safely(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=message.message_id,
    )

    if len(description) < 3:
        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=user_id,
            text=t(
                language,
                "description_too_short",
            ),
        )
        return

    state_data = await state.get_data()

    if state_data.get("editing_task_id") is None:
        await state.clear()

        await show_interface(
            bot=message.bot,
            chat_id=message.chat.id,
            user_id=user_id,
            text=t(
                language,
                "task_not_found",
            ),
            reply_markup=get_back_button(language),
        )
        return

    current_xp = int(
        state_data.get(
            "task_xp",
            10,
        )
    )

    await state.update_data(
        task_description=description,
    )

    await show_interface(
        bot=message.bot,
        chat_id=message.chat.id,
        user_id=user_id,
        text=t(
            language,
            "updated_description",
            description=escape(description),
            xp=current_xp,
        ),
        reply_markup=get_edited_description_menu(
            language,
        ),
    )


@router.callback_query(
    F.data == "edit_xp",
)
async def edit_custom_xp_start(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Показывает выбор нового количества XP.

    Args:
        callback: Нажатие кнопки изменения XP.
        state: Данные редактируемой задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    state_data = await state.get_data()

    if state_data.get("editing_task_id") is None:
        await callback.answer(
            t(language, "task_not_found"),
            show_alert=True,
        )
        return

    description = str(
        state_data.get(
            "task_description",
            "...",
        )
    )
    current_xp = int(
        state_data.get(
            "task_xp",
            10,
        )
    )

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
            "current_xp_card",
            description=escape(description),
            xp=current_xp,
        ),
        reply_markup=get_custom_task_edit_xp_menu(
            language,
        ),
    )

    await state.set_state(
        CustomTaskEditing.choosing_xp,
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("set_xp:"),
    CustomTaskEditing.choosing_xp,
)
async def set_custom_task_xp(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Временно сохраняет выбранный XP.

    Args:
        callback: Нажатие кнопки с новым XP.
        state: Данные редактируемой задачи.
    """
    if callback.message is None:
        await callback.answer()
        return

    callback_data = callback.data or ""

    try:
        new_xp = int(
            callback_data.rsplit(
                ":",
                maxsplit=1,
            )[-1]
        )
    except ValueError:
        await callback.answer(
            "Invalid XP value",
            show_alert=True,
        )
        return

    if new_xp not in {
        5,
        10,
        15,
        20,
    }:
        await callback.answer(
            "Invalid XP value",
            show_alert=True,
        )
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    state_data = await state.get_data()

    if state_data.get("editing_task_id") is None:
        await callback.answer(
            t(language, "task_not_found"),
            show_alert=True,
        )
        return

    description = str(
        state_data.get(
            "task_description",
            "...",
        )
    )

    await state.update_data(
        task_xp=new_xp,
    )

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
            "new_xp_card",
            description=escape(description),
            xp=new_xp,
        ),
        reply_markup=get_edited_xp_menu(
            language,
        ),
    )

    await callback.answer()


@router.callback_query(
    F.data == "save_edited_task",
)
async def save_edited_task(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Сохраняет изменения пользовательской задачи.

    Args:
        callback: Нажатие кнопки сохранения.
        state: Накопленные данные редактирования.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    state_data = await state.get_data()

    task_id = state_data.get(
        "editing_task_id",
    )
    description = state_data.get(
        "task_description",
    )
    xp = state_data.get(
        "task_xp",
    )

    if (
        task_id is None
        or not description
        or xp is None
    ):
        await callback.answer(
            t(language, "edit_data_missing"),
            show_alert=True,
        )
        return

    try:
        updated = update_custom_task(
            user_id=user_id,
            task_id=int(task_id),
            description=str(description),
            xp=int(xp),
        )
    except ValueError:
        await callback.answer(
            t(language, "edit_data_missing"),
            show_alert=True,
        )
        return

    if not updated:
        await state.clear()

        await callback.answer(
            t(language, "task_not_found"),
            show_alert=True,
        )

        screen_text, keyboard = build_active_tasks_screen(
            user_id=user_id,
            language=language,
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
        return

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
            "task_updated",
            description=escape(
                str(description),
            ),
            xp=int(xp),
        ),
        reply_markup=get_back_to_tasks_menu(
            language,
        ),
    )

    await callback.answer()


# =============================================================================
# История выполненных задач
# =============================================================================

def build_history_screen(
    user_id: int,
    language: str,
    page: int = 1,
) -> tuple[str, InlineKeyboardMarkup]:
    """Формирует страницу истории выполненных задач.

    Args:
        user_id: Telegram ID пользователя.
        language: Код языка интерфейса.
        page: Запрошенная страница.

    Returns:
        Текст истории и клавиатура навигации.
    """
    result = get_completed_tasks_page(
        user_id=user_id,
        page=page,
        page_size=5,
    )

    if result is None:
        return (
            t(language, "not_in_house"),
            get_back_button(language),
        )

    records, current_page, total_pages = result

    if not records:
        return (
            t(language, "history_empty"),
            get_history_menu(
                language=language,
                current_page=current_page,
                total_pages=total_pages,
            ),
        )

    lines = [
        t(
            language,
            "history_title",
            page=current_page,
            total_pages=total_pages,
        ),
        "",
    ]

    for record in records:
        if record.template_name is not None:
            task_name = translate_task_name(
                record.template_name,
                language,
            )
        else:
            task_name = record.custom_name or ""

        formatted_date = record.completed_at.strftime(
            "%d.%m.%Y",
        )

        lines.extend(
            [
                t(
                    language,
                    "history_entry",
                    name=escape(task_name),
                    xp=record.xp,
                    executor=escape(
                        record.executor_name,
                    ),
                    date=formatted_date,
                ),
                "",
            ]
        )

    return (
        "\n".join(lines).rstrip(),
        get_history_menu(
            language=language,
            current_page=current_page,
            total_pages=total_pages,
        ),
    )


async def show_history_page(
    callback: CallbackQuery,
    page: int,
) -> None:
    """Отображает выбранную страницу истории.

    Args:
        callback: Нажатие кнопки истории или навигации.
        page: Номер отображаемой страницы.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    screen_text, keyboard = build_history_screen(
        user_id=user_id,
        language=language,
        page=page,
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
    F.data == "menu:history",
)
async def show_history(
    callback: CallbackQuery,
) -> None:
    """Открывает первую страницу истории.

    Args:
        callback: Нажатие пункта истории в главном меню.
    """
    await show_history_page(
        callback=callback,
        page=1,
    )


@router.callback_query(
    F.data.startswith("history:page:"),
)
async def handle_history_pagination(
    callback: CallbackQuery,
) -> None:
    """Переключает страницы истории.

    Args:
        callback: Нажатие кнопки предыдущей или следующей страницы.
    """
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

    await show_history_page(
        callback=callback,
        page=page,
    )


# =============================================================================
# Журнал обновлений
# =============================================================================

def build_changelog_screen(
    language: str,
    page: int = 1,
) -> tuple[str, InlineKeyboardMarkup]:
    """Формирует пользовательскую страницу журнала.

    Args:
        language: Код языка интерфейса.
        page: Запрошенный номер страницы.

    Returns:
        Текст журнала и клавиатура навигации.
    """
    entries, current_page, total_pages = (
        get_changelog_page(
            page=page,
            page_size=3,
        )
    )

    if not entries:
        return (
            t(language, "changelog_empty"),
            get_changelog_menu(
                language=language,
                current_page=current_page,
                total_pages=total_pages,
            ),
        )

    lines = [
        t(
            language,
            "changelog_title",
            page=current_page,
            total_pages=total_pages,
        ),
        "",
    ]

    for entry in entries:
        if language == "en":
            entry_text = (
                entry.message_en
                or entry.message_ru
            )
        else:
            entry_text = entry.message_ru

        lines.extend(
            [
                f"• {entry_text}",
                "",
            ]
        )

    return (
        "\n".join(lines).rstrip(),
        get_changelog_menu(
            language=language,
            current_page=current_page,
            total_pages=total_pages,
        ),
    )


async def show_changelog_page(
    callback: CallbackQuery,
    page: int,
) -> None:
    """Показывает выбранную страницу журнала.

    Args:
        callback: Нажатие пункта журнала или кнопки страницы.
        page: Номер отображаемой страницы.
    """
    if callback.message is None:
        await callback.answer()
        return

    user_id = callback.from_user.id
    language = get_user_language(user_id)

    screen_text, keyboard = build_changelog_screen(
        language=language,
        page=page,
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
    F.data == "menu:changelog",
)
async def show_changelog(
    callback: CallbackQuery,
) -> None:
    """Открывает первую страницу журнала обновлений.

    Args:
        callback: Нажатие пункта журнала.
    """
    await show_changelog_page(
        callback=callback,
        page=1,
    )


@router.callback_query(
    F.data.startswith("changelog:page:"),
    F.data.endswith(":user"),
)
async def handle_changelog_pagination(
    callback: CallbackQuery,
) -> None:
    """Переключает страницы пользовательского журнала.

    Args:
        callback: Нажатие кнопки предыдущей или следующей страницы.
    """
    callback_data = callback.data or ""
    parts = callback_data.split(":")

    try:
        page = int(parts[2])
    except (
        IndexError,
        ValueError,
    ):
        page = 1

    await show_changelog_page(
        callback=callback,
        page=page,
    )
