# Finviz Breadth Tracker

GitHub Actions automation for updating Finviz market breadth data.

The updater fetches `https://finviz.com/` and extracts only these values:

| Date | New High | New High % | New Low | New Low % | Advancing | Advancing % | Declining | Declining % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

It writes the data to:

- `finviz_breadth.csv`
- `finviz_breadth.xlsx`
- `finviz_breadth_log.txt`

Rows use the New York market date. If a row for the current New York date already exists, the script updates it instead of adding a duplicate.

## Run Locally

```bash
python -m pip install -r requirements.txt
python finviz_breadth_updater.py
```

## GitHub Actions

The workflow is defined at `.github/workflows/update-finviz.yml`.

It supports manual runs with `workflow_dispatch` and scheduled daily runs at 9:30 AM Jordan time. GitHub cron uses UTC, so the workflow uses UTC candidate schedules plus an `Asia/Amman` time check before running. The workflow commits only the generated breadth CSV, XLSX, and log file back to the repository.

## Phone delivery with Telegram

- Create a Telegram bot using BotFather.
- Save the bot token as a GitHub repository secret named `TELEGRAM_BOT_TOKEN`.
- Get your Telegram chat ID.
- Save the chat ID as a GitHub repository secret named `TELEGRAM_CHAT_ID`.
- Run the workflow manually to test: Actions -> Update Finviz Breadth -> Run workflow.
- After that, the scheduled workflow sends the data to your phone.

The Telegram message contains only the date and these breadth values with their Finviz percentages: New High, New Low, Advancing, and Declining. If the Telegram secrets are missing, local script runs still update the CSV/XLSX files and log that Telegram delivery was skipped.

## Send updates to multiple people without a server

The current bot sends only to the configured `TELEGRAM_CHAT_ID`.

If `TELEGRAM_CHAT_ID` is your private chat ID, only you receive the message.

To let many people receive the same daily update without running a server, webhook, VPS, Cloudflare Worker, laptop bot, or polling loop:

- Create a Telegram channel or group.
- Add the bot as an admin.
- Give the bot permission to post messages.
- Change the GitHub repository secret `TELEGRAM_CHAT_ID` to the channel username, for example `@finviz_breadth_alerts`, or to the group chat ID.
- Run the workflow manually to test: Actions -> Update Finviz Breadth -> Run workflow.
- Share the channel or group invite link with people.

Interactive commands such as `/latest`, `/start`, `/help`, and `/ping` require a webhook, server, or polling system. They are not supported in this no-server setup.

## How to use this from another laptop

- Go to the GitHub repository.
- Open or download `finviz_breadth.xlsx`.
- To manually update it, go to Actions -> Update Finviz Breadth -> Run workflow.
- The original laptop does not need to be on.
- Python is only needed if you want to test the script locally.
- Excel is only needed to open the `.xlsx` file.
- The CSV file can also be opened in Excel as a backup.

## Transfer / portability

- The GitHub repository is the source of truth.
- The local folder is only a setup copy.
- After confirming the repo is pushed and GitHub Actions works, the local folder can be copied, zipped, moved to another laptop, or deleted.
- To move it to another laptop, either clone the GitHub repo or download it as ZIP.
- Do not copy this project into unrelated repos.

## Limitations

Finviz can block automated requests or change its page layout. In either case, the updater logs the failure and exits with a nonzero status instead of writing uncertain data.
