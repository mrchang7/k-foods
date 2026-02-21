import os
import sys
import sqlite3
import argparse
from typing import Optional
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Setup API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not GEMINI_API_KEY:
    print("=========================================")
    print("❌ 에러: GEMINI_API_KEY가 .env 파일에 없습니다.")
    print("AI 요약을 위해서는 Gemini API 키가 필요합니다.")
    print("=========================================")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Use gemini-3-flash-preview for summarize
model = genai.GenerativeModel('gemini-3-flash-preview')

def get_video_description(youtube, video_id: str) -> str:
    try:
        request = youtube.videos().list(part="snippet", id=video_id)
        response = request.execute()
        items = response.get("items", [])
        if items:
            return items[0]["snippet"].get("description", "")
        return ""
    except Exception as e:
        print(f"Error fetching description for {video_id}: {e}")
        return ""

def get_video_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        # Format text with timestamps
        text_with_timestamps = []
        for t in transcript_list:
            start_time = int(t['start'])
            minutes, seconds = divmod(start_time, 60)
            text_with_timestamps.append(f"[{minutes:02d}:{seconds:02d}] {t['text']}")
        return " ".join(text_with_timestamps)
    except Exception as e:
        return ""

def create_prompt(url: str, title: str, content: str) -> str:
    return f"""
다음은 유튜브 요리 영상("{title}", 링크: {url})의 스크립트(또는 설명)입니다. 이 내용을 바탕으로 시청자가 보기 쉽고, 직관적인 레시피를 **반드시 10줄 이내**로 요약해주세요.

조건:
1. 레시피 본질에 집중하고, 불필요한 말은 제외하세요.
2. 각 단계는 간결하게 작성하고, 시각적으로 깔끔하게 이모지(예: 🥩, 🥄, 🔥 등)를 적절히 활용하세요.
3. 조리 순서의 각 단계 끝에는 해당 조리 과정이 등장하는 **영상 타임스탬프(예: [02:15])** 를 시각적으로 잘 띄게 써주세요.
4. 양식은 다음 구조를 엄격히 지켜주세요 (전체 10줄 이내 제한):

👨‍🍳 [요리명]
📍 핵심 재료
- 재료1, 재료2, ...
📍 조리 순서
1) ... [01:20] ⏰
2) ... [03:05] ⏰
3) ... [04:45] ⏰

내용:
{content}
"""

import time
from google.api_core.exceptions import ResourceExhausted

def summarize_recipe(url: str, title: str, content: str) -> Optional[str]:
    # 만약 텍스트가 너무 짧으면 요리 영상이 아니거나 정보가 없는 것이므로 건너뛰기
    if len(content.strip()) < 50:
        return None
        
    prompt = create_prompt(url, title, content)
    
    max_retries = 3
    base_delay = 15 # Wait at least 15s between requests to avoid RPM issues
    
    for attempt in range(max_retries):
        try:
            time.sleep(base_delay)
            response = model.generate_content(prompt)
            # Gemini가 가끔 마크다운 코드블록을 넣을 수 있으므로 제거
            result = response.text.replace("```markdown", "").replace("```", "").strip()
            return result
        except ResourceExhausted as e:
            wait_time = base_delay * (2 ** attempt)
            print(f"  ⏳ Gemini Quota Exceeded (429). Waiting {wait_time}s before retry {attempt+1}/{max_retries}...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"  ❌ Gemini API 에러: {e}")
            return None
            
    print("  ❌ Max retries reached for Gemini API.")
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=100, help='처리할 최대 영상 개수 (조회수 기준 상위 N개)')
    args = parser.parse_args()
    
    conn = sqlite3.connect('k_foods.db')
    cur = conn.cursor()
    
    # 조회수가 가장 높은 영상 중, recipe_memo를 AI로 다시 만들기 위해
    cur.execute('''
        SELECT video_id, title FROM videos 
        ORDER BY view_count DESC 
        LIMIT ?
    ''', (args.limit,))
    
    videos = cur.fetchall()
    if not videos:
        print("처리할 영상이 없습니다.")
        return
        
    print(f"총 {len(videos)}개의 영상을 처리합니다 (화면에 노출되는 상위 {args.limit}개)...")
    
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    updated_count = 0
    
    for idx, (video_id, title) in enumerate(videos, 1):
        print(f"[{idx}/{len(videos)}] {title[:30]}... 처리 중")
        
        # 1. 자막(Transcript) 가져오기 시도
        content = get_video_transcript(video_id)
        
        # 2. 자막이 없거나 짧으면 설명(Description) 가져오기
        if len(content) < 100:
            content = get_video_description(youtube, video_id)
            
        if not content:
            print("  -> 내용(자막/설명)이 부족하여 건너뜁니다.")
            continue
            
        # 내용이 너무 길면 앞부분 8000자만 사용 (토큰 제한 방지)
        content = content[:8000]
            
        # 3. AI로 요약하기
        url = f"https://youtube.com/watch?v={video_id}"
        ai_recipe = summarize_recipe(url, title, content)
        
        if ai_recipe:
            # DB 업데이트
            cur.execute('UPDATE videos SET recipe_memo = ? WHERE video_id = ?', (ai_recipe, video_id))
            conn.commit()
            updated_count += 1
            print("  -> ✅ AI 요약 성공!")
        else:
            print("  -> ⚠️ 의미 있는 레시피를 추출하지 못했습니다.")
            
    conn.close()
    print(f"\n완료! 총 {updated_count}개의 영상에 대해 AI 레시피 요약을 저장했습니다.")

if __name__ == "__main__":
    main()
