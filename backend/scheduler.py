from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.email import send_daily_report
import datetime

def daily_report_job():
    send_daily_report("admin@sprngenergy.com", "Daily DSM Report", "Summary here...")

scheduler = BackgroundScheduler()
scheduler.add_job(daily_report_job, 'cron', hour=6, minute=0)
scheduler.start()
