from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    semester: int = Field(ge=1, le=8)
    department: str
    hostel: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    semester: int
    department: str
    hostel: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Item Schemas
class ItemCreate(BaseModel):
    name: str
    category: str
    condition: str
    department: Optional[str] = None
    photo_url: Optional[str] = None

class ItemOut(BaseModel):
    id: int
    owner_id: int
    name: str
    category: str
    condition: str
    department: Optional[str]
    photo_url: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Barter Intent Schemas
class BarterIntentCreate(BaseModel):
    item_id: int
    want_category: str
    want_description: Optional[str] = None
    emergency: bool = False

class BarterIntentOut(BaseModel):
    id: int
    user_id: int
    item_id: int
    want_category: str
    want_description: Optional[str]
    emergency: bool
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Match Schemas
class MatchParticipant(BaseModel):
    user_id: int
    user_name: str
    item_id: int
    item_name: str
    wants: str

class MatchOut(BaseModel):
    id: int
    type: str
    participants: List[MatchParticipant]
    status: str
    created_at: datetime
    explanation: Optional[str] = None
    flow: Optional[str] = None
    
    class Config:
        from_attributes = True

# Lost & Found Schemas
class LostFoundCreate(BaseModel):
    item_name: str
    category: str
    description: Optional[str] = None
    type: str  # lost or found
    photo_url: Optional[str] = None

class LostFoundOut(BaseModel):
    id: int
    user_id: int
    item_name: str
    category: str
    description: Optional[str]
    type: str
    photo_url: Optional[str]
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Eco Credit Schemas
class EcoCreditOut(BaseModel):
    id: int
    user_id: int
    amount: int
    reason: str
    match_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserStatsOut(BaseModel):
    user_id: int
    user_name: str
    total_eco_credits: int
    total_swaps: int
    active_items: int
    pending_matches: int
    
    class Config:
        from_attributes = True

# Gemini Analysis Response
class GeminiAnalysisResponse(BaseModel):
    item_name: str
    category: str
    condition: str
    estimated_department: Optional[str]
    description: str
    suggested_wants: List[str]
    eco_value: int
    confidence: float
    reusability_score: int
