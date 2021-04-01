from Bot.Config import Configs
from Bot.Config import Definitions
from datetime import datetime

def validate_settings():
    # all the required fields have been changed from the default value
    validate_settings_file_edited()

    # string settings are actually strings
    validate_string_settings()

    # default logging level is valid
    validate_logging_level()

def validate_settings_file_edited():
    default_stream_settings = {
        Configs.get('admin')     : '123_user_name',
        Configs.get('bot')       : '123_bot_name',
        Configs.get('bot_oauth') : 'oauth:test123'
    }
    for setting, default_value in default_stream_settings.items():
        assert (setting != default_value), "One of the Stream settings in Configs.py has not been filled in! Please fill in your streamer name, Bot name, and the bots oauth.\
                                            \nOpen Configs.py (in the root folder Bot/Configs.py) in a text editor and rerun the program afterwards."

def validate_string_settings():
    for setting in [Configs.get('admin'), Configs.get('Bot')]:
        assert (isinstance(setting, str)), f"One of the string settings ({setting}) in Configs.py is not a string!"

def validate_logging_level():
    level = Configs.get('console_logging_level')
    assert (level in Definitions.LOGGING_LEVELS), f"The selected console logging level ({level}) in Advanced_settings.py is not a valid logging level! Select on from {Definitions.LOGGING_LEVELS}."
