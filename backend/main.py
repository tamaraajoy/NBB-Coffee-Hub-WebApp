from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "NBB Coffee Hub Backend is running"}
