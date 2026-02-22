import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'k_foods.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT count(*) FROM videos WHERE recipe_memo IS NOT NULL AND recipe_memo != ''")
count = cur.fetchone()[0]

if count > 0:
    cur.execute("UPDATE videos SET recipe_memo = NULL")
    conn.commit()

print(f"Reset recipe_memo for {count} videos.")
conn.close()
