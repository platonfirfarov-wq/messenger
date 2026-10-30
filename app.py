from flask import Flask, render_template_string, request, redirect, url_for, session
from datetime import datetime
import threading

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret"  # обязательно поменяйте на случайную строку

# Хранилище сообщений: список словарей
messages = []
# Хранилище пользователей: логин -> данные (тут просто факт входа)
users = {}

# Шаблон HTML (в одном файле для удобства)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Мессенджер</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; }
        .chat-area { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: auto; margin-bottom: 10px; }
        .msg { margin: 5px 0; padding: 5px; background: #f5f5f5; border-radius: 4px; }
        .msg strong { color: #0066cc; }
        form { display: flex; gap: 8px; }
        input[type="text"] { flex: 1; padding: 6px; }
        button { padding: 6px 12px; }
        .login-form { margin-bottom: 20px; }
    </style>
</head>
<body>
    {% if not logged_in %}
        <h2>Вход в мессенджер</h2>
        <form class="login-form" method="POST" action="/login">
            <input type="text" name="username" placeholder="Ваш никнейм" required>
            <button type="submit">Войти</button>
        </form>
    {% else %}
        <h2>Чат ({{ username }})</h2>
        <div class="chat-area" id="chat">
            {% for msg in messages %}
                <div class="msg">
                    <strong>{{ msg.username }}:</strong> {{ msg.text }}
                    <small style="color:#888; margin-left:10px">{{ msg.time }}</small>
                </div>
            {% endfor %}
        </div>
        <form method="POST" action="/send">
            <input type="text" name="text" placeholder="Сообщение" required style="width:70%">
            <button type="submit">Отправить</button>
        </form>
        <p><a href="/logout">Выйти</a></p>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    # Если не авторизованы — на страницу входа, иначе — в чат
    if "username" not in session:
        return render_template_string(HTML_TEMPLATE, logged_in=False, messages=[], username="")
    return render_template_string(
        HTML_TEMPLATE,
        logged_in=True,
        messages=messages,
        username=session["username"]
    )

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    if not username:
        return redirect(url_for("index"))
    session["username"] = username
    users[username] = True
    return redirect(url_for("index"))

@app.route("/send", methods=["POST"])
def send():
    if "username" not in session:
        return redirect(url_for("index"))
    text = request.form.get("text", "").strip()
    if text:
        messages.append({
            "username": session["username"],
            "text": text,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        # Ограничим историю, чтобы не разрасталась бесконечно
        if len(messages) > 200:
            messages.pop(0)
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    # host="0.0.0.0" делает сервер доступным по локальному IP в сети
    app.run(host="0.0.0.0", port=5000, debug=False)
