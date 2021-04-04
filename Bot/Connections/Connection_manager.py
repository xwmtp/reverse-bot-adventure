from Bot.Commands.Bot_settings.Manage_channels import get_channel_names
from Bot.Connections.Message import convert_irc_message
from Bot.Connections.IRC_connection import IRC_connection
from Bot.Responder import Responder
from Bot.Config import Configs, Definitions
import socket
import logging
import time
import re
import traceback
from collections import deque

def setup_and_run_irc():
    responder = Responder()
    connection = IRC_connection(Configs.get('Bot'), Configs.get('bot_oauth'))
    connection_manager = Connection_manager(connection, responder)
    connection_manager.setup()
    connection_manager.run()


class Connection_manager:

    def __init__(self, connection, responder):
        self.connection = connection
        self.responder = responder
        self.data_reader = Data_reader(connection)
        self.reconnecter = Reconnecter(connection)

    def setup(self):
        self.connection.connect_to_irc()
        self.process_welcome_messages()
        self.join_all_saved_channels()

    def process_welcome_messages(self):
        while (True):
            message = self.get_next_message()
            if message:
                response = self.responder.get_response(message)
                if response:
                    self.send_message(response, message.channel)

            if self.data_reader.queue_empty():
                return


    def run(self):
        while (True):
            message = self.get_next_message()
            if not message:
                continue
            if message.in_bot_channel():
                response = self.responder.handle_bot_channel_message(message)
                self.process_bot_channel_response(message, response)
            else:
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
            self.reconnect()

        except ConnectionResetError as e:
            logging.critical(f"ConnectionResetError: {repr(e)}")
            self.reconnect()

        except Exception as e:
            logging.critical(f"Unknown exception while receiving data: {repr(e)}")
            logging.error(traceback.format_exc())

    def send_message(self, content, channel):
        if not channel.startswith('#'):
            channel = '#' + channel
        self.connection.send_message(content, channel)

    def join_channels(self, channel_names):
        channel_names = [c for c in channel_names if len(c) > 1]
        for channel in channel_names:
            self.connection.join_channel(channel)
            self.process_welcome_messages()
        if Configs.get("post_welcome_message").lower() == "true":
            for channel in channel_names:
                self.send_message("Ready to put Bottle on B! Use !help to see commands.", channel)

    def join_all_saved_channels(self):
        channels_to_join = get_channel_names()
        if self.connection.is_connected():
            self.join_channels([Configs.get('Bot')])
            self.join_channels(channels_to_join)
        else:
            logging.critical("Connection is not connected, won't join channels.")

    def reconnect(self):
        self.reconnecter.reconnect()
        self.process_welcome_messages()
        self.join_all_saved_channels()


    def process_bot_channel_response(self, message, response):
        if response is None:
            return
        if 'actions' in response:
            if 'add' in response['actions']:
                self.join_channels([message.sender])
            if 'remove' in response['actions']:
                self.connection.part_channel(message.sender)
        if 'response' in response:
            self.send_message(f"@{message.sender} {response['response']}", message.channel)


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
        logging.debug(f"Received {len(self.lines)} lines")

    def queue_empty(self):
        return len(self.lines) == 0


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
                try:
                    self.validate_reconnect = True
                    self.connection.send_ping(msg='validating_reconnect')
                    logging.info("Reconnected, awaiting validation PONG.")
                    return True
                except Exception as e:
                    logging.error(f"Error occured while reconnecting: {repr(e)}")
            else:
                logging.critical("Reconnection failed, socket is None.")

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