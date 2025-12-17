from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import SessionLocal
from models import Order, OrderItem, Product, User
from routers.auth import get_db

router = APIRouter(prefix="/orders", tags=["orders"])

# --- SCHEMA ---
class CartItem(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    buyer_username: str
    items: List[CartItem]

class ProductMinimal(BaseModel):
    name: str
    image_url: Optional[str] = None
    class Config:
        from_attributes = True

class OrderItemOut(BaseModel):
    product: ProductMinimal
    quantity: int
    price_at_purchase: int
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    total_price: int
    status: str
    created_at: datetime
    items: List[OrderItemOut]
    buyer_id: int 
    buyer_name: Optional[str] = None 

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str

# --- ENDPOINTS ---

@router.post("/")
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # 1. Cek Pembeli
    buyer = db.query(User).filter(User.username == order_data.buyer_username).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="User pembeli tidak ditemukan")

    if not order_data.items:
        raise HTTPException(status_code=400, detail="Keranjang belanja kosong!")

    # 2. Buat Pesanan (Draft)
    new_order = Order(buyer_id=buyer.id, status="Pending", total_price=0)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    total_price = 0
    items_created = 0

    # 3. Masukkan Barang
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        # PERBAIKAN: Error jika produk tidak ada (jangan di-skip)
        if not product:
            db.delete(new_order) # Batalkan order
            db.commit()
            raise HTTPException(status_code=404, detail=f"Produk dengan ID {item.product_id} tidak ditemukan. Mohon hapus keranjang dan belanja ulang.")
        
        # PERBAIKAN: Error jika stok kurang
        if product.stock < item.quantity:
            db.delete(new_order) # Batalkan order
            db.commit()
            raise HTTPException(status_code=400, detail=f"Stok '{product.name}' tidak mencukupi (Sisa: {product.stock})")

        # Kurangi Stok
        product.stock -= item.quantity
        
        # Hitung Subtotal
        subtotal = product.price * item.quantity
        total_price += subtotal

        # Simpan Item
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price_at_purchase=product.price
        )
        db.add(order_item)
        items_created += 1

    # 4. Finalisasi Pesanan
    if items_created == 0:
        db.delete(new_order)
        db.commit()
        raise HTTPException(status_code=400, detail="Gagal membuat pesanan: Tidak ada barang valid.")

    new_order.total_price = total_price
    db.commit()

    return {"message": "Transaksi Berhasil", "order_id": new_order.id}

@router.get("/my-orders/{username}", response_model=List[OrderOut])
def get_my_orders(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user: return []
    return db.query(Order).filter(Order.buyer_id == user.id).order_by(Order.created_at.desc()).all()

@router.get("/incoming/{seller_username}", response_model=List[OrderOut])
def get_incoming_orders(seller_username: str, db: Session = Depends(get_db)):
    """Mengambil pesanan masuk khusus untuk petani tersebut"""
    seller = db.query(User).filter(User.username == seller_username).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    # Ambil order yang memiliki item dari produk seller ini
    orders = (
        db.query(Order)
        .join(OrderItem)
        .join(Product)
        .filter(Product.seller_id == seller.id)
        .distinct()
        .order_by(Order.created_at.desc())
        .all()
    )
    
    # Isi nama pembeli
    for o in orders:
        if o.buyer:
            o.buyer_name = o.buyer.username
            
    return orders

@router.put("/{order_id}/status")
def update_status(order_id: int, status_data: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status_data.status
    db.commit()
    return {"message": "Status updated"}