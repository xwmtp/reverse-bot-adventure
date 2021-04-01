from Bot.Connections.Message import convert_irc_message
from Bot.Connections.IRC_connection import IRC_connection
from Bot.Responder import Responder
from Bot.Config import Configs
import socket
import logging
import time
import re
import traceback
from collections import deque

def setup_and_run_irc():
    responder = Responder()
    connection = IRC_connection(['xwillmarktheplace', 'scaramangado'], Configs.get('Bot'), Configs.get('bot_oauth'))
    connection.setup_connection()

    if connection.is_connected():
        connection_manager = Connection_manager(connection, responder)
        connection_manager.run()


class Connection_manager:

    def __init__(self, connection, responder):
        self.connection = connection
        self.responder = responder
        self.data_reader = Data_reader(connection)
        self.reconnecter = Reconnecter(connection)

    def run(self):
        while (True):
            message = self.get_next_message()
            if not message:
                continue
            response = self.responder.get_response(message)
            if response:
                self.send_message(response, message.channel)

    def get_next_message(self):
        try:
            line = self.data_reader.get_next_line()
            if line:
                message = self.connection.to_message(line)
                message.log(level='info')
                if message.is_private_message() and not message.is_bot_message():
                    return convert_irc_message(message)
                if message.is_ping():
                    self.connection.send_pong()
                if message.is_pong():
                    self.reconnecter.handle_pong()
                if message.is_unknown():
                    message.log(level='warning')

        except socket.timeout:
            logging.info(f"Socket time out after {self.connection.TIMEOUT} seconds.")
            self.reconnecter.handle_timeout()

        except socket.error as e:
            logging.critical(f"Socket error: {repr(e)}")
            print("reconnecting because socket error")
            self.reconnecter.reconnect()

        except ConnectionResetError as e:
            logging.critical(f"ConnectionResetError: {repr(e)}")
            self.reconnecter.reconnect()

        except Exception as e:
            logging.critical(f"Unknown exception while receiving data: {repr(e)}")
            logging.error(traceback.format_exc())

    def send_message(self, content, channel):
        self.connection.send_message(content, channel)


class Data_reader:

    def __init__(self, connection):
        self.connection = connection
        self.buffer = ''
        self.lines = deque()

    def get_next_line(self):
        logging.debug(f"{len(self.lines)} lines waiting.")
        if len(self.lines) == 0:
            self.receive_next_data()
            if len(self.lines) == 0:
                return

        line = self.lines.popleft()
        return line

    def receive_next_data(self):
        data = self.connection.receive_data()
        logging.debug(f"received data: ${data}$ end data")
        if data:
            self.buffer += data
            data_lines = re.split(r"[\r\n]+", self.buffer)
            for line in data_lines[:-1]:
                self.lines.append(line)
            self.buffer = data_lines[-1]


class Reconnecter:

    def __init__(self, connection):
        self.connection = connection
        self.INIT_INTERVAL = 2
        self.MAX_INTERVAL = 120
        self.reconnect_attempts = 0
        self.validate_reconnect = False
        self.awaiting_pong = False

    def reconnect(self):
        interval = self.INIT_INTERVAL
        if not self.validate_reconnect:
            self.reconnect_attempts = 0

        while True:
            self.reconnect_attempts += 1

            if self.reconnect_attempts > 5:
                logging.critical(f"Trying again in {interval}s...")
                time.sleep(interval)
                interval = min(interval * 2, self.MAX_INTERVAL)

            logging.critical(f"Attempting to reconnect (attempt {self.reconnect_attempts})...")
            self.connection.reset_connection()
            if self.connection.is_connected():
                self.validate_reconnect = True
                self.connection.send_ping(msg='validating_reconnect')
                logging.critical("Reconnected, awaiting validation PONG.")
                return True

    def handle_pong(self):
        logging.info("Received PONG.")
        self.awaiting_pong = False
        if self.validate_reconnect:
            logging.info('Reconnect successful, received PONG.')
            self.validate_reconnect = False

    def handle_timeout(self):
        if self.awaiting_pong:
            logging.error(f"Did not receive PONG since last timeout, trying to reconnect.")
            self.awaiting_pong = False
            self.reconnect()
        else:
            self.send_ping()

    def send_ping(self, msg = 'validating_connection'):
        logging.info(f"Sent validation ping 'msg'.")
        self.last_ping_sent = time.time()
        self.connection.send_ping(msg)
        self.awaiting_pong = True