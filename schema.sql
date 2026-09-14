-- ============================================================================
-- 1. ОБЩИЕ НАСТРОЙКИ
-- ============================================================================

-- Включает проверку связей между таблицами в SQLite.
PRAGMA foreign_keys = ON;


-- ============================================================================
-- 2. ДОМАШНИЕ ГРУППЫ
-- ============================================================================

CREATE TABLE IF NOT EXISTS houses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invite_code TEXT NOT NULL UNIQUE,
    name TEXT
);


-- ============================================================================
-- 3. ПОЛЬЗОВАТЕЛИ
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    tg_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,

    gender TEXT NOT NULL DEFAULT 'male'
        CHECK (gender IN ('male', 'female')),

    house_id INTEGER NOT NULL,

    xp INTEGER NOT NULL DEFAULT 0
        CHECK (xp >= 0),

    language TEXT NOT NULL DEFAULT 'ru'
        CHECK (language IN ('ru', 'en')),

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (house_id)
        REFERENCES houses(id)
        ON DELETE CASCADE
);


-- ============================================================================
-- 4. ШАБЛОНЫ СТАНДАРТНЫХ ЗАДАЧ
-- ============================================================================

CREATE TABLE IF NOT EXISTS task_templates (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,

    xp INTEGER NOT NULL
        CHECK (xp >= 0)
);


-- ============================================================================
-- 5. АКТИВНЫЕ ЗАДАЧИ
-- ============================================================================

CREATE TABLE IF NOT EXISTS active_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Для стандартной задачи хранится ссылка на её шаблон.
    template_id INTEGER,

    -- Для пользовательской задачи используются название и награда.
    custom_name TEXT,
    custom_xp INTEGER
        CHECK (custom_xp IS NULL OR custom_xp >= 0),

    house_id INTEGER NOT NULL,
    assigned_by INTEGER NOT NULL,

    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (template_id)
        REFERENCES task_templates(id)
        ON DELETE SET NULL,

    FOREIGN KEY (house_id)
        REFERENCES houses(id)
        ON DELETE CASCADE,

    FOREIGN KEY (assigned_by)
        REFERENCES users(tg_id)
        ON DELETE CASCADE,

    -- Задача должна быть либо стандартной, либо пользовательской.
    CHECK (
        (
            template_id IS NOT NULL
            AND custom_name IS NULL
            AND custom_xp IS NULL
        )
        OR
        (
            template_id IS NULL
            AND custom_name IS NOT NULL
            AND custom_xp IS NOT NULL
        )
    )
);


-- ============================================================================
-- 6. ИСТОРИЯ ВЫПОЛНЕННЫХ ЗАДАЧ
-- ============================================================================

CREATE TABLE IF NOT EXISTS completed_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    template_id INTEGER,
    custom_name TEXT,
    custom_xp INTEGER
        CHECK (custom_xp IS NULL OR custom_xp >= 0),

    completed_by INTEGER NOT NULL,
    house_id INTEGER NOT NULL,

    completed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (template_id)
        REFERENCES task_templates(id)
        ON DELETE SET NULL,

    FOREIGN KEY (completed_by)
        REFERENCES users(tg_id)
        ON DELETE CASCADE,

    FOREIGN KEY (house_id)
        REFERENCES houses(id)
        ON DELETE CASCADE,

    -- Выполненная задача тоже может быть стандартной или пользовательской.
    CHECK (
        (
            template_id IS NOT NULL
            AND custom_name IS NULL
            AND custom_xp IS NULL
        )
        OR
        (
            template_id IS NULL
            AND custom_name IS NOT NULL
            AND custom_xp IS NOT NULL
        )
    )
);


-- ============================================================================
-- 7. ЖУРНАЛ ОБНОВЛЕНИЙ
-- ============================================================================

CREATE TABLE IF NOT EXISTS changelog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Старое поле сохраняется для совместимости с прежней версией базы.
    message TEXT NOT NULL DEFAULT '',

    message_ru TEXT,
    message_en TEXT,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- 8. ИНДЕКСЫ
-- ============================================================================

-- Индексы ускоряют поиск пользователей и задач внутри одной домашней группы.

CREATE INDEX IF NOT EXISTS idx_users_house_id
    ON users(house_id);

CREATE INDEX IF NOT EXISTS idx_active_tasks_house_id
    ON active_tasks(house_id);

CREATE INDEX IF NOT EXISTS idx_completed_tasks_house_id
    ON completed_tasks(house_id);

CREATE INDEX IF NOT EXISTS idx_completed_tasks_completed_by
    ON completed_tasks(completed_by);

CREATE INDEX IF NOT EXISTS idx_changelog_created_at
    ON changelog(created_at);


-- ============================================================================
-- 9. СТАНДАРТНЫЕ ЗАДАЧИ
-- ============================================================================

-- Русские названия являются внутренними постоянными именами.
-- Пользователь увидит перевод, соответствующий выбранному языку.

INSERT OR IGNORE INTO task_templates (id, name, xp) VALUES
    (1,  'Помыть посуду',                         10),
    (2,  'Собрать мешки с мусором',                5),
    (3,  'Вынести мусор',                          10),
    (4,  'Помыть пол в квартире',                  15),
    (5,  'Протереть пыль',                         10),
    (6,  'Пропылесосить квартиру',                 15),
    (7,  'Поставить стирку',                        5),
    (8,  'Развесить бельё',                        10),
    (9,  'Убрать высохшее бельё',                  10),
    (10, 'Приготовить еду',                        20),
    (11, 'Сходить в магазин за покупками',         15),
    (12, 'Заменить постельное бельё',              15),
    (13, 'Сделать уборку в ванной',                20),
    (14, 'Сделать уборку на кухне',                20);