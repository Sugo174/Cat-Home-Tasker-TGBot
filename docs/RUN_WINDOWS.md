# Running Cat Home Tasker on Windows

[Русская версия](RUN_WINDOWS_RU.md) · [Project overview](../README.md)

## Before you start

You need:

- Python 3.14;
- the project source files;
- a Telegram bot token from BotFather;
- a SOCKS5 proxy URL;
- an administration panel password.

Run all commands in PowerShell from the repository root.

Before updating an existing installation,
back up `household.db` and `.env`.

## First installation

Create an environment and install dependencies:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create `.env` using `.env.example` as a template:

```dotenv
BOT_TOKEN=your_bot_token
ADMIN_PASSWORD=your_admin_password
PROXY_URL=socks5://username:password@host:port
```

All three settings are required.
Replace the example values with your own configuration.

Do not publish `.env`: it contains the bot token,
administrator password, and proxy credentials.

## Start the bot

```powershell
.\.venv\Scripts\python.exe bot.py
```

The bot initializes the database and starts receiving
Telegram updates.

Keep the terminal open.
Press Ctrl+C to stop the bot.

Do not run multiple instances with the same token.

## Verify operation

1. Open your bot in Telegram.
2. Send `/start` and select a language.
3. Create a household or join one using an invitation.
4. Check task creation, completion, and your profile.

Send `/admin` to access the administration panel.
Use the password configured in `ADMIN_PASSWORD`.

## Batch file and desktop shortcut

`start_bot.bat` runs `py -3.14 bot.py`.
It uses the installed Python 3.14 rather than `.venv`.

If dependencies are installed only in `.venv`,
use the direct startup command above.

`setup_windows.bat` creates a Cat Home Tasker desktop shortcut.
The shortcut starts `start_bot.bat`.

Creating a shortcut does not install Python or dependencies.

## Updating and preserving data

1. Stop the bot with Ctrl+C.
2. Back up `household.db` and `.env` to a location
   with restricted access.
3. Update application files while preserving the database and settings.
4. Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

5. Start the bot.
6. Check the existing household, tasks, profile,
   and completion history.

The working database is `household.db` beside `config.py`.
Stop the bot before backing up the database by copying its file.

Do not replace the working database with an empty database
from another installation.
Do not replace `.env` with `.env.example`.

## Troubleshooting

### No module named aiogram

Dependencies are missing from the Python environment
used to start the bot.

From the repository root, run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe bot.py
```

If the error occurs only when using the shortcut,
check the dependencies of the installed Python 3.14.
The batch file uses `py -3.14`, not `.venv`.

### Dependencies cannot be installed

Check the selected environment's Python version:

```powershell
.\.venv\Scripts\python.exe --version
```

This guide uses Python 3.14.
Do not use a Python 3.8 environment from another project.

### A required environment variable is missing

Check that `.env` is beside `config.py`
and contains all three settings:

- `BOT_TOKEN`;
- `ADMIN_PASSWORD`;
- `PROXY_URL`.

Make sure the filename is not `.env.txt`.

### The bot does not respond in Telegram

- Check that the bot process is running.
- Inspect errors in its terminal.
- Check the token and proxy availability.
- Make sure another instance with the same token is not running.
- Send `/start` again.

Do not publish the token or proxy credentials when requesting help.

### Previous data is missing after an update

Stop the bot and check the working database location.
Do not delete or overwrite databases until you identify
which copy contains the required data.

## Requesting help

Include:

- the application version or commit;
- Python and Windows versions;
- startup method: terminal, batch file, or shortcut;
- steps to reproduce;
- the full error message with secrets removed.

Remove tokens, passwords, invitation codes,
and participants' personal information from screenshots.

Do not attach the working database or `.env`
to public reports.