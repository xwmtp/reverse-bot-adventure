from Bot.Commands.Abstract_message_handler import Message_handler
from Bot.Manage_settings.File_manager_factory import get_channel_settings_manager
from Bot.Config import Configs
import logging


class Bot_settings_handler(Message_handler):

    def __init__(self):
        super().__init__()
        self.commands = {
            'add': ['!add', '!join'],
            'remove': ['!remove', '!delete', '!remove', '!part'],
            'setsrc' : ['!setsrc', "!set_src"],
            'setracetime' : ['!setracetime', '!setrtgg', '!set_racetime', "!set_rtgg", '!setracetimegg', '!set_racetimegg'],
            'help' : ['!help', '!commands', '!command'],
            'channels_names' : ['!channels', '!count'],
            'channels_settings': ['!channels_settings', "!channel_settings"],
            "ping" : ['!ping']
        }
        self.file_manager = get_channel_settings_manager()

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
        if command in self.commands['setsrc']:
            return self.set_src(sender, args)
        if command in self.commands['setracetime']:
            return self.set_racetime(sender, args)
        if command in self.commands['ping']:
            return self.ping()

        # admin
        if command in self.commands['channels_names']:
            return self.channels_names(sender)
        if command in self.commands['channels_settings']:
            return self.channels_settings(sender)

    def add(self, sender):
        logging.info("Received !add command")
        settings = self.file_manager.read_settings()

        for setting in settings:
            if setting.name.lower() == sender.lower():
                return {"response": "I'm already in your channel!"}

        success = self.file_manager.add_new_setting(sender)
        if success:
            return {"actions": {"add": sender},
                    "response": "Added to your channel. Use !help in your chat to see commands."}
        else:
            logging.error(f"Could not add user {sender} to channels list.")
            return {"response": "Could not add myself to your channel, please try again."}

    def remove(self, sender):
        success = self.file_manager.remove_setting(sender)
        if success:
            return {"actions": {"remove": sender},
                    "response": "Removed myself from your channel."}
        else:
            logging.error(f"Could not remove user {sender} from channels list.")
            return {"response": "Could not successfully remove myself from your channel."}

    def ping(self):
        return {"response" : "Pong!"}

    def help(self):
        return {"response" : "Commands: !add, !remove, !setsrc, !setracetime, !ping (see panels). More information: https://github.com/xwmtp/reverse-bot-adventure"}

    def channels_names(self, sender):
        if sender.lower() != Configs.get('admin').lower():
            return
        settings = self.file_manager.read_settings()
        names = [setting.name for setting in settings]
        return {"response": f"{len(names)} connected: {', '.join(names[:50])}"}

    def channels_settings(self, sender):
        if sender.lower() != Configs.get('admin').lower():
            return
        channels_settings = self.file_manager.read_settings()
        channels_strings = [f"{c.name}|{c.src_name}|{c.racetime_name}" for c in channels_settings]
        return {"response": f"{len(channels_strings)} connected: {', '.join(channels_strings[:50])}"}

    def set_src(self, sender, args):
        if len(args) == 0:
            return {"response" : f"Provide your Speedrun.com user name with the command, e.g. !setsrc username"}
        src_name = ' '.join(args)
        setting = self.file_manager.get_setting(sender)
        if not setting:
            return {"response" : f"You haven't added me yet to your channel! Use !add first."}
        setting.src_name = src_name
        success = self.file_manager.update_setting(setting)
        if success:
            return {"response": f"Your Speedrun.com user name has been set to '{format_name(src_name)}'"}
        else:
            logging.error(f"Could not save src name {src_name} for {sender}")
            return {"response": f"Could not successfully save '{format_name(src_name)}' as your Speedrun.come user name"}

    def set_racetime(self, sender, args):
        if len(args) == 0:
            return {"response" : f"Provide your Racetime.gg user name with the command, e.g. !setracetime username"}
        racetime_name = ' '.join(args)
        setting = self.file_manager.get_setting(sender)
        if not setting:
            return {"response": f"You haven't added me yet to your channel! Use !add first."}
        setting.racetime_name = racetime_name
        success = self.file_manager.update_setting(setting)
        if success:
            return {"response": f"Your Racetime.gg user name has been set to '{format_name(racetime_name)}'"}
        else:
            logging.error(f"Could not save racetime name {racetime_name} for {sender}")
            return {"response": f"Could not successfully save '{format_name(racetime_name)}' as your Racetime.gg user name"}

def format_name(name):
    return name.replace('#','')[:30]