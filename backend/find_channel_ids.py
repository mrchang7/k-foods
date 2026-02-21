"""
find_channel_ids.py - Resolve channel IDs from channel handles using YouTube Data API
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()

HANDLES = [
    "@만개의레시피",
    "@cooking_haru",
    "@honeykki",
    "@슈가맨",
]

def main():
    api_key = os.getenv("YOUTUBE_API_KEY")
    youtube = build("youtube", "v3", developerKey=api_key)
    for handle in HANDLES:
        resp = youtube.search().list(
            part="snippet",
            q=handle,
            type="channel",
            maxResults=1
        ).execute()
        items = resp.get("items", [])
        if items:
            ch = items[0]["snippet"]
            print(f"{handle} -> {items[0]['id']['channelId']}  ({ch['channelTitle']})")
        else:
            print(f"{handle} -> NOT FOUND")

if __name__ == "__main__":
    main()
