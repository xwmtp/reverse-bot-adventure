from Bot.Commands.Speedrun_com.SRC_handler import SRC_handler

class Responder:

    def __init__(self):
        self.handlers = [
            SRC_handler()
        ]

    def get_response(self, message):
        for handler in self.handlers:
            if handler.triggered(message.content.split()[0]):
                return handler.handle_message(message.content, message.sender, message.channel)