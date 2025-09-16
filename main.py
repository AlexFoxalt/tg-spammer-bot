import os
import datetime as dt
import time

import requests
from dotenv import load_dotenv
from scheduler import Scheduler
from scheduler.trigger import Monday, Tuesday, Wednesday, Thursday, Friday

from logger import logger

load_dotenv()

url = (
    f"https://api.telegram.org/{os.environ["BOT_ID"]}:{os.environ["TOKEN"]}/sendMessage"
)
text = """
@yudinekat @laurifity @cqdezzz Напоминание👀\n
Нужно отправить скриншоты операционных показателей в соседний чат. 
"""
body = {"chat_id": os.environ["CHAT_ID"], "text": text}


def main():
    logger.info(f"Job started at {dt.datetime.now()}")
    response = requests.post(url=url, json=body).json()
    if not response.get("ok", ""):
        raise Exception("Request invalid status")


kyiv_tz = dt.timezone(dt.timedelta(hours=3))
schedule = Scheduler(tzinfo=kyiv_tz)
schedule.weekly(
    [
        Monday(dt.time(hour=12, minute=50, tzinfo=kyiv_tz)),
        Tuesday(dt.time(hour=11, minute=50, tzinfo=kyiv_tz)),
        Wednesday(dt.time(hour=11, minute=50, tzinfo=kyiv_tz)),
        Thursday(dt.time(hour=11, minute=50, tzinfo=kyiv_tz)),
        Friday(dt.time(hour=11, minute=50, tzinfo=kyiv_tz)),
    ],
    main,
)

if __name__ == "__main__":
    logger.info(f"Scheduler started at {dt.datetime.now()}")
    while True:
        schedule.exec_jobs()
        time.sleep(1)
        
