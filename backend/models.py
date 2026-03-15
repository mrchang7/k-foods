from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Many-to-Many association table
video_category_map = Table(
    'video_category_map',
    Base.metadata,
    Column('video_id', String, ForeignKey('videos.video_id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.category_id'), primary_key=True)
)

class Video(Base):
    __tablename__ = 'videos'

    video_id = Column(String, primary_key=True, index=True) # YouTube Video ID
    title = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    channel_name = Column(String, nullable=True)
    view_count = Column(Integer, default=0)
    published_at = Column(DateTime, nullable=True)
    url = Column(String, nullable=False)
    recipe_memo = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)

    # Relationships
    categories = relationship('Category', secondary=video_category_map, back_populates='videos')

    @property
    def is_short(self) -> bool:
        # If we have accurate duration from API, use that as the primary source of truth (80 secs = 1분 20초)
        if self.duration is not None:
            if self.duration <= 80:
                return True
            # If duration is known to be > 80, it's NOT a short, regardless of titles
            return False
            
        # Fallback to heuristics if duration is not yet populated
        title_lower = (self.title or "").lower()
        channel_lower = (self.channel_name or "").lower()
        url_lower = (self.url or "").lower()
        
        if "/shorts/" in url_lower:
            return True
            
        short_keywords = ['shorts', 'shrots', 'short', '쇼츠', '1분', '1 minute', '틱톡', 'tiktok']
        for k in short_keywords:
            if k in title_lower:
                return True
                
        short_channels = ['1분', '자취요리신', '레시피 읽어주는 여자', '뚝딱이형', '퉁키']
        for c in short_channels:
            if c in channel_lower:
                return True
                
                
        return False

    @property
    def is_vertical(self) -> bool:
        url_lower = (self.url or "").lower()
        if "vertical=1" in url_lower or "/shorts/" in url_lower:
            return True
        if self.duration is not None and self.duration <= 80:
            return True
        return self.is_short

class Category(Base):
    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, nullable=False) # e.g. 국/탕, 볶음, 소고기
    category_type = Column(String, nullable=False) # e.g. 종류별, 재료별, 조리법별 (Level 1)
    
    # Self-referential relationship for hierarchical structure
    parent_id = Column(Integer, ForeignKey('categories.category_id'), nullable=True)
    
    # Relationships
    children = relationship('Category', backref='parent', remote_side=[category_id])
    videos = relationship('Video', secondary=video_category_map, back_populates='categories')


