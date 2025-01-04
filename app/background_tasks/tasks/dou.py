import glob
import os
from datetime import datetime, timedelta

from sqlmodel import select

from app.db.database import get_session
from app.db.loginuser.crud import get_all_login_users
from app.db.loginuser.model import LoginUser
from app.db.pendinguser.model import PendingUser

USER_LIFETIME = timedelta(minutes=10)

log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)


def get_log_filename():
    return os.path.join(log_directory, f'deleted_users_{datetime.utcnow().strftime("%Y-%m-%d")}.log')


def log_deletion(user):
    log_message = (
        f"{datetime.utcnow().isoformat()} - INFO - Удален пользователь: "
        f"ФИО: {user.last_name} {user.first_name} {user.middle_name}, "
        f"Почта: {user.email}, ID: {user.user_id}\n"
    )

    with open(get_log_filename(), 'a', encoding='utf-8') as f:
        f.write(log_message)


def delete_old_pending_users():
    session = next(get_session())
    try:
        cutoff_time = datetime.utcnow() - USER_LIFETIME
        old_users = session.exec(select(PendingUser).where(PendingUser.key_expiry < cutoff_time)).all()

        for user in old_users:
            log_deletion(user)
            session.delete(user)

        session.commit()
    except Exception as e:
        print(f"Ошибка при удалении старых пользователей: {str(e)}")
    finally:
        session.close()


def log_login_deletion(user):
    log_message = (
        f"{datetime.utcnow().isoformat()} - INFO - Удален входящий пользователь: "
        f"Почта: {user.email}, ID: {user.user_id}\n"
    )

    with open(get_log_filename(), 'a', encoding='utf-8') as f:
        f.write(log_message)


def delete_old_login_users():
    session = next(get_session())
    try:
        cutoff_time = datetime.utcnow() - USER_LIFETIME
        old_users = session.exec(select(LoginUser).where(LoginUser.key_expiry < cutoff_time)).all()

        for user in old_users:
            log_login_deletion(user)
            session.delete(user)

        session.commit()
    except Exception as e:
        print(f"Ошибка при удалении старых пользователей: {str(e)}")
    finally:
        session.close()


def clear_old_logs():
    week_ago = datetime.utcnow() - timedelta(days=7)
    log_files = glob.glob(os.path.join(log_directory, "deleted_users_*.log"))

    for log_file in log_files:
        file_date_str = os.path.basename(log_file).split('_')[2].split('.')[0]
        file_date = datetime.strptime(file_date_str, '%Y-%m-%d')

        if file_date < week_ago:
            os.remove(log_file)
            print(f"Удален старый лог: {log_file}")
