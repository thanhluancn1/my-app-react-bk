from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.db.session import get_db_cursor
from app.schemas.school import ClassDTO, ClassCreate, StudentDTO, StudentCreate
from app.api.deps import get_current_user 
from typing import List
from app.schemas.school import ClassWithLessonsDTO

router = APIRouter()

# --- 1. GET: Lấy danh sách ---
@router.get("/school-data", response_model=List[ClassDTO])
def get_school_data(
    current_user: dict = Depends(get_current_user),
    cursor = Depends(get_db_cursor)
):
    sql = """
        SELECT 
            c.class_id,
            c.class_name,
            s.name as school_name,
            c.subject_name,
            c.grade_level,
            c.teacher_id,
            c.start_year,
            c.end_year,
            c.status as class_status,
            COALESCE(
                json_agg(
                    json_build_object(
                        'student_id', st.student_id,
                        'full_name', st.full_name,
                        'date_of_birth', st.date_of_birth,
                        'email', st.email,
                        'phone_number', st.phone_number,
                        'status', st.status
                    ) 
                ) FILTER (WHERE st.student_id IS NOT NULL), 
                '[]'
            ) as students
        FROM edu.classes c
        JOIN edu.schools s ON c.school_id = s.school_id
        LEFT JOIN edu.students st ON c.class_id = st.class_id
        
        -- Lọc theo teacher_id (người dùng hiện tại)
        WHERE c.teacher_id = %s
        
        GROUP BY c.class_id, s.name
        ORDER BY c.class_id DESC;
    """
    try:
        cursor.execute(sql, (current_user['user_id'],)) 
        results = cursor.fetchall()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 2. POST: Tạo lớp học ---
@router.post("/classes", response_model=ClassDTO, status_code=status.HTTP_201_CREATED)
def create_class(
    class_in: ClassCreate, 
    current_user: dict = Depends(get_current_user), 
    cursor = Depends(get_db_cursor)
):
    # 1. Tìm hoặc tạo trường học
    cursor.execute("SELECT school_id FROM edu.schools WHERE name = %s", (class_in.school_name,))
    school_row = cursor.fetchone()
    
    if school_row:
        school_id = school_row['school_id']
    else:
        cursor.execute(
            "INSERT INTO edu.schools (name) VALUES (%s) RETURNING school_id", 
            (class_in.school_name,)
        )
        school_id = cursor.fetchone()['school_id']

    # 2. Tạo Lớp (Thêm grade_level và teacher_id)
    sql = """
        INSERT INTO edu.classes 
        (class_name, school_id, subject_name, grade_level, start_year, end_year, status, teacher_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING class_id, class_name, subject_name, grade_level, start_year, end_year, status as class_status, teacher_id
    """
    
    cursor.execute(sql, (
        class_in.class_name, 
        school_id, 
        class_in.subject_name,
        class_in.grade_level,
        class_in.start_year, 
        class_in.end_year, 
        class_in.class_status,
        current_user['user_id']
    ))
    
    new_class = cursor.fetchone()
    
    return {
        **new_class,
        "school_name": class_in.school_name,
        "students": []
    }

# --- 3. PUT: Cập nhật lớp học ---
@router.put("/classes/{class_id}", response_model=ClassDTO)
def update_class(
    class_id: int, 
    class_in: ClassCreate, 
    current_user: dict = Depends(get_current_user), 
    cursor = Depends(get_db_cursor)
):
    # 1. Xử lý trường học
    cursor.execute("SELECT school_id FROM edu.schools WHERE name = %s", (class_in.school_name,))
    school_row = cursor.fetchone()
    if school_row:
        school_id = school_row['school_id']
    else:
        cursor.execute("INSERT INTO edu.schools (name) VALUES (%s) RETURNING school_id", (class_in.school_name,))
        school_id = cursor.fetchone()['school_id']

    # 2. Update lớp (Thêm grade_level)
    sql = """
        UPDATE edu.classes 
        SET class_name=%s, school_id=%s, subject_name=%s, grade_level=%s, start_year=%s, end_year=%s, status=%s
        WHERE class_id = %s
        RETURNING class_id, class_name, subject_name, grade_level, start_year, end_year, status as class_status, teacher_id
    """
    cursor.execute(sql, (
        class_in.class_name, school_id, class_in.subject_name, class_in.grade_level,
        class_in.start_year, class_in.end_year, class_in.class_status,
        class_id
    ))
    updated_class = cursor.fetchone()
    
    if not updated_class:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")

    return {
        **updated_class,
        "school_name": class_in.school_name,
        "students": [] 
    }

# --- 4. POST: Tạo học sinh ---
@router.post("/students", response_model=StudentDTO, status_code=status.HTTP_201_CREATED)
def create_student(student_in: StudentCreate, cursor = Depends(get_db_cursor)):
    sql = """
        INSERT INTO edu.students (full_name, class_id, date_of_birth, email, phone_number, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING student_id, full_name, date_of_birth, email, phone_number, status
    """
    try:
        cursor.execute(sql, (
            student_in.full_name, student_in.class_id, student_in.date_of_birth,
            student_in.email, student_in.phone_number, student_in.status
        ))
        return cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- 5. PUT: Cập nhật học sinh ---
@router.put("/students/{student_id}", response_model=StudentDTO)
def update_student(student_id: int, student_in: StudentCreate, cursor = Depends(get_db_cursor)):
    sql = """
        UPDATE edu.students 
        SET full_name=%s, class_id=%s, date_of_birth=%s, email=%s, phone_number=%s, status=%s
        WHERE student_id = %s
        RETURNING student_id, full_name, date_of_birth, email, phone_number, status
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

@router.get("/teacher/classes-lessons", response_model=List[ClassWithLessonsDTO])
def get_teacher_classes_with_lessons(
    current_user: dict = Depends(get_current_user),
    cursor = Depends(get_db_cursor)
):
    """
    Lấy danh sách các lớp mà giáo viên đang dạy.
    Với mỗi lớp, tự động tìm ra danh sách bài học tương ứng dựa trên Khối (Grade) và Môn (Subject).
    """
    
    # Logic JOIN phức tạp:
    # 1. Lấy các lớp do giáo viên này dạy (c.teacher_id = user_id)
    # 2. JOIN sang bảng GradeLevels dựa trên c.grade_level (VD: số 10)
    # 3. JOIN sang bảng Subjects dựa trên GradeLevels.id VÀ c.subject_name (VD: "Toán")
    # 4. Từ Subject -> Books -> Chapters -> Lessons để lấy danh sách bài
    
    sql = """
        SELECT 
            c.class_id,
            c.class_name,
            s.name as school_name,
            c.subject_name,
            c.grade_level,
            
            -- Gom nhóm danh sách bài học thành JSON
            COALESCE(
                json_agg(
                    json_build_object(
                        'lesson_id', l.lesson_id,
                        'lesson_name', l.lesson_name,
                        'chapter_name', ch.chapter_name
                    ) ORDER BY l.order_number
                ) FILTER (WHERE l.lesson_id IS NOT NULL), 
                '[]'
            ) as lessons
            
        FROM edu.classes c
        JOIN edu.schools s ON c.school_id = s.school_id
        
        -- Cầu nối 1: Tìm ID của Khối lớp (dựa trên số 10, 11...)
        LEFT JOIN edu.grade_levels g ON g.value = c.grade_level
        
        -- Cầu nối 2: Tìm ID của Môn học (dựa trên Khối ID và Tên môn)
        LEFT JOIN edu.subjects sub ON sub.grade_level_id = g.grade_level_id 
                                   AND sub.subject_name = c.subject_name
                                   
        -- Đi xuống cây kiến thức để lấy bài học
        LEFT JOIN edu.books b ON b.subject_id = sub.subject_id
        LEFT JOIN edu.chapters ch ON ch.book_id = b.book_id
        LEFT JOIN edu.lessons l ON l.chapter_id = ch.chapter_id
        
        WHERE c.teacher_id = %s
        
        GROUP BY c.class_id, s.name, c.subject_name, c.grade_level
        ORDER BY c.class_id DESC;
    """
    
    try:
        cursor.execute(sql, (current_user['user_id'],))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy dữ liệu lớp học & bài giảng: {str(e)}")