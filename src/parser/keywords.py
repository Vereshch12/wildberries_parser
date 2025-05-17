import os
import time
import shutil
from .config import logger, STOP_WORDS

def extract_keywords_manual(data, title):
    """Ручное извлечение ключевых слов."""
    logger.info("Starting manual keyword extraction")
    start_time = time.time()
    keywords = []

    # Сначала добавляем слова из названия
    title_words = [word for word in title.split() if word.lower() not in STOP_WORDS and len(word) > 2]
    logger.info(f"Extracted {len(title_words)} keywords from title: {title_words}")
    keywords.extend(title_words)

    # Затем добавляем слова из options
    option_words = set()
    for opt in data.get("options", []):
        if opt["name"] in ["Особенности продукта", "Назначение киселя", "Состав"]:
            option_words.update(opt["value"].replace(";", ",").split(", "))
    option_words = [word for word in option_words if word.lower() not in STOP_WORDS and len(word) > 2 and word not in keywords]
    logger.info(f"Extracted {len(option_words)} keywords from options: {option_words}")
    keywords.extend(option_words)

    # Добавляем слова из compositions
    composition_words = [comp["name"] for comp in data.get("compositions", []) if comp["name"].lower() not in STOP_WORDS and len(comp["name"]) > 2 and comp["name"] not in keywords]
    logger.info(f"Extracted {len(composition_words)} keywords from compositions: {composition_words}")
    keywords.extend(composition_words)

    # Ограничиваем до 10 ключевых слов
    keywords = keywords[:10]
    elapsed_time = time.time() - start_time
    logger.info(f"Manual keyword extraction completed in {elapsed_time:.2f}s, final keywords: {keywords}")
    return keywords

def extract_keywords_ai(title, description):
    """Извлечение 5 ключевых слов с использованием KeyBERT."""
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