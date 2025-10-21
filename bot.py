import os
    import sys
    import asyncio
    import logging
    import argparse
    from typing import List

    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log = logging.getLogger("reminder-bot")

    DEFAULT_TEXT = ("Please review and cancel any unverified withdrawals. "
                    "Don’t forget to follow up on pending documents and send the necessary emails.")

    def _chat_ids_from_env() -> List[int]:
        raw = os.getenv("CHAT_IDS", "").strip()
        if not raw:
            return []
        ids = []
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                ids.append(int(part))
            except ValueError:
                log.warning("Skipping non-numeric CHAT_ID: %s", part)
        return ids

    async def send_reminder_once():
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise SystemExit("Missing BOT_TOKEN in environment.")
        text = os.getenv("REMINDER_TEXT", DEFAULT_TEXT)
        chat_ids = _chat_ids_from_env()
        if not chat_ids:
            raise SystemExit("CHAT_IDS is empty. Set one or more numeric IDs (comma-separated).")

        app = ApplicationBuilder().token(token).build()
        async with app:
            for cid in chat_ids:
                try:
                    await app.bot.send_message(chat_id=cid, text=text)
                    log.info("Sent reminder to chat_id=%s", cid)
                except Exception as e:
                    log.exception("Failed to send to %s: %s", cid, e)

    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat
        msg = (
            "Hi! I'll send a daily reminder via Heroku Scheduler.

"
            "Your chat id is: {}.
"
            "Add it to the CHAT_IDS env var (comma-separated for multiple).".format(chat.id)
        )
        await update.message.reply_text(msg)
        log.info("START from user=%s chat_id=%s", user.id if user else None, chat.id if chat else None)

    async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        await update.message.reply_text(f"Your chat id: {chat.id}")
        log.info("/id -> %s", chat.id)

    async def run_polling():
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise SystemExit("Missing BOT_TOKEN in environment.")
        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler("start", cmd_start))
        app.add_handler(CommandHandler("id", cmd_id))
        await app.initialize()
        await app.start()
        log.info("Polling started. Press Ctrl+C to stop.")
        try:
            await app.updater.start_polling()
        finally:
            await app.stop()
            await app.shutdown()

    def main():
        parser = argparse.ArgumentParser(description="Telegram reminder bot")
        parser.add_argument("--send-reminder", action="store_true", help="Send the reminder now and exit")
        parser.add_argument("--poll", action="store_true", help="Run bot in polling mode (for /start, /id)")
        args = parser.parse_args()

        if args.poll:
            asyncio.run(run_polling())
        else:
            # default behavior is to send once (works well with Heroku Scheduler)
            asyncio.run(send_reminder_once())

    if __name__ == "__main__":
        main()