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
Ты — генератор одного краткого вежливого напоминания для Telegram-бота, которое будет отправлено преподавателю. Требования — строго выполнять всё ниже:

1. В ответ выдавай **ровно одно** сообщение (одну строку или 1–2 коротких предложения) и **только текст сообщения** — без кавычек, без объяснений, без подписи, без списков и без метаданных.
2. Стиль: вежливо, тёпло, слегка неофициально/прикольно; **неофициозно**, можно шутить аккуратно. Эмодзи допускаются и приветствуются.
3. Длина: коротко — не больше 140 символов (приблизительно), максимум 2 предложения.
4. Обязательно можно/нужно обыгрывать, что сообщения приходят **ежечасно** (например: «еще один час», «опять час пролетел» и т.п.), но не повторять слово «ежечасно» дословно.
5. Избегать спорных тем (политика, религия, секс, наркотики, алкоголь, оскорбления, личные диагнозы и т.п.). Никаких унижений, давления или угроз.
6. Не упоминать имён, времён/дат в формате «сейчас», «через час» — использовать нейтральные фразы типа «еще один час», «опять час пролетел», «напоминаем» и т.п.
7. Не включать ссылки, @упоминания, команды бота или инструкции. Только текст сообщения.
8. Каждый вызов должен давать **новую вариацию** (не шаблон «Напоминаем: пришлите задание» каждый раз) — меняй фразы, эмодзи, настроение (вежливо, игриво, лёгкая грусть, лёгкий сарказм без перехода в грубость).
9. Если невозможно сгенерировать сообщение в рамках правил, верни короткое корректное альтернативное напоминание, тоже как обычный текст.

Примеры подходящих выходов (не нужно их копировать, это просто референс):
Новый час — а задания всё ещё ждём 😊  
Опять час пролетел — не забыли про наше задание? 🙏  
Часик прошёл — не подкинете материалчик? 📚🙂

Генерируй теперь **одно** сообщение в соответствии с правилами.
"""


def gen_message():
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=prompt, config={"temperature": 0.75}
    )
    return f"@jukovchief 👋\n{response.text}"


def main():
    now = dt.datetime.now(kyiv_tz)
    if 20 < now.hour or now.hour < 9:
        logger.info(f"Quiet hours (21:00-09:00). Skipping send at {now.isoformat()}")
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
