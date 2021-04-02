from dataclasses import dataclass
import logging

from Bot.Config import Definitions

FILE_PATH = Definitions.CHANNELS_FILE
DELIMITER = '#'

def read_channels_settings():
    with open(FILE_PATH, 'r') as file:
        raw_channels_settings = file.read().splitlines()

    list_of_channel_settings = []
    for channel_setting in raw_channels_settings:
        try:
            channel, src_name, racetime_name = channel_setting.split(DELIMITER)
            list_of_channel_settings.append(Channel_setting(channel, src_name, racetime_name))
        except ValueError:
            logging.warning(f"Could not parse channel setting {channel_setting}")
            continue
    return list_of_channel_settings

def get_channel_names():
    settings = read_channels_settings()
    return [s.channel for s in settings]

def get_channel_settings(name):
    settings = read_channels_settings()
    for setting in settings:
        if setting.channel.lower() == name.lower():
            return setting

def update_channel_settings(channel, src_name='', racetime_name=''):
    if src_name == '' and racetime_name == '':
        return True
    channels_settings = read_channels_settings()
    for setting in channels_settings:
        if setting.channel.lower() == channel.lower():
            if src_name != '':
                setting.src_name = format_name(src_name)
            if racetime_name != '':
                setting.racetime_name = format_name(racetime_name)
    success = overwrite_channels_settings(channels_settings)
    return success


def overwrite_channels_settings(channels_settings):
    try:
        with open(FILE_PATH, 'w') as file:
            file.write('\n'.join([str(c) for c in channels_settings]) + '\n')
        return True
    except Exception as e:
        logging.error(f"Error while overwriting channels_settings: {repr(e)}")
        return False

def add_new_channel_setting(channel):
    channel_setting = Channel_setting(channel, '', '')
    try:
        with open(FILE_PATH, 'a') as file:
            file.write(str(channel_setting) + '\n')
        return True
    except Exception as e:
        logging.error(f"Error while adding channels_setting {channel_setting}. Error: {repr(e)}")
        return False

def format_name(name):
    return name.replace('#','')[:30]

@dataclass
class Channel_setting:
    channel: str
    src_name: str
    racetime_name: str

    def __str__(self):
        return DELIMITER.join([self.channel, self.src_name, self.racetime_name])