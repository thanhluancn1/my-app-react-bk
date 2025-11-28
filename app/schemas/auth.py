from pydantic import BaseModel
from .user import UserResponse # Import từ file user cùng thư mục

# Dữ liệu đăng nhập gửi lên
class LoginRequest(BaseModel):
    username: str
    password: str

# Dữ liệu Token trả về
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse