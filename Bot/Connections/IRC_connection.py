import socket
import logging
import re
import time

from Bot.Config import Configs

class IRC_connection:

    def __init__(self, bot_name, bot_oauth):
        self.HOST = "irc.twitch.tv"
        self.PORT = 6667
        self.TIMEOUT = 60
        self.NICK = bot_name
        self.PASS = bot_oauth
        self.socket = socket.socket()

    def connect_to_irc(self):
        try:
            self.socket.settimeout(self.TIMEOUT)
            self.socket.connect((self.HOST, self.PORT))

            logging.info(f"Connecting to Bot account '{self.NICK}'...")
            self.socket.send(bytes(f'PASS {self.PASS}\r\n', 'UTF-8'))
            self.socket.send(bytes(f'NICK {self.PASS}\r\n', 'UTF-8'))
            self.socket.send(bytes('CAP REQ :twitch.tv/tags\r\n', 'UTF-8'))

            logging.info('Connected Bot to twitch IRC.')

        except Exception as e:
            logging.critical(
                f"Failed connecting to Bot {self.NICK} Error: {repr(e)}")

    def join_channel(self, channel_name):
        try:
            time.sleep(1)
            self.socket.send(bytes(f'JOIN #{channel_name}\r\n', 'UTF-8'))
            logging.info(f"Joined channel #{channel_name}")

        except Exception as e:
            logging.critical(
                f"Failed to join channel #{channel_name} Error: {repr(e)}")

    def part_channel(self, channel_name):
        try:
            self.socket.send(bytes(f'PART #{channel_name}\r\n', 'UTF-8'))
            logging.info(f"Parted channel #{channel_name}")

        except Exception as e:
            logging.critical(
                f"Failed to part channel #{channel_name} Error: {repr(e)}")

    def reset_connection(self):
        self.socket.close()
        self.socket = socket.socket()
        self.socket = self.setup_connection() #todo

    def is_connected(self):
        return self.socket is not None

    def send_pong(self, msg):
        self.socket.send(bytes(f'PONG {msg}\r\n', 'UTF-8'))

    def send_ping(self, msg):
        self.socket.send(bytes(f'PING {msg}\r\n', 'UTF-8'))

    def send_message(self, msg, channel):
        if msg == 'SOCKET':
            raise socket.error
        if msg == '' or msg == []:
            return
        if isinstance(msg, list):
            for m in msg:
                self.socket.send(bytes(f'PRIVMSG {channel} :{m}\r\n', 'UTF-8'))
        else:
            self.socket.send(bytes(f'PRIVMSG {channel} :{msg}\r\n', 'UTF-8'))
        logging.info(f"Sent message in {channel}: {msg}")

    def receive_data(self, characters=2048):
        return self.socket.recv(characters).decode('UTF-8')

    def to_message(self, line):
        return IRC_message(line)


class IRC_message:

    def __init__(self, raw_message):
        message_parts = str.rstrip(raw_message).split(' ')
        logging.debug(f"to parse: {message_parts}")
        if message_parts[0][0] == '@':
            self.tag = message_parts[0]
            message_parts = message_parts[1:]
        else:
            self.tag = None
        self.irc_message = ' '.join(message_parts)
        self.client_identifier = message_parts[0]
        self.command = message_parts[1]
        self.recipient = message_parts[2] if len(message_parts) > 2 else ''
        self.content = ' '.join(message_parts[3:])[1:]
        self.KNOWN_COMMANDS = ['PRIVMSG', 'JOIN', 'PING', 'PONG', 'CAP']
        logging.debug(
            f'Parsed tag {self.tag}, client {self.client_identifier}, command {self.command}, rec {self.recipient}, content {self.content}')

    def sender(self):
        if self.command == 'PRIVMSG':
            match = re.search(r"(?<=:)\w+(?=!)", self.client_identifier)
            if match:
                return match.group()

    def is_private_message(self):
        return self.command == 'PRIVMSG'

    def is_bot_message(self):
        sender = self.sender()
        if not sender:
            return False
        return sender.lower() == Configs.get('Bot').lower()

    def is_ping(self):
        return self.command == 'PING'

    def is_pong(self):
        return self.command == 'PONG'

    def is_unknown(self):
        if self.command in self.KNOWN_COMMANDS:
            return False
        try:
            int(self.command)
            return True
        except ValueError:
            return False

    def log(self, level='info'):
        if level=='warning:':
            logging.warning(f"Message: {self.irc_message}")
        else:
            logging.info(f"Message: {self.irc_message}")
