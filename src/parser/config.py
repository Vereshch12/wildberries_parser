import logging
import os
from logging.handlers import RotatingFileHandler

# Диагностический лог при загрузке модуля
logger = logging.getLogger(__name__)
logger.info("Starting parser/config.py module initialization")

# Настройка логирования
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

use_ai_raw = os.getenv("USE_AI", "false")
logger.info(f"Environment variable USE_AI: {use_ai_raw}")

STOP_WORDS = {
    "и", "с", "для", "в", "на", "от", "по", "не", "при", "а", "но", "или", "что",
    "это", "все", "как", "так", "же", "бы", "к", "у", "о", "из", "за", "до",
    "под", "над", "без", "со", "про", "чтобы", "если", "когда", "где", "очень",
    "каждый", "любой", "другой", "этот", "тот", "самый", "какой", "какая", "какое"
}

# Константы для поиска
SEARCH_BASE_URL = (
    "https://search.wb.ru/exactmatch/ru/common/v13/search?"
    "ab_testing=false&appType=1&curr=rub&dest=-1257786&hide_dtype=13&"
    "lang=ru&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false"
)
SEARCH_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
}
MAX_SEARCH_PAGES = 100

logger.info("parser/config.py module initialization completed")