from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)
    is_verified = Column(Boolean, default=True)

    # --- TAMBAHAN DATA PROFIL ---
    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    kecamatan = Column(String, nullable=True)
    city = Column(String, nullable=True)
    province = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)

    # --- KHUSUS PETANI ---
    shop_name = Column(String, nullable=True) # Nama Toko/Kebun
    farm_area = Column(String, nullable=True) # Luas Lahan
    coffee_types = Column(String, nullable=True) # Jenis Kopi
    description = Column(Text, nullable=True) # Deskripsi Kebun

    # Relasi
    products = relationship("Product", back_populates="seller")
    orders = relationship("Order", back_populates="buyer")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Integer)
    stock = Column(Integer)
    image_url = Column(String, nullable=True)
    seller_id = Column(Integer, ForeignKey("users.id"))
    
    seller = relationship("User", back_populates="products")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Integer)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    buyer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price_at_purchase = Column(Integer)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    
class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    image_url = Column(String, nullable=True)
    author_username = Column(String) # Admin yang nulis
    created_at = Column(DateTime, default=datetime.utcnow)


class CoffeePrice(Base):
    __tablename__ = "coffee_prices"

    id = Column(Integer, primary_key=True, index=True)
    coffee_type = Column(String, index=True) # Contoh: Arabika, Robusta
    price = Column(Integer) # Harga per kg
    description = Column(String, nullable=True) # Keterangan (misal: "Naik 2%")
    updated_at = Column(DateTime, default=datetime.utcnow)