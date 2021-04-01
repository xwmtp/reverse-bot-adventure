import re
from dataclasses import dataclass
from Bot.Config import Configs


def convert_irc_message(irc_message):
    permission = 'viewer'
    if irc_message.tag is not None:
        match = re.search(r"badges=[^;]*;", irc_message.tag)
        if match:
            badges = match.group()
            for possible_permission in ['broadcaster', 'moderator', 'subscriber']:
                if possible_permission in badges:
                    permission = possible_permission
    return Message(irc_message.content, irc_message.recipient, irc_message.sender(), permission)

@dataclass
class Message:
    content: str
    channel: str
    sender: str
    permission: str

    def in_bot_channel(self):
        return self.channel.lower()[1:] == Configs.get("Bot")



