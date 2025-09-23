import os
import datetime as dt
import time

import requests
from dotenv import load_dotenv
from scheduler import Scheduler
from google import genai

from logger import logger

load_dotenv()

url = f"https://api.telegram.org/bot{os.environ['UNIVER_BOT_TOKEN']}/sendMessage"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
prompt = """
Сгенерируй короткое и вежливое напоминание преподавателю о том, что нужно прислать задание.
Возвращай только текст сообщения "as is", без лишних слов или тех.информации.

Правила:
* Тон дружелюбный, можно слегка шутливый.
* Допускаются эмодзи (но не слишком много).
* Сообщение не должно быть длинным.
* Можно обыгрывать то, что прошёл ещё один час.
* Никакой политики, религии, грубостей или спорных тем.
* Стиль — лёгкий, неформальный, но уважительный.

Примеры сообщений:
1. "Прошел ещё один час ⏰ Задание всё ещё ждём 👀"
2. "Новый час настал, а заданий пока нет... 😅"
3. "Час пролетел — задания так и не появилось 🕒"

Сгенерируй 1 новое сообщение в этом стиле.
"""


def gen_message():
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=prompt, config={"temperature": 1}
    )
    return f"@jukovchief 👋\n{response.text}"


def main():
    now = dt.datetime.now(kyiv_tz)
    if 20 <= now.hour or now.hour < 9:
        logger.info(f"Quiet hours (22:00-09:00). Skipping send at {now.isoformat()}")
        return

    logger.info(f"Job started at {now.isoformat()}")

    text = gen_message()
    body = {"chat_id": os.environ["UNIVER_CHAT_ID"], "text": text}
    logger.info(f"Generated message:\n\n{text}")
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
