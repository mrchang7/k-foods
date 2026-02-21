import sqlite3
import builtins

def main():
    conn = sqlite3.connect('k_foods.db')
    cur = conn.cursor()
    cur.execute('SELECT title, recipe_memo FROM videos WHERE recipe_memo IS NOT NULL AND recipe_memo != "" AND length(recipe_memo) > 30 ORDER BY view_count DESC LIMIT 3 OFFSET 5')
    
    with open('inspect_output.txt', 'w', encoding='utf-8') as f:
        for row in cur.fetchall():
            f.write(f"TITLE: {row[0]}\nRECIPE:\n{row[1]}\n{'='*40}\n")
            
    conn.close()

if __name__ == "__main__":
    main()
