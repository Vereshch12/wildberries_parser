import logging
import os
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
logger.info("Starting bot/config.py module initialization")

log_dir = "/app/logs"
try:
    os.makedirs(log_dir, exist_ok=True)
    logger.info(f"Created log directory: {log_dir}")
except Exception as e:
    logger.error(f"Failed to create log directory {log_dir}: {str(e)}")

log_file = os.path.join(log_dir, "parser.log")
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10 МБ
    backupCount=5  # Хранить до 5 резервных копий
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        file_handler
    ]
)

# Переменная для отслеживания активных поисков
active_searches = {}

logger.info("bot/config.py module initialization completed")