from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(
    prefix="/api/categories",
    tags=["categories"]
)

@router.get("", response_model=List[schemas.CategoryBase])
def get_categories(db: Session = Depends(get_db)):
    # Fetch all categories as a flat list, let frontend group by parent_id
    categories = db.query(models.Category).all()
    return categories
