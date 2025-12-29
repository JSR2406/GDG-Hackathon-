from sqlalchemy.orm import Session
from app import models, crud
from difflib import SequenceMatcher
from typing import Dict, List, Optional
import json

def similarity_score(a: str, b: str) -> float:
    """Calculate similarity between two strings using SequenceMatcher"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def calculate_match_score(user_a: models.User, user_b: models.User, 
                         edge_a: models.BarterEdge, edge_b: models.BarterEdge,
                         is_emergency: bool = False) -> float:
    """Calculate match score based on department, semester, hostel proximity"""
    score = 0.0
    
    # Department match bonus
    if user_a.department == user_b.department:
        score += 2.0
    
    # Semester proximity bonus
    if abs(user_a.semester - user_b.semester) <= 1:
        score += 1.0
    
    # Hostel match bonus (important for emergency swaps)
    if user_a.hostel == user_b.hostel:
        score += 3.0 if is_emergency else 1.0
    
    # Emergency priority
    if edge_a.emergency or edge_b.emergency:
        score += 5.0
    
    return score

def item_matches_want(item_category: str, want_category: str) -> float:
    """Check if item category matches what user wants"""
    return similarity_score(item_category, want_category)

def find_direct_match(db: Session, user_id: int) -> Optional[Dict]:
    """Find 2-way direct swap: A has what B wants, B has what A wants"""
    
    # Get user's active barter edges
    user_edges = crud.get_user_barter_edges(db, user_id)
    if not user_edges:
        return None
    
    # Get all other active barter edges
    all_edges = crud.get_active_barter_edges(db)
    
    for my_edge in user_edges:
        my_item = crud.get_item(db, my_edge.item_id)
        my_user = crud.get_user(db, user_id)
        
        if not my_item or not my_user:
            continue
        
        for other_edge in all_edges:
            if other_edge.user_id == user_id:
                continue
            
            other_item = crud.get_item(db, other_edge.item_id)
            other_user = crud.get_user(db, other_edge.user_id)
            
            if not other_item or not other_user:
                continue
            
            # Check if mutual match exists
            i_want_their_item = item_matches_want(other_item.category, my_edge.want_category)
            they_want_my_item = item_matches_want(my_item.category, other_edge.want_category)
            
            if i_want_their_item >= 0.7 and they_want_my_item >= 0.7:
                # Calculate match quality score
                match_score = calculate_match_score(
                    my_user, other_user, my_edge, other_edge,
                    is_emergency=(my_edge.emergency or other_edge.emergency)
                )
                
                participants = [
                    {
                        "user_id": my_user.id,
                        "user_name": my_user.name,
                        "item_id": my_item.id,
                        "item_name": my_item.name,
                        "wants": my_edge.want_category
                    },
                    {
                        "user_id": other_user.id,
                        "user_name": other_user.name,
                        "item_id": other_item.id,
                        "item_name": other_item.name,
                        "wants": other_edge.want_category
                    }
                ]
                
                return {
                    "type": "direct",
                    "participants": participants,
                    "match_score": match_score,
                    "explanation": f"Perfect 2-way match found! {my_user.name} and {other_user.name} have what each other wants.",
                    "flow": f"{my_user.name} ({my_item.name}) ↔ {other_user.name} ({other_item.name})"
                }
    
    return None

def find_three_way_cycle(db: Session, user_id: int) -> Optional[Dict]:
    """Find 3-way cycle: A→B→C→A where each has what the next wants"""
    
    user_edges = crud.get_user_barter_edges(db, user_id)
    if not user_edges:
        return None
    
    all_edges = crud.get_active_barter_edges(db)
    
    for edge_a in user_edges:
        item_a = crud.get_item(db, edge_a.item_id)
        user_a = crud.get_user(db, user_id)
        
        if not item_a or not user_a:
            continue
        
        # Find B: someone who has what A wants
        for edge_b in all_edges:
            if edge_b.user_id == user_id:
                continue
            
            item_b = crud.get_item(db, edge_b.item_id)
            user_b = crud.get_user(db, edge_b.user_id)
            
            if not item_b or not user_b:
                continue
            
            # Check if B has what A wants
            if item_matches_want(item_b.category, edge_a.want_category) < 0.7:
                continue
            
            # Find C: someone who has what B wants
            for edge_c in all_edges:
                if edge_c.user_id in [user_id, edge_b.user_id]:
                    continue
                
                item_c = crud.get_item(db, edge_c.item_id)
                user_c = crud.get_user(db, edge_c.user_id)
                
                if not item_c or not user_c:
                    continue
                
                # Check if C has what B wants AND C wants what A has
                b_wants_c = item_matches_want(item_c.category, edge_b.want_category)
                c_wants_a = item_matches_want(item_a.category, edge_c.want_category)
                
                if b_wants_c >= 0.7 and c_wants_a >= 0.7:
                    # Found a 3-way cycle!
                    participants = [
                        {
                            "user_id": user_a.id,
                            "user_name": user_a.name,
                            "item_id": item_a.id,
                            "item_name": item_a.name,
                            "wants": edge_a.want_category
                        },
                        {
                            "user_id": user_b.id,
                            "user_name": user_b.name,
                            "item_id": item_b.id,
                            "item_name": item_b.name,
                            "wants": edge_b.want_category
                        },
                        {
                            "user_id": user_c.id,
                            "user_name": user_c.name,
                            "item_id": item_c.id,
                            "item_name": item_c.name,
                            "wants": edge_c.want_category
                        }
                    ]
                    
                    return {
                        "type": "three_way",
                        "participants": participants,
                        "explanation": f"Amazing 3-way circular swap detected! {user_a.name}, {user_b.name}, and {user_c.name} form a perfect cycle.",
                        "flow": f"{user_a.name} ({item_a.name}) → {user_b.name} ({item_b.name}) → {user_c.name} ({item_c.name}) → {user_a.name}"
                    }
    
    return None

def run_matching(db: Session, user_id: int) -> Optional[Dict]:
    """
    Orchestrate matching: try direct match first, then 3-way cycle
    Returns match details or None if no match found
    """
    
    # Try direct match first (faster and simpler)
    direct_match = find_direct_match(db, user_id)
    if direct_match:
        return direct_match
    
    # Try 3-way cycle if no direct match
    three_way_match = find_three_way_cycle(db, user_id)
    if three_way_match:
        return three_way_match
    
    return None
