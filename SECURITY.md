# Security policy

## Reporting a vulnerability

Do not publish credentials, personal information,
or working exploit details in a public issue.

Contact the maintainer through an available private channel.
Include the affected version or commit, reproduction conditions,
and potential impact using sanitized examples.

If no private channel is available, open an issue requesting
one without disclosing sensitive details.

## Secrets and personal data

Do not commit or publicly share:

- `.env`;
- Telegram bot tokens;
- administrator passwords;
- proxy credentials;
- household invitation codes;
- working databases or backups;
- participants' personal information or private task contents.

Use `.env.example` only as a template.
It must not contain working secrets.

## Administration and invitations

Share the administrator password only with authorized administrators.

Treat household invitation codes as access information.
Share them only with intended household members.

Restrict access to the computer hosting the bot,
its configuration, and its database.

## Development and testing

Use a separate Telegram bot token and test database
for development.

Do not run development and production instances
with the same bot token.

Remove personal information and secrets from screenshots,
logs, and test examples before sharing them.

## Backups and updates

The working database is `household.db` beside `config.py`.

Stop the bot before making a simple file-copy backup.
Back up the database and `.env` before updating.

Keep backups outside the public repository
and restrict access to authorized users.

## Exposed credentials

If a bot token is exposed, replace it through BotFather
and update the local configuration.

Replace exposed administrator passwords or proxy credentials.

Removing a secret from the latest commit does not remove it
from earlier Git history. Replace exposed credentials
before considering repository cleanup.