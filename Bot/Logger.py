from Bot.Config import Configs
import logging
import os

def initalize_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')

    if not os.path.exists('logs'):
        os.mkdir('logs')

    def add_logging_handler(handler, level):
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # console handler
    add_logging_handler(logging.StreamHandler(), Configs.get('console_logging_level'))

    # file handler (errors)
    add_logging_handler(logging.FileHandler("logs/ERROR.log", "a"), logging.WARNING)

def update_logging_levels(new_level):
    try:
        logging.getLogger().handlers[0].setLevel(new_level)
        logging.getLogger().handlers[1].setLevel(new_level)
    except Exception as e:
        logging.error(f"Could not update logging level: {repr(e)}")
