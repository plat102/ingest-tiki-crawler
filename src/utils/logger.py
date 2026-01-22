import logging
import sys
from src.config import LOG_FILE_APP, LOG_FILE_ERROR

def setup_logging():
    """3 handlers
    - Console
    - App
    - Error
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE_APP, encoding='utf-8'), # Write log to file
            logging.StreamHandler(sys.stdout) # Write to terminal
        ]
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Common format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # General handler
    file_handler = logging.FileHandler(LOG_FILE_APP, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Error handler
    error_handler = logging.FileHandler(LOG_FILE_ERROR, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    logging.info('Logging initialized.')
