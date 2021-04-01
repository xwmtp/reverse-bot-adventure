from Bot.Utils import *

class Message_handler():
    """Abstract class defining a general message handler."""

    def __init__(self):
        # commands in the class
        self.commands = {}

    def handle_message(self, msg, sender, channel):
        """Abstract method. Each message handler has to implement a way to handle incoming messages."""
        raise NotImplementedError('Subclasses must override handle_message()!')

    def get_commands(self):
        """
        Get all the commands of this class, including aliases.
        Each message handler has to define commands, otherwise an error will be raised.
        """
        if self.commands == {}:
            raise NotImplementedError('Subclasses must have self.commands attribute.')
        return flatten(self.commands.values())

    def triggered(self, phrase):
        for trigger in self.get_commands():
            if phrase.lower() == trigger.lower():
                return True
        return False
