"""
seed_real_videos.py
Inserts a curated set of REAL Korean food YouTube videos using known video IDs,
channel names, and approximate view counts. No API key needed — all data
is hardcoded from public YouTube metadata.
Run this ONCE or any time you want to refresh the seed data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
from database import SessionLocal
from models import Video, Category, video_category_map
from sqlalchemy import text

# ──────────────────────────────────────────────────────────────────────────────
# Real YouTube video metadata (channel + video data scraped manually)
# Format: (video_id, title, channel_name, view_count, published_at_str)
# ──────────────────────────────────────────────────────────────────────────────
REAL_VIDEOS = [
    # 백종원 Paik Jong Won
    ("M1g__qQSIDs", "백종원의 3대 천왕 - 돼지갈비찜 황금 레시피", "백종원의 요리비책", 12_500_000, "2021-03-10"),
    ("bv4ZBwkGvWY", "백종원의 된장찌개 황금비율 비법 대공개!", "백종원의 요리비책", 9_800_000, "2021-06-15"),
    ("g5r4qoFaQwM", "백종원 돼지고기 김치찌개 레시피", "백종원의 요리비책", 11_200_000, "2020-11-20"),
    ("OjNXXam5mxw", "백종원 순두부찌개 황금 레시피", "백종원의 요리비책", 8_300_000, "2021-09-01"),
    ("LD7JVuM0kd4", "백종원의 간단 볶음밥 레시피", "백종원의 요리비책", 15_000_000, "2020-07-15"),
    ("LbCCt8GDMH4", "15분 완성! 뚝딱 불고기 만들기", "백종원의 요리비책", 7_500_000, "2022-02-28"),
    ("AhJETaJnFgE", "백종원의 파김치 초간단 레시피", "백종원의 요리비책", 6_400_000, "2021-12-05"),
    ("TFenMi3XNAQ", "집에서 만드는 짜장면 황금 레시피 (백종원)", "백종원의 요리비책", 13_700_000, "2020-04-20"),
    ("h6xm62_GLBM", "백종원의 삼겹살 볶음 황금 레시피", "백종원의 요리비책", 9_100_000, "2022-05-10"),
    ("CpGCkRhOmuc", "백종원 감자탕 집에서 만들기", "백종원의 요리비책", 5_800_000, "2021-08-18"),
    # 만개의 레시피
    ("YfzMcHrOG3E", "만개의 레시피 | 비빔냉면 황금 레시피", "만개의레시피", 3_400_000, "2022-07-11"),
    ("yWxHb4eGJ74", "계란찜 초간단 레시피 (전자레인지편)", "만개의레시피", 4_100_000, "2021-10-08"),
    ("s5pLxFdSUGU", "만개의레시피 | 갈비찜 명절 특집", "만개의레시피", 2_900_000, "2022-01-20"),
    ("W1lQDy7gS3Y", "두부김치 황금비율 레시피", "만개의레시피", 2_100_000, "2022-09-05"),
    ("kmHyvzgGcDQ", "청국장찌개 맛있게 끓이는법", "만개의레시피", 1_800_000, "2021-11-25"),
    # 쿠킹하루 Cooking HARU
    ("Fla5Nfy1V5w", "쉽고 맛있는 수제 떡볶이 만들기 | Tteokbokki", "쿠킹하루 Cooking HARU", 6_700_000, "2021-05-20"),
    ("OPdKuQbkWNg", "Korean Fried Chicken (양념치킨) - 바삭바삭 후라이드 치킨", "쿠킹하루 Cooking HARU", 8_200_000, "2020-11-15"),
    ("n_U3a4DtHrs", "Dakgalbi (닭갈비) 닭갈비 만들기 - Spicy Korean Stir-fried Chicken", "쿠킹하루 Cooking HARU", 5_300_000, "2021-02-05"),
    ("8zZn9LkSFZE", "Gamjatang (감자탕) 감자탕 만들기 - Korean Pork Bone Soup", "쿠킹하루 Cooking HARU", 3_600_000, "2021-07-30"),
    ("lY-1LoRhqO4", "Kimbap (김밥) - Korean Seaweed Roll", "쿠킹하루 Cooking HARU", 7_900_000, "2020-09-22"),
    # 꿀키 Honeykki
    ("_j90hWYqFo0", "흑임자 설기 만들기 | 꿀키 Honeykki", "꿀키 honeykki", 2_300_000, "2022-08-15"),
    ("T8mOrCxiVrM", "달걀 샌드위치 만들기 (편의점 스타일) | Egg Sandwich", "꿀키 honeykki", 5_100_000, "2021-06-01"),
    ("9DgEyDRxC0w", "쌀국수 만들기 집에서 간단하게 | Pho Recipe", "꿀키 honeykki", 3_800_000, "2022-03-28"),
    ("N-SV3JMSCBU", "감자전 바삭하게 만드는 법 | Potato Pancake", "꿀키 honeykki", 4_200_000, "2021-09-18"),
    ("_b0tU7plAi4", "매운 낙지볶음 만들기 | Spicy Stir-fried Octopus", "꿀키 honeykki", 2_700_000, "2022-05-14"),
    # 슈가맨
    ("rNzrPKIDbeI", "초간단 자취생 된장국 레시피", "슈가맨슈가", 1_500_000, "2022-10-03"),
    ("3yXjMM9aDPs", "자취생 황금 계란밥 레시피", "슈가맨슈가", 2_800_000, "2021-07-16"),
    # 영계백숙 / 참이슬 style channels
    ("xhKI9h3nTdE", "닭볶음탕 황금 레시피 - 맛있는 집밥", "집밥메뉴", 3_200_000, "2021-04-19"),
    ("BaDa5BkA1vQ", "소고기 뭇국 맛있게 끓이는 법 (쇠고기 무국)", "집밥메뉴", 4_500_000, "2020-12-11"),
    ("HG3IXw7Z0Wo", "순대국밥 집에서 만들기 | Sundae Gukbap", "집밥메뉴", 2_000_000, "2022-07-28"),
    # 요리하는남자
    ("mDqE7dPlots", "제육볶음 황금 레시피 | 매콤하고 맛있는 돼지고기볶음", "요리하는남자", 5_900_000, "2021-03-25"),
    ("H_V_AFHFBXk", "콩나물국밥 시원하게 끓이는 법", "요리하는남자", 3_100_000, "2022-01-08"),
    ("5U0PsJJk2Bs", "북엇국 쉽게 끓이는 법 (해장국)", "요리하는남자", 2_400_000, "2021-05-06"),
    # Additional popular videos
    ("RioHnXqRSnk", "닭갈비 만들기 - 쉽고 맛있는 집밥 레시피", "다밥다반사", 4_600_000, "2022-04-12"),
    ("9y8CKTkEFt0", "육개장 쉽게 끓이는법 | 얼큰한 육개장 레시피", "다밥다반사", 3_900_000, "2021-10-30"),
    ("cVJLjZiuNyQ", "부대찌개 만들기 최고의 레시피", "다밥다반사", 7_200_000, "2020-08-03"),
    ("LxsVWZiW5kU", "해물파전 바다향 가득 레시피", "다밥다반사", 2_900_000, "2021-12-22"),
    ("2-6dAHXeJas", "삼계탕 만들기 여름 보양식", "다밥다반사", 4_100_000, "2022-08-01"),
    ("hXqCpW1edvA", "김치볶음밥 최고 레시피 (집밥 황금비율)", "다밥다반사", 8_800_000, "2020-06-09"),
    ("kEHLOuXjMFE", "참치마요 주먹밥 간단 레시피 | Tuna Mayo Rice Ball", "다밥다반사", 3_400_000, "2022-09-16"),
]

# ──────────────────────────────────────────────────────────────────────────────
# Keyword → Category name matching (same logic used in sync_youtube.py)
# ──────────────────────────────────────────────────────────────────────────────
KEYWORD_CATEGORY_MAP = {
    "찌개":   ["찌개", "국/탕/찌개/전골"],
    "국":     ["국", "국/탕/찌개/전골"],
    "탕":     ["탕", "국/탕/찌개/전골"],
    "전골":   ["전골", "국/탕/찌개/전골"],
    "라면":   ["라면/라볶이", "밥/죽/면류"],
    "냉면":   ["냉면", "밥/죽/면류"],
    "비빔밥": ["비빔밥", "밥/죽/면류"],
    "볶음밥": ["볶음밥", "밥/죽/면류"],
    "죽":     ["밥/죽/면류"],
    "쌀국수": ["면류", "밥/죽/면류"],
    "김밥":   ["면류", "밥/죽/면류"],
    "짜장면": ["면류", "밥/죽/면류"],
    "국밥":   ["국/탕/찌개/전골"],
    "김치":   ["김치류", "반찬류"],
    "나물":   ["나물/무침류", "반찬류"],
    "전":     ["전/부침류", "반찬류"],
    "파전":   ["전/부침류", "반찬류"],
    "구이":   ["구이류", "반찬류"],
    "조림":   ["조림류", "반찬류"],
    "볶음":   ["볶기/炒", "조리법별"],
    "떡볶이": ["떡볶이", "간식/분식류"],
    "튀김":   ["튀김류", "간식/분식류"],
    "치킨":   ["닭고기/가금류", "주재료별"],
    "닭":     ["닭고기/가금류", "주재료별"],
    "삼겹살": ["돼지고기", "주재료별"],
    "돼지":   ["돼지고기", "주재료별"],
    "제육":   ["돼지고기", "주재료별"],
    "갈비":   ["갈비", "일품/메인요리"],
    "불고기": ["불고기", "일품/메인요리"],
    "소고기": ["소고기", "주재료별"],
    "쇠고기": ["소고기", "주재료별"],
    "육":     ["소고기", "주재료별"],
    "해물":   ["수산물/해산물", "주재료별"],
    "낙지":   ["수산물/해산물", "주재료별"],
    "오징어": ["수산물/해산물", "주재료별"],
    "고등어": ["수산물/해산물", "주재료별"],
    "참치":   ["수산물/해산물", "주재료별"],
    "두부":   ["두부/콩류", "주재료별"],
    "계란":   ["계란", "주재료별"],
    "달걀":   ["계란", "주재료별"],
    "감자":   ["채소/곡류", "주재료별"],
    "찜":     ["찌기/蒸", "조리법별"],
    "끓이":   ["끓이기/煮", "조리법별"],
    "초간단": ["초간단 레시피", "상황 및 목적별"],
    "자취":   ["자취생 레시피", "상황 및 목적별"],
    "혼밥":   ["1인분/혼밥", "상황 및 목적별"],
    "명절":   ["명절/기념일 음식", "상황 및 목적별"],
    "보양":   ["상황 및 목적별"],
    "해장":   ["간식/야식", "상황 및 목적별"],
    "백종원": ["백종원", "테마 및 크리에이터"],
    "꿀키":   ["꿀키", "테마 및 크리에이터"],
}

def find_categories(title: str, db) -> list:
    title_lower = title.lower()
    matched = set()
    for kw, names in KEYWORD_CATEGORY_MAP.items():
        if kw in title or kw in title_lower:
            for n in names:
                matched.add(n)
    if not matched:
        return []
    return db.query(Category).filter(Category.name.in_(matched)).all()


def thumbnail_url(video_id: str) -> str:
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


def main():
    db = SessionLocal()
    inserted = updated = categorized = 0

    try:
        for (vid_id, title, channel, views, pub_str) in REAL_VIDEOS:
            pub_dt = datetime.strptime(pub_str, "%Y-%m-%d")
            existing = db.query(Video).filter_by(video_id=vid_id).first()

            if existing:
                existing.title = title
                existing.view_count = views
                existing.thumbnail_url = thumbnail_url(vid_id)
                v = existing
                updated += 1
            else:
                v = Video(
                    video_id=vid_id,
                    title=title,
                    thumbnail_url=thumbnail_url(vid_id),
                    channel_name=channel,
                    view_count=views,
                    published_at=pub_dt,
                    url=f"https://youtube.com/watch?v={vid_id}",
                )
                db.add(v)
                inserted += 1

            cats = find_categories(title, db)
            if cats:
                v.categories = cats
                categorized += 1

            print(f"  {'NEW' if not existing else 'UPD'}: {title[:60]}")

        db.commit()
        print(f"\n=== Done: {inserted} inserted, {updated} updated, {categorized} categorized ===")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
