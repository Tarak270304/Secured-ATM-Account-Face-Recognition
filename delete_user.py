import sqlite3

conn = sqlite3.connect("atm_users.db")
cursor = conn.cursor()
cursor.execute("DELETE FROM users WHERE name = 'tarak'")
conn.commit()
conn.close()

print("User 'tarak' deleted.")
