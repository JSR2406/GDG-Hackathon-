from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.services.gemini_agent import get_gemini_analyzer
from typing import List
import os
import shutil
from datetime import datetime

router = APIRouter(prefix="/items", tags=["items"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/users/{user_id}/items", response_model=schemas.ItemOut)
def create_item(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Create a new item for a user"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.create_item(db, item, user_id)

@router.post("/users/{user_id}/items/upload-photo")
async def upload_item_photo(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload item photo and get Gemini AI analysis"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Analyze with Gemini
    analyzer = get_gemini_analyzer()
    analysis = await analyzer.analyze_item_photo(file_path)
    
    # Create item with analysis
    item_data = schemas.ItemCreate(
        name=analysis["item_name"],
        category=analysis["category"],
        condition=analysis["condition"],
        department=analysis.get("estimated_department"),
        photo_url=f"/uploads/{filename}"
    )
    
    item = crud.create_item(db, item_data, user_id)
    
    return {
        "item": item,
        "analysis": analysis,
        "photo_url": f"/uploads/{filename}"
    }

@router.get("/users/{user_id}/items", response_model=List[schemas.ItemOut])
def get_user_items(user_id: int, db: Session = Depends(get_db)):
    """Get all items for a user"""
    return crud.get_user_items(db, user_id)

@router.get("/{item_id}", response_model=schemas.ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get item by ID"""
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
