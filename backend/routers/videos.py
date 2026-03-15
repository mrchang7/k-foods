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
    q: Optional[str] = Query(None, description="Text search on title and channel name"),
    only_shorts: Optional[bool] = Query(False, description="Whether to include only shorts"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    seed: int = Query(0, description="Random seed for consistent pagination shuffling"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Video)

    if exclude_ids:
        query = query.filter(models.Video.video_id.not_in(exclude_ids))

    # Full-text search filter (title or channel name)
    if q:
        query = query.filter(
            or_(
                models.Video.title.like(f"%{q}%"),
                models.Video.channel_name.like(f"%{q}%"),
            )
        )

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
            
    # Identify non-food content
    is_non_food = or_(
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
    )

    # Identify shorts
    is_short_cond = or_(
        models.Video.url.like('%/shorts/%'),
        models.Video.title.like('%shorts%'),
        models.Video.title.like('%shrots%'),
        models.Video.title.like('%short%'),
        models.Video.title.like('%쇼츠%'),
        models.Video.title.like('%1분%'),
        models.Video.title.like('%1 minute%'),
        models.Video.title.like('%틱톡%'),
        models.Video.title.like('%tiktok%'),
        models.Video.channel_name.like('%1분%'),
        models.Video.channel_name.like('%자취요리신%'),
        models.Video.channel_name.like('%레시피 읽어주는 여자%'),
        models.Video.channel_name.like('%뚝딱이형%'),
        models.Video.channel_name.like('%퉁키%'),
        models.Video.duration <= 80
    )
    
    # Always exclude non-food content
    query = query.filter(~is_non_food)
    
    if only_shorts:
        # If requesting only shorts, ONLY include videos that match shorts criteria
        query = query.filter(is_short_cond)
    else:
        # If not requesting shorts (main feed), EXCLUDE shorts entirely
        query = query.filter(~is_short_cond)
    
    # When searching by keyword, sort by pure view count (more relevant).
    # Otherwise, use Time-Decay Score + Daily Random Variation + Shorts Penalty.
    if q:
        query = query.order_by(desc(models.Video.view_count))

        # Getting total count
        total = query.with_entities(func.count(models.Video.video_id)).scalar()

        # Pagination
        videos = query.offset(offset).limit(limit).all()

        return schemas.VideoListResponse(
            total=total or 0,
            videos=videos
        )

    today_seed = datetime.utcnow().strftime('%Y%m%d')
    days_passed = func.julianday('now') - func.julianday(models.Video.published_at)
    decay_factor = func.power((days_passed + 1), 1.5)
    
    # Seed-based pseudo-randomness:
    # Instead of a small +/- 30% variance that fails to overcome large view gaps,
    # we generate a massive deterministic multiplier (0.5x to 5.5x) based on the seed
    # so that videos truly shuffle their apparent ranks per session.
    if seed != 0:
        pseudo_rand = ((models.Video.view_count * 17) + seed) % 100
        random_modifier = (pseudo_rand + 10) / 20.0
    else:
        pseudo_rand_static = (models.Video.view_count * 17) % 100
        random_modifier = (pseudo_rand_static + 10) / 20.0

    query = query.order_by(desc((models.Video.view_count * random_modifier) / decay_factor))

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
    offset: int = Query(0, ge=0, description="Pagination offset"),
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
        models.Video.url.like('%/shorts/%'),
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
        models.Video.channel_name.like('%퉁키%'),
        models.Video.duration <= 80
    )
    short_penalty = case((is_penalized, 0.001), else_=1.0)
        
    query = db.query(models.Video)\
              .filter(models.Video.published_at >= time_threshold)\
              .order_by(desc(models.Video.view_count * short_penalty))\
              .offset(offset)\
              .limit(limit)
              
    videos = query.all()
    
    # If not enough recent videos are found, fallback to slightly older ones
    # to ensure the UI isn't empty if no one uploaded in the exact timeframe.
    if len(videos) < limit // 2:
        fallback_threshold = time_threshold - timedelta(days=14)
        query = db.query(models.Video)\
                  .filter(models.Video.published_at >= fallback_threshold)\
                  .order_by(desc(models.Video.view_count * short_penalty))\
                  .offset(offset)\
                  .limit(limit)
        videos = query.all()
        
    return videos
