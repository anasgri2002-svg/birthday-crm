from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

DATA_FILE = "data.json"


# ---------------------------
# 🔹 DATA
# ---------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------
# 🔹 HELPERS
# ---------------------------
def days_until(date_str):
    today = datetime.now().date()
    day, month = map(int, date_str.split("."))
    year = today.year
    target = datetime(year, month, day).date()
    if target < today:
        target = datetime(year + 1, month, day).date()
    return (target - today).days


def work_years(start_date):
    day, month, year = map(int, start_date.split("."))
    start = datetime(year, month, day).date()
    today = datetime.now().date()
    return today.year - start.year


# ---------------------------
# 🔹 CRM ROUTES
# ---------------------------

@app.route("/")
def home():
    return "CRM працює ✔"


@app.route("/add", methods=["POST"])
def add():
    data = load_data()

    item = request.json

    data.append({
        "surname": item["surname"],
        "name": item["name"],
        "birthday": item["birthday"],
        "start_date": item["start_date"]
    })

    save_data(data)
    return jsonify({"status": "ok"})


@app.route("/list")
def list_all():
    return jsonify(load_data())


@app.route("/delete", methods=["POST"])
def delete():
    surname = request.json["surname"]

    data = load_data()
    data = [x for x in data if x["surname"] != surname]

    save_data(data)
    return jsonify({"status": "deleted"})


@app.route("/search")
def search():
    surname = request.args.get("surname")
    data = load_data()

    result = [x for x in data if surname.lower() in x["surname"].lower()]
    return jsonify(result)


# ---------------------------
# 🔹 NOTIFICATIONS
# ---------------------------
def notify():
    data = load_data()
    today = datetime.now().strftime("%d.%m")

    birthdays = []
    work_anniv = []

    for p in data:
        if p["birthday"] == today:
            birthdays.append(p)

        if p["start_date"][:5] == today:
            years = work_years(p["start_date"])
            work_anniv.append((p, years))

    if birthdays:
        print("\n🎂 Сьогодні вітаємо:")
        for p in birthdays:
            print(f"👉 {p['surname']} {p['name']}")

    if work_anniv:
        print("\n🏢 Річниці роботи:")
        for p, years in work_anniv:
            print(f"👉 {p['surname']} {p['name']} — {years} років")


def notify_tomorrow():
    data = load_data()
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m")

    birthdays = [p for p in data if p["birthday"] == tomorrow]

    if birthdays:
        print("\n📢 Нагадування на завтра:")
        print("Нагадую, завтра будемо вітати:")

        for p in birthdays:
            print(f"👉 {p['surname']} {p['name']}")


# ---------------------------
# 🔹 SCHEDULER
# ---------------------------
scheduler = BackgroundScheduler()
scheduler.add_job(notify, "cron", hour=8, minute=0)
scheduler.add_job(notify_tomorrow, "cron", hour=8, minute=0)
scheduler.start()


# ---------------------------
# 🔹 START
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
