import os
import sys
import sqlite3
import argparse
import subprocess
import tempfile
import time
import json
from typing import Optional
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from googleapiclient.discovery import build
from google.api_core.exceptions import ResourceExhausted

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

# 기본 텍스트 요약용 모델 (성능 중시)
text_model = genai.GenerativeModel('gemini-3-pro-preview')
# 오디오 분석용 모델 (속도, 가성비 중시)
audio_model = genai.GenerativeModel('gemini-3-flash-preview')

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
        # 수동 자막 및 자동 생성 자막까지 모두 탐색 (더 적극적으로)
        transcript_data = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_data.find_manually_created_transcript(['ko', 'en'])
        except:
            transcript = transcript_data.find_generated_transcript(['ko', 'en'])
            
        transcript_list = transcript.fetch()
        
        # Format text with timestamps
        text_with_timestamps = []
        for t in transcript_list:
            start_time = int(t['start'])
            minutes, seconds = divmod(start_time, 60)
            text_with_timestamps.append(f"({minutes:02d}:{seconds:02d}) {t['text']}")
        return " ".join(text_with_timestamps)
    except Exception as e:
        return ""

def create_prompt(url: str, title: str, content: str) -> str:
    return f"""
다음은 유튜브 영상("{title}", 링크: {url})의 스크립트(또는 설명)입니다. 이 내용을 바탕으로 시청자가 보기 쉽고, 직관적인 레시피를 **반드시 10줄 이내**로 요약해주세요.

조건:
1. 레시피 본질에 집중하고, 불필요한 말은 제외하세요.
2. 각 단계는 1줄 넘지 않도록 명사형 종결어미(~함, ~음 등)를 사용하여 아주 간결하게 작성하세요. **조리 순서 및 문장 전체에 이모지(emoji)나 기호를 일절 사용하지 말고 오직 텍스트만 사용하세요.**
3. 조리 순서의 각 단계 맨 끝에는 해당 조리 과정이 등장하는 **영상 타임스탬프(예: (02:15))** 를 소괄호로 묶어서 써주세요.
4. 핵심 재료는 재료명과 분량(양)을 반드시 함께 적어주세요. 여러 줄로 나누지 말고 무조건 **한 줄** 안에 쉼표(,)로 연결하여 작성하세요. (예: 감자 2개, 양파 1/2개, 간장 2큰술)
5. 양식은 다음 구조를 엄격히 지켜주세요 (전체 7줄 이내 제한):
6. **중요: 만약 이 영상이 요리 레시피를 설명하는 영상이 아니라면 (예: 주방 도구 소개, 단순 먹방, 브이로그, 인터뷰 등 요리 과정이 없는 영상) 다른 말은 일절 하지 말고 오직 `NOT_A_RECIPE` 라는 단어만 출력하세요.**

👨‍🍳 [요리명]
📍 핵심 재료: 양파 1/2개, 당근 1/4개, 간장 2큰술... (단일 줄)
📍 조리 순서
1) ... (01:20)
2) ... (03:05)
3) ... (04:45)

내용:
{content}
"""

def summarize_recipe(url: str, title: str, content: str) -> Optional[str]:
    if len(content.strip()) < 50:
        return None
        
    prompt = create_prompt(url, title, content)
    
    max_retries = 3
    base_delay = 15
    
    for attempt in range(max_retries):
        try:
            time.sleep(base_delay)
            response = text_model.generate_content(prompt)
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

def extract_recipe_from_audio(video_id: str, title: str) -> Optional[str]:
    url = f"https://www.youtube.com/watch?v={video_id}"
    temp_dir = tempfile.gettempdir()
    audio_path_template = os.path.join(temp_dir, f"temp_{video_id}.%(ext)s")
    downloaded_file = None
    remote_file = None
    
    print("  -> 📥 자막/설명이 부족하여 오디오 다운로드를 시작합니다 (yt-dlp)...")
    try:
        # yt-dlp로 변환없이(m4a/webm) 가장 용량이 작은 오디오만 빠르게 다운로드
        subprocess.run([
            sys.executable, "-m", "yt_dlp",
            "-f", "worstaudio[ext=m4a]/worstaudio",
            "-o", audio_path_template,
            url
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 파일 확인
        for filename in os.listdir(temp_dir):
            if filename.startswith(f"temp_{video_id}"):
                downloaded_file = os.path.join(temp_dir, filename)
                break
                
        if not downloaded_file:
            print("  ❌ 오디오 파일 다운로드 실패.")
            return None
            
        file_size_mb = os.path.getsize(downloaded_file) / (1024 * 1024)
        print(f"  -> 📤 오디오 파일을 Gemini API에 업로드합니다: {os.path.basename(downloaded_file)} ({file_size_mb:.2f}MB)")
        
        remote_file = genai.upload_file(downloaded_file)
        
        # 업로드 완료 대기
        while remote_file.state.name == "PROCESSING":
            time.sleep(2)
            remote_file = genai.get_file(remote_file.name)
            
        if remote_file.state.name == "FAILED":
            print("  ❌ 오디오 파일 처리 실패 (Gemini API 내부 오류).")
            return None
            
        prompt = f"""이 오디오("{title}")를 듣고 레시피를 JSON으로 뽑아줘.

조건:
1. 레시피 본질에 집중하고, 불필요한 말은 제외하세요.
2. 각 단계는 1줄을 넘지 않도록 명사형 종결어미(~함, ~음 등)를 사용하여 아주 간결하게 작성하세요. **조리 순서 및 문장 전체에 이모지(emoji)나 기호를 일절 사용하지 말고 오직 텍스트만 사용하세요.**
3. 조리 순서 끝에 해당 조리 과정이 등장하는 영상 타임스탬프(예: (02:15))를 소괄호로 적어주세요.
4. 핵심 재료는 재료명과 분량(양)을 반드시 함께 적어주세요. 모두 하나의 문자열에 쉼표(,)로 연결하여 길이가 1인 배열에 담아주세요. (예: ["감자 2개, 양파 1/2개, 간장 2큰술"])
5. 출력은 반드시 순수 JSON이어야 합니다 (마크다운 없이).
6. **중요: 만약 이 영상이 요리 레시피를 설명하는 영상이 아니라면 (예: 주방 도구 소개, 단순 먹방, 브이로그, 인터뷰 등 요리 과정이 없는 영상) `is_recipe` 필드를 false로 설정하세요.**

형식 구조:
{{
  "is_recipe": true,
  "title": "{title} 레시피",
  "ingredients": ["감자 2개, 간장 2큰술, 대파 1단"],
  "steps": [
    "1) ... (01:20)",
    "2) ... (03:05)"
  ]
}}"""
        
        print("  -> 🤖 Gemini 1.5 Flash에 오디오 분석을 요청합니다...")
        response = audio_model.generate_content([remote_file, prompt])
        
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        
        # JSON을 파싱해서 화면용 텍스트 포맷에 맞춘다
        try:
            parsed = json.loads(raw_text)
            
            # 요리 영상이 아니라고 판단되면 조기 종료 플래그 반환
            if not parsed.get("is_recipe", True):
                return "NOT_A_RECIPE"
                
            formatted = f"👨‍🍳 {parsed.get('title', '레시피')}\n📍 핵심 재료: "
            ingredients = parsed.get('ingredients', [])
            formatted += ", ".join(ingredients) + "\n"
            formatted += "📍 조리 순서\n"
            for step in parsed.get('steps', []):
                formatted += f"{step}\n"
            return formatted.strip()
        except:
            # JSON 파싱 실패시 생성된 텍스트라도 반환
            return raw_text

    except ResourceExhausted:
        print("  ⏳ Gemini Quota Exceeded (429) during audio processing.")
        return None
    except Exception as e:
        print(f"  ❌ 오디오 추출 중 에러 발생: {e}")
        return None
    finally:
        if remote_file:
            try:
                genai.delete_file(remote_file.name)
                print("  -> 🧹 원격 오디오 파일(Gemini 서버) 삭제 완료.")
            except:
                pass
        if downloaded_file and os.path.exists(downloaded_file):
            try:
                os.remove(downloaded_file)
                print("  -> 🧹 로컬 임시 오디오 파일 삭제 완료.")
            except:
                pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--min-views', type=int, default=50000, help='처리할 최소 조회수 기준 (기본 5만)')
    args = parser.parse_args()
    
    conn = sqlite3.connect('k_foods.db')
    cur = conn.cursor()
    
    # 레시피 데이터가 없는 특정 조회수 이상 영상들 모두 조회
    cur.execute('''
        SELECT video_id, title FROM videos 
        WHERE (recipe_memo IS NULL OR recipe_memo = '') AND view_count >= ?
        ORDER BY view_count DESC
    ''', (args.min_views,))
    
    videos = cur.fetchall()
    if not videos:
        print(f"조회수 {args.min_views} 이상인 처리할 영상이 없습니다.")
        return
        
    print(f"총 {len(videos)}개의 영상을 천천히 백그라운드에서 처리합니다 (조회수 {args.min_views} 이상)...")
    
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    updated_count = 0
    
    for idx, (video_id, title) in enumerate(videos, 1):
        print(f"\n==========================================")
        print(f"[{idx}/{len(videos)}] {title[:30]}... 처리 중")
        
        extracted_recipe = None

        # 1. 자막(Transcript) 가져오기 시도 (수동/자동 모두)
        content = get_video_transcript(video_id)
        
        # 2. 자막이 100자 이상이면 텍스트 기반 추출
        if len(content) >= 100:
            print("  -> 📝 자막(텍스트) 기반 추출을 진행합니다.")
            content = content[:15000] # 조금 더 길게 허용 (15k자)
            url = f"https://youtube.com/watch?v={video_id}"
            extracted_recipe = summarize_recipe(url, title, content)
        else:
            print("  -> ⚠️ 자막이 없거나 너무 짧습니다.")
            
        # 3. 텍스트 추출로 실패했거나 자막이 아예 없으면 오디오 통채로 분석 (최적화)
        if not extracted_recipe:
            extracted_recipe = extract_recipe_from_audio(video_id, title)
            
        # 4. 최종 결과 DB 저장 및 예외 처리
        if extracted_recipe == "NOT_A_RECIPE":
            cur.execute('DELETE FROM videos WHERE video_id = ?', (video_id,))
            conn.commit()
            print("  -> 🗑️ 요리 레시피 영상이 아니어서 데이터베이스에서 완전히 삭제했습니다.")
        elif extracted_recipe:
            cur.execute('UPDATE videos SET recipe_memo = ? WHERE video_id = ?', (extracted_recipe, video_id))
            conn.commit()
            updated_count += 1
            print("  -> ✅ 레시피 추출성공 및 데이터베이스 저장 완료!")
        else:
            print("  -> ⚠️ 의미 있는 레시피를 추출하지 못했습니다. (API 제한 등)")
            
        # 5. 과부하 방지 및 API Limit(429) 회피 용도로 의도적 대기
        print("  -> ⏳ 진행 속도 조절 및 서버 안정화를 위해 15초간 대기합니다...")
        time.sleep(15)
            
    conn.close()
    print(f"\\n완료! 총 {updated_count}개의 영상에 대해 AI 레시피 요약을 저장했습니다.")

if __name__ == "__main__":
    main()
