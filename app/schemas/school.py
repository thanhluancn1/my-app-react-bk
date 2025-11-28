from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# --- STUDENT ---
class StudentDTO(BaseModel):
    student_id: int
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
    class_id: int
    class_name: str
    school_name: str
    subject_name: Optional[str] = None
    grade_level: Optional[int] = None
    start_year: int
    end_year: int
    class_status: str
    students: List[StudentDTO] = []

class ClassCreate(BaseModel):
    class_name: str
    school_name: str
    subject_name: Optional[str] = None
    grade_level: Optional[int] = None
    start_year: int
    end_year: int
    class_status: str = "Hoạt động"