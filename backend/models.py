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

    # Relationships
    categories = relationship('Category', secondary=video_category_map, back_populates='videos')


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


