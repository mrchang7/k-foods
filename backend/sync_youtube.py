import os
from googleapiclient.discovery import build
from database import SessionLocal
from models import Video
from datetime import datetime
from dotenv import load_dotenv

# Load env variables for local testing
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "your_api_key_here":
    print("Warning: YOUTUBE_API_KEY is missing or invalid. Set it in .env for actual syncing.")

def get_youtube_service():
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "your_api_key_here":
        return None
    return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def sync_videos():
    print("Starting YouTube Sync Process...")
    youtube = get_youtube_service()
    if not youtube:
        print("Aborting sync: Valid YouTube API key is required.")
        return

    db = SessionLocal()
    
    # For demonstration, we'll search for recent videos from a known channel "백종원 PAIK JONG WON"
    # Channel ID for Paik's Cuisine is UCyn-K7rZLXjGl7VXGweIlcA
    target_channel_id = "UCyn-K7rZLXjGl7VXGweIlcA" 
    
    try:
        # 1. Fetch latest videos from channel
        request = youtube.search().list(
            part="snippet",
            channelId=target_channel_id,
            maxResults=10,
            order="date",
            type="video"
        )
        response = request.execute()
        
        # Collect video IDs to fetch statistics
        video_ids = [item['id']['videoId'] for item in response.get('items', [])]
        
        if not video_ids:
            print("No videos found.")
            return

        # 2. Fetch statistics (viewCount) for these videos
        stat_request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        )
        stat_response = stat_request.execute()
        
        # 3. Upsert into database
        for item in stat_response.get('items', []):
            vid_id = item['id']
            snippet = item['snippet']
            stats = item['statistics']
            
            # Check if video already exists
            existing_video = db.query(Video).filter_by(video_id=vid_id).first()
            
            published_date = datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
            view_count = int(stats.get('viewCount', 0))
            
            if existing_video:
                print(f"Updating video: {snippet['title']} (Views: {view_count})")
                existing_video.view_count = view_count
                existing_video.title = snippet['title']
                existing_video.thumbnail_url = snippet['thumbnails']['high']['url']
            else:
                print(f"Inserting new video: {snippet['title']} (Views: {view_count})")
                new_video = Video(
                    video_id=vid_id,
                    title=snippet['title'],
                    thumbnail_url=snippet['thumbnails']['high']['url'],
                    channel_name=snippet['channelTitle'],
                    view_count=view_count,
                    published_at=published_date,
                    url=f"https://youtube.com/watch?v={vid_id}"
                )
                db.add(new_video)
        
        db.commit()
        print("Sync completed successfully.")

    except Exception as e:
         print(f"Error during sync: {e}")
         db.rollback()
    finally:
         db.close()

if __name__ == "__main__":
    sync_videos()
