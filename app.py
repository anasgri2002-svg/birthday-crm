from flask import Flask, render_template_string, request, redirect
import json
import os

app = Flask(__name__)

FILE = "data.json"


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


HTML = """
<h2>📋 HR CRM система</h2>

<h3>➕ Добавить сотрудника</h3>
<form method="POST" action="/add">
    <input name="name" placeholder="Фамилия Имя">
    <input name="birthday" placeholder="ДР (12.09)">
    <input name="work" placeholder="Дата работы (19.05)">
    <button>Добавить</button>
</form>

<hr>

<h3>📋 Список сотрудников</h3>

<table border="1" cellpadding="6">
<tr>
<th>ФИО</th>
<th>ДР</th>
<th>Работа</th>
<th>Удалить</th>
</tr>

{% for name, info in data.items() %}
<tr>
<td>{{name}}</td>
<td>{{info['birthday']}}</td>
<td>{{info['work']}}</td>
<td><a href="/delete/{{name}}">❌</a></td>
</tr>
{% endfor %}

</table>
"""


@app.route("/")
def index():
    return render_template_string(HTML, data=load_data())


@app.route("/add", methods=["POST"])
def add():
    data = load_data()

    name = request.form["name"]
    birthday = request.form["birthday"]
    work = request.form["work"]

    data[name] = {
        "birthday": birthday,
        "work": work
    }

    save_data(data)
    return redirect("/")


@app.route("/delete/<name>")
def delete(name):
    data = load_data()

    if name in data:
        del data[name]

    save_data(data)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)