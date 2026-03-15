import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import SessionLocal
from models import Video
from schemas import VideoWithCategories

db = SessionLocal()
v_model = db.query(Video).filter(Video.video_id == 'jiToVYf8hyQ').first()
if v_model:
    print("Found video in DB.")
    schema_v = VideoWithCategories.model_validate(v_model)
    dumped = schema_v.model_dump()
    print("is_short:", dumped.get('is_short'))
    print("is_vertical:", dumped.get('is_vertical'))
else:
    print("Video not found.")
