from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from typing import List
import json

router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/{user_id}")
def get_user_matches(user_id: int, db: Session = Depends(get_db)):
    """Get all matches for a user"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    matches = crud.get_user_matches(db, user_id)
    
    # Format matches with parsed JSON
    formatted_matches = []
    for match in matches:
        formatted_matches.append({
            "id": match.id,
            "type": match.type,
            "participants": json.loads(match.participants),
            "status": match.status,
            "created_at": match.created_at,
            "accepted_by": json.loads(match.accepted_by) if match.accepted_by else []
        })
    
    return formatted_matches

@router.post("/{match_id}/accept")
def accept_match(match_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Accept a match and award eco credits if all participants accept"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    match = crud.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Verify user is part of this match
    participants = json.loads(match.participants)
    participant_ids = [p["user_id"] for p in participants]
    
    if user_id not in participant_ids:
        raise HTTPException(status_code=403, detail="User is not part of this match")
    
    # Accept the match
    updated_match = crud.accept_match(db, match_id, user_id)
    
    return {
        "match_id": match_id,
        "status": updated_match.status,
        "accepted_by": json.loads(updated_match.accepted_by),
        "message": "Match completed! Eco-credits awarded." if updated_match.status == "completed" else "Match accepted. Waiting for other participants."
    }
