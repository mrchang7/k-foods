import sys
import os
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from googleapiclient.discovery import build
from database import SessionLocal
from models import Video

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def clean_database():
    print(f"\n{'='*60}")
    print("  Removing Unplayable Videos (Private/Deleted/NoEmbed)...")
    print(f"{'='*60}\n")
    
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    db = SessionLocal()
    
    try:
        videos = db.query(Video).all()
        total_videos = len(videos)
        print(f"Total videos in DB: {total_videos}")
        
        removed_count = 0
        
        # Map video ID to Video object for easy lookup
        vid_map = {v.video_id: v for v in videos}
        video_ids = list(vid_map.keys())
        
        for batch in chunker(video_ids, 50):
            try:
                resp = youtube.videos().list(
                    part="status",
                    id=",".join(batch),
                ).execute()
                
                # Videos returned by the API
                returned_items = resp.get("items", [])
                
                # 1. Any video ID queried but NOT returned is deleted or private
                returned_ids = {item["id"] for item in returned_items}
                missing_ids = set(batch) - returned_ids
                
                for missing_id in missing_ids:
                    print(f"  🗑️ Removing (Deleted/Private): {missing_id} - {vid_map[missing_id].title}")
                    db.delete(vid_map[missing_id])
                    removed_count += 1
                
                # 2. Check embeddable status for returned videos
                for item in returned_items:
                    vid_id = item["id"]
                    status = item.get("status", {})
                    if not status.get("embeddable", True):
                        print(f"  🗑️ Removing (Not Embeddable): {vid_id} - {vid_map[vid_id].title}")
                        db.delete(vid_map[vid_id])
                        removed_count += 1
                        
                db.commit()
            except Exception as e:
                print(f"Error processing batch: {e}")
                db.rollback()
                
        print(f"\n✅ Clean up complete! Removed {removed_count} videos.")
    except Exception as e:
        print(f"Fatal Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_database()
