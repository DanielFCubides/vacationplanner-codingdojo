import logging


def setup_logger(*, logger_name: str):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    return logger
