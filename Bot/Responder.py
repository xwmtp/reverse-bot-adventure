from Bot.Commands.Bot_settings.Bot_settings_handler import Bot_settings_handler
from Bot.Commands.Other_commands.General_commands import General_commands
from Bot.Commands.Probability_commands.Probability_handler import Probability_handler
from Bot.Commands.Racetime.Racetime_handler import Racetime_handler
from Bot.Commands.Speedrun_com.SRC_handler import SRC_handler
from Bot.Config import Configs
import logging

class Responder:

    def __init__(self):
        self.handlers = [
            General_commands(),
            SRC_handler(),
            Racetime_handler(),
            Probability_handler()
        ]
        self.settings_handler = Bot_settings_handler()

    def get_response(self, message):
        for handler in self.handlers:
            if handler.triggered(message.content.split()[0]):
                try:
                    return handler.handle_message(message.content.lower(), message.sender, message.channel)
                except Exception as e:
                    logging.error(f"An error occured while handling message {message.content} in channel {message.channel}. Error: {repr(e)}")
                    if Configs.get("debug_mode"):
                        raise e

    def handle_bot_channel_message(self, message):
        try:
            return self.settings_handler.handle_message(message.content.lower(), message.sender, message.channel)
        except Exception as e:
            logging.error(f"An error occured while handling message {message.content} in the Bot channel. Error: {repr(e)}")
