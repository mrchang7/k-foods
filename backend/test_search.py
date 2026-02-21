import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from routers.videos import get_videos

db = SessionLocal()
try:
    res = get_videos(q="김치", limit=5, offset=0, exclude_ids=None, category_ids=None, db=db)
    print("Search Result Total:", res.total)
    for v in res.videos:
        print(" -", v.title, v.view_count)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
