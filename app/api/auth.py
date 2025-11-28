# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta

# Import các thành phần cần thiết
from app.core.security import verify_password, create_access_token, get_password_hash
from app.db.session import get_db_cursor
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter()

# --- 1. API Login ---
@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, cursor = Depends(get_db_cursor)):
    """
    API đăng nhập: Nhận username/password -> Trả về JWT Token
    """
    # A. Tìm user trong Database
    query = "SELECT * FROM edu.users WHERE username = %s"
    cursor.execute(query, (login_data.username,))
    user = cursor.fetchone()

    # B. Kiểm tra User tồn tại
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản không tồn tại hoặc sai tên đăng nhập"
        )

    # C. Kiểm tra Mật khẩu (Hash)
    if not verify_password(login_data.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu không chính xác"
        )

    # D. Kiểm tra Trạng thái tài khoản
    if user['status'] != 'Hoạt động':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này đã bị khóa hoặc chưa kích hoạt"
        )

    # E. Thành công -> Tạo Token
    access_token_expires = timedelta(minutes=60 * 24) # 24h
    access_token = create_access_token(
        subject=user['username'],
        expires_delta=access_token_expires
    )
    
    # Xóa field mật khẩu trước khi trả về
    del user['password_hash']

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

# --- 2. API Tạo người dùng mới (Register) ---
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, cursor = Depends(get_db_cursor)):
    """
    Tạo người dùng mới (Giáo viên, Học sinh, Admin)
    """
    # A. Kiểm tra trùng lặp Username
    check_query = "SELECT id FROM edu.users WHERE username = %s"
    cursor.execute(check_query, (user_in.username,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác."
        )

    # B. Mã hóa mật khẩu
    hashed_password = get_password_hash(user_in.password)

    # C. Thực hiện Insert
    insert_query = """
        INSERT INTO edu.users 
        (username, password_hash, full_name, email, phone, avatar_url, role, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, username, full_name, email, phone, avatar_url, role, status, created_at;
    """
    
    try:
        cursor.execute(insert_query, (
            user_in.username,
            hashed_password,
            user_in.full_name,
            user_in.email,
            user_in.phone,
            user_in.avatar_url,
            user_in.role,
            user_in.status
        ))
        
        new_user = cursor.fetchone()
        return new_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi hệ thống: {str(e)}"
        )