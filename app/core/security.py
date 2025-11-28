# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt # Thư viện xử lý JWT
from passlib.context import CryptContext # Thư viện xử lý Hash mật khẩu
from app.core.config import settings

# Cấu hình thuật toán Hash (dùng bcrypt rất mạnh)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256" # Thuật toán ký Token

# --- 1. Hàm xử lý Mật khẩu ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra mật khẩu nhập vào (plain) có khớp với hash trong DB không.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Tạo hash từ mật khẩu thô (Dùng khi tạo User mới).
    """
    return pwd_context.hash(password)

# --- 2. Hàm tạo Token (JWT) ---

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Tạo chuỗi Access Token chứa thông tin user (subject) và thời gian hết hạn.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Mặc định token sống 60 phút nếu không quy định
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    
    # Payload: Nội dung bên trong token
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Ký token bằng SECRET_KEY trong file .env
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt