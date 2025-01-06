# Используем официальный образ Python
FROM python:3.10.10-slim

# Устанавливаем зависимости для системы
RUN apt-get update && apt-get install -y \
    apt-utils \
    gcc \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry и обновляем pip
RUN pip install --upgrade pip && pip install --no-cache-dir poetry

# Настраиваем Poetry для работы без виртуального окружения
RUN poetry config virtualenvs.create false

# Устанавливаем рабочую директорию в контейнере
WORKDIR /nextauth_backend

# Копируем только файлы pyproject.toml и poetry.lock для установки зависимостей
COPY pyproject.toml poetry.lock /nextauth_backend/

# Устанавливаем зависимости через Poetry
RUN poetry install --only main --no-root

# Копируем остальные файлы проекта
COPY . .

# Указываем переменную окружения для игнорирования предупреждений pip
ENV PIP_ROOT_USER_ACTION=ignore

# Открываем порт, на котором будет работать приложение
EXPOSE 8001

# Указываем команду для запуска приложения через Python
CMD ["python", "main.py"]
