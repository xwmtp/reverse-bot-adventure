from Bot.Commands.Abstract_message_handler import Message_handler
from Bot.Commands.Bot_settings.Manage_channels import read_channels_settings, overwrite_channels_settings, \
    add_new_channel_setting
from Bot.Config import Configs, Definitions
import logging


class Bot_settings_handler(Message_handler):

    def __init__(self):
        super().__init__()
        self.commands = {
            'add': ['!add', '!join'],
            'remove': ['!remove', '!delete', '!remove', '!part'],
            'help' : ['!help', '!commands', '!commands'],
            'channels' : ['!channels', '!count']
        }
        self.channels_file = Definitions.CHANNELS_FILE

    def handle_message(self, msg, sender, channel):
        split_msg = msg.lower().split()
        command = split_msg[0]
        args = split_msg[1:]

        if command in self.commands['add']:
            return self.add(sender)
        if command in self.commands['remove']:
            return self.remove(sender)
        if command in self.commands['help']:
            return self.help()
        if command in self.commands['channels']:
            return self.channels_count(sender)

    def add(self, sender):
        logging.info("Received !add command")
        settings = read_channels_settings()

        for setting in settings:
            if setting.channel.lower() == sender.lower():
                return {"response": "I'm already in your channel!"}

        success = add_new_channel_setting(sender)
        if success:
            return {"actions": {"add": sender},
                    "response": "Added to your channel. Use !help in your chat to see commands."}
        else:
            logging.error(f"Could not add user {sender} to channels list.")
            return {"response": "Could not add myself to your channel, please try again."}


    def remove(self, sender):
        settings = read_channels_settings()

        new_settings = []
        found_sender = False
        for setting in settings:
            if setting.channel.lower() != sender.lower():
                new_settings.append(setting)
            else:
                found_sender = True
        if not found_sender:
            return {"response": "I'm currently not in your channel!"}

        success = overwrite_channels_settings(new_settings)
        if success:
            return {"actions": {"remove": sender},
                    "response": "Removed myself from your channel."}
        else:
            logging.error(f"Could not remove user {sender} from channels list.")
            return {"response": "Could not successfully remove myself from your channel."}


    def help(self):
        return {"response" : "Commands: !add, !remove"}

    def channels_count(self, sender):
        if sender.lower() != Configs.get('admin').lower():
            return
        with open(self.channels_file, 'r') as file:
            channels = file.read().splitlines()
        channels = [c for c in channels if len(c) > 1]
        return {"response": f"{len(channels)} connected: {', '.join(channels[:50])}"}

