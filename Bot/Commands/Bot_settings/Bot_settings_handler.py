from Bot.Commands.Abstract_message_handler import Message_handler
from Bot.Config import Configs, Definitions
from Bot.Utils import make_ordinal
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
        with open(self.channels_file, 'r') as file:
            channels = file.read().splitlines()

        for channel in channels:
            if channel.lower() == sender.lower():
                return {"response": "I'm already in your channel!"}

        try:
            with open(self.channels_file, 'a') as file:
                file.write(sender.lower() + '\n')
            return {"actions": {"add": sender},
                    "response": "Added to your channel. Use !help in your chat to see commands."}
        except Exception as e:
            logging.error(f"Could not add user {sender} to channels list. Error: {repr(e)}")

    def remove(self, sender):
        with open(self.channels_file, 'r') as file:
            channels = file.read().splitlines()

        new_channels = []
        found_sender = False
        for channel in channels:
            if channel.lower() != sender.lower():
                new_channels.append(channel)
            else:
                found_sender = True

        if not found_sender:
            return {"response": "I'm not in your channel!"}

        try:
            with open(self.channels_file, 'w') as file:
                file.write('\n'.join(new_channels) + '\n')
            return {"actions": {"remove": sender},
                    "response": "Removed myself from your channel."}
        except Exception as e:
            logging.error(f"Could not remove user {sender} from channels list. Error: {repr(e)}")

    def help(self):
        return {"response" : "Commands: !add, !remove"}

    def channels_count(self, sender):
        if sender.lower() != Configs.get('admin').lower():
            return
        with open(self.channels_file, 'r') as file:
            channels = file.read().splitlines()
        channels = [c for c in channels if len(c) > 1]
        return {"response": f"{len(channels)} connected: {', '.join(channels[:50])}"}

