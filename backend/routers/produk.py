from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database import SessionLocal
from models import Product, User
from routers.auth import get_db

router = APIRouter(prefix="/products", tags=["products"])

# --- SCHEMAS ---
class ProductCreate(BaseModel):
    name: str
    description: str
    price: int
    stock: int
    image_url: Optional[str] = None
    seller_username: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: int
    stock: int
    image_url: Optional[str] = None
    seller_id: int
    
    # Info tambahan (opsional, biar frontend tau siapa penjualnya)
    seller_name: Optional[str] = None

    class Config:
        from_attributes = True

# --- ENDPOINTS ---

@router.get("/", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    """Mengambil semua produk (Untuk Beranda & Admin)"""
    products = db.query(Product).all()
    
    # Isi nama seller manual
    for p in products:
        if p.seller:
            p.seller_name = p.seller.username
            
    return products

@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Tambah Produk Baru"""
    seller = db.query(User).filter(User.username == product.seller_username).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        image_url=product.image_url,
        seller_id=seller.id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/{username}", response_model=List[ProductOut])
def get_my_products(username: str, db: Session = Depends(get_db)):
    """Mengambil produk milik user tertentu (Petani)"""
    seller = db.query(User).filter(User.username == username).first()
    if not seller:
        return []
    return db.query(Product).filter(Product.seller_id == seller.id).all()

# --- FITUR BARU: EDIT & HAPUS ---

@router.put("/{product_id}")
def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)):
    """Edit Produk"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update field yang dikirim saja
    for key, value in product_data.dict(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    return {"message": "Product updated"}

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Hapus Produk"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}