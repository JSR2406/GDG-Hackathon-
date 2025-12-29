from sqlalchemy.orm import Session
from app import models, schemas
import json
from typing import List, Optional
from datetime import datetime

# ==================== USER CRUD ====================
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# ==================== ITEM CRUD ====================
def create_item(db: Session, item: schemas.ItemCreate, owner_id: int):
    db_item = models.Item(**item.model_dump(), owner_id=owner_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def get_user_items(db: Session, user_id: int):
    return db.query(models.Item).filter(models.Item.owner_id == user_id).all()

def update_item_status(db: Session, item_id: int, status: str):
    db_item = get_item(db, item_id)
    if db_item:
        db_item.status = status
        db.commit()
        db.refresh(db_item)
    return db_item

# ==================== BARTER EDGE CRUD ====================
def create_barter_edge(db: Session, barter: schemas.BarterIntentCreate, user_id: int):
    db_barter = models.BarterEdge(**barter.model_dump(), user_id=user_id)
    db.add(db_barter)
    db.commit()
    db.refresh(db_barter)
    return db_barter

def get_active_barter_edges(db: Session):
    return db.query(models.BarterEdge).filter(models.BarterEdge.active == True).all()

def get_user_barter_edges(db: Session, user_id: int):
    return db.query(models.BarterEdge).filter(
        models.BarterEdge.user_id == user_id,
        models.BarterEdge.active == True
    ).all()

def deactivate_barter_edge(db: Session, edge_id: int):
    db_edge = db.query(models.BarterEdge).filter(models.BarterEdge.id == edge_id).first()
    if db_edge:
        db_edge.active = False
        db.commit()
        db.refresh(db_edge)
    return db_edge

# ==================== MATCH CRUD ====================
def create_match(db: Session, user_id: int, match_type: str, participants: List[dict]):
    """Create a new match with participants as JSON"""
    db_match = models.Match(
        user_id=user_id,
        type=match_type,
        participants=json.dumps(participants),
        status="pending",
        accepted_by=json.dumps([])
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def get_match(db: Session, match_id: int):
    return db.query(models.Match).filter(models.Match.id == match_id).first()

def get_user_matches(db: Session, user_id: int):
    return db.query(models.Match).filter(models.Match.user_id == user_id).all()

def accept_match(db: Session, match_id: int, user_id: int):
    """Accept a match and award eco credits if all participants accepted"""
    db_match = get_match(db, match_id)
    if not db_match:
        return None
    
    # Parse accepted_by list
    accepted_by = json.loads(db_match.accepted_by) if db_match.accepted_by else []
    
    # Add user if not already accepted
    if user_id not in accepted_by:
        accepted_by.append(user_id)
        db_match.accepted_by = json.dumps(accepted_by)
    
    # Check if all participants have accepted
    participants = json.loads(db_match.participants)
    all_user_ids = [p['user_id'] for p in participants]
    
    if set(accepted_by) == set(all_user_ids):
        db_match.status = "completed"
        
        # Award eco credits to all participants
        for participant in participants:
            award_eco_credit(
                db=db,
                user_id=participant['user_id'],
                amount=10,
                reason=f"Completed {db_match.type} swap",
                match_id=match_id
            )
        
        # Update item statuses
        for participant in participants:
            update_item_status(db, participant['item_id'], "swapped")
    
    db.commit()
    db.refresh(db_match)
    return db_match

# ==================== LOST & FOUND CRUD ====================
def create_lost_found(db: Session, lost_found: schemas.LostFoundCreate, user_id: int):
    db_lost_found = models.LostFound(**lost_found.model_dump(), user_id=user_id)
    db.add(db_lost_found)
    db.commit()
    db.refresh(db_lost_found)
    return db_lost_found

def get_lost_found_items(db: Session, type_filter: Optional[str] = None):
    query = db.query(models.LostFound).filter(models.LostFound.active == True)
    if type_filter:
        query = query.filter(models.LostFound.type == type_filter)
    return query.all()

def get_lost_found_by_category(db: Session, category: str):
    return db.query(models.LostFound).filter(
        models.LostFound.category == category,
        models.LostFound.active == True
    ).all()

# ==================== ECO CREDIT CRUD ====================
def award_eco_credit(db: Session, user_id: int, amount: int, reason: str, match_id: Optional[int] = None):
    """Award eco credits to a user"""
    db_credit = models.EcoCredit(
        user_id=user_id,
        amount=amount,
        reason=reason,
        match_id=match_id
    )
    db.add(db_credit)
    db.commit()
    db.refresh(db_credit)
    return db_credit

def get_user_total_eco_credits(db: Session, user_id: int) -> int:
    """Get total eco credits for a user"""
    credits = db.query(models.EcoCredit).filter(models.EcoCredit.user_id == user_id).all()
    return sum(credit.amount for credit in credits)

def get_user_stats(db: Session, user_id: int):
    """Get comprehensive user statistics"""
    user = get_user(db, user_id)
    if not user:
        return None
    
    total_credits = get_user_total_eco_credits(db, user_id)
    total_swaps = db.query(models.Match).filter(
        models.Match.user_id == user_id,
        models.Match.status == "completed"
    ).count()
    active_items = db.query(models.Item).filter(
        models.Item.owner_id == user_id,
        models.Item.status == "available"
    ).count()
    pending_matches = db.query(models.Match).filter(
        models.Match.user_id == user_id,
        models.Match.status == "pending"
    ).count()
    
    return {
        "user_id": user_id,
        "user_name": user.name,
        "total_eco_credits": total_credits,
        "total_swaps": total_swaps,
        "active_items": active_items,
        "pending_matches": pending_matches
    }
