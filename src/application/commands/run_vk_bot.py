from config import Config
from application.bot.vk_bot import VkBot


def run_command():
    vk_bot = VkBot(Config.VK_GROUP_TOKEN)
    vk_bot.start()
