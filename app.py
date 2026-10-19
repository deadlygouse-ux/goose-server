import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))

# Используем /tmp/ для базы данных, чтобы Render мог её создать
DB_PATH = '/tmp/goose.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (nick TEXT PRIMARY KEY, cosmetic TEXT)''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    nick = data.get('nick')
    cosmetic = data.get('cosmetic', 'capybara')
    
    if not nick:
        return jsonify({"status": "error", "message": "Ник не может быть пустым"}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (nick, cosmetic) VALUES (?, ?)", (nick, cosmetic))
        conn.commit()
        return jsonify({"status": "ok", "message": f"Ник {nick} зарегистрирован с {cosmetic}"})
    except sqlite3.IntegrityError:
        # Если ник уже есть, обновляем ему косметику
        c.execute("UPDATE users SET cosmetic = ? WHERE nick = ?", (cosmetic, nick))
        conn.commit()
        return jsonify({"status": "ok", "message": f"Косметика для {nick} обновлена"})
    finally:
        conn.close()

@app.route('/get_cosmetics', methods=['GET'])
def get_cosmetics():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT nick, cosmetic FROM users")
    users = [{"nick": row[0], "cosmetic": row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(users)

# Инициализируем базу при старте
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
