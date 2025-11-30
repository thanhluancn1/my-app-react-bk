from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# --- STUDENT ---

class StudentDTO(BaseModel):
    student_id: int # Đổi từ id -> student_id
    full_name: str
    date_of_birth: Optional[date] = None 
    email: Optional[str] = None
    phone_number: Optional[str] = None
    status: str

class StudentCreate(BaseModel):
    class_id: int
    full_name: str
    date_of_birth: Optional[date] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    status: str = "Hoạt động"

# --- CLASS ---

class ClassDTO(BaseModel):
    class_id: int # Đổi từ id -> class_id
    class_name: str
    school_name: str
    subject_name: Optional[str] = None
    
    # Thêm trường mới
    grade_level: Optional[int] = None
    teacher_id: Optional[int] = None
    
    start_year: int
    end_year: int
    class_status: str
    students: List[StudentDTO] = []

class ClassCreate(BaseModel):
    class_name: str
    school_name: str
    subject_name: Optional[str] = None
    
    # Thêm trường mới vào Input
    grade_level: int
    
    start_year: int
    end_year: int
    class_status: str = "Hoạt động"

# ==========================================
# SCHEMAS CHO API: LỚP HỌC KÈM BÀI GIẢNG (TEACHER VIEW)
# ==========================================

# 1. Thông tin bài học tóm tắt (để hiển thị trong dropdown chọn bài)
class LessonSimpleDTO(BaseModel):
    lesson_id: int
    lesson_name: str
    chapter_name: Optional[str] = None # Thêm tên chương để giáo viên dễ phân biệt

# 2. Lớp học kèm danh sách bài học (Dựa trên Grade + Subject)
class ClassWithLessonsDTO(BaseModel):
    class_id: int
    class_name: str
    school_name: str
    subject_name: Optional[str] = None
    grade_level: int
    
    # Danh sách bài học tương ứng với Khối & Môn của lớp này
    lessons: List[LessonSimpleDTO] = []