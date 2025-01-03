from apscheduler.schedulers.background import BackgroundScheduler

from app.background_tasks.tasks import dopu


# Настройка фоновых задач
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(dopu.delete_old_pending_users, 'interval', minutes=1)
    scheduler.add_job(dopu.clear_old_logs, 'interval', days=1)
    scheduler.start()
