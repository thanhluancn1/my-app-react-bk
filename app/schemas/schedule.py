# app/schemas/schedule.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

# Input: Tạo lịch mới
class ScheduleCreate(BaseModel):
    class_id: int
    lesson_id: Optional[int] = None 
    schedule_date: date # <--- Đã đổi tên
    start_period: int
    end_period: int

# Output: Hiển thị lên UI
class ScheduleDTO(BaseModel):
    schedule_id: int
    class_id: int
    class_name: str
    subject_name: Optional[str] = None
    
    lesson_id: Optional[int] = None
    lesson_name: Optional[str] = None
    
    schedule_date: date # <--- Đã đổi tên
    week_day: str
    start_period: int
    end_period: int