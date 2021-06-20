from Bot.Connections.Connection_manager import setup_and_run_irc
from Bot.Config import Configs
from Bot.Config.Validate_settings import validate_settings
from Bot.Logger import initalize_logger
import os


if __name__ == '__main__':
    print("Welcome to Reverse Bot Adventure")
    first_time_boot = not os.path.exists(f'Settings/Settings.ini')
    if first_time_boot:
        Configs.create_settings()
        print("Created 'Settings/settings.ini'. Fill in the settings and restart the program.")
    else:
        Configs.import_settings()
        initalize_logger()
        validate_settings()

        setup_and_run_irc()
