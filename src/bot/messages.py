def format_product_info(product_info):
    """Формирует текст сообщения с информацией о товаре."""
    keywords = '\n'.join([f"  • {kw}" for kw in product_info['keywords']]) if product_info['keywords'] else "  Нет ключевых слов"
    response = (
        f"🛒 *Информация о товаре*:\n\n"
        f"  📌 *Артикул*: {product_info['article']}\n"
        f"  📛 *Название*: {product_info['title']}\n"
        f"  🏷️ *Бренд*: {product_info['brand']}\n"
        f"  📝 *Описание* (первые 100 символов):\n    {product_info['description'][:100]}...\n"
        f"  🥄 *Состав*: {product_info['composition']}\n"
        f"  🌍 *Страна производства*: {product_info['country']}\n"
    )
    if product_info['old_price'] is not None:
        response += f"  💸 *Старая цена*: {product_info['old_price']} руб.\n"
    if product_info['new_price'] is not None:
        response += f"  💰 *Новая цена*: {product_info['new_price']} руб.\n"
    response += f"  🔑 *Ключевые слова*:\n{keywords}\n\n📎Начните поиск по ключевым словам или пришлите новую ссылку!"
    return response

def format_intermediate_results(keyword, keyword_idx, total_keywords, total_products, page, previous_results):
    """Формирует текст промежуточных результатов поиска."""
    message_text = f"📊 Промежуточные результаты ({keyword_idx}/{total_keywords}):\n\n"
    if previous_results:
        message_text += "\n".join(previous_results) + "\n\n"
    message_text += (
        f"🔎 Ключевое слово \"{keyword}\" (обновление каждые 5 страниц):\n"
        f"  • Всего товаров в выдаче: {total_products}\n"
        f"  • Текущая страница: {page}\n"
        f"  • Статус: Поиск продолжается, ожидайте..."
    )
    return message_text

def format_final_results(results):
    """Формирует текст финальных результатов поиска."""
    return "✅ Поиск завершен!\n\n📎Присылайте новую ссылку для анализа!\n\n📊 Результаты поиска:\n" + "\n".join(results)

def format_cancelled_results(results):
    """Формирует текст результатов при отмене поиска."""
    if results:
        return "❌ Поиск отменен!\n\n📊 Текущие результаты:\n\n" + "\n".join(results)
    return "❌ Поиск отменен!\n\n📊 Результатов пока нет."