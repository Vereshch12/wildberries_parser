import os
import logging

# Диагностический лог при загрузке модуля
logger = logging.getLogger(__name__)
logger.info("Starting config.py module initialization")

# Настройка логирования
log_dir = "/app/logs"
try:
    os.makedirs(log_dir, exist_ok=True)
    logger.info(f"Created log directory: {log_dir}")
except Exception as e:
    logger.error(f"Failed to create log directory {log_dir}: {str(e)}")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, "parser.log"))
    ]
)

# Логирование значения USE_AI
use_ai_raw = os.getenv("USE_AI", "false")
logger.info(f"Environment variable USE_AI: {use_ai_raw}")

# Расширенный список стоп-слов
STOP_WORDS = {
    "и", "с", "для", "в", "на", "от", "по", "не", "при", "а", "но", "или", "что",
    "это", "все", "как", "так", "же", "бы", "к", "у", "о", "из", "за", "до",
    "под", "над", "без", "со", "про", "чтобы", "если", "когда", "где", "очень",
    "каждый", "любой", "другой", "этот", "тот", "самый", "какой", "какая", "какое"
}

logger.info("config.py module initialization completed")