import requests
from urllib.parse import quote
from .config import logger, SEARCH_BASE_URL, SEARCH_HEADERS, MAX_SEARCH_PAGES
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.messages import format_intermediate_results
import asyncio

async def search_product_by_keywords(nm_id, keyword, update_message=None, keyword_idx=1, total_keywords=1, previous_results=None, cancel_event=None, update_page_interval=5):
    """Ищет товар по ключевому слову на страницах выдачи Wildberries."""
    logger.info(f"Searching for nm_id={nm_id} with keyword='{keyword}'")
    encoded_keyword = quote(keyword)
    page = 1
    total_products = 0

    cancel_button = InlineKeyboardButton(text="❌ Отменить поиск", callback_data=f"cancel_{nm_id}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])

    while page <= MAX_SEARCH_PAGES:
        if cancel_event and cancel_event.is_set():
            logger.info(f"Search cancelled for nm_id={nm_id}, keyword='{keyword}'")
            return None

        url = f"{SEARCH_BASE_URL}&query={encoded_keyword}&page={page}"
        logger.info(f"Requesting search page {page} for keyword='{keyword}': {url}")
        try:
            await asyncio.sleep(1)
            if cancel_event and cancel_event.is_set():
                logger.info(f"Search cancelled for nm_id={nm_id}, keyword='{keyword}' before request")
                return None

            response = requests.get(url, headers=SEARCH_HEADERS, timeout=5)
            response.raise_for_status()
            data = response.json()

            products = data.get("data", {}).get("products", [])
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

            # Обновляем сообщение только на страницах, кратных update_page_interval (у тг ограничение, блок, если слишком часто обновлять)
            if update_message and (page % update_page_interval == 0 or page == 1):
                message_text = format_intermediate_results(
                    keyword, keyword_idx, total_keywords, total_products, page, previous_results
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

    logger.info(f"Product nm_id={nm_id} not found for keyword='{keyword}' after {MAX_SEARCH_PAGES} pages")
    return None, None, total_products