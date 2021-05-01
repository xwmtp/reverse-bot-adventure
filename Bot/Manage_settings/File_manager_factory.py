from Bot.Manage_settings.File_manager import File_manager
from Bot.Manage_settings.Settings_models import *
from Bot.Config.Definitions import SETTINGS_DIR
import os
import logging

DELIMITER = '#'

def get_channel_settings_manager():
    path = SETTINGS_DIR / 'channels.txt'
    create_if_not_exist(path)
    return File_manager(setting_class=Channel_setting,
                        file_path=path,
                        delimiter=DELIMITER)



def create_if_not_exist(file_path):
    if not os.path.exists(file_path):
        open(file_path, 'a').close()
        logging.info(f"Created file {file_path}")