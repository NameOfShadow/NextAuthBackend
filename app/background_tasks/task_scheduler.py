from apscheduler.schedulers.background import BackgroundScheduler

from app.background_tasks.tasks import dou


# Настройка фоновых задач
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(dou.delete_old_pending_users, 'interval', minutes=1)
    scheduler.add_job(dou.delete_old_login_users, 'interval', minutes=1)
    scheduler.add_job(dou.clear_old_logs, 'interval', days=1)
    scheduler.start()
