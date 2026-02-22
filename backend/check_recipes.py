import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'k_foods.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT count(*) FROM videos WHERE recipe_memo IS NOT NULL AND recipe_memo != ''")
print("Total recipes:", cur.fetchone()[0])

cur.execute("SELECT count(*) FROM videos WHERE recipe_memo LIKE '%돼지고기 500g, 김치 1/4포기%'")
print("Dummy recipes:", cur.fetchone()[0])

conn.close()
