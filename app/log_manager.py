import logging

LOGGING_LEVEL = (
	logging.INFO
)  # (DEBUG, INFO, WARNING, ERROR, CRITICAL) Shows all levels at or above selected


global_logger = logging.getLogger(__name__)
global_logger.setLevel(LOGGING_LEVEL)
log_format = logging.Formatter("[%(asctime)s] [%(module)s/%(levelname)s]: %(message)s")

file_handler = logging.FileHandler("runtime.log")
file_handler.setFormatter(log_format)

global_logger.addHandler(file_handler)
