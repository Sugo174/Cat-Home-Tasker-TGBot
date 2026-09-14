"""FSM-состояния Telegram-бота.

FSM (Finite State Machine) позволяет боту запоминать, на каком этапе
диалога находится пользователь. Например, после запроса имени бот
переходит в состояние ожидания имени и понимает, как обработать
следующее сообщение.
"""

from aiogram.fsm.state import State, StatesGroup


# =============================================================================
# Создание пользовательских задач
# =============================================================================

class CustomTaskCreation(StatesGroup):
    """Состояния создания пользовательской задачи.

    Attributes:
        waiting_for_description: Ожидание описания новой задачи.
        waiting_for_xp: Ожидание выбора награды за задачу.
    """

    waiting_for_description = State()
    waiting_for_xp = State()


class CustomTaskEditing(StatesGroup):
    """Состояния редактирования пользовательской задачи.

    Attributes:
        waiting_for_description: Ожидание нового описания задачи.
        choosing_xp: Ожидание выбора нового количества XP.
    """

    waiting_for_description = State()
    choosing_xp = State()


# =============================================================================
# Регистрация пользователя
# =============================================================================

class UserRegistration(StatesGroup):
    """Состояния пошаговой регистрации пользователя.

    Attributes:
        waiting_for_language: Ожидание выбора языка интерфейса.
        waiting_for_name: Ожидание имени или ника.
        waiting_for_gender: Ожидание выбора пола.
        waiting_for_invite_code: Ожидание кода дома или команды
            создания нового дома.
    """

    waiting_for_language = State()
    waiting_for_name = State()
    waiting_for_gender = State()
    waiting_for_invite_code = State()


# =============================================================================
# Редактирование профиля
# =============================================================================

class ProfileEdit(StatesGroup):
    """Состояния редактирования профиля пользователя.

    Attributes:
        editing_name: Ожидание нового имени.
        editing_gender: Ожидание нового значения пола.
    """

    editing_name = State()
    editing_gender = State()


# =============================================================================
# Административная панель
# =============================================================================

class AdminState(StatesGroup):
    """Основные состояния административной панели.

    Attributes:
        waiting_for_password: Ожидание пароля администратора.
        browsing_houses: Просмотр списка зарегистрированных домов.
        managing_house: Управление выбранным домом.
    """

    waiting_for_password = State()
    browsing_houses = State()
    managing_house = State()


class AdminEditXP(StatesGroup):
    """Состояние изменения количества XP пользователя.

    Attributes:
        waiting_for_xp: Ожидание нового целого значения XP.
    """

    waiting_for_xp = State()


class AdminChangelog(StatesGroup):
    """Состояния создания двуязычной записи журнала.

    Attributes:
        waiting_for_russian: Ожидание русской версии записи.
        waiting_for_english: Ожидание английской версии записи.
    """

    waiting_for_russian = State()
    waiting_for_english = State()


class AdminChangelogEdit(StatesGroup):
    """Состояния редактирования двуязычной записи журнала.

    Attributes:
        waiting_for_russian: Ожидание новой русской версии.
        waiting_for_english: Ожидание новой английской версии.
    """

    waiting_for_russian = State()
    waiting_for_english = State()
