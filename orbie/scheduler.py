from apscheduler.schedulers.background import BackgroundScheduler
from main import daily_update

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(daily_update, 'interval', hours=24)
    scheduler.start()

if __name__ == "__main__":
    start_scheduler()
