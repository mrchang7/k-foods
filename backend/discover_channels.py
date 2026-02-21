import os, sys, json
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    print("No API Key")
    sys.exit(1)

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

queries = ["요리 레시피", "집밥", "한국 음식 만들기", "간단 요리", "반찬 만들기", "베이킹", "먹방 요리", "국 찌개 레시피", "korean food recipe", "자취 요리"]
channels_dict = {}

print("Starting discovery...")
for q in queries:
    print(f"Searching for {q}...")
    try:
        req = youtube.search().list(part="snippet", q=q, type="channel", maxResults=50, regionCode="KR", relevanceLanguage="ko")
        res = req.execute()
        for item in res.get("items", []):
            cid = item["snippet"]["channelId"]
            ctitle = item["snippet"]["channelTitle"]
            channels_dict[cid] = ctitle
    except Exception as e:
        print(e)

# Also add the original hardcoded ones to guarantee quality
original_channels = [
    {"name": "백종원의 요리비책", "id": "UCyn-K7rZLXjGl7VXGweIlcA"},
    {"name": "만개의레시피",       "id": "UCKA_6r3CWC76x_EaFO6jsPA"},
    {"name": "쿠킹하루",           "id": "UCC8bTxyN2ZCfMzS_JAEClfA"},
    {"name": "Honeykki 꿀키",      "id": "UCvQPUPoMK0Smj-OHeUe9SEw"},
    {"name": "Maangchi",           "id": "UC8gFadPgK2r1nwRzL7S034w"},
    {"name": "Seonkyoung Longest", "id": "UCvN79pS2Xf6U_93w3b7sL5A"},
    {"name": "1분요리 뚝딱이형",   "id": "UCbp5w2D7Lz-gEqmYqgC5Gaw"},
    {"name": "우리의식탁",         "id": "UCy-0k-_rYQstfVb586WkLNg"},
    {"name": "아내의 식탁",        "id": "UC1B5aG6qJ2bH1660Zio_S9A"},
    {"name": "마카롱여사",         "id": "UCqX6A-gP-o8J8eY8K1v6dEQ"},
    {"name": "하루한끼",           "id": "UCPWFxcwPliEBMwAuaUo0kPQ"},
    {"name": "자취요리신",         "id": "UCpT8Y13gT1S65P-N0g-7A2w"},
    {"name": "요리왕비룡",         "id": "UCy4wKx1d-9eIfS5yM0Ff4Jw"},
    {"name": "엄마의 손맛",        "id": "UCwUuzTIOIf9P2z-g58-ZkWA"},
    {"name": "심방골주부",         "id": "UC1-qXndF-U5f_5Xw-cR6rWQ"},
    {"name": "하정우요리",         "id": "UCq_m35EheD0gDte1S1zHhFA"},
]

for ch in original_channels:
    channels_dict[ch["id"]] = ch["name"]

channels_list = [{"name": name, "id": cid} for cid, name in channels_dict.items()]

print(f"Found {len(channels_list)} unique channels.")

with open("channels.json", "w", encoding="utf-8") as f:
    json.dump(channels_list, f, ensure_ascii=False, indent=2)

print("Saved to channels.json")
