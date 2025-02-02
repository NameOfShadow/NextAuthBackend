# Сервис регистрации

Этот сервис обрабатывает регистрацию пользователей, а также отправку кода подтверждения на email и валидацию введённого кода. Сервис использует FastAPI для работы с HTTP запросами и SQLModel для взаимодействия с базой данных.

## Функции

1. **Регистрация пользователя**:
   - При регистрации новый пользователь получает код подтверждения на свой email.
   - Код действителен в течение 1 минуты!

2. **Валидация кода**:
   - После ввода кода пользователем сервис проверяет его на соответствие с данным кодом, отправленным на email.
   - Если код истек или неверный, пользователь получает ошибку.

## Технологии

- **Poetry**: Управление зависимостями.
- **Fastapi**: Главный фреймворк для создания API.
- **Uvicorn**: Современный веб сервер для запуска API.
- **SQLModel(SQLite)** Современная библиотека для удобной работы с базой данных SQLite(В будущем планируется переход на PostgreSQL и добавление Redis).
- **Aiosmtplib**: Библиотека для асинхронной отправки писем.
- **Apscheduler**: Библиотека для создания фоновых задач по очистке старых данных в БД.

## Установка

Чтобы установить и запустить проект, выполните следующие шаги:

### 1. Клонируйте репозиторий:

```bash
git clone https://github.com/NameOfShadow/NextAuthBackend
```

### 2. Перейдите в директорию проекта:
```bash
cd NextAuthBackend
```

### 3. Установите зависимости:
```bash
poetry install
```

### 4. Запустите приложение:
```bash
python main.py
```

Приложение будет доступно по адресу http://localhost:8001.

## Разработчик
**Email:** [0nameofshadow0@gmail.com](mailto:0nameofshadow0@gmail.com)  
**GitHub:** [@NameOfShadow](https://github.com/NameOfShadow)

> "Всегда стремлюсь создавать что-то новое, что помогает мне достигать своих целей."

---

Мой GitHub является местом, где я храню свои проекты.
