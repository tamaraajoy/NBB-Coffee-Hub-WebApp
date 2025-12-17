from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import User, Product, Order
from routers.auth import get_db

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
def get_admin_stats(db: Session = Depends(get_db)):
    """Menghitung ringkasan data untuk Dashboard Admin"""
    
    # Hitung total user
    total_users = db.query(User).count()
    
    # Hitung total petani
    total_petani = db.query(User).filter(User.role == "petani").count()
    
    # Hitung total produk
    total_products = db.query(Product).count()
    
    # Hitung total stok (Sum kolom stock)
    total_stock = db.query(func.sum(Product.stock)).scalar() or 0
    
    # Hitung total pesanan
    total_orders = db.query(Order).count()
    
    # Hitung estimasi pendapatan (Total harga semua order)
    total_revenue = db.query(func.sum(Order.total_price)).scalar() or 0

    return {
        "total_users": total_users,
        "total_petani": total_petani,
        "total_products": total_products,
        "total_stock": total_stock,
        "total_orders": total_orders,
        "total_revenue": total_revenue
    }