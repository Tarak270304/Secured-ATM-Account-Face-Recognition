import sqlite3

conn = sqlite3.connect("atm_users.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN account_number TEXT")
    conn.commit()
    print("✅ Column 'account_number' added successfully.")
except sqlite3.OperationalError as e:
    print("⚠️ Column may already exist or another error occurred:", e)

conn.close()
