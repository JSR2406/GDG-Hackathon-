from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    semester = Column(Integer, nullable=False)
    department = Column(String(100), nullable=False)
    hostel = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    items = relationship("Item", back_populates="owner")
    barter_edges = relationship("BarterEdge", back_populates="user")
    matches = relationship("Match", back_populates="user")
    lost_found_items = relationship("LostFound", back_populates="user")
    eco_credits = relationship("EcoCredit", back_populates="user")


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    condition = Column(String(50), nullable=False)
    department = Column(String(100))
    photo_url = Column(String(500))
    status = Column(String(50), default="available")  # available, in_swap, swapped
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="items")
    barter_edges = relationship("BarterEdge", back_populates="item")


class BarterEdge(Base):
    __tablename__ = "barter_edges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    want_category = Column(String(100), nullable=False)
    want_description = Column(Text)
    emergency = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="barter_edges")
    item = relationship("Item", back_populates="barter_edges")


class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)  # direct, three_way
    participants = Column(Text, nullable=False)  # JSON string
    status = Column(String(50), default="pending")  # pending, accepted, completed, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_by = Column(Text)  # JSON array of user IDs who accepted
    
    # Relationships
    user = relationship("User", back_populates="matches")


class LostFound(Base):
    __tablename__ = "lost_found"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    type = Column(String(10), nullable=False)  # lost, found
    photo_url = Column(String(500))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="lost_found_items")


class EcoCredit(Base):
    __tablename__ = "eco_credits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    reason = Column(String(200), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="eco_credits")
