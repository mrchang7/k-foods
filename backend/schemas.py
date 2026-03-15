from pydantic import BaseModel, HttpUrl, computed_field
from typing import List, Optional
from datetime import datetime

class CategoryBase(BaseModel):
    category_id: int
    name: str
    category_type: str
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True

class CategoryWithChildren(CategoryBase):
    children: List['CategoryWithChildren'] = []

    class Config:
        from_attributes = True

class VideoBase(BaseModel):
    video_id: str
    title: str
    thumbnail_url: Optional[str] = None
    channel_name: Optional[str] = None
    view_count: int
    published_at: Optional[datetime] = None
    url: str
    recipe_memo: Optional[str] = None
    duration: Optional[int] = None
    is_short: bool = False
    is_vertical: bool = False

class VideoWithCategories(VideoBase):
    categories: List[CategoryBase] = []

    class Config:
        from_attributes = True

# Helper responses
class VideoListResponse(BaseModel):
    total: int
    videos: List[VideoWithCategories]
