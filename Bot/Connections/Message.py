import re

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

class Message:
    def __init__(self, content, channel, sender, permission):
        self.content = content
        self.channel = channel
        self.sender = sender
        self.permission = permission
