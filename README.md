# Сервис регистрации

Этот сервис обрабатывает регистрацию пользователей, а также отправку кода подтверждения на email и валидацию введённого кода. Сервис использует FastAPI для работы с HTTP запросами и SQLAlchemy для взаимодействия с базой данных.

## Функции

1. **Регистрация пользователя**:
   - При регистрации новый пользователь получает код подтверждения на свой email.
   - Код действителен в течение 1 минуты.

2. **Валидация кода**:
   - После ввода кода пользователем сервис проверяет его на соответствие с данным кодом, отправленным на email.
   - Если код истек или неверный, пользователь получает ошибку.