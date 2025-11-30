# app/schemas/__init__.py

from .user import UserCreate, UserResponse
from .auth import LoginRequest, TokenResponse
from .school import ClassDTO, ClassCreate, StudentDTO, StudentCreate
from .schedule import ScheduleCreate, ScheduleDTO

from .knowledge import (
    # CRUD Schemas
    GradeCreate, GradeUpdate, GradeResponse,
    SubjectCreate, SubjectUpdate, SubjectResponse,
    BookCreate, BookUpdate, BookResponse,
    ChapterCreate, ChapterUpdate, ChapterResponse,
    LessonCreate, LessonUpdate, LessonResponse,
    KnowledgeUnitCreate, KnowledgeUnitUpdate, KnowledgeUnitResponse,
    
    # Nested DTOs
    GradeDTO, SubjectDTO, BookDTO, ChapterDTO, LessonDTO, KnowledgeUnitDTO
)