from Bot.Manage_settings.File_manager import File_manager
from Bot.Manage_settings.Settings_models import *
from Bot.Config.Definitions import SETTINGS_DIR

DELIMITER = '#'

def get_channel_settings_manager():
    return File_manager(setting_class=Channel_setting,
                        file_path=SETTINGS_DIR / 'channels.txt',
                        delimiter=DELIMITER)