import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))

def init_db():
    conn = sqlite3.connect('goose.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (nick TEXT PRIMARY KEY, cosmetic TEXT)''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    nick = data.get('nick')
    cosmetic = data.get('cosmetic', 'capybara')
    conn = sqlite3.connect('goose.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (nick, cosmetic) VALUES (?, ?)", (nick, cosmetic))
        conn.commit()
        return jsonify({"status": "ok", "message": f"Ник {nick} зарегистрирован"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Ник занят"}), 400
    finally:
        conn.close()

@app.route('/get_cosmetics', methods=['GET'])
def get_cosmetics():
    conn = sqlite3.connect('goose.db')
    c = conn.cursor()
    c.execute("SELECT nick, cosmetic FROM users")
    users = [{"nick": row[0], "cosmetic": row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(users)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=port)
