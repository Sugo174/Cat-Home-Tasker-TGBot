# Cat Home Tasker Bot

[Русская версия](README.ru.md) · [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

<p align="center">
  <img src="assets/cat-home-tasker.png" alt="Cat Home Tasker" width="320">
</p>

[![Python tests](https://github.com/Sugo174/Cat-Home-Tasker-TGBot/actions/workflows/tests.yml/badge.svg)](https://github.com/Sugo174/Cat-Home-Tasker-TGBot/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Telegram bot for sharing household chores with game elements.

Household members create and complete tasks, earn experience points,
and level up. The interface is available in Russian and English.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Bot](#running-the-bot)
- [Getting Started](#getting-started)
- [Administration](#administration)
- [Data Storage](#data-storage)
- [Backup and Updates](#backup-and-updates)
- [Technology](#technology)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Documentation](#documentation)
- [Screenshots](#screenshots)
- [Changelog](#changelog)
- [Contributing](#contributing)
- [License](#license)

## Features

- Household creation and joining by invitation code.
- Standard and custom household tasks.
- Experience points and user levels.
- Task completion history.
- User profiles.
- Administrative panel for managing households and users.
- Bilingual bot changelog.
- Telegram connectivity through a SOCKS5 proxy.
- SQLite database storage.

## Requirements

- Python 3.14 for the current Windows startup workflow.
- A Telegram bot token from [BotFather](https://t.me/BotFather).
- A SOCKS5 proxy.
- An administration panel password.

All three settings, `BOT_TOKEN`, `ADMIN_PASSWORD`, and `PROXY_URL`,
are required by the current configuration.

## Installation

Run commands in PowerShell from the repository root.

Create a separate environment and install dependencies:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

For a first installation, create `.env` using `.env.example`
as a template and fill in your settings:

```dotenv
BOT_TOKEN=your_bot_token
ADMIN_PASSWORD=your_admin_password
PROXY_URL=socks5://username:password@host:port
```

| Variable | Purpose |
|---|---|
| `BOT_TOKEN` | Bot token obtained from BotFather |
| `ADMIN_PASSWORD` | Administration panel password |
| `PROXY_URL` | SOCKS5 proxy URL |

Replace the examples with your own values.
Do not publish `.env` or commit it to Git.

When updating an existing installation, preserve its working `.env`
instead of replacing it with the example file.

## Running the Bot

Start the bot using the prepared environment:

```powershell
.\.venv\Scripts\python.exe bot.py
```

The bot initializes the database automatically at startup.
It must remain running, and the computer must be able to access
Telegram through the configured proxy.

Do not run multiple instances with the same bot token.

### Batch File

`start_bot.bat` runs `py -3.14 bot.py`.
It uses the installed Python 3.14 rather than explicitly selecting `.venv`.

If dependencies are installed only in `.venv`,
use the direct startup command above.

### Windows Desktop Shortcut

`setup_windows.bat` creates a Cat Home Tasker desktop shortcut
with the application icon.

The shortcut starts `start_bot.bat` from the project folder.
It does not install Python or dependencies.

## Getting Started

1. Open your bot in Telegram and send `/start`.
2. Select a language.
3. Create a household or join one using an invitation code.
4. Add tasks and mark them as completed.
5. Check your profile, experience points, and task completion history.

## Administration

Send `/admin` and enter the password configured in `ADMIN_PASSWORD`.

Do not share the password with members who do not need
administrative access.

## Data Storage

The bot uses SQLite. Its working database, `household.db`,
is located beside `config.py`.

The database contains user, household, task, and progress data.
It is not included in the public repository.

Do not delete or replace the working database during an update:
this may cause loss of accumulated data.

## Backup and Updates

1. Stop the bot with Ctrl+C in its terminal.
2. Back up `household.db` and `.env`.
3. Update application files while preserving the working database and settings.
4. Update dependencies if needed:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

5. Start the bot.
6. Check access to the existing household, tasks, profile, and history.

Stop the bot before backing up the database by copying its file.
Keep backups outside the repository and restrict access to them.

## Technology

- Python.
- aiogram 3.
- SQLite.
- python-dotenv.
- aiohttp-socks.

## Project Structure

- `bot.py` — Application startup and Telegram update polling.
- `config.py` — Environment settings and file paths.
- `database.py` — Database operations.
- `handlers/user.py` — User workflows.
- `handlers/admin.py` — Administration panel.
- `keyboards.py` — Interface keyboards.
- `localization.py` — Russian and English translations.
- `states.py` — Conversation states.
- `schema.sql` — Database schema.
- `requirements.txt` — Python dependencies.
- `.env.example` — Configuration template.
- `tests/` — Automated tests.
- `assets/` — Application icons.
- `media/` — Documentation media.
- `start_bot.bat` — Windows startup script.
- `setup_windows.bat` — Desktop shortcut setup.
- `CHANGELOG.md` — Version history.
- `LICENSE` — MIT License.

## Running Tests

From the repository root, run:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests
```

For manual checks, use a separate test bot and a separate project copy
with a test database. Do not experiment with the production token
or working database.

## Documentation

- [Windows startup, updates, and troubleshooting](docs/RUN_WINDOWS.md).
- [Инструкция для Windows на русском](docs/RUN_WINDOWS_RU.md).
- [Changelog](CHANGELOG.md).

## Screenshots

### Main Interface

| Language Selection | Main Menu | User Profile |
|---|---|---|
| <img src="media/screenshots/language-selection.png" alt="Language selection" width="260"> | <img src="media/screenshots/main-menu.png" alt="Main menu" width="260"> | <img src="media/screenshots/user-profile.png" alt="User profile" width="260"> |

### Tasks and Progress

| Active Tasks | Custom Task | Completed Task History |
|---|---|---|
| <img src="media/screenshots/active-tasks.png" alt="Active household tasks" width="260"> | <img src="media/screenshots/custom-task.png" alt="Custom task creation" width="260"> | <img src="media/screenshots/completed-task-history.png" alt="Completed task history" width="260"> |

### Household and Administration

| Household | Changelog | Administration Panel |
|---|---|---|
| <img src="media/screenshots/household.png" alt="Household information" width="260"> | <img src="media/screenshots/changelog.png" alt="Bot changelog" width="260"> | <img src="media/screenshots/admin-panel.png" alt="Administration panel" width="260"> |

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the version history.

## Contributing

For development setup, validation, and issue reporting,
see [CONTRIBUTING.md](CONTRIBUTING.md).

For vulnerability reporting and handling secrets and personal data,
see [SECURITY.md](SECURITY.md).

## License

This project is distributed under the MIT License.
See [LICENSE](LICENSE) for the full terms.
