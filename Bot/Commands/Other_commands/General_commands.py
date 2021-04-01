from Bot.Commands.Abstract_message_handler import Message_handler


class General_commands(Message_handler):

    def __init__(self):
        super().__init__()

        self.commands = {
            'commands_list': ['!command', '!commands'],
            'help' : ['!help']
        }

    def handle_message(self, msg, sender, channel):
        split_msg = msg.lower().split(' ')
        command = split_msg[0]
        for function_name, triggers in self.commands.items():
            if command in triggers:
                return eval(f'self.{function_name}("{msg}","{sender}")')

    def help(self, msg, sender):
        return "Commands: !wr, !pb, !src, !race, !commands, !help. " + \
                "The wr, pb and src commands can take a category as their argument. " + \
                "Visit twitch.tv/ReverseBotAdventure to remove the bot or set your src/racetime user names (use !help). " + \
                "Don't forget to mod the bot in your chat for quick responses"

    def commands_list(self, msg, sender):
        return "Commands: !wr, !pb, !src, !race, !commands, !help. " + \
               "The wr, pb and src commands can take a category as their argument."
