# Telegram-бот для парсинга Wildberries

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Docker](https://img.shields.io/badge/Docker-20.10.0+-blue)

Телеграм-бот для парсинга товаров с Wildberries, извлечения ключевых слов и поиска позиций в поисковой выдаче.

## Установка и запуск

1. **Установите Docker и Docker Compose**:
    - Скачайте и установите [Docker](https://docs.docker.com/get-docker/) (версия 20.10.0+).
    - Docker Compose (версия 1.29.0+) обычно идет с Docker.
    - Запустите Docker Desktop

2. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/Vereshch12/wildberries_parser.git
   cd wildberries-parser-bot
   ```

3. **Создайте файл `.env`**:
   В корне проекта создайте файл `.env` и добавьте:
   ```env
   TELEGRAM_TOKEN=ваш_токен
   ```
   Получите токен у [@BotFather](https://t.me/BotFather) в Telegram.

   **Опционально**: Для ИИ-извлечения ключевых слов добавьте:
   ```env
   USE_AI=true
   ```
   ⚠️ **Предупреждение**: Использование `USE_AI=true` **не рекомендуется**, так как этот метод находится в экспериментальной стадии и не был тщательно протестирован. Сборка контейнера занимает больше времени из-за установки крупных пакетов (например, `sentence-transformers`, `torch`), а обработка работает медленнее, чем ручной метод. Используйте только для тестирования!

4. **Запустите бот**:
   ```bash
   docker-compose up --build
   ```
   Логи пишутся в `./logs/parser.log` и выводятся в консоль.

   Для остановки:
   ```bash
   docker-compose down
   ```

5. **Проверьте бота**:
   В Telegram отправьте боту `/start` или URL товара (например, `https://www.wildberries.ru/catalog/120693960/detail.aspx`).

## Версии и зависимости

- **Python**: 3.9
- **Docker**: 20.10.0+
- **Docker Compose**: 1.29.0+
- **Зависимости**:
    - `aiogram==2.25.1` (Telegram API)
    - `requests==2.28.1` (HTTP-запросы)
    - ИИ-режим (`USE_AI=true`): `sentence-transformers==2.2.2`, `torch==1.12.1`
- **Модель ИИ** (для `USE_AI=true`): `sentence-transformers/all-MiniLM-L6-v2`

## Логирование

- Логи сохраняются в `./logs/parser.log` с ротацией (макс. 10 МБ, до 5 копий).
- Директория `./logs` очищается при каждом запуске.