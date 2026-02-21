"""
Auto-tag videos into empty/sparse categories based on title keywords.
Run this once to populate category mappings for videos that lack them.
"""
import sqlite3
import sys

conn = sqlite3.connect('k_foods.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Keyword rules: (category_id, [keywords that should match this category])
RULES = [
    # 음식 형태별 sub-categories
    (10, ['밥', '볶음밥', '덮밥', '비빔밥', '솥밥', '영양밥', '무밥', '콩나물밥']),                          # 밥류
    (11, ['죽', '스프', '수프', '포리지']),                                                                 # 죽/스프
    (12, ['면', '국수', '라면', '파스타', '우동', '소면', '냉면', '짜장', '짬뽕', '수제비', '만두', '떡볶이', '잡채']),  # 면류
    (13, ['국', '미역국', '된장국', '북엇국', '콩나물국', '육개장']),                                       # 국
    (14, ['탕', '설렁탕', '순댓국', '감자탕', '매운탕', '해장국', '곰탕', '갈비탕']),                      # 탕
    (15, ['찌개', '김치찌개', '된장찌개', '순두부찌개', '부대찌개', '청국장']),                               # 찌개
    (9,  ['볶음', '구이', '조림', '튀김', '전', '스테이크', '까르보나라', '오므라이스']),                    # 일품/메인요리
    (8,  ['반찬', '무침', '나물', '장아찌', '젓갈', '김치', '비빔']),                                     # 반찬류
    # 주재료별
    (16, ['고기', '닭', '돼지', '소고기', '삼겹살', '갈비', '육류']),                                     # 육류
    (17, ['생선', '해산물', '새우', '오징어', '조개', '꽃게', '고등어', '삼치', '낙지', '문어', '전복']),   # 수산물
    (18, ['채소', '야채', '감자', '고구마', '버섯', '두부', '콩', '시금치', '브로콜리', '당근']),           # 채소/곡류
    (20, ['돼지', '삼겹살', '목살', '항정살', '제육', '돼지국밥']),                                        # 돼지고기
    (19, ['소고기', '한우', '갈비', '불고기', '육회', '스테이크']),                                        # 소고기
    # 조리법별
    (21, ['끓이', '보글보글', '국물', '탕', '찌개', '스프']),                                              # 끓이기
    (22, ['볶음', '튀김', '炒', '부침', '전', '전골']),                                                    # 볶기/튀기기
    # 상황 및 목적별
    (23, ['저녁', '한상', '집밥', '정식', '특식']),                                                        # 든든한 저녁 메인
    (24, ['레시피', '황금', '비법', '정통', '원조']),                                                      # 전문가 레시피
]

# Fetch all videos
cur.execute("SELECT video_id, title FROM videos")
videos = cur.fetchall()

inserted = 0
skipped = 0

for video in videos:
    vid_id = video['video_id']
    title = video['title']

    for cat_id, keywords in RULES:
        # Check if already tagged
        cur.execute("SELECT 1 FROM video_category_map WHERE video_id=? AND category_id=?", (vid_id, cat_id))
        if cur.fetchone():
            skipped += 1
            continue

        # Check if any keyword matches in title
        if any(kw in title for kw in keywords):
            cur.execute("INSERT OR IGNORE INTO video_category_map (video_id, category_id) VALUES (?, ?)", (vid_id, cat_id))
            inserted += 1

conn.commit()
conn.close()
print(f"Done. Inserted {inserted} new tags, skipped {skipped} existing.")
