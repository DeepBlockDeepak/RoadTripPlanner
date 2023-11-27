import logging
from logging.handlers import RotatingFileHandler

# Set the logging level here (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOGGING_LEVEL = logging.INFO

# Configure global logger
global_logger = logging.getLogger(__name__)
global_logger.setLevel(LOGGING_LEVEL)

# Log format to include timestamp, logger name, log level, and message
log_format = logging.Formatter(
	"[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S"
)

# File handler with log rotation
file_handler = RotatingFileHandler("runtime.log", maxBytes=1048576, backupCount=5)
file_handler.setFormatter(log_format)

# Console handler to output logs to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

# Add handlers to the global logger
global_logger.addHandler(file_handler)
global_logger.addHandler(console_handler)
