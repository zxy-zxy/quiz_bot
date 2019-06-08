from application.bot.telegram_bot import TelegramBot


def run_command(telegram_bot_token):
    bot = TelegramBot(telegram_bot_token)
    bot.start()
