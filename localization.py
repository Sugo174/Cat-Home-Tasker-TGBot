"""Локализация и игровые элементы Telegram-бота.

Модуль содержит пользовательские тексты на русском и английском
языках, переводы стандартных задач, уровни, титулы и прогресс-бар.

Этот модуль не обращается к базе данных и не зависит от обработчиков
Telegram.
"""

from typing import Any


# =============================================================================
# Пользовательские тексты
# =============================================================================

TRANSLATIONS = {
    "ru": {
        "main_title": "🏡 Главное меню:",
        "welcome_back": "🏡 Добро пожаловать в дом!",
        "menu_tasks": "📋 Список активных задач дома",
        "menu_add_task": "➕ Выбор задач в список дома",
        "menu_invite": "🔑 Код приглашения в дом",
        "menu_history": "📜 История выполненных задач",
        "menu_profile": "👤 Мой профиль",
        "menu_house": "👥 Мой дом",
        "menu_changelog": "📰 Журнал обновлений бота",
        "menu_language": "🌐 Язык",
        "back_to_menu": "⬅️ Назад в меню",
        "language_title": "🌐 Выберите язык:",
        "language_changed": "✅ Язык изменён на русский.",
        "registration_name_prompt": "👋 Привет! Как тебя зовут? (Введи имя или ник)",
        "name_too_short": "Имя должно быть от 2 символов. Попробуй ещё:",
        "gender_prompt": "Выбери свой пол:",
        "gender_male": "Мужской 👨",
        "gender_female": "Женский 👩",
        "house_choice": (
            "Отлично!\n\n"
            "Хочешь создать новый дом 🏠 или присоединиться к существующему?\n\n"
            "• Напиши <b>создать</b>, чтобы создать дом\n"
            "• Или введи <b>код дома</b>, чтобы присоединиться"
        ),
        "house_created": (
            "🏡 Дом создан! Твой код: <b>{code}</b>\n\n"
            "Отправь его, чтобы пригласить кого-то!"
        ),
        "invalid_house_code": (
            "❌ Неверный код дома. Попробуй ещё или напиши «создать»."
        ),
        "joined_house": "✅ Добро пожаловать в дом!",
        "profile_not_found": "❌ Пользователь не найден.",
        "profile_gender": "пол: {gender}",
        "profile_level": "Ур. {level} • {emoji} {title}",
        "profile_edit": "✏️ Редактировать профиль",
        "profile_edit_title": "✏️ Редактирование профиля:",
        "profile_change_name": "✏️ Изменить имя",
        "profile_change_gender": "⚧️ Изменить пол",
        "back": "⬅️ Назад",
        "enter_new_name": "✏️ Введите новое имя:",
        "edit_name_too_short": "❌ Имя должно быть от 2 символов. Попробуй ещё:",
        "select_new_gender": "⚧️ Выбери новый пол:",
        "gender_updated": "✅ Пол обновлён!",
        "not_in_house": "❌ Ты не состоишь в доме.",
        "house_empty": "👥 В доме пока никого нет.",
        "house_title": "🏡 <b>Мой дом</b>",
        "you_marker": " 👤 (ты)",
        "member_level": "Ур. {level} • {emoji} {title}",
        "active_tasks_empty": "📝 В доме нет активных задач.",
        "active_tasks_title": "🧹 <b>Активные задачи:</b>",
        "task_added_by": "• {name} (+{xp} XP) (добавил: {assigned_by})",
        "add_task_title": "➕ Создание задач:",
        "choose_standard_task": "📋 Выбрать стандартную задачу",
        "create_custom_task": "✏️ Создать свою задачу",
        "standard_tasks_empty": "📋 Нет стандартных задач.",
        "standard_tasks_page": "📋 Стандартные задачи (стр. {page} из {total_pages}):",
        "previous_page": "◀️ Предыдущая страница",
        "next_page": "Следующая страница ▶️",
        "custom_new_description": "✏️ Введите новое описание задачи:",
        "custom_choose_xp": "📊 Выберите XP за выполнение задачи:",
        "cancel": "❌ Отмена",
        "custom_description_prompt": "✏️ Введите описание новой задачи:",
        "description_too_short": "❌ Описание должно быть от 3 символов. Попробуй ещё:",
        "task_preview": "📋 Превью задачи:\n<b>{description}</b>",
        "continue": "✅ Далее",
        "edit": "✏️ Редактировать",
        "description_not_found": "❌ Описание задачи не найдено.",
        "custom_task_added": "✅ Задача добавлена: <b>{description}</b> (+{xp} XP)",
        "complete_task": "✅ Выполнить",
        "back_to_add_tasks": "⬅️ Назад к добавлению задач",
        "task_not_found": "❌ Задача не найдена.",
        "task_card": "📋 <b>{name}</b> (+{xp} XP)\n\nВыберите действие:",
        "add_to_active": "➕ Добавить в активные",
        "back_to_task_selection": "⬅️ Назад к задачам",
        "task_completed_now": "🏆 Выполнено: <b>{name}</b> (+{xp} XP)\n\n",
        "task_added_to_active": "➕ Добавлена задача: <b>{name}</b>\n\n",
        "active_task_card": "📋 <b>{name}</b> (+{xp} XP)\nДобавил: {assigned_by}",
        "delete_task": "🗑 Удалить",
        "edit_task": "✏️ Редактировать",
        "back_to_tasks": "⬅️ Назад к задачам",
        "task_no_longer_active": "❌ Задача уже выполнена или не найдена.",
        "task_deleted": "🗑 Задача удалена!",
        "edit_task_menu": "📋 <b>Редактирование задачи</b>\n\nОписание:\n{description}\n\nXP: {xp}",
        "edit_description": "✏️ Редактировать описание",
        "change_xp": "🔢 Изменить XP",
        "enter_new_description": "✏️ Введите новое описание задачи:",
        "save": "✅ Сохранить",
        "updated_description": "📋 Обновлённое описание:\n<b>{description}</b>\n\nXP: {xp}",
        "current_xp_card": "📋 Описание:\n<b>{description}</b>\n\nТекущий XP: {xp}",
        "new_xp_card": "📋 Описание:\n<b>{description}</b>\n\nНовый XP: {xp}",
        "change_description": "✏️ Изменить описание",
        "edit_data_missing": "❌ Данные редактирования не найдены.",
        "task_updated": "✅ Задача обновлена:\n<b>{description}</b> (+{xp} XP)",
        "history_empty": "📭 В доме пока никто ничего не сделал.",
        "history_title": "📜 <b>История выполненных задач</b> (стр. {page} из {total_pages}):",
        "history_entry": "✅ {name} (+{xp} XP)\n   👤 {executor}\n   📅 {date}",
        "register_first": "❌ Сначала зарегистрируйся через /start.",
        "invite_code_message": "🔑 <b>Код приглашения твоего дома:</b>\n\n<code>{code}</code>\n\nОтправь его, чтобы пригласить кого-то!",
        "changelog_empty": "📰 <b>Журнал обновлений</b>\n\nПока пусто.",
        "changelog_title": "📰 <b>Журнал обновлений</b> (стр. {page} из {total_pages}):",
        "admin_password_prompt": "🔒 Введите пароль администратора:",
        "admin_wrong_password": "❌ Неверный пароль. Попробуйте снова:",
        "admin_no_houses": "🏠 Домов пока нет.",
        "admin_houses_title": "🏠 <b>Дома</b> (стр. {page} из {total_pages}):",
        "admin_house_button": "Дом {house_id} ({invite_code})",
        "admin_manage_changelog": "📝 Управление журналом",
        "admin_exit": "🚪 Выйти из админки",
        "admin_house_empty": "👥 В доме {house_id} нет участников.",
        "admin_house_members": "👥 <b>Участники дома {house_id}</b>",
        "admin_member_line": "• {name} (ID: {user_id}) — ур. {level}",
        "admin_manage_user": "🔧 {name}",
        "admin_clear_history": "🗑 Очистить историю",
        "admin_delete_house": "🗑 Удалить дом",
        "admin_back_to_houses": "⬅️ Назад к домам",
        "admin_user_not_found": "❌ Пользователь не найден.",
        "admin_user_management": "🛠 <b>Управление пользователем</b>\n\nИмя: {name}\nТекущий XP: {xp}",
        "admin_set_xp": "✏️ Установить XP",
        "admin_reset_xp": "🔄 Сбросить XP",
        "admin_delete_user": "🗑 Удалить пользователя",
        "admin_back_to_house": "⬅️ Назад к дому",
        "admin_xp_reset": "✅ XP пользователя сброшен!",
        "admin_user_deleted": "🗑 Пользователь удалён!",
        "admin_history_cleared": "🗑 История дома очищена!",
        "admin_confirm_delete_house": "⚠️ Точно удалить дом {house_id}?\n\nБудут удалены все участники, активные задачи и история.",
        "admin_confirm_delete": "✅ Да, удалить",
        "admin_house_deleted": "✅ Дом {house_id} удалён!",
        "admin_house_not_found": "❌ Дом не найден.",
        "admin_enter_xp": "✏️ Введите новое значение XP — целое число от 0:",
        "admin_invalid_xp": "❌ XP должен быть целым неотрицательным числом.\n\nПопробуйте снова:",
        "admin_exited": "🚪 Вы вышли из админки.",
        "admin_unknown_action": "❌ Неизвестное действие.",
        "admin_changelog_empty": "📝 <b>Управление журналом обновлений</b>\n\nЗаписей пока нет.",
        "admin_changelog_title": "📝 <b>Управление журналом обновлений</b> (стр. {page} из {total_pages}):",
        "admin_add_changelog": "➕ Добавить запись",
        "admin_edit_changelog": "✏️ Редактировать",
        "admin_delete_changelog": "🗑 Удалить",
        "admin_enter_changelog": "✏️ Введите текст новой записи журнала:",
        "admin_changelog_empty_text": "❌ Текст не может быть пустым.\n\nВведите текст новой записи:",
        "admin_edit_changelog_prompt": "✏️ Введите новый текст записи:",
        "admin_edit_changelog_empty": "❌ Текст не может быть пустым.\n\nВведите новый текст записи:",
        "admin_changelog_not_found": "❌ Запись журнала не найдена.",
        "admin_confirm_delete_changelog": "⚠️ Удалить эту запись журнала?\n\nЭто действие нельзя отменить.",
        "admin_changelog_deleted": "🗑 Запись журнала удалена!",
        "admin_enter_changelog_ru": "🇷🇺 Введите текст записи на русском языке:",
        "admin_enter_changelog_en": "🇬🇧 Теперь введите текст записи на английском языке:",
        "admin_changelog_ru_empty": "❌ Русский текст не может быть пустым.\n\nВведите текст на русском:",
        "admin_changelog_en_empty": "❌ Английский текст не может быть пустым.\n\nВведите текст на английском:",
        "admin_translation_missing": "Перевод пока не добавлен",
        "admin_edit_changelog_ru": "🇷🇺 Введите новый текст записи на русском языке:",
        "admin_edit_changelog_en": "🇬🇧 Теперь введите новый текст записи на английском языке:",
        "admin_edit_changelog_ru_empty": "❌ Русский текст не может быть пустым.\n\nВведите русский вариант:",
        "admin_edit_changelog_en_empty": "❌ Английский текст не может быть пустым.\n\nВведите английский вариант:",
    },
    "en": {
        "main_title": "🏡 Main menu:",
        "welcome_back": "🏡 Welcome home!",
        "menu_tasks": "📋 Active household tasks",
        "menu_add_task": "➕ Add a household task",
        "menu_invite": "🔑 House invitation code",
        "menu_history": "📜 Completed task history",
        "menu_profile": "👤 My profile",
        "menu_house": "👥 My household",
        "menu_changelog": "📰 Bot changelog",
        "menu_language": "🌐 Language",
        "back_to_menu": "⬅️ Back to main menu",
        "language_title": "🌐 Select a language:",
        "language_changed": "✅ Language changed to English.",
        "registration_name_prompt": "👋 Hi! What is your name? Enter your name or nickname.",
        "name_too_short": "The name must contain at least 2 characters. Try again:",
        "gender_prompt": "Select your gender:",
        "gender_male": "Male 👨",
        "gender_female": "Female 👩",
        "house_choice": (
            "Great!\n\n"
            "Would you like to create a new household 🏠 or join an existing one?\n\n"
            "• Type <b>create</b> to create a household\n"
            "• Or enter a <b>house invitation code</b> to join"
        ),
        "house_created": (
            "🏡 Household created! Your invitation code: <b>{code}</b>\n\n"
            "Send it to someone you want to invite!"
        ),
        "invalid_house_code": (
            "❌ Invalid invitation code. Try again or type “create”."
        ),
        "joined_house": "✅ Welcome to the household!",
        "profile_not_found": "❌ User not found.",
        "profile_gender": "Gender: {gender}",
        "profile_level": "Level {level} • {emoji} {title}",
        "profile_edit": "✏️ Edit profile",
        "profile_edit_title": "✏️ Edit profile:",
        "profile_change_name": "✏️ Change name",
        "profile_change_gender": "⚧️ Change gender",
        "back": "⬅️ Back",
        "enter_new_name": "✏️ Enter a new name:",
        "edit_name_too_short": "❌ The name must contain at least 2 characters. Try again:",
        "select_new_gender": "⚧️ Select a new gender:",
        "gender_updated": "✅ Gender updated!",
        "not_in_house": "❌ You are not a member of a household.",
        "house_empty": "👥 There are no household members yet.",
        "house_title": "🏡 <b>My household</b>",
        "you_marker": " 👤 (you)",
        "member_level": "Level {level} • {emoji} {title}",
        "active_tasks_empty": "📝 There are no active household tasks.",
        "active_tasks_title": "🧹 <b>Active tasks:</b>",
        "task_added_by": "• {name} (+{xp} XP) (added by: {assigned_by})",
        "add_task_title": "➕ Add a task:",
        "choose_standard_task": "📋 Select a standard task",
        "create_custom_task": "✏️ Create a custom task",
        "standard_tasks_empty": "📋 There are no standard tasks.",
        "standard_tasks_page": "📋 Standard tasks (page {page} of {total_pages}):",
        "previous_page": "◀️ Previous page",
        "next_page": "Next page ▶️",
        "custom_new_description": "✏️ Enter a new task description:",
        "custom_choose_xp": "📊 Select the XP reward for completing the task:",
        "cancel": "❌ Cancel",
        "custom_description_prompt": "✏️ Enter a description for the new task:",
        "description_too_short": "❌ The description must contain at least 3 characters. Try again:",
        "task_preview": "📋 Task preview:\n<b>{description}</b>",
        "continue": "✅ Continue",
        "edit": "✏️ Edit",
        "description_not_found": "❌ Task description not found.",
        "custom_task_added": "✅ Task added: <b>{description}</b> (+{xp} XP)",
        "complete_task": "✅ Complete",
        "back_to_add_tasks": "⬅️ Back to task selection",
        "task_not_found": "❌ Task not found.",
        "task_card": "📋 <b>{name}</b> (+{xp} XP)\n\nSelect an action:",
        "add_to_active": "➕ Add to active tasks",
        "back_to_task_selection": "⬅️ Back to tasks",
        "task_completed_now": "🏆 Completed: <b>{name}</b> (+{xp} XP)\n\n",
        "task_added_to_active": "➕ Task added: <b>{name}</b>\n\n",
        "active_task_card": "📋 <b>{name}</b> (+{xp} XP)\nAdded by: {assigned_by}",
        "delete_task": "🗑 Delete",
        "edit_task": "✏️ Edit",
        "back_to_tasks": "⬅️ Back to tasks",
        "task_no_longer_active": "❌ The task has already been completed or was not found.",
        "task_deleted": "🗑 Task deleted!",
        "edit_task_menu": "📋 <b>Edit task</b>\n\nDescription:\n{description}\n\nXP: {xp}",
        "edit_description": "✏️ Edit description",
        "change_xp": "🔢 Change XP",
        "enter_new_description": "✏️ Enter a new task description:",
        "save": "✅ Save",
        "updated_description": "📋 Updated description:\n<b>{description}</b>\n\nXP: {xp}",
        "current_xp_card": "📋 Description:\n<b>{description}</b>\n\nCurrent XP: {xp}",
        "new_xp_card": "📋 Description:\n<b>{description}</b>\n\nNew XP: {xp}",
        "change_description": "✏️ Change description",
        "edit_data_missing": "❌ Task editing data was not found.",
        "task_updated": "✅ Task updated:\n<b>{description}</b> (+{xp} XP)",
        "history_empty": "📭 No tasks have been completed in this household yet.",
        "history_title": "📜 <b>Completed task history</b> (page {page} of {total_pages}):",
        "history_entry": "✅ {name} (+{xp} XP)\n   👤 {executor}\n   📅 {date}",
        "register_first": "❌ Please register first using /start.",
        "invite_code_message": "🔑 <b>Your household invitation code:</b>\n\n<code>{code}</code>\n\nSend it to someone you want to invite!",
        "changelog_empty": "📰 <b>Bot changelog</b>\n\nThere are no entries yet.",
        "changelog_title": "📰 <b>Bot changelog</b> (page {page} of {total_pages}):",
        "admin_password_prompt": "🔒 Enter the administrator password:",
        "admin_wrong_password": "❌ Incorrect password. Please try again:",
        "admin_no_houses": "🏠 There are no households yet.",
        "admin_houses_title": "🏠 <b>Households</b> (page {page} of {total_pages}):",
        "admin_house_button": "Household {house_id} ({invite_code})",
        "admin_manage_changelog": "📝 Manage changelog",
        "admin_exit": "🚪 Exit admin panel",
        "admin_house_empty": "👥 Household {house_id} has no members.",
        "admin_house_members": "👥 <b>Members of household {house_id}</b>",
        "admin_member_line": "• {name} (ID: {user_id}) — level {level}",
        "admin_manage_user": "🔧 {name}",
        "admin_clear_history": "🗑 Clear history",
        "admin_delete_house": "🗑 Delete household",
        "admin_back_to_houses": "⬅️ Back to households",
        "admin_user_not_found": "❌ User not found.",
        "admin_user_management": "🛠 <b>User management</b>\n\nName: {name}\nCurrent XP: {xp}",
        "admin_set_xp": "✏️ Set XP",
        "admin_reset_xp": "🔄 Reset XP",
        "admin_delete_user": "🗑 Delete user",
        "admin_back_to_house": "⬅️ Back to household",
        "admin_xp_reset": "✅ User XP has been reset!",
        "admin_user_deleted": "🗑 User deleted!",
        "admin_history_cleared": "🗑 Household history cleared!",
        "admin_confirm_delete_house": "⚠️ Delete household {house_id}?\n\nAll members, active tasks, and history will be deleted.",
        "admin_confirm_delete": "✅ Yes, delete",
        "admin_house_deleted": "✅ Household {house_id} deleted!",
        "admin_house_not_found": "❌ Household not found.",
        "admin_enter_xp": "✏️ Enter a new XP value — a whole number starting from 0:",
        "admin_invalid_xp": "❌ XP must be a non-negative whole number.\n\nPlease try again:",
        "admin_exited": "🚪 You have exited the admin panel.",
        "admin_unknown_action": "❌ Unknown action.",
        "admin_changelog_empty": "📝 <b>Changelog management</b>\n\nThere are no entries yet.",
        "admin_changelog_title": "📝 <b>Changelog management</b> (page {page} of {total_pages}):",
        "admin_add_changelog": "➕ Add entry",
        "admin_edit_changelog": "✏️ Edit",
        "admin_delete_changelog": "🗑 Delete",
        "admin_enter_changelog": "✏️ Enter the text for the new changelog entry:",
        "admin_changelog_empty_text": "❌ The text cannot be empty.\n\nEnter the new entry:",
        "admin_edit_changelog_prompt": "✏️ Enter the new text for this entry:",
        "admin_edit_changelog_empty": "❌ The text cannot be empty.\n\nEnter the new entry text:",
        "admin_changelog_not_found": "❌ Changelog entry not found.",
        "admin_confirm_delete_changelog": "⚠️ Delete this changelog entry?\n\nThis action cannot be undone.",
        "admin_changelog_deleted": "🗑 Changelog entry deleted!",
        "admin_enter_changelog_ru": "🇷🇺 Enter the Russian version of the entry:",
        "admin_enter_changelog_en": "🇬🇧 Now enter the English version of the entry:",
        "admin_changelog_ru_empty": "❌ The Russian text cannot be empty.\n\nEnter the Russian version:",
        "admin_changelog_en_empty": "❌ The English text cannot be empty.\n\nEnter the English version:",
        "admin_translation_missing": "Translation has not been added yet",
        "admin_edit_changelog_ru": "🇷🇺 Enter the new Russian version of the entry:",
        "admin_edit_changelog_en": "🇬🇧 Now enter the new English version of the entry:",
        "admin_edit_changelog_ru_empty": "❌ The Russian text cannot be empty.\n\nEnter the Russian version:",
        "admin_edit_changelog_en_empty": "❌ The English text cannot be empty.\n\nEnter the English version:",
    },
}

TASK_NAME_TRANSLATIONS = {
    "en": {
        "Помыть посуду": "Wash the dishes",
        "Собрать мешки с мусором": "Collect the trash bags",
        "Вынести мусор": "Take out the trash",
        "Помыть пол в квартире": "Wash the floors",
        "Протереть пыль": "Dust the furniture",
        "Пропылесосить квартиру": "Vacuum the home",
        "Поставить стирку": "Start the laundry",
        "Развесить бельё": "Hang the laundry",
        "Убрать высохшее бельё": "Put away the dry laundry",
        "Приготовить еду": "Cook a meal",
        "Сходить в магазин за покупками": "Go grocery shopping",
        "Заменить постельное бельё": "Change the bed linen",
        "Сделать уборку в ванной": "Clean the bathroom",
        "Сделать уборку на кухне": "Clean the kitchen",
    }
}

# =============================================================================
# Работа с переводами
# =============================================================================

SUPPORTED_LANGUAGES = frozenset(
    TRANSLATIONS.keys()
)

DEFAULT_LANGUAGE = "ru"


def normalize_language(language: str | None) -> str:
    """Возвращает поддерживаемый код языка.

    Args:
        language: Предполагаемый код языка.

    Returns:
        Переданный код ``ru`` или ``en``. Для неизвестного значения
        возвращается русский язык.
    """
    if language in SUPPORTED_LANGUAGES:
        return language

    return DEFAULT_LANGUAGE


def t(
    language: str,
    key: str,
    **values: Any,
) -> str:
    """Возвращает локализованный текст.

    Если язык или ключ не найден, функция использует русский вариант.
    Именованные значения подставляются в шаблоны вида ``{name}``.

    Args:
        language: Код языка пользователя.
        key: Ключ текста в словаре ``TRANSLATIONS``.
        **values: Значения для подстановки в текст.

    Returns:
        Готовый локализованный текст.
    """
    selected_language = normalize_language(language)

    language_texts = TRANSLATIONS[selected_language]
    fallback_texts = TRANSLATIONS[DEFAULT_LANGUAGE]

    text = language_texts.get(
        key,
        fallback_texts.get(key, key),
    )

    return text.format(**values)


def translate_task_name(
    name: str,
    language: str,
) -> str:
    """Переводит название стандартной задачи.

    Пользовательские задачи не изменяются. Если перевод стандартной
    задачи отсутствует, возвращается исходное название.

    Args:
        name: Название задачи, сохранённое в базе.
        language: Код языка пользователя.

    Returns:
        Переведённое или исходное название задачи.
    """
    selected_language = normalize_language(language)

    language_tasks = TASK_NAME_TRANSLATIONS.get(
        selected_language,
        {},
    )

    return language_tasks.get(name, name)


# =============================================================================
# Уровни и титулы
# =============================================================================

LEVEL_TITLES = {
    "ru": {
        1: ("Новичок", "🐣"),
        2: ("Помощник", "🧽"),
        3: ("Уборщик-стажёр", "🧹"),
        4: ("Мастер чистоты", "🧺"),
        5: ("Хранитель порядка", "🏡"),
        6: ("Домашний герой", "🦸‍♂️"),
        7: ("Гуру уюта", "🕊️"),
        8: ("Архитектор чистоты", "🏗️"),
        9: ("Император уборки", "👑"),
        10: ("Легенда быта", "🌟"),
        11: ("Повелитель пылесоса", "🌀"),
        12: ("Маг моющего средства", "🧴"),
        13: ("Властелин влажной тряпки", "💦"),
        14: ("Верховный уборщик", "🧘‍♀️"),
        15: ("Страж чистых полов", "🛡️"),
        16: ("Алхимик уюта", "🧪"),
        17: ("Непобедимый в борьбе с пылью", "🥇"),
        18: ("Свет домашнего очага", "🔥"),
        19: ("Божество гармонии", "🕉️"),
        20: ("Вечный хранитель дома", "🏯"),
    },
    "en": {
        1: ("Beginner", "🐣"),
        2: ("Helper", "🧽"),
        3: ("Cleaning Trainee", "🧹"),
        4: ("Cleaning Master", "🧺"),
        5: ("Keeper of Order", "🏡"),
        6: ("Household Hero", "🦸‍♂️"),
        7: ("Comfort Guru", "🕊️"),
        8: ("Architect of Cleanliness", "🏗️"),
        9: ("Cleaning Emperor", "👑"),
        10: ("Household Legend", "🌟"),
        11: ("Vacuum Commander", "🌀"),
        12: ("Detergent Wizard", "🧴"),
        13: ("Lord of the Damp Cloth", "💦"),
        14: ("Supreme Cleaner", "🧘‍♀️"),
        15: ("Guardian of Clean Floors", "🛡️"),
        16: ("Comfort Alchemist", "🧪"),
        17: ("Undefeated Dust Fighter", "🥇"),
        18: ("Light of the Hearth", "🔥"),
        19: ("Deity of Harmony", "🕉️"),
        20: ("Eternal Keeper of the Home", "🏯"),
    },
}


def calculate_level(
    xp: int,
    language: str = DEFAULT_LANGUAGE,
) -> dict[str, int | str]:
    """Рассчитывает уровень и прогресс пользователя.

    Для перехода с первого уровня требуется 50 XP, со второго —
    100 XP, с третьего — 150 XP. Требование увеличивается на 50 XP
    с каждым уровнем.

    Args:
        xp: Общее количество заработанного опыта.
        language: Код языка для выбора титула.

    Returns:
        Словарь с уровнем, текущим прогрессом, требованием следующего
        уровня, титулом и эмодзи.
    """
    remaining_xp = max(0, xp)
    level = 1

    while True:
        xp_for_next = 50 * level

        if remaining_xp < xp_for_next:
            break

        remaining_xp -= xp_for_next
        level += 1

    selected_language = normalize_language(language)
    selected_titles = LEVEL_TITLES[selected_language]

    # После двадцатого уровня сохраняется последний доступный титул,
    # но числовой уровень продолжает увеличиваться.
    display_level = min(level, 20)
    title, emoji = selected_titles[display_level]

    return {
        "level": level,
        "xp_current": remaining_xp,
        "xp_for_next": 50 * level,
        "title": title,
        "emoji": emoji,
    }


def make_progress_bar(
    current: int,
    total: int,
    length: int = 10,
) -> str:
    """Создаёт текстовый прогресс-бар из эмодзи.

    Args:
        current: Текущее значение.
        total: Значение, необходимое для завершения прогресса.
        length: Количество ячеек в полосе.

    Returns:
        Строка вида ``🟩🟩🟩⬜⬜⬜⬜⬜⬜⬜ 30%``.
    """
    if total <= 0:
        percent = 100
    else:
        percent = min(
            100,
            max(0, int(current / total * 100)),
        )

    filled_cells = int(length * percent / 100)
    empty_cells = length - filled_cells

    bar = (
        "🟩" * filled_cells
        + "⬜" * empty_cells
    )

    return f"{bar} {percent}%"
