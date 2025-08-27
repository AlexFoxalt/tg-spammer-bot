import os
import datetime as dt
import time
from zoneinfo import ZoneInfo  # Python 3.9+
import requests
from dotenv import load_dotenv
from scheduler import Scheduler
from scheduler.trigger import Monday, Tuesday, Wednesday, Thursday, Friday

from logger import logger

load_dotenv()

# === CONFIG: choose your timezone here or via env var ===
TARGET_TZ = os.environ.get("TARGET_TZ", "Europe/Kyiv")

# Make the whole process use that timezone for "local time" calls.
# This affects time.localtime(), time.tzname, and functions that rely on libc localtime.
os.environ["TZ"] = TARGET_TZ
time.tzset()  # POSIX-only: available on Ubuntu/Linux

# Also keep a ZoneInfo object for tz-aware datetimes and logging
TZ = ZoneInfo(TARGET_TZ)


# Build the Telegram URL (avoid nested quotes problem)
BOT_ID = os.environ["BOT_ID"]
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
url = f"https://api.telegram.org/{BOT_ID}:{TOKEN}/sendMessage"

text = """
@yudinekat @laurifity @cqdezzz Напоминание👀\n
Нужно отправить скриншоты операционных показателей в соседний чат. 
"""
body = {"chat_id": CHAT_ID, "text": text}


def main():
    # log with an explicit timezone-aware timestamp
    logger.info(f"Job started at {dt.datetime.now(TZ).isoformat()}")
    response = requests.post(url=url, json=body).json()
    if not response.get("ok", ""):
        raise Exception("Request invalid status")


schedule = Scheduler()
# NOTE: the triggers you already use are naive times (dt.time). Because we set TZ via tzset(),
# libraries that use "localtime" will match the TARGET_TZ. If your scheduler accepts tz-aware
# triggers, prefer providing aware datetimes/triggers (see alternative below).
schedule.weekly(Monday(dt.time(hour=9, minute=50)), main)
schedule.weekly(
    [
        Tuesday(dt.time(hour=8, minute=50)),
        Wednesday(dt.time(hour=11, minute=50)),
        Thursday(dt.time(hour=8, minute=50)),
        Friday(dt.time(hour=8, minute=50)),
    ],
    main,
)

init_log = False
while True:
    if not init_log:
        # log process start with zone-aware timestamp so you can verify it uses TARGET_TZ
        logger.info(
            f"Scheduler started at {dt.datetime.now(TZ).isoformat()} (tz={TARGET_TZ})"
        )
        init_log = True

    schedule.exec_jobs()
    time.sleep(1)
