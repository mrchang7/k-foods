import os
from database import engine, SessionLocal
from models import Base, Category, Video
from datetime import datetime

def init_db():
    print("Dropping all existing tables to apply new taxonomy schema...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    print("Inserting hierarchical categories...")
    # Level 1: 대분류
    cat_type = Category(name="음식 형태별", category_type="대분류")
    cat_ing = Category(name="주재료별", category_type="대분류")
    cat_method = Category(name="조리법별", category_type="대분류")
    cat_occ = Category(name="상황 및 목적별", category_type="대분류")
    cat_theme = Category(name="테마 및 크리에이터", category_type="대분류")
    
    db.add_all([cat_type, cat_ing, cat_method, cat_occ, cat_theme])
    db.commit()

    # Level 2 & 3: 음식 형태별
    cat_rice = Category(name="밥/죽/면류", category_type="음식 형태별", parent_id=cat_type.category_id)
    cat_soup = Category(name="국/탕/찌개/전골", category_type="음식 형태별", parent_id=cat_type.category_id)
    cat_side = Category(name="반찬류", category_type="음식 형태별", parent_id=cat_type.category_id)
    cat_main = Category(name="일품/메인요리", category_type="음식 형태별", parent_id=cat_type.category_id)
    db.add_all([cat_rice, cat_soup, cat_side, cat_main])
    db.commit()

    # Sub of 밥/죽/면류
    db.add_all([
        Category(name="밥류", category_type="음식 형태별", parent_id=cat_rice.category_id),
        Category(name="죽/스프", category_type="음식 형태별", parent_id=cat_rice.category_id),
        Category(name="면류", category_type="음식 형태별", parent_id=cat_rice.category_id),
    ])

    # Sub of 국/탕/찌개/전골
    c_guk = Category(name="국", category_type="음식 형태별", parent_id=cat_soup.category_id)
    c_tang = Category(name="탕", category_type="음식 형태별", parent_id=cat_soup.category_id)
    c_jjigae = Category(name="찌개", category_type="음식 형태별", parent_id=cat_soup.category_id)
    db.add_all([c_guk, c_tang, c_jjigae])
    db.commit()

    # Level 2: 주재료별
    cat_meat = Category(name="육류", category_type="주재료별", parent_id=cat_ing.category_id)
    cat_sea = Category(name="수산물", category_type="주재료별", parent_id=cat_ing.category_id)
    cat_veg = Category(name="채소/곡류", category_type="주재료별", parent_id=cat_ing.category_id)
    db.add_all([cat_meat, cat_sea, cat_veg])
    db.commit()

    c_beef = Category(name="소고기", category_type="주재료별", parent_id=cat_meat.category_id)
    c_pork = Category(name="돼지고기", category_type="주재료별", parent_id=cat_meat.category_id)
    db.add_all([c_beef, c_pork])
    db.commit()

    # Level 2: 조리법별
    cat_boil = Category(name="끓이기", category_type="조리법별", parent_id=cat_method.category_id)
    cat_fry = Category(name="볶기/튀기기", category_type="조리법별", parent_id=cat_method.category_id)
    db.add_all([cat_boil, cat_fry])
    db.commit()

    # Level 2: 상황별 / 테마별
    cat_dinner = Category(name="든든한 저녁 메인", category_type="상황 및 목적별", parent_id=cat_occ.category_id)
    cat_expert = Category(name="전문가 레시피", category_type="테마 및 크리에이터", parent_id=cat_theme.category_id)
    db.add_all([cat_dinner, cat_expert])
    db.commit()
    
    print("Inserting dummy videos with multi-tagging...")
    
    v1 = Video(
        video_id="dummy_kimchi_jjigae",
        title="백종원의 돼지고기 김치찌개",
        thumbnail_url="https://via.placeholder.com/320x180",
        channel_name="백종원의 요리비책",
        view_count=3500000,
        published_at=datetime.utcnow(),
        url="https://youtube.com/watch?v=dummy1"
    )
    # Multi-tagging
    v1.categories.extend([c_jjigae, c_pork, cat_boil, cat_dinner, cat_expert])
    db.add(v1)
    
    v2 = Video(
        video_id="dummy_bulgogi",
        title="15분 완성 뚝딱 불고기",
        thumbnail_url="https://via.placeholder.com/320x180",
        channel_name="요리왕 비룡",
        view_count=800000,
        published_at=datetime.utcnow(),
        url="https://youtube.com/watch?v=dummy2"
    )
    v2.categories.extend([cat_main, c_beef, cat_fry, cat_dinner])
    db.add(v2)

    db.commit()
        
    db.close()
    print("Database initialization with hierarchical taxonomy complete.")

if __name__ == "__main__":
    init_db()
