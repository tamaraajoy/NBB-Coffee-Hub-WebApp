from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal
from models import User
from routers.auth import get_db

router = APIRouter(prefix="/users", tags=["users"])

# --- SCHEMA INPUT/OUTPUT ---
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    kecamatan: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    profile_image_url: Optional[str] = None
    
    # Khusus Petani
    shop_name: Optional[str] = None
    farm_area: Optional[str] = None
    coffee_types: Optional[str] = None
    description: Optional[str] = None

class UserProfileOut(BaseModel):
    username: str
    email: str
    role: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    kecamatan: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    profile_image_url: Optional[str] = None
    shop_name: Optional[str] = None
    farm_area: Optional[str] = None
    coffee_types: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

# --- ENDPOINTS ---

@router.get("/{username}", response_model=UserProfileOut)
def get_user_profile(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{username}", response_model=UserProfileOut)
def update_user_profile(username: str, profile_data: UserProfileUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update field satu per satu jika ada datanya
    for key, value in profile_data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user