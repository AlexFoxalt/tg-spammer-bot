import os
import datetime as dt
import time

import requests
from dotenv import load_dotenv
from scheduler import Scheduler

from logger import logger

load_dotenv()

url = f"https://api.telegram.org/bot{os.environ['UNIVER_BOT_TOKEN']}/sendMessage"
text = """
@jukovchief 👋\n
Новый час, а задания всё нет❓\n
Все грустят 😿
"""
body = {"chat_id": os.environ["UNIVER_CHAT_ID"], "text": text}


def main():
    now = dt.datetime.now(kyiv_tz)
    if 22 <= now.hour or now.hour < 9:
        logger.info(f"Quiet hours (22:00-09:00). Skipping send at {now.isoformat()}")
        return
        
    logger.info(f"Job started at {now.isoformat()}")
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
