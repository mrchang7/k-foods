import sqlite3
import json

conn = sqlite3.connect('k_foods.db')
cur = conn.cursor()
cur.execute("SELECT title, duration FROM videos WHERE title LIKE '%잡채 만들어보세요%' OR title LIKE '%한입 치즈돈까스%' OR title LIKE '%버섯솥밥%'")
results = cur.fetchall()
with open('temp_out.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False)
conn.close()
