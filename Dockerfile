# Используем официальный образ Python 3.10.10 как базовый
FROM python:3.10.10-slim

# Установим зависимости для системы
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Устанавливаем рабочую директорию в контейнере
WORKDIR /nextauth_backend

# Копируем только файл pyproject.toml и poetry.lock для установки зависимостей
COPY pyproject.toml poetry.lock /nextauth_backend/

# Устанавливаем зависимости с помощью poetry
RUN poetry install --no-dev --no-root

# Копируем все файлы проекта в рабочую директорию контейнера
COPY . .

# Открываем порт, на котором будет работать приложение
EXPOSE 8001

# Указываем команду для запуска приложения с Uvicorn (предполагается, что ваше приложение находится в файле main.py)
CMD ["python", "nextauth_backend/main.py"]
