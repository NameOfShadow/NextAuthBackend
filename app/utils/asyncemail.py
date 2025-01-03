import os
import asyncio
import aiosmtplib
import logging

from typing import List, Optional
from email.message import EmailMessage


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

        if log_file_path:
            log_dir = os.path.dirname(log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Настройка логирования
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(log_file_path, encoding="utf-8"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logging.getLogger(__name__)

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
            if self.logger:
                self.logger.info(f"Сообщение успешно отправлено! Тема: '{subject}', Получатели: {recipients}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Ошибка при отправке письма. Тема: '{subject}', Ошибка: {e}")


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
