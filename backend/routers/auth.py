from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

from database import SessionLocal
from models import User

# ---------- KONFIGURASI ----------
SECRET_KEY = "ganti_dengan_secret_key_yang_kuat"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter()

# ---------- SCHEMA ----------
class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str  # Tambahan agar frontend tahu role user

# ---------- DB Session ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- UTIL ----------
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---------- ENDPOINTS ----------
@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau Password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # --- BAGIAN PENGECEKAN EMAIL KITA HAPUS SEMENTARA AGAR BISA LOGIN ---
    # if not db_user.is_verified:
    #     raise HTTPException(status_code=403, detail="Email belum diverifikasi")
    
    # Masukkan role ke dalam token agar bisa dibaca frontend (opsional)
    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role}
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": db_user.role}

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Cek username/email kembar
    if db.query(User).filter((User.username == user.username) | (User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="Email atau Username sudah terdaftar")

    hashed_pw = get_password_hash(user.password)
    
    # Kita set is_verified langsung jadi True saat daftar
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pw,
        role=user.role,
        is_verified=True 
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "Pendaftaran Berhasil! Silakan Login."}