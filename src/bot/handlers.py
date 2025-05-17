from aiogram import types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from parser.parser import get_product_info
from parser.search import search_product_by_keywords
from .messages import format_product_info, format_final_results, format_cancelled_results
from .config import logger, active_searches
import asyncio

# Регистрация обработчиков
from aiogram import Dispatcher
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply('Привет! Я бот для парсинга Wildberries. Отправь мне ссылку на товар.')

@dp.message()
async def handle_link(message: types.Message):
    product_info = get_product_info(message.text)
    if 'error' in product_info:
        await message.reply(f"❌ Ошибка: {product_info['error']}")
        return

    response = format_product_info(product_info)
    search_button = InlineKeyboardButton(text="🔍 Начать поиск по ключевым словам", callback_data=f"search_{product_info['article']}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[search_button]])

    try:
        if product_info['photos']:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=product_info['photos'][0],
                caption=response,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        else:
            await message.reply(response, parse_mode='Markdown', reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"{response}\n⚠️ Не удалось загрузить изображение: {str(e)}", parse_mode='Markdown', reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith('search_'))
async def process_search_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    nm_id = int(callback_query.data.split('_')[1])
    logger.info(f"Starting search for nm_id={nm_id}")

    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logger.error(f"Failed to remove search button: {str(e)}")

    cancel_button = InlineKeyboardButton(text="❌ Отменить поиск", callback_data=f"cancel_{nm_id}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])
    search_message = await callback_query.message.reply(
        "🔍 Поиск начат. Это займет некоторое время, ожидайте...",
        reply_markup=keyboard
    )

    cancel_event = asyncio.Event()
    chat_id = callback_query.message.chat.id
    active_searches[chat_id] = {'nm_id': nm_id, 'cancel_event': cancel_event}

    product_info = get_product_info(f"https://www.wildberries.ru/catalog/{nm_id}/detail.aspx")
    if 'error' in product_info:
        await search_message.edit_text(f"❌ Ошибка при получении данных: {product_info['error']}", reply_markup=None)
        if chat_id in active_searches:
            del active_searches[chat_id]
        return

    keywords = product_info['keywords']
    if not keywords:
        await search_message.edit_text("❌ Нет ключевых слов для поиска.", reply_markup=None)
        if chat_id in active_searches:
            del active_searches[chat_id]
        return

    results = []
    for idx, keyword in enumerate(keywords, 1):
        if cancel_event.is_set():
            break

        search_result = await search_product_by_keywords(
            nm_id, keyword, update_message=search_message, keyword_idx=idx,
            total_keywords=len(keywords), previous_results=results, cancel_event=cancel_event
        )
        if search_result is None:
            results.append(f"  {idx}. Ключевое слово \"{keyword}\": ошибка при поиске")
        else:
            position, page, total_products = search_result
            if position is not None and page is not None:
                results.append(
                    f"  {idx}. Ключевое слово \"{keyword}\":\n"
                    f"    • Всего товаров: {total_products}\n"
                    f"    • Позиция в выдаче: {position}\n"
                    f"    • Страница выдачи: {page}"
                )
            else:
                results.append(
                    f"  {idx}. Ключевое слово \"{keyword}\":\n"
                    f"    • Всего товаров: {total_products}\n"
                    f"    • Товар не найден"
                )

    if not cancel_event.is_set():
        final_text = format_final_results(results)
        await search_message.edit_text(final_text, reply_markup=None)

    if chat_id in active_searches:
        del active_searches[chat_id]

@dp.callback_query(lambda c: c.data.startswith('cancel_'))
async def process_cancel_callback(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    if chat_id not in active_searches:
        await callback_query.message.edit_text("❌ Поиск уже завершен или не начинался.", reply_markup=None)
        await callback_query.answer()
        return

    active_searches[chat_id]['cancel_event'].set()

    current_message = callback_query.message.text
    results = []
    if "Промежуточные результаты" in current_message:
        lines = current_message.split('\n')
        for line in lines:
            if line.startswith("🔎 Ключевое слово"):
                break
            if line.strip().startswith("1. ") or line.strip().startswith("  1. "):
                results = lines[lines.index(line):]
                break

    final_text = format_cancelled_results(results)
    await callback_query.message.edit_text(final_text, reply_markup=None)
    await callback_query.message.reply("ℹ️ Поиск отменен. Вы можете прислать новую ссылку на товар.")

    if chat_id in active_searches:
        del active_searches[chat_id]

    await callback_query.answer()