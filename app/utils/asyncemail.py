import os
import asyncio
import aiosmtplib
from typing import List, Optional
from email.message import EmailMessage
from datetime import datetime


class EmailSender:
    def __init__(
        self,
        email_address: str,
        email_password: str,
        smtp_server: str,
        smtp_port: int = 587,
        log_file_path: Optional[str] = None
    ) -> None:
        """
        Инициализация отправителя.

        :param email_address: Email-адрес отправителя.
        :param email_password: Пароль или токен для аутентификации.
        :param smtp_server: Адрес SMTP сервера.
        :param smtp_port: Порт SMTP сервера (по умолчанию 587 для STARTTLS).
        :param log_file_path: Путь к файлу логов (если не указан, логи не будут записываться).
        """
        self.email_address = email_address
        self.email_password = email_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.log_file_path = log_file_path

        # Создание директории для файла логов, если она не существует
        if self.log_file_path:
            log_dir = os.path.dirname(self.log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

    def _log(self, message: str, level: str = "INFO") -> None:
        """
        Кастомная функция для записи логов в файл.

        :param message: Сообщение для записи в лог.
        :param level: Уровень логирования (например, INFO, ERROR).
        """
        if self.log_file_path:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"[{timestamp}] [{level}] {message}\n"
            with open(self.log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_message)

    async def send_email(
        self,
        subject: str,
        body: str,
        recipients: List[str],
        sender: Optional[str] = None
    ) -> None:
        """
        Отправляет email сообщение.

        :param subject: Тема письма.
        :param body: Текст письма.
        :param recipients: Список получателей.
        :param sender: Адрес отправителя (по умолчанию используется email_address).
        """
        sender = sender or self.email_address

        # Создаём EmailMessage
        message = EmailMessage()
        message["From"] = sender
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        message.set_content(body)

        try:
            # Отправка сообщения
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                username=self.email_address,
                password=self.email_password,
                start_tls=True  # Автоматическое использование STARTTLS
            )
            log_message = f"Сообщение успешно отправлено! Тема: '{subject}', Получатели: {recipients}"
            self._log(log_message, level="INFO")
        except Exception as e:
            log_message = f"Ошибка при отправке письма. Тема: '{subject}', Ошибка: {e}"
            self._log(log_message, level="ERROR")


# Пример использования
"""
async def main():
    # Базовые настройки
    DEFAULT_EMAIL = "nextauthtelegram@gmail.com"
    DEFAULT_PASSWORD = "tzhw bthd uiuy vnap"
    DEFAULT_SMTP_SERVER = "smtp.gmail.com"
    DEFAULT_SMTP_PORT = 587
    LOG_FILE_PATH = "./custom_log.log"  # Укажите свой путь
    # Если логирование не нужно, можно передать None
    #LOG_FILE_PATH = None  # Или укажите свой путь

    # Инициализация отправителя
    email_sender = EmailSender(
        email_address=DEFAULT_EMAIL,
        email_password=DEFAULT_PASSWORD,
        smtp_server=DEFAULT_SMTP_SERVER,
        smtp_port=DEFAULT_SMTP_PORT,
        log_file_path=LOG_FILE_PATH  # Если None, логи не будут записываться
    )

    # Отправка письма
    await email_sender.send_email(
        subject="Простое письмо",
        body="Это тестовое письмо, отправленное с базовыми настройками.",
        recipients=["0nameofshadow0@gmail.com"]
    )

if __name__ == "__main__":
    asyncio.run(main())
"""
