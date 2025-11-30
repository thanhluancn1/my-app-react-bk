# app/api/schedule.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import date
from typing import List

from app.db.session import get_db_cursor
from app.api.deps import get_current_user
from app.schemas.schedule import ScheduleDTO, ScheduleCreate

router = APIRouter()

# Helper: Map thứ trong tuần
def get_weekday_str(d: date) -> str:
    days = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    return days[d.weekday()]

# ==========================================
# 1. GET: Lấy danh sách lịch dạy
# ==========================================
@router.get("/schedules", response_model=List[ScheduleDTO])
def get_schedules(
    start_date: date = Query(..., description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Ngày kết thúc (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user),
    cursor = Depends(get_db_cursor)
):
    # Cập nhật SQL: Dùng schedule_date
    sql = """
        SELECT 
            s.schedule_id,
            s.schedule_date, -- <--- Đổi tên
            s.week_day,
            s.start_period,
            s.end_period,
            s.class_id,
            c.class_name,
            c.subject_name,
            s.lesson_id,
            l.lesson_name
        FROM edu.schedules s
        JOIN edu.classes c ON s.class_id = c.class_id
        LEFT JOIN edu.lessons l ON s.lesson_id = l.lesson_id
        WHERE s.schedule_date >= %s AND s.schedule_date <= %s -- <--- Đổi tên
    """
    params = [start_date, end_date]

    if current_user['role'] == 'giáo viên':
        sql += " AND s.teacher_id = %s"
        params.append(current_user['user_id'])
    
    sql += " ORDER BY s.schedule_date, s.start_period" # <--- Đổi tên

    try:
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(500, f"Lỗi tải lịch: {str(e)}")

# ==========================================
# 2. POST: Tạo lịch mới
# ==========================================
@router.post("/schedules", response_model=ScheduleDTO, status_code=201)
def create_schedule(
    data: ScheduleCreate,
    current_user: dict = Depends(get_current_user),
    cursor = Depends(get_db_cursor)
):
    # 1. Tính thứ trong tuần (Dùng schedule_date)
    week_day_str = get_weekday_str(data.schedule_date) 
    teacher_id = current_user['user_id']

    # 2. Validate: Check trùng lịch của Giáo viên (Dùng schedule_date)
    check_sql = """
        SELECT schedule_id FROM edu.schedules 
        WHERE teacher_id = %s 
          AND schedule_date = %s -- <--- Đổi tên
          AND start_period <= %s 
          AND end_period >= %s
    """
    cursor.execute(check_sql, (teacher_id, data.schedule_date, data.end_period, data.start_period))
    if cursor.fetchone():
        raise HTTPException(400, f"Bạn đã có lịch dạy khác vào khung giờ này ({week_day_str}).")

    # 3. Validate: Check trùng lịch của Lớp học (Dùng schedule_date)
    check_class_sql = """
        SELECT schedule_id FROM edu.schedules 
        WHERE class_id = %s 
          AND schedule_date = %s -- <--- Đổi tên
          AND start_period <= %s 
          AND end_period >= %s
    """
    cursor.execute(check_class_sql, (data.class_id, data.schedule_date, data.end_period, data.start_period))
    if cursor.fetchone():
        raise HTTPException(400, f"Lớp này đã có lịch học môn khác vào khung giờ này.")

    # 4. Insert (Dùng schedule_date)
    insert_sql = """
        INSERT INTO edu.schedules (class_id, lesson_id, teacher_id, schedule_date, week_day, start_period, end_period)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING schedule_id
    """
    try:
        cursor.execute(insert_sql, (
            data.class_id, data.lesson_id, teacher_id, 
            data.schedule_date, week_day_str, data.start_period, data.end_period
        ))
        new_id = cursor.fetchone()['schedule_id']
        
        # 5. Fetch lại data đầy đủ
        fetch_sql = """
            SELECT 
                s.schedule_id, s.schedule_date, s.week_day, s.start_period, s.end_period,
                s.class_id, c.class_name, c.subject_name,
                s.lesson_id, l.lesson_name
            FROM edu.schedules s
            JOIN edu.classes c ON s.class_id = c.class_id
            LEFT JOIN edu.lessons l ON s.lesson_id = l.lesson_id
            WHERE s.schedule_id = %s
        """
        cursor.execute(fetch_sql, (new_id,))
        return cursor.fetchone()

    except Exception as e:
        raise HTTPException(500, f"Lỗi tạo lịch: {str(e)}")
    
# ==========================================
# 3. PUT: Cập nhật lịch (MỚI - SỬA LỖI TRÙNG LỊCH)
# ==========================================
@router.put("/schedules/{schedule_id}", response_model=ScheduleDTO)
def update_schedule(
    schedule_id: int,
    data: ScheduleCreate,
    current_user: dict = Depends(get_current_user),
    cursor = Depends(get_db_cursor)
):
    # 1. Tính thứ trong tuần
    week_day_str = get_weekday_str(data.schedule_date)
    teacher_id = current_user['user_id']

    # 2. Validate: Check trùng lịch của Giáo viên (LOẠI TRỪ CHÍNH NÓ)
    # Thêm điều kiện: AND schedule_id != %s
    check_sql = """
        SELECT schedule_id FROM edu.schedules 
        WHERE teacher_id = %s 
          AND schedule_date = %s
          AND start_period <= %s 
          AND end_period >= %s
          AND schedule_id != %s 
    """
    cursor.execute(check_sql, (teacher_id, data.schedule_date, data.end_period, data.start_period, schedule_id))
    if cursor.fetchone():
        raise HTTPException(400, f"Bạn đã có lịch dạy khác vào khung giờ này ({week_day_str}).")

    # 3. Validate: Check trùng lịch của Lớp học (LOẠI TRỪ CHÍNH NÓ)
    check_class_sql = """
        SELECT schedule_id FROM edu.schedules 
        WHERE class_id = %s 
          AND schedule_date = %s
          AND start_period <= %s 
          AND end_period >= %s
          AND schedule_id != %s
    """
    cursor.execute(check_class_sql, (data.class_id, data.schedule_date, data.end_period, data.start_period, schedule_id))
    if cursor.fetchone():
        raise HTTPException(400, f"Lớp này đã có lịch học môn khác vào khung giờ này.")

    # 4. Update
    update_sql = """
        UPDATE edu.schedules 
        SET class_id = %s, lesson_id = %s, schedule_date = %s, week_day = %s, start_period = %s, end_period = %s
        WHERE schedule_id = %s
        RETURNING schedule_id
    """
    try:
        cursor.execute(update_sql, (
            data.class_id, data.lesson_id, 
            data.schedule_date, week_day_str, data.start_period, data.end_period,
            schedule_id
        ))
        
        # Kiểm tra xem update có thành công không (có dòng nào bị tác động không)
        if cursor.rowcount == 0:
             raise HTTPException(404, "Không tìm thấy lịch dạy hoặc bạn không có quyền sửa.")

        # 5. Fetch lại data đầy đủ để trả về UI
        fetch_sql = """
            SELECT 
                s.schedule_id, s.schedule_date, s.week_day, s.start_period, s.end_period,
                s.class_id, c.class_name, c.subject_name,
                s.lesson_id, l.lesson_name
            FROM edu.schedules s
            JOIN edu.classes c ON s.class_id = c.class_id
            LEFT JOIN edu.lessons l ON s.lesson_id = l.lesson_id
            WHERE s.schedule_id = %s
        """
        cursor.execute(fetch_sql, (schedule_id,))
        return cursor.fetchone()

    except Exception as e:
        # Nếu đã raise HTTP exception ở trên thì ném tiếp
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(500, f"Lỗi cập nhật lịch: {str(e)}")

# ==========================================
# 3. DELETE: Xóa lịch (Giữ nguyên logic cũ vì xóa theo ID)
# ==========================================
@router.delete("/schedules/{id}")
def delete_schedule(
    id: int,
    current_user: dict = Depends(get_current_user),
    cursor = Depends(get_db_cursor)
):
    check_owner_sql = "SELECT teacher_id FROM edu.schedules WHERE schedule_id = %s"
    cursor.execute(check_owner_sql, (id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(404, "Không tìm thấy lịch dạy")
        
    if current_user['role'] != 'admin' and row['teacher_id'] != current_user['user_id']:
        raise HTTPException(403, "Bạn không có quyền xóa lịch dạy của người khác")

    cursor.execute("DELETE FROM edu.schedules WHERE schedule_id = %s RETURNING schedule_id", (id,))
    return {"message": "Xóa thành công", "id": id}