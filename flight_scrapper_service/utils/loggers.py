import logging

def setup_logger():
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.INFO)

    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    return logger
