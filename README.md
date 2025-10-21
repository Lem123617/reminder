# Telegram Reminder Bot (Heroku + Scheduler)

A tiny bot that sends a daily reminder at **07:00 UTC** (Heroku Scheduler).  
Default reminder text:
> Please review and cancel any unverified withdrawals. Don’t forget to follow up on pending documents and send the necessary emails.

## Timezone note
- On **October 21, 2025**, Europe/Kyiv is **UTC+3** (EEST).  
  So **07:00 UTC = 10:00 Kyiv**. If you need the reminder at 08:00–09:00 Kyiv, set the Scheduler for **05:00–06:00 UTC** respectively.

## 1) Create a bot and get the token
- You already have a token. **Never commit it to Git.**

## 2) One-time chat ID discovery
You can set `CHAT_IDS` to a comma-separated list of numeric chat IDs (e.g. `12345,67890`).  
To find your chat ID:
- Option A: Write `/id` to your bot after you run it once in polling mode (see below).
- Option B: DM `@userinfobot` in Telegram to get your ID.

### Temporary polling to get your ID (optional)
```bash
# run locally to print your ID on /start or /id
export BOT_TOKEN=XXXX:YYYY
python bot.py --poll
```
Then message your bot on Telegram and send `/id`. Copy the printed ID(s) from the logs.

## 3) Deploy to Heroku
```bash
heroku create your-reminder-bot
heroku buildpacks:add heroku/python
git push heroku main
```

## 4) Set config vars
```bash
heroku config:set BOT_TOKEN=XXXX:YYYY
heroku config:set CHAT_IDS=123456789,987654321
# optional custom text
heroku config:set REMINDER_TEXT="Please review and cancel any unverified withdrawals. Don’t forget to follow up on pending documents and send the necessary emails."
```

## 5) Add Heroku Scheduler
- Add the **Heroku Scheduler** add-on.
- Create a job: **Every day at 07:00 UTC**  
  Command:
```
python bot.py --send-reminder
```

## 6) Optional: run ad-hoc
```bash
heroku run python bot.py --send-reminder
```

## Files
- `bot.py` — sends the reminder (one-shot) or runs polling for `/start`, `/id`.
- `requirements.txt` — minimal deps.
- `Procfile` — defines a worker dyno (optional for Scheduler).
- `runtime.txt` — Python version pin.