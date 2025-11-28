# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import school, auth  # <--- Import thêm auth
from app.api import school, auth, knowledge

app = FastAPI(title=settings.PROJECT_NAME)

# --- Cấu hình CORS ---
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to AronEdu API"}

# --- Đăng ký các Router ---

# 1. Router Authentication (Login, Register)
app.include_router(
    auth.router, 
    prefix=settings.API_V1_STR, 
    tags=["Auth"]
)

# 2. Router School (Classes, Students)
app.include_router(
    school.router, 
    prefix=settings.API_V1_STR, 
    tags=["School"]
)

app.include_router(knowledge.router, prefix=settings.API_V1_STR, tags=["Knowledge"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)