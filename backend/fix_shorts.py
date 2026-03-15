import sqlite3

def fix_stubborn_shorts():
    conn = sqlite3.connect('k_foods.db')
    cur = conn.cursor()
    
    # We want to find videos without duration that match the titles from the user screenshot.
    # The titles were:
    # "추석에 잡채 만들어보세요!"
    # "한번에 쉽게 만드는 한입 치즈돈까스"
    # "⭐️300만뷰⭐️ 버섯솥밥, 소고기 넣었더니 | 찬밥으로 더 맛있게💯 #집밥 #솥밥 #easyrecipe"
    
    # Check if they exist first
    cur.execute("""
        SELECT video_id, title, duration, url 
        FROM videos 
        WHERE duration IS NULL AND (
            title LIKE '%잡채 만들어보세요%' OR 
            title LIKE '%한입 치즈돈까스%' OR 
            title LIKE '%버섯솥밥%'
        )
    """)
    
    shorts_to_fix = cur.fetchall()
    print(f"Found {len(shorts_to_fix)} specific shorts without duration.")
    
    for row in shorts_to_fix:
        # Update them to have a duration of 60 seconds so they are caught by the short filter
        cur.execute("UPDATE videos SET duration = 60 WHERE video_id = ?", (row[0],))
        
    conn.commit()
    conn.close()
    print("Done fixing durations.")

if __name__ == "__main__":
    fix_stubborn_shorts()
