
import schedule
import time
from pipelines.daily_pipeline import run_daily_pipeline

def start_scheduler():

    schedule.every().day.at("09:00").do(run_daily_pipeline)

    while True:
        schedule.run_pending()
        time.sleep(30)
