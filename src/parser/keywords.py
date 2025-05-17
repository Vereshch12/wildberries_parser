import os
import time
import shutil
import re
from .config import logger, STOP_WORDS
import pymorphy2

def extract_keywords_manual(data, title):
    """Ручное извлечение ключевых слов: сначала из названия, затем из options, затем из compositions."""
    logger.info("Starting manual keyword extraction")
    start_time = time.time()
    morph = pymorphy2.MorphAnalyzer()
    keywords = []  # Список для сохранения порядка
    seen_keywords = set()  # Множество для исключения дубликатов

    # Фильтр для исключения цифр и символов
    def is_valid_phrase(phrase):
        return bool(re.match(r'^[а-яА-Яa-zA-Z\s]+$', phrase)) and len(phrase) > 2

    # Обработка слова или фразы
    def process_phrase(phrase):
        phrase = phrase.strip()
        if not is_valid_phrase(phrase) or phrase.lower() in STOP_WORDS:
            return None
        # Если фраза содержит пробел (словосочетание), сохраняем как есть
        if ' ' in phrase:
            return phrase
        # Для одиночных слов применяем лемматизацию
        return morph.parse(phrase)[0].normal_form

    # 1. Извлекаем все слова из названия
    title_words = title.split()
    for word in title_words:
        result = process_phrase(word)
        if result and result not in seen_keywords:
            keywords.append(result)
            seen_keywords.add(result)
    # Затем добавляем полное название как фразу, если оно содержит пробелы
    if ' ' in title.strip():
        result = process_phrase(title)
        if result and result not in seen_keywords:
            keywords.append(result)
            seen_keywords.add(result)
    logger.info(f"Extracted {len(keywords)} keywords from title: {keywords}")

    # 2. Ключевые слова из options
    for opt in data.get("options", []):
        if opt["name"] in ["Особенности продукта", "Назначение киселя", "Состав"]:
            option_phrases = opt["value"].replace(";", ",").split(", ")
            for phrase in option_phrases:
                result = process_phrase(phrase)
                if result and result not in seen_keywords:
                    keywords.append(result)
                    seen_keywords.add(result)
    logger.info(f"Extracted {len(keywords)} keywords after options: {keywords}")

    # 3. Ключевые слова из compositions
    for comp in data.get("compositions", []):
        phrase = comp["name"].strip()
        result = process_phrase(phrase)
        if result and result not in seen_keywords:
            keywords.append(result)
            seen_keywords.add(result)
    logger.info(f"Extracted {len(keywords)} keywords after compositions: {keywords}")

    # Ограничиваем до 10 ключевых слов
    keywords = keywords[:10]
    elapsed_time = time.time() - start_time
    logger.info(f"Manual keyword extraction completed in {elapsed_time:.2f}s, final keywords: {keywords}")
    return keywords

def extract_keywords_ai(title, description):
    """Извлечение 5 ключевых слов с использованием KeyBERT. Работает долго и не очень"""
    logger.info("Starting AI keyword extraction")
    start_time = time.time()
    try:
        cache_dir = os.path.expanduser("~/.cache/huggingface")
        if os.path.exists(cache_dir):
            logger.info(f"Clearing Hugging Face cache at {cache_dir}")
            shutil.rmtree(cache_dir)
        from keybert import KeyBERT
        kw_model = KeyBERT(model='sentence-transformers/all-MiniLM-L6-v2')
        text = f"{title}. {description}"
        keywords = kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words=STOP_WORDS,
            top_n=5,
            diversity=0.5
        )
        elapsed_time = time.time() - start_time
        keywords = [kw[0] for kw in keywords]
        logger.info(f"AI keyword extraction completed in {elapsed_time:.2f}s, keywords: {keywords}")
        return keywords
    except ImportError:
        logger.error("KeyBERT not installed, cannot use AI method")
        return ["ошибка", "keybert", "не", "установлен"]
    except Exception as e:
        logger.error(f"Error in KeyBERT: {str(e)}")
        return ["ошибка", "ключевые", "слова", "не", "сгенерированы"]