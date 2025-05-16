# Используем официальный образ Python 3.9
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY ./src .

# Команда для запуска приложения (заглушка, будет заменена позже)
CMD ["python", "main.py"]
