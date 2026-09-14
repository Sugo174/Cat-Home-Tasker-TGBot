# Cat Home Tasker Bot

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

The current version is **1.0.6**.

## License

This project is distributed under the [MIT License](LICENSE).