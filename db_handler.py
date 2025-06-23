import sqlite3
import os

db_path = "atm_users.db"

def init_db():
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                pin TEXT NOT NULL,
                balance REAL DEFAULT 1000.0
            )
        """)
        conn.commit()
def register_user(name, pin, account_number):
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (name, pin, account_number) VALUES (?, ?, ?)", (name, pin, account_number))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False


def verify_pin(name, pin):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE name=? AND pin=?", (name, pin))
        return c.fetchone() is not None

def get_balance(name):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE name=?", (name,))
        result = c.fetchone()
        return result[0] if result else 0.0

def update_balance(name, amount):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance - ? WHERE name=?", (amount, name))
        conn.commit()
def delete_user(name):
    conn = sqlite3.connect("atm_users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE name = ?", (name,))
    conn.commit()
    conn.close()
def get_account_number(name):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT account_number FROM users WHERE name=?", (name,))
        result = c.fetchone()
        return result[0] if result else "N/A"
