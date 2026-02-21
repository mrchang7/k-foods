import sys
import os
# Force UTF-8 output on Windows to avoid emoji encoding errors
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Video, Category, video_category_map
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# ─── Target Channels ───────────────────────────────────────────────────────────
# Popular Korean food/cooking YouTube channels and their IDs
TARGET_CHANNELS = [
    {"name": "백종원의 요리비책", "id": "UCyn-K7rZLXjGl7VXGweIlcA"},  # Paik Jong Won
    {"name": "만개의레시피",       "id": "UCKA_6r3CWC76x_EaFO6jsPA"},  # 10000 Recipes
    {"name": "쿠킹하루",           "id": "UCC8bTxyN2ZCfMzS_JAEClfA"},  # Cooking Haru
    {"name": "Honeykki 꿀키",      "id": "UCvQPUPoMK0Smj-OHeUe9SEw"},  # Honeykki
    {"name": "Maangchi",           "id": "UC8gFadPgK2r1nwRzL7S034w"},  # Maangchi
    {"name": "Seonkyoung Longest", "id": "UCvN79pS2Xf6U_93w3b7sL5A"},  # Seonkyoung Longest
]

# ─── Keyword → Category Name Mapping ──────────────────────────────────────────
# Keywords in video titles map to category names in the DB
KEYWORD_CATEGORY_MAP = {
    # 음식 종류
    "찌개":   ["찌개", "국/탕/찌개/전골"],
    "국":     ["국", "국/탕/찌개/전골"],
    "탕":     ["탕", "국/탕/찌개/전골"],
    "전골":   ["전골", "국/탕/찌개/전골"],
    "라면":   ["라면/라볶이", "밥/죽/면류"],
    "면":     ["면류", "밥/죽/면류"],
    "냉면":   ["냉면", "밥/죽/면류"],
    "비빔밥": ["비빔밥", "밥/죽/면류"],
    "볶음밥": ["볶음밥", "밥/죽/면류"],
    "죽":     ["밥/죽/면류"],
    "김치":   ["김치류", "반찬류"],
    "나물":   ["나물/무침류", "반찬류"],
    "전":     ["전/부침류", "반찬류"],
    "구이":   ["구이류", "반찬류"],
    "조림":   ["조림류", "반찬류"],
    "떡볶이": ["떡볶이", "간식/분식류"],
    "튀김":   ["튀김류", "간식/분식류"],
    "케이크": ["케이크/빵", "간식/디저트류"],
    "빵":     ["케이크/빵", "간식/디저트류"],
    "쿠키":   ["간식/디저트류"],
    "불고기": ["불고기", "일품/메인요리"],
    "갈비":   ["갈비", "일품/메인요리"],
    "삼겹살": ["돼지고기", "주재료별"],
    "치킨":   ["닭고기/가금류", "주재료별"],
    "닭":     ["닭고기/가금류", "주재료별"],
    "오리":   ["닭고기/가금류", "주재료별"],
    "소고기": ["소고기", "주재료별"],
    "돼지":   ["돼지고기", "주재료별"],
    "해산물": ["수산물/해산물", "주재료별"],
    "새우":   ["수산물/해산물", "주재료별"],
    "오징어": ["수산물/해산물", "주재료별"],
    "꽃게":   ["수산물/해산물", "주재료별"],
    "고등어": ["수산물/해산물", "주재료별"],
    "두부":   ["두부/콩류", "주재료별"],
    "계란":   ["계란", "주재료별"],
    "달걀":   ["계란", "주재료별"],
    "볶기":   ["볶기/炒", "조리법별"],
    "볶음":   ["볶기/炒", "조리법별"],
    "끓이기": ["끓이기/煮", "조리법별"],
    "굽기":   ["굽기/焼き", "조리법별"],
    "찜":     ["찌기/蒸", "조리법별"],
    "초간단": ["초간단 레시피", "상황 및 목적별"],
    "자취":   ["자취생 레시피", "상황 및 목적별"],
    "혼밥":   ["1인분/혼밥", "상황 및 목적별"],
    "다이어트":["다이어트식", "상황 및 목적별"],
    "명절":   ["명절/기념일 음식", "상황 및 목적별"],
    "간식":   ["간식/야식", "상황 및 목적별"],
    "야식":   ["간식/야식", "상황 및 목적별"],
    "백종원": ["백종원", "테마 및 크리에이터"],
    "꿀키":   ["꿀키", "테마 및 크리에이터"],
}


def get_youtube_service():
    if not YOUTUBE_API_KEY:
        print("ERROR: YOUTUBE_API_KEY not set in .env")
        sys.exit(1)
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def find_matching_categories(title: str, db: Session) -> list[Category]:
    """Return Category objects from DB that match keywords found in the video title."""
    title_lower = title.lower()
    matched_names = set()
    
    for keyword, cat_names in KEYWORD_CATEGORY_MAP.items():
        if keyword in title_lower or keyword in title:
            for name in cat_names:
                matched_names.add(name)

    if not matched_names:
        return []

    # Fetch matching categories from DB
    categories = db.query(Category).filter(Category.name.in_(matched_names)).all()
    return categories


def fetch_channel_videos(youtube, channel_id: str, max_results: int = 30) -> list[dict]:
    """Fetch latest video IDs + basic snippet from a channel's uploads."""
    # Get the uploads playlist ID
    channel_resp = youtube.channels().list(part="contentDetails", id=channel_id).execute()
    if not channel_resp.get("items"):
        return []
    
    uploads_playlist_id = channel_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    # Page through playlist items
    videos = []
    next_page_token = None
    
    while len(videos) < max_results:
        page_size = min(50, max_results - len(videos))
        playlist_resp = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=page_size,
            pageToken=next_page_token,
        ).execute()
        
        for item in playlist_resp.get("items", []):
            snippet = item["snippet"]
            vid_id = snippet["resourceId"]["videoId"]
            videos.append(vid_id)
        
        next_page_token = playlist_resp.get("nextPageToken")
        if not next_page_token:
            break
    
    return videos


def fetch_video_details(youtube, video_ids: list[str]) -> list[dict]:
    """Batch fetch video statistics and snippet details."""
    results = []
    # YouTube API allows max 50 IDs per request
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        resp = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(batch),
        ).execute()
        results.extend(resp.get("items", []))
    return results


def sync_videos():
    print(f"\n{'='*60}")
    print("  Korean Food YouTube Sync Starting...")
    print(f"{'='*60}\n")
    
    youtube = get_youtube_service()
    db = SessionLocal()
    
    total_inserted = 0
    total_updated = 0
    total_categorized = 0
    
    try:
        for channel in TARGET_CHANNELS:
            print(f"📺 Fetching from: {channel['name']}  (ID: {channel['id']})")
            
            try:
                video_ids = fetch_channel_videos(youtube, channel["id"], max_results=50)
                if not video_ids:
                    print(f"  ⚠️  No videos found.\n")
                    continue
                
                print(f"  → Found {len(video_ids)} video IDs, fetching details...")
                details = fetch_video_details(youtube, video_ids)
                
                for item in details:
                    vid_id    = item["id"]
                    snippet   = item["snippet"]
                    stats     = item.get("statistics", {})
                    title     = snippet["title"]
                    channel_title = snippet["channelTitle"]
                    thumb_url = snippet.get("thumbnails", {}).get("high", {}).get("url", "")
                    view_count = int(stats.get("viewCount", 0))
                    published_str = snippet.get("publishedAt", "")
                    
                    try:
                        published_at = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
                    except Exception:
                        published_at = datetime.utcnow()
                    
                    # Upsert the video
                    existing = db.query(Video).filter_by(video_id=vid_id).first()
                    if existing:
                        existing.title = title
                        existing.view_count = view_count
                        existing.thumbnail_url = thumb_url
                        video_obj = existing
                        total_updated += 1
                    else:
                        video_obj = Video(
                            video_id=vid_id,
                            title=title,
                            thumbnail_url=thumb_url,
                            channel_name=channel_title,
                            view_count=view_count,
                            published_at=published_at,
                            url=f"https://youtube.com/watch?v={vid_id}",
                        )
                        db.add(video_obj)
                        total_inserted += 1
                    
                    # Auto-categorize by keyword matching
                    matched_cats = find_matching_categories(title, db)
                    if matched_cats:
                        # Clear existing categories then re-assign
                        video_obj.categories = matched_cats
                        total_categorized += 1
                    
                    print(f"  ✅ [{'+' if not existing else '~'}] {title[:60]} | 조회수: {view_count:,} | 카테고리: {len(matched_cats)}개")
                
                db.commit()
                print()
            
            except Exception as channel_err:
                print(f"  ❌ Error fetching channel {channel['name']}: {channel_err}\n")
                db.rollback()
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        db.rollback()
    finally:
        db.close()
    
    print(f"\n{'='*60}")
    print(f"  ✅ Sync Complete!")
    print(f"  Inserted: {total_inserted} | Updated: {total_updated} | Categorized: {total_categorized}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    sync_videos()
