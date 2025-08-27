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


schedule = Scheduler()
schedule.weekly(Monday(dt.time(hour=9, minute=50)), main)
schedule.weekly(
    [
        Tuesday(dt.time(hour=8, minute=50)),
        Wednesday(dt.time(hour=8, minute=50)),
        Thursday(dt.time(hour=8, minute=50)),
        Friday(dt.time(hour=8, minute=50)),
    ],
    main,
)

init_log = False
while True:
    if not init_log:
        logger.info(f"Scheduler started at {dt.datetime.now()}")
        init_log = True

    schedule.exec_jobs()
    time.sleep(1)
