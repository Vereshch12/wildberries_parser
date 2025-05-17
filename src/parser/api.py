import requests
import time
from .config import logger

def get_basket(nm_id, vol, part, basket_num=24, max_basket=30):
    """
    Определяет basket-XX и возвращает JSON-данные для товара.

    Использует фиксированные диапазоны для vol <= 3917 (basket-01 до basket-22).
    Для vol > 3917 использует basket-23, затем перебирает basket-24 до max_basket.
    Возвращает кортеж (basket, json_data) или (None, None) при ошибке.

    Args:
        nm_id (int): ID товара.
        vol (int): nm_id // 100000.
        part (int): nm_id // 1000.
        basket_num (int): Текущий номер корзины для перебора (начинается с 24).
        max_basket (int): Максимальный номер корзины для перебора (по умолчанию 30).

    Returns:
        tuple: (str or None, dict or None) - имя корзины и JSON-данные или (None, None).
    """
    logger.info(f"get_basket called with nm_id={nm_id}, vol={vol}, part={part}, basket_num={basket_num}")

    # Диапазоны для basket-01 до basket-22
    ranges = [
        (0, 143, "01"), (144, 287, "02"), (288, 431, "03"),
        (432, 719, "04"), (720, 1007, "05"), (1008, 1061, "06"),
        (1062, 1115, "07"), (1116, 1169, "08"), (1170, 1313, "09"),
        (1314, 1601, "10"), (1602, 1655, "11"), (1656, 1919, "12"),
        (1920, 2045, "13"), (2046, 2189, "14"), (2190, 2405, "15"),
        (2406, 2621, "16"), (2622, 2837, "17"), (2838, 3053, "18"),
        (3054, 3269, "19"), (3270, 3485, "20"), (3486, 3701, "21"),
        (3702, 3917, "22")
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
    }

    # Определение корзины
    basket = None
    if vol <= 3917:
        logger.info(f"vol={vol} <= 3917, checking ranges")
        for start, end, basket_suffix in ranges:
            if start <= vol <= end:
                basket = f"basket-{basket_suffix}"
                logger.info(f"Found matching range {start}-{end}, using {basket}")
                break
        if not basket:
            basket = "basket-23"
            logger.info(f"vol={vol} <= 3917 but no range matched, defaulting to {basket}")
    else:
        logger.info(f"vol={vol} > 3917, starting with basket-23 or searching at basket_num={basket_num}")
        if basket_num > max_basket:
            logger.error(f"Exhausted basket search up to basket_num={basket_num}")
            return None, None
        basket = f"basket-{basket_num:02d}" if basket_num > 23 else "basket-23"

    # Выполнение запроса
    json_url = f"https://{basket}.wbbasket.ru/vol{vol}/part{part}/{nm_id}/info/ru/card.json"
    logger.info(f"Attempting request to {json_url}")
    start_time = time.time()
    try:
        time.sleep(1)  # Задержка для предотвращения блокировок
        response = requests.get(json_url, headers=headers, timeout=5)
        response.raise_for_status()
        elapsed_time = time.time() - start_time
        logger.info(f"Request to {json_url} succeeded, took {elapsed_time:.2f}s")
        return basket, response.json()
    except requests.RequestException as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Request to {json_url} failed after {elapsed_time:.2f}s: {str(e)}")
        if vol > 3917 and basket == "basket-23":
            logger.info(f"Proceeding to next basket_num={basket_num}")
            return get_basket(nm_id, vol, part, basket_num, max_basket)
        return None, None

def get_prices(nm_id):
    """
    Получает старую и новую цену товара.

    Выполняет GET-запрос к https://card.wb.ru/cards/v2/detail для получения цен.
    Возвращает кортеж (old_price, new_price) или (None, None) при ошибке.

    Args:
        nm_id (int): ID товара.

    Returns:
        tuple: (float or None, float or None) - старая и новая цена (в рублях) или (None, None).
    """
    logger.info(f"get_prices called with nm_id={nm_id}")
    price_url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1257786&spp=30&ab_testing=false&lang=ru&nm={nm_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
    }
    logger.info(f"Attempting price request to {price_url}")
    start_time = time.time()
    try:
        time.sleep(1)  # Задержка для предотвращения блокировок
        response = requests.get(price_url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        products = data.get("data", {}).get("products", [])
        if not products or not products[0].get("sizes"):
            logger.error(f"No products or sizes found in price response for nm_id={nm_id}")
            return None, None
        price_data = products[0]["sizes"][0].get("price", {})
        old_price = price_data.get("basic", 0) / 100 if price_data.get("basic") else None
        new_price = price_data.get("product", 0) / 100 if price_data.get("product") else None
        elapsed_time = time.time() - start_time
        logger.info(f"Price request to {price_url} succeeded, took {elapsed_time:.2f}s, old_price={old_price}, new_price={new_price}")
        return old_price, new_price
    except requests.RequestException as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Price request to {price_url} failed after {elapsed_time:.2f}s: {str(e)}")
        return None, None
    except (KeyError, IndexError) as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Error parsing price response for nm_id={nm_id}: {str(e)}")
        return None, None