import os
import time
import requests
from urllib.parse import quote
from .config import logger
from .utils import extract_product_id
from .api import get_basket, get_prices
from .keywords import extract_keywords_manual, extract_keywords_ai
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

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

async def search_product_by_keywords(nm_id, keyword, update_message=None, keyword_idx=1, total_keywords=1, previous_results=None, cancel_event=None):
    """Ищет товар по ключевому слову на страницах выдачи Wildberries."""
    logger.info(f"Searching for nm_id={nm_id} with keyword='{keyword}'")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
    }
    base_url = (
        "https://search.wb.ru/exactmatch/ru/common/v13/search?"
        "ab_testing=false&appType=1&curr=rub&dest=-1257786&hide_dtype=13&"
        "lang=ru&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false"
    )
    encoded_keyword = quote(keyword)
    page = 1
    max_pages = 100  # Ограничение на количество страниц для поиска
    total_products = 0

    # Создаем клавиатуру с кнопкой "Отмена"
    cancel_button = InlineKeyboardButton(text="❌ Отменить поиск", callback_data=f"cancel_{nm_id}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])

    while page <= max_pages:
        # Проверяем, не отменен ли поиск
        if cancel_event and cancel_event.is_set():
            logger.info(f"Search cancelled for nm_id={nm_id}, keyword='{keyword}'")
            return None

        url = f"{base_url}&query={encoded_keyword}&page={page}"
        logger.info(f"Requesting search page {page} for keyword='{keyword}': {url}")
        try:
            time.sleep(1)  # Задержка для предотвращения блокировок
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()

            products = data.get("data", {}).get("products", [])
            # Фиксируем total_products только на первой странице
            if page == 1:
                total_products = data.get("data", {}).get("total", 0)
            if not products:
                logger.info(f"No products found on page {page} for keyword='{keyword}'")
                break

            # Подсчет позиции
            for idx, product in enumerate(products, start=(page-1)*100+1):
                if product.get("id") == nm_id:
                    logger.info(f"Found product nm_id={nm_id} on page {page}, position {idx}")
                    return idx, page, total_products

            # Обновляем сообщение, если оно предоставлено
            if update_message:
                message_text = (
                    f"📊 Промежуточные результаты ({keyword_idx}/{total_keywords}):\n\n"
                )
                if previous_results:
                    message_text += "\n".join(previous_results) + "\n\n"
                message_text += (
                    f"🔎 Ключевое слово \"{keyword}\":\n"
                    f"  • Всего товаров: {total_products}\n"
                    f"  • Текущая страница: {page}\n"
                    f"  • Статус: Поиск продолжается, ожидайте..."
                )
                try:
                    await update_message.edit_text(message_text, reply_markup=keyboard)
                except Exception as e:
                    logger.error(f"Failed to update message for keyword='{keyword}', page={page}: {str(e)}")

            page += 1

        except requests.RequestException as e:
            logger.error(f"Search request failed for keyword='{keyword}', page={page}: {str(e)}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing search response for keyword='{keyword}', page={page}: {str(e)}")
            return None

    logger.info(f"Product nm_id={nm_id} not found for keyword='{keyword}' after {max_pages} pages")
    return None, None, total_products