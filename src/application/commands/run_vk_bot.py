from application.bot.vk_bot import VkBot


def run_command(vk_group_token):
    vk_bot = VkBot(vk_group_token)
    vk_bot.start()
