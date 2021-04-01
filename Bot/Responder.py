from Bot.Commands.Bot_settings.Bot_settings_handler import Bot_settings_handler
from Bot.Commands.Other_commands.General_commands import General_commands
from Bot.Commands.Speedrun_com.SRC_handler import SRC_handler

class Responder:

    def __init__(self):
        self.handlers = [
            SRC_handler(),
            General_commands()
        ]
        self.settings_handler = Bot_settings_handler()

    def get_response(self, message):
        for handler in self.handlers:
            if handler.triggered(message.content.split()[0]):
                return handler.handle_message(message.content.lower(), message.sender, message.channel)

    def handle_bot_channel_message(self, message):
        return self.settings_handler.handle_message(message.content.lower(), message.sender, message.channel)
