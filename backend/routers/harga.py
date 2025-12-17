from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import SessionLocal
from models import CoffeePrice
from routers.auth import get_db

router = APIRouter(prefix="/prices", tags=["prices"])

# --- SCHEMA ---
class PriceCreate(BaseModel):
    coffee_type: str
    price: int
    description: Optional[str] = None

class PriceOut(BaseModel):
    id: int
    coffee_type: str
    price: int
    description: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True

# --- ENDPOINTS ---

@router.get("/", response_model=List[PriceOut])
def get_prices(db: Session = Depends(get_db)):
    """Ambil daftar harga pasar terbaru"""
    return db.query(CoffeePrice).order_by(CoffeePrice.updated_at.desc()).all()

@router.post("/", response_model=PriceOut)
def update_price(price_data: PriceCreate, db: Session = Depends(get_db)):
    """Admin update/tambah harga baru"""
    # Cek apakah jenis kopi ini sudah ada datanya?
    existing_price = db.query(CoffeePrice).filter(CoffeePrice.coffee_type == price_data.coffee_type).first()
    
    if existing_price:
        # Update yang sudah ada
        existing_price.price = price_data.price
        existing_price.description = price_data.description
        existing_price.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_price)
        return existing_price
    else:
        # Buat baru
        new_price = CoffeePrice(
            coffee_type=price_data.coffee_type,
            price=price_data.price,
            description=price_data.description
        )
        db.add(new_price)
        db.commit()
        db.refresh(new_price)
        return new_price

@router.delete("/{price_id}")
def delete_price(price_id: int, db: Session = Depends(get_db)):
    price = db.query(CoffeePrice).filter(CoffeePrice.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    
    db.delete(price)
    db.commit()
    return {"message": "Data harga dihapus"}