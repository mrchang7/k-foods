import sqlite3
import random

conn = sqlite3.connect('k_foods.db')
cur = conn.cursor()

# Get 5 top videos
cur.execute('SELECT video_id FROM videos ORDER BY view_count DESC LIMIT 5')
video_ids = [row[0] for row in cur.fetchall()]

recipe = """📍 재료 준비
- 주재료: 돼지고기 500g, 김치 1/4포기
- 부재료: 대파 1대, 양파 1/2개, 청양고추 2개
- 양념장: 고춧가루 2큰술, 간장 1큰술, 다진마늘 1큰술, 참기름 1큰술

👨‍🍳 조리 순서
1) 돼지고기는 먹기 좋은 크기로 썰어 후추와 맛술로 밑간을 해둡니다.
2) 김치는 속을 가볍게 털어내고 적당한 크기로 썰어줍니다.
3) 팬에 참기름을 두르고 김치를 먼저 볶다가 고기를 넣어 함께 볶습니다.
4) 고기가 반쯤 익으면 양념장을 넣고 중불에서 볶아줍니다.
5) 마지막으로 대파, 양파, 청양고추를 넣고 숨이 죽을 때까지 볶아 완성합니다."""

for vid in video_ids:
    cur.execute('UPDATE videos SET recipe_memo = ? WHERE video_id = ?', (recipe, vid))

conn.commit()
conn.close()
print("Seeded top 5 videos with recipes.")
