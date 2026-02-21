from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional

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
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Video)

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
    
    # Applying order by view_count DESC
    query = query.order_by(desc(models.Video.view_count))

    # Getting total count
    total = query.with_entities(func.count(models.Video.video_id)).scalar()

    # Pagination
    videos = query.offset(offset).limit(limit).all()

    return schemas.VideoListResponse(
        total=total or 0,
        videos=videos
    )
