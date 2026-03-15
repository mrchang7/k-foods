import sys
import os
import time

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from googleapiclient.discovery import build
from database import SessionLocal
from models import Video
from dotenv import load_dotenv

load_dotenv('C:/retire/k-foods/backend/.env')
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    print("ERROR: YOUTUBE_API_KEY not set in .env")
    sys.exit(1)

def run():
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    db = SessionLocal()
    
    videos = db.query(Video).filter(
        (Video.duration > 80) | (Video.duration == None)
    ).filter(
        ~Video.url.like('%vertical=1%')
    ).all()
    
    print(f"Total potential disguised videos to check: {len(videos)}")
    
    updated_count = 0
    for i in range(0, len(videos), 50):
        batch = videos[i:i+50]
        vid_map = {v.video_id: v for v in batch}
        
        try:
            resp = youtube.videos().list(
                part="snippet",
                id=",".join(vid_map.keys())
            ).execute()
            
            for item in resp.get('items', []):
                vid = item['id']
                tags = item['snippet'].get('tags', [])
                
                is_short_tag = False
                for t in tags:
                    t_lower = t.lower().replace(" ", "")
                    if 'short' in t_lower or '쇼츠' in t_lower:
                        is_short_tag = True
                        break
                        
                if is_short_tag:
                    video_obj = vid_map[vid]
                    if '?' in video_obj.url:
                        video_obj.url += '&vertical=1'
                    else:
                        video_obj.url += '?vertical=1'
                    updated_count += 1
                    print(f"[{updated_count}] Flagged as vertical: {video_obj.title[:40]}")
                    
            db.commit()
            time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching batch at index {i}: {e}")
            db.rollback()
            
    db.close()
    print(f"Finished! Total disguised vertical videos updated: {updated_count}")

if __name__ == "__main__":
    run()
