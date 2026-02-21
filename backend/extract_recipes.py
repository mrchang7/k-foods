import os
import sqlite3
import argparse
import re
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Get API key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    print("YOUTUBE_API_KEY is missing from .env.")
    exit(1)

def build_youtube_client():
    return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def extract_recipe_heuristic(description):
    if not description:
        return None
        
    lines = description.split('\n')
    recipe_lines = []
    in_recipe = False
    
    # Keywords that often start a recipe block
    start_keywords = ['재료', '준비물', '레시피', '만드는 법', '만드는법', '조리과정', '조리 순서', 'ingredient', 'recipe']
    # Keywords that often end a recipe block or indicate unrelated text
    end_keywords = ['구독', '좋아요', '비즈니스', '광고', '협찬', 'instagram', '인스타그램', 'tiktok', 'email', '이메일']
    
    for line in lines:
        cleaned_line = line.strip().lower()
        if not cleaned_line:
            if in_recipe:
                recipe_lines.append(line)
            continue
            
        # Check start
        if any(keyword in cleaned_line for keyword in start_keywords) and len(cleaned_line) < 30:
            in_recipe = True
            
        # Check end
        if in_recipe and any(keyword in cleaned_line for keyword in end_keywords):
            # Optional: break or just mark end
            in_recipe = False
            continue
            
        if in_recipe:
            recipe_lines.append(line)
            
    result = '\n'.join(recipe_lines).strip()
    
    if len(result) > 20: 
        return result
        
    # If heuristic failed, just look for "재료" and return a chunk around it as fallback
    if "재료" in description:
        # Simple fallback: return everything from "재료" to the end, truncated at reasonable length
        start_idx = description.find("재료")
        # Try to find common ending markers to truncate the rest
        end_idx = len(description)
        for end_kw in end_keywords:
            idx = description.find(end_kw, start_idx)
            if idx != -1 and idx < end_idx:
                end_idx = idx
                
        fallback = description[start_idx:end_idx].strip()
        if len(fallback) > 20 and len(fallback) < 2000:
            return fallback
            
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=100, help='Number of videos to process')
    args = parser.parse_args()
    
    conn = sqlite3.connect('k_foods.db')
    cur = conn.cursor()
    
    # Select videos that don't have a recipe yet, ordered by views
    cur.execute('''
        SELECT video_id FROM videos 
        WHERE recipe_memo IS NULL 
        ORDER BY view_count DESC 
        LIMIT ?
    ''', (args.limit,))
    
    videos = cur.fetchall()
    if not videos:
        print("No videos found needing recipe extraction.")
        return
        
    video_ids = [row[0] for row in videos]
    print(f"Found {len(video_ids)} videos to process.")
    
    youtube = build_youtube_client()
    
    chunk_size = 50
    updated_count = 0
    
    for i in range(0, len(video_ids), chunk_size):
        chunk = video_ids[i:i + chunk_size]
        print(f"Fetching chunk {i+1} to {i+len(chunk)}...")
        
        try:
            request = youtube.videos().list(
                part="snippet",
                id=",".join(chunk)
            )
            response = request.execute()
            
            for item in response.get("items", []):
                vid = item["id"]
                desc = item["snippet"].get("description", "")
                
                recipe = extract_recipe_heuristic(desc)
                if recipe:
                    cur.execute('UPDATE videos SET recipe_memo = ? WHERE video_id = ?', (recipe, vid))
                    updated_count += 1
                else:
                    # Mark as empty so we don't try again right away? 
                    # For now just leave it NULL, or we could set it to "레시피 정보 없음"
                    pass
                    
        except Exception as e:
            print(f"Error fetching from YouTube API: {e}")
            break
            
    conn.commit()
    conn.close()
    
    print(f"Finished! Extracted and saved recipes for {updated_count} videos.")

if __name__ == "__main__":
    main()
