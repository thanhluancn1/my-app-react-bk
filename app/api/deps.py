from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.session import get_db_cursor

# 1. Cấu hình OAuth2
# tokenUrl: Đường dẫn API Login để Swagger UI biết nơi lấy token
# (Giúp nút "Authorize" màu xanh trong docs hoạt động)
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login"
)

# 2. Hàm Dependency chính: Lấy User hiện tại từ Token
def get_current_user(
    token: str = Depends(reusable_oauth2),
    cursor = Depends(get_db_cursor)
) -> dict:
    """
    Hàm này sẽ tự động:
    1. Nhận token từ Header Authorization (Bearer ...)
    2. Giải mã Token để lấy username (sub)
    3. Truy vấn Database để tìm User
    4. Trả về object User nếu hợp lệ, hoặc báo lỗi nếu không
    """
    
    # A. Giải mã Token
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ (thiếu thông tin định danh)",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Không thể xác thực token (Token hết hạn hoặc sai)",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # B. Tìm User trong Database
    try:
        # Query tìm user
        query = "SELECT * FROM edu.users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        # Kiểm tra tồn tại
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Người dùng không tồn tại",
            )
            
        # Kiểm tra trạng thái (Nếu bị khóa thì chặn luôn)
        if user['status'] != 'Hoạt động':
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản này đang bị khóa hoặc không hoạt động"
            )
            
        # C. Trả về User (để các API khác dùng)
        return user
        
    except Exception as e:
        # Nếu lỗi này không phải HTTP Exception đã raise ở trên
        if not isinstance(e, HTTPException):
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi xác thực Database: {str(e)}"
            )
        raise e