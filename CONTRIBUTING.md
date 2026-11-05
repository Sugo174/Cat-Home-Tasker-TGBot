# Contributing

## Reporting a problem

Check the [Windows guide](docs/RUN_WINDOWS.md)
or [Russian Windows guide](docs/RUN_WINDOWS_RU.md) first.

Include:

- the application version or commit;
- Python and operating system versions;
- startup method: terminal, batch file, or shortcut;
- steps to reproduce;
- expected and actual behaviour;
- sanitized error messages.

Do not attach `.env`, working databases, tokens, passwords,
invitation codes, or participants' personal information.

For vulnerabilities, follow [SECURITY.md](SECURITY.md).

## Development setup

Follow the installation instructions in [README.md](README.md).

Use a separate virtual environment, test bot token,
and test database. A separate project copy is recommended
for manual integration checks.

Do not run development and production instances
with the same bot token.

## Code changes

- Keep changes focused on one problem or feature.
- Update Russian and English interface text when applicable.
- Preserve household boundaries and access checks.
- Check that task completion and experience awards behave correctly
  when buttons are pressed repeatedly.
- Document database schema changes and how existing data is preserved.
- Update both README files and user guides when behaviour changes.
- Use synthetic data in tests and examples.

## Validation

Run tests from the repository root:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests
```

For user workflow changes, check the affected scenario
with a separate test bot.

Describe the checks performed and any remaining limitations.
Automated tests do not by themselves confirm Telegram connectivity
or the complete user experience.

## Commits and pull requests

Use clear English commit messages.

Explain the problem, the resulting behaviour,
and how the change was checked.
Mention database or deployment requirements.

Do not commit local configuration, databases, backups,
Python environments, or release archives.