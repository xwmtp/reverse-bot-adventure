from Bot.Commands.Abstract_message_handler import Message_handler
from Bot.Commands.Probability_commands.Probability_event import *


class Probability_handler(Message_handler):

    def __init__(self):
        super().__init__()

        self.commands = {
            'dampe': ['!dampe'],
            'rock' : ['!rock', '!rocks'],
            'truth_spinner' : ['!spinner', '!truthspinner', '!truth_spinner'],
            'bush_patch' : ['!bushes', '!bush', '!bushpatch', '!bushespatch', '!bush_patch', '!bushes_patch']
        }

        self.file_manager = get_probabilities_settings_manager()
        self.probability_events = {
            'dampe' : Dampe_event(),
            'rock' : Rock_event(),
            'truth_spinner' : Spinner_event(),
            'bush_patch' : Bush_event()
        }

    def handle_message(self, msg, sender, channel):
        split_msg = msg.lower().split(' ')
        command = split_msg[0]
        if len(split_msg) > 0:
            args = split_msg[1:]
        else:
            args = []

        for command_type in self.commands:
            if command in self.commands[command_type]:
                event = self.probability_events[command_type]
                return event.respond(args, sender.lower(), channel[1:].lower())

