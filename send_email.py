from app.utils.asyncemail import EmailSender
from config import settings

# Инициализация отправителя
email_sender = EmailSender(
    email_address=settings.email_address,
    email_password=settings.email_password,
    smtp_server=settings.smtp_server,
    smtp_port=settings.smtp_port,
    log_file_path="./logs/email.log",
)
