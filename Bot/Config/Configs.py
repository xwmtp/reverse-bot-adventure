from Bot.Config import Definitions
from shutil import copyfile
import os
import configparser
import logging
import sys

class Config:

    def __init__(self, name, file_location):
        self.name = name
        self.config_parser = configparser.ConfigParser()
        self.file_location = file_location

    def load_settings(self):
        self.config_parser.read_file(open(f'{self.file_location}//{self.name}.ini'))
        self.dict = {s:dict(self.config_parser.items(s)) for s in self.config_parser.sections()}
        self.dict = self.parse_dict_values(self.dict)
        if self.dict == {}:
            raise ValueError(f'Empty config dictionary, no setting were found.')

    def copy_from_template(self):
        base_name = self.name.split('-')[0]
        if not os.path.exists(self.file_location):
            os.makedirs(self.file_location)
        copyfile(rf'Bot/Config/Templates/{base_name}_template.ini', fr'{self.file_location}\{self.name}.ini')

    def parse_dict_values(self, dct):

        def parse_setting_string(string):
            # parse to list
            if ',' in string:
                settings = [s.strip().lower() for s in string.split(',')]
                logging.debug(settings)
                return settings
            # parse to boolean
            if string.lower() in ['yes', 'no']:
                return string.lower() == 'yes'
            # parse to logging level
            if string.lower() in ['debug', 'info', 'warning', 'error']:
                return getattr(logging, string.upper())
            return string

        def transform_setting(setting, option):
            if option != 'bot_oauth':
                if isinstance(setting, list):
                    setting = [s.lower() for s in setting]
                elif isinstance(setting, str):
                    setting = setting.lower()
            if option == 'editors':
                if not isinstance(setting, list):
                    setting = [setting]
                setting = [get('streamer')] + setting
            if option == 'racetime games' and not isinstance(setting, list):
                return [setting]
            return setting

        for section, settings in dct.items():
            for option, value in settings.items():
                parsed_setting = parse_setting_string(value)
                transformed_setting = transform_setting(parsed_setting, option)
                dct[section][option] = transformed_setting
        return dct


configs = [
    Config(f'Settings', Definitions.ROOT_DIR / 'Settings')
]

def create_settings():
    for config in configs:
        config.copy_from_template()
    open(Definitions.ROOT_DIR / 'Settings/channels.txt', 'a').close()

def import_settings():
    for config in configs:
        config.load_settings()

def get(option):
    option = option.lower()
    for config in configs:
        for section in config.dict.keys():
            if option in config.dict[section].keys():
                return config.dict[section][option]

    logging.warning(f"Setting '{option}' does not exist!")

def get_section(section):
    section = section.lower()
    for config in configs:
        if section in config.dict.keys():
            return config.dict[section]

def set(option, value):
    option = option.lower()
    for config in configs:
        for section in config.dict.keys():
            if option in config.dict[section].keys():
                config.dict[section][option] = value
                return True
    logging.warning(f"Option '{option}' does not exist and cannot be updated.")
    return False
