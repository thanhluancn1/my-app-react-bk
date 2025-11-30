from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict

from app.db.session import get_db_cursor
from app.api.deps import get_current_user
from app.schemas.knowledge import (
    # Input Schemas
    GradeCreate, GradeUpdate, GradeResponse,
    SubjectCreate, SubjectUpdate, SubjectResponse,
    BookCreate, BookUpdate, BookResponse,
    ChapterCreate, ChapterUpdate, ChapterResponse,
    LessonCreate, LessonUpdate, LessonResponse,
    KnowledgeUnitCreate, KnowledgeUnitUpdate, KnowledgeUnitResponse,
    # Output Tree Schema
    GradeDTO
)

router = APIRouter()

# ============================================================
# HELPER: CHECK ADMIN
# ============================================================
def check_is_admin(user: dict):
    if user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Quản trị viên mới có quyền chỉnh sửa dữ liệu."
        )

# ============================================================
# 1. API LẤY CÂY KIẾN THỨC (THE "DIVINE" QUERY)
# ============================================================
@router.get("/knowledge-tree", response_model=List[GradeDTO])
def get_knowledge_tree(
    current_user: dict = Depends(get_current_user),
    cursor = Depends(get_db_cursor)
):
    """
    Lấy toàn bộ cây kiến thức.
    - Admin: Thấy hết.
    - Giáo viên: Chỉ thấy môn mình dạy (theo subject_id).
    """
    
    # Điều kiện lọc theo giáo viên
    subject_filter = ""
    params = []
    
    # Nếu là giáo viên và có môn phụ trách -> Thêm điều kiện lọc Subject
    if current_user['role'] == 'giáo viên' and current_user.get('subject_id'):
        subject_filter = "AND s.subject_id = %s"
        params.append(current_user['subject_id'])

    # Query lồng nhau 6 cấp sử dụng json_agg
    # Cấu trúc: Grade -> Subject -> Book -> Chapter -> Lesson -> KnowledgeUnit
    sql = f"""
        SELECT 
            g.grade_level_id,
            g.grade_level_name,
            g.value,
            COALESCE(
                json_agg(
                    json_build_object(
                        'subject_id', s.subject_id,
                        'subject_name', s.subject_name,
                        'books', (
                            SELECT COALESCE(
                                json_agg(
                                    json_build_object(
                                        'book_id', b.book_id,
                                        'book_name', b.book_name,
                                        'chapters', (
                                            SELECT COALESCE(
                                                json_agg(
                                                    json_build_object(
                                                        'chapter_id', c.chapter_id,
                                                        'chapter_name', c.chapter_name,
                                                        'order_number', c.order_number,
                                                        'lessons', (
                                                            SELECT COALESCE(
                                                                json_agg(
                                                                    json_build_object(
                                                                        'lesson_id', l.lesson_id,
                                                                        'lesson_name', l.lesson_name,
                                                                        'description', l.description,
                                                                        'order_number', l.order_number,
                                                                        'knowledge_units', (
                                                                            SELECT COALESCE(
                                                                                json_agg(
                                                                                    json_build_object(
                                                                                        'knowledge_unit_id', k.knowledge_unit_id,
                                                                                        'content', k.content,
                                                                                        'knowledge_type', k.knowledge_type
                                                                                    ) ORDER BY k.knowledge_unit_id
                                                                                ), '[]'
                                                                            )
                                                                            FROM edu.knowledge_units k WHERE k.lesson_id = l.lesson_id
                                                                        )
                                                                    ) ORDER BY l.order_number
                                                                ), '[]'
                                                            )
                                                            FROM edu.lessons l WHERE l.chapter_id = c.chapter_id
                                                        )
                                                    ) ORDER BY c.order_number
                                                ), '[]'
                                            )
                                            FROM edu.chapters c WHERE c.book_id = b.book_id
                                        )
                                    ) ORDER BY b.book_id
                                ), '[]'
                            )
                            FROM edu.books b WHERE b.subject_id = s.subject_id
                        )
                    ) ORDER BY s.subject_id
                ) FILTER (WHERE s.subject_id IS NOT NULL), 
                '[]'
            ) as subjects
        FROM edu.grade_levels g
        LEFT JOIN edu.subjects s ON g.grade_level_id = s.grade_level_id {subject_filter}
        GROUP BY g.grade_level_id
        ORDER BY g.value;
    """
    
    try:
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(500, f"Lỗi lấy cây kiến thức: {str(e)}")

# ============================================================
# 2. GROUP CRUD: GRADES (KHỐI LỚP)
# ============================================================
@router.post("/grades", response_model=GradeResponse, status_code=201)
def create_grade(data: GradeCreate, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute(
        "INSERT INTO edu.grade_levels (grade_level_name, value) VALUES (%s, %s) RETURNING *",
        (data.grade_level_name, data.value)
    )
    return cursor.fetchone()

@router.put("/grades/{id}", response_model=GradeResponse)
def update_grade(id: int, data: GradeUpdate, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute(
        "UPDATE edu.grade_levels SET grade_level_name=COALESCE(%s, grade_level_name), value=COALESCE(%s, value) WHERE grade_level_id=%s RETURNING *",
        (data.grade_level_name, data.value, id)
    )
    res = cursor.fetchone()
    if not res: raise HTTPException(404, "Không tìm thấy Khối")
    return res

@router.delete("/grades/{id}")
def delete_grade(id: int, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute("DELETE FROM edu.grade_levels WHERE grade_level_id=%s RETURNING grade_level_id", (id,))
    if not cursor.fetchone(): raise HTTPException(404, "Không tìm thấy Khối")
    return {"message": "Xóa thành công"}

# ============================================================
# 3. GROUP CRUD: SUBJECTS (MÔN HỌC)
# ============================================================
@router.post("/subjects", response_model=SubjectResponse, status_code=201)
def create_subject(data: SubjectCreate, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute(
        "INSERT INTO edu.subjects (subject_name, grade_level_id) VALUES (%s, %s) RETURNING *",
        (data.subject_name, data.grade_level_id)
    )
    return cursor.fetchone()

@router.put("/subjects/{id}", response_model=SubjectResponse)
def update_subject(id: int, data: SubjectUpdate, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute(
        "UPDATE edu.subjects SET subject_name=COALESCE(%s, subject_name), grade_level_id=COALESCE(%s, grade_level_id) WHERE subject_id=%s RETURNING *",
        (data.subject_name, data.grade_level_id, id)
    )
    res = cursor.fetchone()
    if not res: raise HTTPException(404, "Không tìm thấy Môn học")
    return res

@router.delete("/subjects/{id}")
def delete_subject(id: int, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute("DELETE FROM edu.subjects WHERE subject_id=%s RETURNING subject_id", (id,))
    if not cursor.fetchone(): raise HTTPException(404, "Không tìm thấy Môn học")
    return {"message": "Xóa thành công"}

# ============================================================
# 4. GROUP CRUD: BOOKS (SÁCH)
# ============================================================
@router.post("/books", response_model=BookResponse, status_code=201)
def create_book(data: BookCreate, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute(
        "INSERT INTO edu.books (book_name, subject_id) VALUES (%s, %s) RETURNING *",
        (data.book_name, data.subject_id)
    )
    return cursor.fetchone()

@router.put("/books/{id}", response_model=BookResponse)
def update_book(id: int, data: BookUpdate, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute(
        "UPDATE edu.books SET book_name=COALESCE(%s, book_name), subject_id=COALESCE(%s, subject_id) WHERE book_id=%s RETURNING *",
        (data.book_name, data.subject_id, id)
    )
    res = cursor.fetchone()
    if not res: raise HTTPException(404, "Không tìm thấy Sách")
    return res

@router.delete("/books/{id}")
def delete_book(id: int, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute("DELETE FROM edu.books WHERE book_id=%s RETURNING book_id", (id,))
    if not cursor.fetchone(): raise HTTPException(404, "Không tìm thấy Sách")
    return {"message": "Xóa thành công"}

# ============================================================
# 5. GROUP CRUD: CHAPTERS (CHƯƠNG)
# ============================================================
@router.post("/chapters", response_model=ChapterResponse, status_code=201)
def create_chapter(data: ChapterCreate, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute(
        "INSERT INTO edu.chapters (chapter_name, book_id, order_number) VALUES (%s, %s, %s) RETURNING *",
        (data.chapter_name, data.book_id, data.order_number)
    )
    return cursor.fetchone()

@router.put("/chapters/{id}", response_model=ChapterResponse)
def update_chapter(id: int, data: ChapterUpdate, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute(
        "UPDATE edu.chapters SET chapter_name=COALESCE(%s, chapter_name), order_number=COALESCE(%s, order_number) WHERE chapter_id=%s RETURNING *",
        (data.chapter_name, data.order_number, id)
    )
    res = cursor.fetchone()
    if not res: raise HTTPException(404, "Không tìm thấy Chương")
    return res

@router.delete("/chapters/{id}")
def delete_chapter(id: int, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute("DELETE FROM edu.chapters WHERE chapter_id=%s RETURNING chapter_id", (id,))
    if not cursor.fetchone(): raise HTTPException(404, "Không tìm thấy Chương")
    return {"message": "Xóa thành công"}

# ============================================================
# 6. GROUP CRUD: LESSONS (BÀI HỌC)
# ============================================================
@router.post("/lessons", response_model=LessonResponse, status_code=201)
def create_lesson(data: LessonCreate, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute(
        "INSERT INTO edu.lessons (lesson_name, chapter_id, description, order_number) VALUES (%s, %s, %s, %s) RETURNING *",
        (data.lesson_name, data.chapter_id, data.description, data.order_number)
    )
    return cursor.fetchone()

@router.put("/lessons/{id}", response_model=LessonResponse)
def update_lesson(id: int, data: LessonUpdate, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute(
        """UPDATE edu.lessons 
           SET lesson_name=COALESCE(%s, lesson_name), 
               description=COALESCE(%s, description),
               order_number=COALESCE(%s, order_number)
           WHERE lesson_id=%s RETURNING *""",
        (data.lesson_name, data.description, data.order_number, id)
    )
    res = cursor.fetchone()
    if not res: raise HTTPException(404, "Không tìm thấy Bài học")
    return res

@router.delete("/lessons/{id}")
def delete_lesson(id: int, user=Depends(get_current_user), cursor=Depends(get_db_cursor)):
    check_is_admin(user)
    cursor.execute("DELETE FROM edu.lessons WHERE lesson_id=%s RETURNING lesson_id", (id,))
    if not cursor.fetchone(): raise HTTPException(404, "Không tìm thấy Bài học")
    return {"message": "Xóa thành công"}

# ============================================================
# 7. GROUP CRUD: KNOWLEDGE UNITS (ĐƠN VỊ KIẾN THỨC)
# ============================================================

@router.post("/knowledge-units", response_model=KnowledgeUnitResponse, status_code=201)
def create_unit(
    data: KnowledgeUnitCreate, 
    user: dict = Depends(get_current_user), # Đã import từ app.api.deps
    cursor = Depends(get_db_cursor)         # Đã import từ app.db.session
):
    """
    Tạo mới một Knowledge Unit
    """
    check_is_admin(user) # Chỉ Admin mới được tạo
    
    query = """
        INSERT INTO edu.knowledge_units (content, lesson_id, knowledge_type) 
        VALUES (%s, %s, %s) 
        RETURNING knowledge_unit_id, content, lesson_id, knowledge_type
    """
    try:
        cursor.execute(query, (data.content, data.lesson_id, data.knowledge_type))
        return cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi tạo Unit: {str(e)}")

@router.put("/knowledge-units/{id}", response_model=KnowledgeUnitResponse)
def update_unit(
    id: int, 
    data: KnowledgeUnitUpdate, 
    user: dict = Depends(get_current_user), 
    cursor = Depends(get_db_cursor)
):
    """
    Cập nhật Knowledge Unit
    """
    check_is_admin(user)
    
    query = """
        UPDATE edu.knowledge_units 
        SET content = COALESCE(%s, content), 
            knowledge_type = COALESCE(%s, knowledge_type) 
        WHERE knowledge_unit_id = %s 
        RETURNING knowledge_unit_id, content, lesson_id, knowledge_type
    """
    try:
        cursor.execute(query, (data.content, data.knowledge_type, id))
        updated_unit = cursor.fetchone()
        
        if not updated_unit:
            raise HTTPException(status_code=404, detail="Không tìm thấy Đơn vị kiến thức")
            
        return updated_unit
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi cập nhật Unit: {str(e)}")

@router.delete("/knowledge-units/{id}")
def delete_unit(
    id: int, 
    user: dict = Depends(get_current_user), 
    cursor = Depends(get_db_cursor)
):
    """
    Xóa Knowledge Unit
    """
    check_is_admin(user)
    
    query = "DELETE FROM edu.knowledge_units WHERE knowledge_unit_id = %s RETURNING knowledge_unit_id"
    
    try:
        cursor.execute(query, (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Không tìm thấy Đơn vị kiến thức")
        return {"message": "Xóa thành công", "id": id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xóa Unit: {str(e)}")