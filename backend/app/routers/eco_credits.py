from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.database import get_db
from typing import List

router = APIRouter(prefix="/eco-credits", tags=["eco-credits"])

@router.get("/{user_id}", response_model=List[schemas.EcoCreditOut])
def get_user_eco_credits(user_id: int, db: Session = Depends(get_db)):
    """Get all eco credit transactions for a user"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    credits = db.query(models.EcoCredit).filter(models.EcoCredit.user_id == user_id).all()
    return credits

@router.get("/leaderboard/top")
def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    """Get top users by eco credits"""
    users = crud.get_all_users(db)
    
    leaderboard = []
    for user in users:
        total_credits = crud.get_user_total_eco_credits(db, user.id)
        if total_credits > 0:
            leaderboard.append({
                "rank": 0,  # Will be set after sorting
                "user_id": user.id,
                "user_name": user.name,
                "department": user.department,
                "total_eco_credits": total_credits
            })
    
    # Sort by credits descending
    leaderboard.sort(key=lambda x: x["total_eco_credits"], reverse=True)
    
    # Assign ranks
    for idx, entry in enumerate(leaderboard[:limit]):
        entry["rank"] = idx + 1
    
    return leaderboard[:limit]
