from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.services.matching_engine import run_matching
from typing import List
import json

router = APIRouter(prefix="/barter", tags=["barter"])

@router.post("/barter-intents", response_model=dict)
def create_barter_intent(
    user_id: int = Query(...),
    intent: schemas.BarterIntentCreate = None,
    db: Session = Depends(get_db)
):
    """Create a barter intent and trigger matching"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify item exists and belongs to user
    item = crud.get_item(db, intent.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Item does not belong to user")
    
    # Create barter edge
    barter_edge = crud.create_barter_edge(db, intent, user_id)
    
    # Run matching algorithm
    match_result = run_matching(db, user_id)
    
    if match_result:
        # Create match in database
        match = crud.create_match(
            db=db,
            user_id=user_id,
            match_type=match_result["type"],
            participants=match_result["participants"]
        )
        
        return {
            "barter_intent": schemas.BarterIntentOut.model_validate(barter_edge),
            "match_found": True,
            "match": {
                "id": match.id,
                "type": match_result["type"],
                "participants": match_result["participants"],
                "explanation": match_result.get("explanation"),
                "flow": match_result.get("flow")
            }
        }
    else:
        return {
            "barter_intent": schemas.BarterIntentOut.model_validate(barter_edge),
            "match_found": False,
            "message": "No matches found yet. We'll notify you when a match is available!"
        }

@router.get("/barter-intents/{user_id}", response_model=List[schemas.BarterIntentOut])
def get_user_barter_intents(user_id: int, db: Session = Depends(get_db)):
    """Get all barter intents for a user"""
    return crud.get_user_barter_edges(db, user_id)
