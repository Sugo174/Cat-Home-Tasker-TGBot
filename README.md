# Cat Home Tasker Bot

<p align="center">
  <img src="assets/cat-home-tasker.png" alt="Cat Home Tasker" width="320">
</p>

[![Python tests](https://github.com/Sugo174/Cat-Home-Tasker-TGBot/actions/workflows/tests.yml/badge.svg)](https://github.com/Sugo174/Cat-Home-Tasker-TGBot/actions/workflows/tests.yml)

A Telegram bot that turns household chores into a shared game. Household members can create and complete tasks, earn experience points, track progress, and manage their profiles through a Russian or English interface.

## Features

- Household creation and joining by invitation code
- Standard and custom household tasks
- Experience points and user levels
- Task completion history
- User profiles
- Russian and English interface
- In-place menu navigation with message replacement
- Administrative panel for managing households and users
- Bilingual bot changelog
- SOCKS5 proxy support
- SQLite database storage

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

## Technology

- Python
- aiogram 3
- SQLite
- python-dotenv
- aiohttp-socks

## Project Structure

```text
.
├── handlers/
│   ├── __init__.py
│   ├── admin.py          # Administrative panel handlers
│   └── user.py           # User interface and task handlers
├── bot.py                # Application entry point
├── config.py             # Environment variables and paths
├── database.py           # Database models and operations
├── keyboards.py          # Inline keyboard layouts
├── localization.py       # Russian and English translations
├── states.py             # Finite-state machine states
├── schema.sql            # SQLite database schema
├── requirements.txt      # Python dependencies
├── .env.example          # Environment configuration example
├── start_bot.bat         # Windows startup script
├── assets/
│   └── cat-home-tasker.ico       # Desktop shortcut icon
├── create_desktop_shortcut.ps1   # Creates the Windows desktop shortcut
├── setup_windows.bat             # Runs the shortcut setup script
└── README.md
```

## Requirements

- Python 3.10 or newer
- Telegram bot token from [@BotFather](https://t.me/BotFather)
- SOCKS5 proxy connection

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Sugo174/Cat-Home-Tasker-TGBot.git
cd Cat-Home-Tasker-TGBot
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux or macOS:

```bash
source .venv/bin/activate
```

3. Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and provide your settings:

```env
BOT_TOKEN=your_bot_token
ADMIN_PASSWORD=your_admin_password
PROXY_URL=socks5://username:password@host:port
```

The `.env` file contains private information and must not be committed to Git.

## Running the Bot

Run the bot directly:

```bash
python bot.py
```

On Windows, you can also use:

```text
start_bot.bat
```

### Windows Desktop Shortcut

After installing the dependencies and configuring `.env`, Windows users can create a desktop shortcut:

1. Run `setup_windows.bat` once from the project folder.
2. A **Cat Home Tasker** shortcut with the application icon will appear on the desktop.
3. Use this shortcut to start the bot.

The shortcut starts `start_bot.bat` from the correct project folder.

## Administration

Send the following command to the bot:

```text
/admin
```

Enter the password configured in `ADMIN_PASSWORD` to open the administration panel.

## Data Storage

The bot creates a local SQLite database automatically. Database files are excluded from Git and should be backed up separately when the bot is used in production.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete version history.

The current version is **1.0.7**.

## License

This project is distributed under the [MIT License](LICENSE).