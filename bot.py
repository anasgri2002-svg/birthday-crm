import asyncio
import json
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "8422106005:AAFUbt-FeTZq4s0j7TO2SgYlikN-IdOHEKI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

FILE = "data.json"
CHAT_ID = None


# ---------- КНОПКИ ----------
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Додати")],
        [KeyboardButton(text="📋 Список")],
        [KeyboardButton(text="🗑 Видалити")],
    ],
    resize_keyboard=True
)


# ---------- БАЗА ----------
def load_data():
    if not os.path.exists(FILE):
        return {}
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------- ДАТЫ ----------
def parse_date(ddmm: str):
    return datetime.strptime(ddmm, "%d.%m").date()


def calc_years(work_date: str):
    try:
        d = datetime.strptime(work_date, "%d.%m.%Y").date()
        today = datetime.now().date()
        return today.year - d.year - ((today.month, today.day) < (d.month, d.day))
    except:
        return None


# ---------- НАПОМИНАНИЯ ----------
async def send_notifications():
    global CHAT_ID
    if not CHAT_ID:
        return

    data = load_data()
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    bday_tomorrow = []
    bday_today = []
    anniversaries = []

    for full_name, info in data.items():
        try:
            birthday = parse_date(info["birthday"])
            work = info["work"]

            work_date = datetime.strptime(work, "%d.%m.%Y").date()

            # завтра ДР
            if (birthday.month, birthday.day) == (tomorrow.month, tomorrow.day):
                bday_tomorrow.append(full_name)

            # сегодня ДР
            if (birthday.month, birthday.day) == (today.month, today.day):
                bday_today.append(full_name)

            # годовщина работы
            if (work_date.month, work_date.day) == (today.month, today.day):
                years = calc_years(work)
                anniversaries.append((full_name, years))

        except:
            continue

    # ---------- ЗАВТРА ----------
    if bday_tomorrow:
        text = "⏰ Нагадую, завтра будемо вітати:\n"
        for n in bday_tomorrow:
            text += f"• {n}\n"
        await bot.send_message(CHAT_ID, text)

    # ---------- СЕГОДНЯ ----------
    if bday_today:
        text = "🎉 Вітаємо наших іменинників:\n"
        for n in bday_today:
            text += f"• {n}\n"
        text += "\nБажаємо щастя, здоров’я та успіхів! 🎂"
        await bot.send_message(CHAT_ID, text)

    # ---------- ГОДОВЩИНЫ ----------
    if anniversaries:
        text = "🏢 Річниця роботи:\n\n"
        for name, years in anniversaries:
            text += f"• {name} — {years} р.\n"
        text += "\nДякуємо за вашу роботу ❤️"
        await bot.send_message(CHAT_ID, text)


# ---------- START ----------
@dp.message(Command("start"))
async def start(message: types.Message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    await message.answer("🎂 HR система запущена", reply_markup=kb)


# ---------- СПИСОК ----------
@dp.message(F.text == "📋 Список")
async def list_users(message: types.Message):
    data = load_data()

    if not data:
        await message.answer("📭 Порожньо")
        return

    text = "📋 Співробітники:\n\n"

    for name, info in data.items():
        text += (
            f"• {name}\n"
            f"  🎂 {info['birthday']}\n"
            f"  🏢 {info['work']}\n\n"
        )

    await message.answer(text)


# ---------- УДАЛЕНИЕ ----------
@dp.message(F.text == "🗑 Видалити")
async def delete_start(message: types.Message):
    await message.answer("Напиши: Прізвище Ім’я")


# ---------- ОБРАБОТКА ----------
@dp.message()
async def handler(message: types.Message):
    global CHAT_ID
    CHAT_ID = message.chat.id

    text = message.text

    if not text or text.startswith("/"):
        return

    if text in ["➕ Додати", "📋 Список", "🗑 Видалити"]:
        return

    data = load_data()
    parts = text.split()

    # ➕ ДОБАВЛЕНИЕ
    if len(parts) == 4:
        surname, name, birthday, work = parts
        full_name = f"{surname} {name}"

        # проверка года
        try:
            datetime.strptime(work, "%d.%m.%Y")
        except:
            return await message.answer("❌ Формат роботи: ДД.ММ.РРРР")

        data[full_name] = {
            "birthday": birthday,
            "work": work
        }

        save_data(data)
        await message.answer(f"✅ Додано: {full_name}")
        return

    # 🗑 УДАЛЕНИЕ
    if len(parts) == 2:
        full_name = f"{parts[0]} {parts[1]}"

        if full_name in data:
            del data[full_name]
            save_data(data)
            await message.answer(f"🗑 Видалено: {full_name}")
        else:
            await message.answer("❌ Не знайдено")
        return


# ---------- SCHEDULER ----------
async def main():
    print("🤖 HR система запущена...")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_notifications, "cron", hour=8, minute=0)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())