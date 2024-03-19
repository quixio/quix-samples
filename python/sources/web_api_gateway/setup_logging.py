import logging


def get_logger():
    # Set up logging
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)  # Set to DEBUG for more detailed output
    logger.propagate = False  # Prevent the log messages from propagating to the root logger

    # Create handlers (console and file handler for example)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger