from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Dữ liệu tạo người dùng mới (Register)
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "học sinh"
    status: str = "Hoạt động"

# Dữ liệu người dùng trả về (Output)
class UserResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    status: str
    created_at: datetime