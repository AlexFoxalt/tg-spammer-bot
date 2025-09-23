import os
import datetime as dt
import time

import requests
from dotenv import load_dotenv
from scheduler import Scheduler

from logger import logger

load_dotenv()

url = f"https://api.telegram.org/bot{os.environ["UNIVER_BOT_TOKEN"]}/sendMessage"
text = """
@jukovchief 👋\n
Новый час, а задания всё нет❓\n
Все грустят 😿
"""
body = {"chat_id": os.environ["UNIVER_CHAT_ID"], "text": text}


def main():
    logger.info(f"Job started at {dt.datetime.now()}")
    response = requests.post(url=url, json=body).json()
    if not response.get("ok", ""):
        raise Exception("Request invalid status")


kyiv_tz = dt.timezone(dt.timedelta(hours=3))
schedule = Scheduler(tzinfo=kyiv_tz)
schedule.hourly(dt.time(minute=0, tzinfo=kyiv_tz), main)


if __name__ == "__main__":
    logger.info(f"Scheduler started at {dt.datetime.now()}")

    while True:
        schedule.exec_jobs()
        time.sleep(1)
