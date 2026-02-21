from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, case, or_
from typing import List, Optional
from datetime import datetime

from database import get_db
import models
import schemas

router = APIRouter(
    prefix="/api/videos",
    tags=["videos"]
)

@router.get("", response_model=schemas.VideoListResponse)
def get_videos(
    category_ids: Optional[List[int]] = Query(None, description="Filter by category IDs (OR condition by default if multiple)"),
    exclude_ids: Optional[List[str]] = Query(None, description="Filter out specific video IDs (e.g., currently trending ones)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Video)

    if exclude_ids:
        query = query.filter(models.Video.video_id.not_in(exclude_ids))

    # Filtering by categories (Faceted Search Logic)
    # Categories from the same parent act as OR.
    # Categories from different parents act as AND.
    if category_ids:
        from collections import defaultdict
        from sqlalchemy import select

        # 1. Fetch requested categories to group them by their parent_id
        selected_cats = db.query(models.Category).filter(models.Category.category_id.in_(category_ids)).all()
        
        grouped_filters = defaultdict(list)
        for cat in selected_cats:
            # If a category doesn't have a parent, it acts as its own unique filter group
            group_key = cat.parent_id if cat.parent_id is not None else f"standalone_{cat.category_id}"
            grouped_filters[group_key].append(cat.category_id)
            
        # 2. Apply AND between groups for faceted intersection
        for group_key, cat_ids in grouped_filters.items():
            subquery = select(models.video_category_map.c.video_id).where(
                models.video_category_map.c.category_id.in_(cat_ids)
            )
            query = query.filter(models.Video.video_id.in_(subquery))
    
    from sqlalchemy import case, or_

    # Applying order by Time-Decay Score + Daily Random Variation + Shorts Penalty
    today_seed = datetime.utcnow().strftime('%Y%m%d')
    days_passed = func.julianday('now') - func.julianday(models.Video.published_at)
    decay_factor = func.power((days_passed + 1), 1.5)
    
    random_modifier = 1.0 + ((models.Video.view_count % 100) - 50) / 100.0
    
    # Identify shorts and non-food content (SQLite LIKE is case-insensitive for ASCII)
    is_penalized = or_(
        models.Video.title.like('%shorts%'),
        models.Video.title.like('%shrots%'),
        models.Video.title.like('%short%'),
        models.Video.title.like('%쇼츠%'),
        models.Video.title.like('%1분%'),
        models.Video.title.like('%1 minute%'),
        models.Video.title.like('%틱톡%'),
        models.Video.title.like('%tiktok%'),
        models.Video.title.like('%브이로그%'),
        models.Video.title.like('%vlog%'),
        models.Video.title.like('%패션%'),
        models.Video.title.like('%옷%'),
        models.Video.title.like('%일상%'),
        models.Video.title.like('%다이어트%'),
        models.Video.title.like('%동대문%'),
        models.Video.title.like('%언박싱%'),
        models.Video.title.like('%하울%'),
        models.Video.title.like('%다이소%'),
        models.Video.title.like('%쇼핑%'),
        models.Video.channel_name.like('%1분%'),
        models.Video.channel_name.like('%자취요리신%'),
        models.Video.channel_name.like('%레시피 읽어주는 여자%'),
        models.Video.channel_name.like('%뚝딱이형%'),
        models.Video.channel_name.like('%퉁키%')
    )
    
    # Apply a 99.9% penalty to penalized videos' scores
    short_penalty = case((is_penalized, 0.001), else_=1.0)
    
    query = query.order_by(desc((models.Video.view_count * random_modifier * short_penalty) / decay_factor))

    # Getting total count
    total = query.with_entities(func.count(models.Video.video_id)).scalar()

    # Pagination
    videos = query.offset(offset).limit(limit).all()

    return schemas.VideoListResponse(
        total=total or 0,
        videos=videos
    )

@router.get("/trending", response_model=List[schemas.VideoWithCategories])
def get_trending_videos(
    period: str = Query("weekly", description="Period: daily, weekly, monthly"),
    limit: int = Query(10, ge=1, le=50, description="Number of top videos to return"),
    db: Session = Depends(get_db)
):
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    
    if period == "daily":
        time_threshold = now - timedelta(days=2) # Using 2 days to ensure we have enough data
    elif period == "weekly":
        time_threshold = now - timedelta(days=7)
    elif period == "monthly":
        time_threshold = now - timedelta(days=30)
    else:
        raise HTTPException(status_code=400, detail="Invalid period. Must be daily, weekly, or monthly.")
        
    is_penalized = or_(
        models.Video.title.like('%shorts%'),
        models.Video.title.like('%shrots%'),
        models.Video.title.like('%short%'),
        models.Video.title.like('%쇼츠%'),
        models.Video.title.like('%1분%'),
        models.Video.title.like('%1 minute%'),
        models.Video.title.like('%틱톡%'),
        models.Video.title.like('%tiktok%'),
        models.Video.title.like('%브이로그%'),
        models.Video.title.like('%vlog%'),
        models.Video.title.like('%패션%'),
        models.Video.title.like('%옷%'),
        models.Video.title.like('%일상%'),
        models.Video.title.like('%다이어트%'),
        models.Video.title.like('%동대문%'),
        models.Video.title.like('%언박싱%'),
        models.Video.title.like('%하울%'),
        models.Video.title.like('%다이소%'),
        models.Video.title.like('%쇼핑%'),
        models.Video.channel_name.like('%1분%'),
        models.Video.channel_name.like('%자취요리신%'),
        models.Video.channel_name.like('%레시피 읽어주는 여자%'),
        models.Video.channel_name.like('%뚝딱이형%'),
        models.Video.channel_name.like('%퉁키%')
    )
    short_penalty = case((is_penalized, 0.001), else_=1.0)
        
    query = db.query(models.Video)\
              .filter(models.Video.published_at >= time_threshold)\
              .order_by(desc(models.Video.view_count * short_penalty))\
              .limit(limit)
              
    videos = query.all()
    
    # If not enough recent videos are found, fallback to slightly older ones
    # to ensure the UI isn't empty if no one uploaded in the exact timeframe.
    if len(videos) < limit // 2:
        fallback_threshold = time_threshold - timedelta(days=14)
        query = db.query(models.Video)\
                  .filter(models.Video.published_at >= fallback_threshold)\
                  .order_by(desc(models.Video.view_count * short_penalty))\
                  .limit(limit)
        videos = query.all()
        
    return videos
