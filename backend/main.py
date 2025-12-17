from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import auth, produk  
from routers import auth, produk, pesanan
from routers import auth, produk, pesanan, users
from routers import auth, produk, pesanan, users, admin
from routers import auth, produk, pesanan, users, admin, blog
from routers import auth, produk, pesanan, users, admin, blog, harga


# Membuat tabel di database otomatis
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Izinkan akses dari frontend (Live Server)
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:3000" # Tambahan umum
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Daftarkan Router
app.include_router(auth.router)
app.include_router(produk.router) 
app.include_router(pesanan.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(blog.router)
app.include_router(harga.router)

@app.get("/")
def read_root():
    return {"message": "NBB Coffee Hub Backend is running"}