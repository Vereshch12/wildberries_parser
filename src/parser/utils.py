import re
from .config import logger

def extract_product_id(url):
    """Извлекает ID товара из URL."""
    logger.info(f"Extracting product ID from URL: {url}")
    match = re.search(r'/catalog/(\d+)/detail\.aspx', url)
    if match:
        nm_id = int(match.group(1))
        logger.info(f"Extracted nm_id={nm_id}")
        return nm_id
    logger.error("No product ID found in URL")
    return None