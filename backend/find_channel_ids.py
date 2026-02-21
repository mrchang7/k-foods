"""
find_channel_ids.py - Resolve channel IDs from channel handles using YouTube Data API
"""
import sys, os
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()

HANDLES = [
    "Maangchi",
    "Seonkyoung Longest",
    "1분요리 뚝딱이형",
    "우리의식탁",
    "아내의 식탁",
    "마카롱여사",
    "하루한끼",
    "자취요리신",
    "요리왕비룡",
    "엄마의 손맛",
    "심방골주부",
    "Meatater",
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
