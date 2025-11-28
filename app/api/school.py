from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.db.session import get_db_cursor
from app.schemas import ClassDTO, ClassCreate, StudentDTO, StudentCreate
# 1. Import dependency bảo mật mới
from app.api.deps import get_current_user 

router = APIRouter()

# --- 1. GET: Lấy danh sách (Đã bảo mật) ---
@router.get("/school-data", response_model=List[ClassDTO])
def get_school_data(
    current_user: dict = Depends(get_current_user),
    cursor = Depends(get_db_cursor)
):
    
    sql = """
        SELECT 
            c.id as class_id,
            c.class_name,
            s.name as school_name,
            c.subject_name,
            c.start_year,
            c.end_year,
            c.status as class_status,
            COALESCE(
                json_agg(
                    json_build_object(
                        'student_id', st.id,
                        'full_name', st.full_name,
                        'date_of_birth', st.date_of_birth,
                        'email', st.email,
                        'phone_number', st.phone_number,
                        'status', st.status
                    ) 
                ) FILTER (WHERE st.id IS NOT NULL), 
                '[]'
            ) as students
        FROM edu.classes c
        JOIN edu.schools s ON c.school_id = s.id
        LEFT JOIN edu.students st ON c.id = st.class_id
        
        -- CẬP NHẬT: Lọc theo teacher_id
        WHERE c.teacher_id = %s
        
        GROUP BY c.id, s.name
        ORDER BY c.id DESC;
    """
    try:
        cursor.execute(sql, (current_user['id'],)) # Truyền ID vào WHERE
        results = cursor.fetchall()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 2. POST: Tạo lớp học (Bảo mật) ---
@router.post("/classes", response_model=ClassDTO, status_code=status.HTTP_201_CREATED)
def create_class(
    class_in: ClassCreate, 
    current_user: dict = Depends(get_current_user), # <--- Bắt buộc đăng nhập
    cursor = Depends(get_db_cursor)
):
    # 1. Tìm hoặc tạo trường học
    cursor.execute("SELECT id FROM edu.schools WHERE name = %s", (class_in.school_name,))
    school_row = cursor.fetchone()
    
    if school_row:
        school_id = school_row['id']
    else:
        cursor.execute(
            "INSERT INTO edu.schools (name) VALUES (%s) RETURNING id", 
            (class_in.school_name,)
        )
        school_id = cursor.fetchone()['id']

    # 2. Tạo lớp
    sql = """
        INSERT INTO edu.classes 
        (class_name, school_id, subject_name, grade_level, start_year, end_year, status, teacher_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, class_name, subject_name, grade_level, start_year, end_year, status as class_status
    """
    
    cursor.execute(sql, (
        class_in.class_name, 
        school_id, 
        class_in.subject_name,
        class_in.grade_level,
        class_in.start_year, 
        class_in.end_year, 
        class_in.class_status,
        current_user['id'] # <--- Lưu ID user vào cột teacher_id
    ))
    
    new_class = cursor.fetchone()
    
    return {
        **new_class,
        "class_id": new_class['id'],
        "school_name": class_in.school_name,
        "students": []
    }

# --- 3. PUT: Cập nhật lớp học (Bảo mật) ---
@router.put("/classes/{class_id}", response_model=ClassDTO)
def update_class(
    class_id: int, 
    class_in: ClassCreate, 
    current_user: dict = Depends(get_current_user), # <--- Bắt buộc đăng nhập
    cursor = Depends(get_db_cursor)
):
    # 1. Xử lý trường học
    cursor.execute("SELECT id FROM edu.schools WHERE name = %s", (class_in.school_name,))
    school_row = cursor.fetchone()
    if school_row:
        school_id = school_row['id']
    else:
        cursor.execute("INSERT INTO edu.schools (name) VALUES (%s) RETURNING id", (class_in.school_name,))
        school_id = cursor.fetchone()['id']

    # 2. Update lớp
    sql = """
        UPDATE edu.classes 
        SET class_name=%s, school_id=%s, subject_name=%s, grade_level=%s, start_year=%s, end_year=%s, status=%s
        WHERE id = %s
        RETURNING id, class_name, subject_name, grade_level, start_year, end_year, status as class_status
    """
    cursor.execute(sql, (
        class_in.class_name, school_id, class_in.subject_name,
        class_in.grade_level, class_in.start_year, class_in.end_year, class_in.class_status,
        class_id
    ))
    updated_class = cursor.fetchone()
    
    if not updated_class:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

    return {
        **updated_class,
        "class_id": updated_class['id'],
        "school_name": class_in.school_name,
        "students": []
    }

# --- 4. POST: Tạo học sinh (Bảo mật) ---
@router.post("/students", response_model=StudentDTO, status_code=status.HTTP_201_CREATED)
def create_student(
    student_in: StudentCreate, 
    current_user: dict = Depends(get_current_user), # <--- Bắt buộc đăng nhập
    cursor = Depends(get_db_cursor)
):
    sql = """
        INSERT INTO edu.students (full_name, class_id, date_of_birth, email, phone_number, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id as student_id, full_name, date_of_birth, email, phone_number, status
    """
    try:
        cursor.execute(sql, (
            student_in.full_name, student_in.class_id, student_in.date_of_birth,
            student_in.email, student_in.phone_number, student_in.status
        ))
        return cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- 5. PUT: Cập nhật học sinh (Bảo mật) ---
@router.put("/students/{student_id}", response_model=StudentDTO)
def update_student(
    student_id: int, 
    student_in: StudentCreate, 
    current_user: dict = Depends(get_current_user), # <--- Bắt buộc đăng nhập
    cursor = Depends(get_db_cursor)
):
    sql = """
        UPDATE edu.students 
        SET full_name=%s, class_id=%s, date_of_birth=%s, email=%s, phone_number=%s, status=%s
        WHERE id = %s
        RETURNING id as student_id, full_name, date_of_birth, email, phone_number, status
    """
    cursor.execute(sql, (
        student_in.full_name, student_in.class_id, student_in.date_of_birth,
        student_in.email, student_in.phone_number, student_in.status,
        student_id
    ))
    updated_student = cursor.fetchone()
    
    if not updated_student:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh")
        
    return updated_student