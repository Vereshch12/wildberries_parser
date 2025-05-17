import os
import time
from .config import logger
from .utils import extract_product_id
from .api import get_basket, get_prices
from .keywords import extract_keywords_manual, extract_keywords_ai

def get_product_info(url):
    """Получает информацию о товаре из JSON Wildberries."""
    logger.info(f"Processing product URL: {url}")
    nm_id = extract_product_id(url)
    if not nm_id:
        logger.error("Invalid URL format")
        return {'error': 'Неверный формат ссылки'}

    vol = nm_id // 100000
    part = nm_id // 1000
    logger.info(f"Calculated vol={vol}, part={part}")

    basket, data = get_basket(nm_id, vol, part)
    if not basket or not data:
        logger.error(f"Failed to find basket for nm_id={nm_id}")
        return {'error': f'Не удалось найти подходящую корзину для nm_id={nm_id}'}

    logger.info(f"Found basket: {basket}")
    title = data.get("imt_name", "Название не найдено")
    brand = data.get("selling", {}).get("brand_name", "Бренд не найден")
    article = data.get("nm_id", "Артикул не найден")
    description = data.get("description", "Описание не найдено")
    photos = [f"https://{basket}.wbbasket.ru/vol{vol}/part{part}/{nm_id}/images/big/{i}.webp"
              for i in range(1, data.get("media", {}).get("photo_count", 1) + 1)]
    composition = next((opt["value"] for opt in data.get("options", []) if opt["name"] == "Состав"), "Не указан")
    country = next((opt["value"] for opt in data.get("options", []) if opt["name"] == "Страна производства"), "Не указана")

    # Получение цен
    old_price, new_price = get_prices(nm_id)
    logger.info(f"Retrieved prices for nm_id={nm_id}: old_price={old_price}, new_price={new_price}")

    use_ai = os.getenv("USE_AI", "false").lower() == "true"
    logger.info(f"Using {'AI (KeyBERT)' if use_ai else 'manual'} method for keyword extraction")
    start_time = time.time()
    keywords = extract_keywords_ai(title, description) if use_ai else extract_keywords_manual(data, title)
    elapsed_time = time.time() - start_time
    logger.info(f"Keyword extraction completed in {elapsed_time:.2f}s")

    result = {
        "title": title,
        "brand": brand,
        "article": article,
        "description": description,
        "photos": photos,
        "composition": composition,
        "country": country,
        "keywords": keywords,
        "old_price": old_price,
        "new_price": new_price
    }
    logger.info(f"Product info retrieved: title={title}, basket={basket}, old_price={old_price}, new_price={new_price}")
    return result