from config import Config
from application.bot.telegram_bot import TelegramBot


def run_command():
    bot = TelegramBot(Config.TELEGRAM_BOT_TOKEN)
    bot.start()
