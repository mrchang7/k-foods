"""
Restructures the category taxonomy and re-tags all videos.
New structure focused on what users actually search for:
  - 음식 종류 (Food Type) - Rice, Noodles, Soup etc.
  - 주재료 (Main Ingredient) - Meat, Seafood, Veg etc.
  - 조리 방법 (Cooking Method) - Boil, Fry, Grill etc.
  - 상황 (Occasion) - Weekday dinner, Party, Kids etc.
"""
import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('k_foods.db')
cur = conn.cursor()

# 1. Clear existing category mappings and categories
print("Clearing old data...")
cur.execute("DELETE FROM video_category_map")
cur.execute("DELETE FROM categories")
conn.commit()

# 2. Insert new taxonomy
# Format: (id, name, category_type, parent_id)
NEW_CATEGORIES = [
    # ── 대분류 (Top-level Nav items) ──────────────────────
    (1,  '음식 종류',   '대분류', None),
    (2,  '주재료',      '대분류', None),
    (3,  '조리 방법',   '대분류', None),
    (4,  '상황 & 목적', '대분류', None),

    # ── 음식 종류 (Food Type) sub-categories ─────────────
    (10, '밥류',            '음식 종류', 1),
    (11, '국/탕/찌개',      '음식 종류', 1),
    (12, '면/파스타',       '음식 종류', 1),
    (13, '반찬/나물',       '음식 종류', 1),
    (14, '구이/볶음',       '음식 종류', 1),
    (15, '전/튀김',         '음식 종류', 1),
    (16, '김치',            '음식 종류', 1),
    (17, '디저트/빵/케이크','음식 종류', 1),
    (18, '떡/한과',         '음식 종류', 1),
    (19, '음료/차/술',      '음식 종류', 1),

    # ── 주재료 (Ingredient) sub-categories ───────────────
    (30, '소고기',    '주재료', 2),
    (31, '돼지고기',  '주재료', 2),
    (32, '닭/오리',   '주재료', 2),
    (33, '해산물',    '주재료', 2),
    (34, '채소',      '주재료', 2),
    (35, '두부/콩',   '주재료', 2),
    (36, '달걀',      '주재료', 2),
    (37, '버섯',      '주재료', 2),
    (38, '쌀/곡류',   '주재료', 2),

    # ── 조리 방법 (Cooking Method) sub-categories ────────
    (50, '끓이기',   '조리 방법', 3),
    (51, '볶기',     '조리 방법', 3),
    (52, '굽기/직화','조리 방법', 3),
    (53, '튀기기',   '조리 방법', 3),
    (54, '찌기',     '조리 방법', 3),
    (55, '무침/절임','조리 방법', 3),
    (56, '에어프라이어', '조리 방법', 3),
    (57, '전자레인지',   '조리 방법', 3),

    # ── 상황 & 목적 (Occasion) sub-categories ────────────
    (70, '혼밥/자취 요리', '상황 & 목적', 4),
    (71, '손님 초대',      '상황 & 목적', 4),
    (72, '다이어트/건강식','상황 & 목적', 4),
    (73, '술안주',         '상황 & 목적', 4),
    (74, '명절/제사 음식', '상황 & 목적', 4),
    (75, '아이 반찬',      '상황 & 목적', 4),
    (76, '도시락',         '상황 & 목적', 4),
]

for cat in NEW_CATEGORIES:
    cur.execute(
        "INSERT INTO categories (category_id, name, category_type, parent_id) VALUES (?, ?, ?, ?)",
        cat
    )
conn.commit()
print(f"Inserted {len(NEW_CATEGORIES)} categories.")

# 3. Keyword tagging rules
# (category_id, [keywords])
RULES = [
    # 음식 종류
    (10, ['밥', '볶음밥', '덮밥', '비빔밥', '솥밥', '영양밥', '콩나물밥', '새우밥', '오므라이스', '리조또', '초밥']),
    (11, ['국', '탕', '찌개', '전골', '미역국', '된장국', '북엇국', '육개장', '설렁탕', '순댓국',
          '감자탕', '매운탕', '해장국', '곰탕', '갈비탕', '김치찌개', '된장찌개', '순두부찌개',
          '부대찌개', '청국장', '뚝배기', '국물', '해물탕', '낙지전골', '부대전골']),
    (12, ['면', '국수', '라면', '파스타', '우동', '소면', '냉면', '짜장', '짬뽕', '수제비',
          '만두', '떡볶이', '잡채', '당면', '스파게티', '페투치니', '볶음면', '비빔국수']),
    (13, ['반찬', '나물', '무침', '조림', '장아찌', '볶음김치', '깍두기', '콩자반', '멸치볶음',
          '감자조림', '두부조림', '어묵', '계란말이', '시금치', '고사리', '도라지']),
    (14, ['구이', '볶음', '삼겹살', '목살', '제육볶음', '오징어볶음', '낙지볶음', '닭볶음탕',
          '불고기', '갈비', '스테이크', '차돌박이', '목살구이', '된장삼겹']),
    (15, ['전', '튀김', '부침', '파전', '빈대떡', '감자전', '김치전', '해물파전', '동그랑땡',
          '치킨', '돈까스', '탕수육', '새우튀김', '꽈리고추튀김']),
    (16, ['김치', '배추김치', '깍두기', '열무김치', '백김치', '총각김치', '파김치', '묵은지']),
    (17, ['케이크', '쿠키', '디저트', '브라우니', '마카롱', '크림', '빵', '마들렌', '스콘',
          '와플', '팬케이크', '초콜릿', '아이스크림', '푸딩', '젤리', '타르트', '치즈케이크']),
    (18, ['떡', '한과', '강정', '약과', '식혜', '수정과', '인절미', '떡국', '송편']),
    (19, ['음료', '차', '술', '막걸리', '커피', '라테', '주스', '스무디', '청', '레몬차', '생강차']),

    # 주재료
    (30, ['소고기', '한우', '육회', '불고기', '갈비', '차돌박이', '안심', '등심', '사골']),
    (31, ['돼지고기', '돼지', '삼겹살', '목살', '항정살', '제육', '돼지국밥', '수육', '보쌈']),
    (32, ['닭', '오리', '닭갈비', '치킨', '닭볶음탕', '삼계탕', '닭한마리', '닭가슴살']),
    (33, ['생선', '해산물', '새우', '오징어', '조개', '꽃게', '고등어', '삼치', '낙지', '문어',
          '전복', '굴', '홍합', '가자미', '연어', '참치', '멸치', '바지락', '대구', '갈치', '아귀']),
    (34, ['채소', '야채', '감자', '고구마', '양파', '마늘', '파프리카', '애호박', '가지', '상추',
          '브로콜리', '당근', '배추', '무', '콩나물', '숙주', '파', '쑥', '고춧가루']),
    (35, ['두부', '콩', '청국장', '된장', '순두부', '콩나물']),
    (36, ['달걀', '계란', '스크램블', '에그', '계란말이', '달걀볶음', '계란찜']),
    (37, ['버섯', '표고', '새송이', '느타리', '팽이버섯', '송이버섯']),
    (38, ['쌀', '현미', '잡곡', '보리', '귀리', '퀴노아']),

    # 조리 방법
    (50, ['끓이', '졸이', '보글', '국물', '탕', '찌개', '전골']),
    (51, ['볶음', '볶아', '팬볶음', '기름에 볶']),
    (52, ['구이', '굽기', '직화', '그릴', '오븐구이', '석쇠', 'BBQ']),
    (53, ['튀김', '튀기', '기름에 튀', '바삭', '카라아게']),
    (54, ['찜', '찌기', '수증기', '찜기', '찜닭', '계란찜']),
    (55, ['무침', '절임', '나물', '겉절이', '비빔']),
    (56, ['에어프라이어', '에프', 'air fryer']),
    (57, ['전자레인지', '전레', '레인지', '5분', '10분']),

    # 상황 & 목적
    (70, ['혼밥', '자취', '혼자', '간단', '초간단', '10분', '5분', '15분 안에', '뚝딱']),
    (71, ['손님', '파티', '홈파티', '초대', '모임', '특별한']),
    (72, ['다이어트', '저칼로리', '건강', '헬시', '저탄', '클린']),
    (73, ['안주', '술안주', '막걸리 안주', '맥주 안주', '소주 안주']),
    (74, ['명절', '제사', '추석', '설날', '차례', '잡채', '나물', '전']),
    (75, ['아이', '어린이', '유아', '아기', '이유식', '키즈', '아이 반찬']),
    (76, ['도시락', '오찬', '점심', '캠핑', '소풍', '피크닉']),
]

# 4. Fetch all videos and apply rules
print("Tagging videos...")
cur.execute("SELECT video_id, title FROM videos")
videos = cur.fetchall()

inserted = 0
for video_id, title in videos:
    for cat_id, keywords in RULES:
        if any(kw in title for kw in keywords):
            cur.execute(
                "INSERT OR IGNORE INTO video_category_map (video_id, category_id) VALUES (?, ?)",
                (video_id, cat_id)
            )
            inserted += 1

conn.commit()

# 5. Report coverage
print(f"\nInserted {inserted} category tags total.\n")
print("Category coverage:")
cur.execute('''
    SELECT c.category_id, c.name, COUNT(vcm.video_id) as cnt
    FROM categories c
    LEFT JOIN video_category_map vcm ON c.category_id = vcm.category_id
    WHERE c.parent_id IS NOT NULL
    GROUP BY c.category_id, c.name
    ORDER BY c.parent_id, cnt DESC
''')
for row in cur.fetchall():
    print(f"  [{row[0]:2}] {row[1]}: {row[2]} videos")

conn.close()
print("\nDone.")
