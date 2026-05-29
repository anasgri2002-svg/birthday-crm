import os
from flask import Flask, render_template_string

app = Flask(__name__)

# 🧠 Простая главная страница CRM
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Birthday CRM</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial;
            background: #f4f4f4;
            text-align: center;
            padding-top: 50px;
        }
        .box {
            background: white;
            padding: 30px;
            margin: auto;
            width: 60%;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        p { font-size: 18px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🎂 Birthday HR CRM</h1>
        <p>Система работает 24/7</p>
        <p>Telegram бот подключается отдельно</p>
        <p>Версия MVP</p>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
