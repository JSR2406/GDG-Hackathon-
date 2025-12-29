from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from typing import List, Optional
import os
import shutil
from datetime import datetime

router = APIRouter(prefix="/lost-found", tags=["lost-found"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
def create_lost_found_item(
    user_id: int = Query(...),
    item: schemas.LostFoundCreate = None,
    db: Session = Depends(get_db)
):
    """Create a lost or found item posting"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if item.type not in ["lost", "found"]:
        raise HTTPException(status_code=400, detail="Type must be 'lost' or 'found'")
    
    return crud.create_lost_found(db, item, user_id)

@router.post("/upload")
async def upload_lost_found_photo(
    file: UploadFile = File(...)
):
    """Upload photo for lost/found item and return URL"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean filename
    clean_name = "".join(c for c in file.filename if c.isalnum() or c in "._-")
    filename = f"lostfound_{timestamp}_{clean_name}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"photo_url": f"/uploads/{filename}"}

@router.get("/")
def get_lost_found_items(
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get lost & found items with optional filters"""
    if category:
        return crud.get_lost_found_by_category(db, category)
    else:
        return crud.get_lost_found_items(db, type_filter=type)

@router.get("/{item_id}", response_model=schemas.LostFoundOut)
def get_lost_found_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific lost & found item"""
    item = db.query(crud.models.LostFound).filter(crud.models.LostFound.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
