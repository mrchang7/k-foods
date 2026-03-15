import os
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# We'll use absolute path for the DB just in case
engine = create_engine("sqlite:///c:/retire/k-foods/backend/k_foods.db")
Session = sessionmaker(bind=engine)
db = Session()

load_dotenv("c:/retire/k-foods/backend/.env")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def parse_duration(duration_str):
    # e.g. PT1H2M10S, PT1M30S, PT45S
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    h, m, s = match.groups()
    hours = int(h) if h else 0
    minutes = int(m) if m else 0
    seconds = int(s) if s else 0
    return hours * 3600 + minutes * 60 + seconds

def main():
    if not YOUTUBE_API_KEY:
        print("No YOUTUBE_API_KEY")
        return

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    
    # Check if duration col exists, if not, add it
    try:
        db.execute("ALTER TABLE videos ADD COLUMN duration INTEGER;")
        db.commit()
        print("Added duration column")
    except Exception as e:
        print("Column might already exist:", e)
    
    from sqlalchemy.sql import text
    # Select videos with NULL duration
    res = db.execute(text("SELECT video_id FROM videos WHERE duration IS NULL")).fetchall()
    video_ids = [row[0] for row in res]
    print(f"Found {len(video_ids)} videos without duration")
    
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        try:
            resp = youtube.videos().list(
                part="contentDetails",
                id=",".join(batch)
            ).execute()
            
            for item in resp.get("items", []):
                vid = item["id"]
                dur_str = item["contentDetails"]["duration"]
                dur_sec = parse_duration(dur_str)
                
                db.execute(text("UPDATE videos SET duration = :dur WHERE video_id = :vid"), {"dur": dur_sec, "vid": vid})
            
            db.commit()
            print(f"Processed {min(i+50, len(video_ids))}/{len(video_ids)}")
        except Exception as e:
            print(f"Failed batch: {e}")

if __name__ == "__main__":
    main()
