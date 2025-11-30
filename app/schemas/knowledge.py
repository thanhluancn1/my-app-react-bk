from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# ==========================================
# 1. INPUT SCHEMAS (Create & Update)
# ==========================================

# --- GRADE ---
class GradeCreate(BaseModel):
    grade_level_name: str
    value: int

class GradeUpdate(BaseModel):
    grade_level_name: Optional[str] = None
    value: Optional[int] = None

class GradeResponse(GradeCreate):
    grade_level_id: int

# --- SUBJECT ---
class SubjectCreate(BaseModel):
    subject_name: str
    grade_level_id: int

class SubjectUpdate(BaseModel):
    subject_name: Optional[str] = None
    grade_level_id: Optional[int] = None

class SubjectResponse(SubjectCreate):
    subject_id: int

# --- BOOK ---
class BookCreate(BaseModel):
    book_name: str
    subject_id: int

class BookUpdate(BaseModel):
    book_name: Optional[str] = None
    subject_id: Optional[int] = None

class BookResponse(BookCreate):
    book_id: int

# --- CHAPTER ---
class ChapterCreate(BaseModel):
    chapter_name: str
    book_id: int
    order_number: Optional[int] = 0

class ChapterUpdate(BaseModel):
    chapter_name: Optional[str] = None
    order_number: Optional[int] = None

class ChapterResponse(ChapterCreate):
    chapter_id: int

# --- LESSON ---
class LessonCreate(BaseModel):
    lesson_name: str
    chapter_id: int
    description: Optional[str] = None
    order_number: Optional[int] = 0

class LessonUpdate(BaseModel):
    lesson_name: Optional[str] = None
    description: Optional[str] = None
    order_number: Optional[int] = None

class LessonResponse(LessonCreate):
    lesson_id: int

# --- KNOWLEDGE UNIT (Đơn vị kiến thức) ---
class KnowledgeUnitCreate(BaseModel):
    content: str
    lesson_id: int
    # SỬA Ở ĐÂY: Đổi 'Concept', 'Skill' thành tiếng Việt
    knowledge_type: Literal['Khái niệm', 'Kỹ năng'] = Field(..., description="Loại: Khái niệm hoặc Kỹ năng")

class KnowledgeUnitUpdate(BaseModel):
    content: Optional[str] = None
    # SỬA Ở ĐÂY:
    knowledge_type: Optional[Literal['Khái niệm', 'Kỹ năng']] = None

class KnowledgeUnitResponse(KnowledgeUnitCreate):
    knowledge_unit_id: int
# ==========================================
# 2. NESTED OUTPUT SCHEMAS (Cho API Get Tree)
# ==========================================

class KnowledgeUnitDTO(BaseModel):
    knowledge_unit_id: int
    content: str
    knowledge_type: str

class LessonDTO(BaseModel):
    lesson_id: int
    lesson_name: str
    description: Optional[str] = None
    order_number: int
    knowledge_units: List[KnowledgeUnitDTO] = []

class ChapterDTO(BaseModel):
    chapter_id: int
    chapter_name: str
    order_number: int
    lessons: List[LessonDTO] = []

class BookDTO(BaseModel):
    book_id: int
    book_name: str
    chapters: List[ChapterDTO] = []

class SubjectDTO(BaseModel):
    subject_id: int
    subject_name: str
    books: List[BookDTO] = []

class GradeDTO(BaseModel):
    grade_level_id: int
    grade_level_name: str
    value: int
    subjects: List[SubjectDTO] = []