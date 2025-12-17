from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from database import SessionLocal
from models import Blog, User
from routers.auth import get_db

router = APIRouter(prefix="/blogs", tags=["blogs"])

# --- SCHEMA ---
class BlogCreate(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None
    author_username: str

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None

class BlogOut(BaseModel):
    id: int
    title: str
    content: str
    image_url: Optional[str] = None
    author_username: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- ENDPOINTS ---

@router.get("/", response_model=List[BlogOut])
def get_blogs(db: Session = Depends(get_db)):
    """Ambil semua artikel (terbaru di atas)"""
    return db.query(Blog).order_by(Blog.created_at.desc()).all()

@router.post("/", response_model=BlogOut)
def create_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    """Admin membuat artikel baru"""
    # Cek apakah user admin? (Sederhana: kita percaya frontend kirim role yg benar, 
    # idealnya cek di DB tapi ini cukup untuk MVP)
    
    new_blog = Blog(
        title=blog.title,
        content=blog.content,
        image_url=blog.image_url,
        author_username=blog.author_username
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@router.put("/{blog_id}")
def update_blog(blog_id: int, blog_data: BlogUpdate, db: Session = Depends(get_db)):
    """Edit artikel"""
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")
    
    for key, value in blog_data.dict(exclude_unset=True).items():
        setattr(blog, key, value)
    
    db.commit()
    return {"message": "Artikel berhasil diupdate"}

@router.delete("/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    """Hapus artikel"""
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")
    
    db.delete(blog)
    db.commit()
    return {"message": "Artikel berhasil dihapus"}