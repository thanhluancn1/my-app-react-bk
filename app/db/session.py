# app/db/session.py
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import logging
from app.core.config import settings

# Cấu hình logging để dễ debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Tạo hồ kết nối (Connection Pool)
    # Minconn=1, Maxconn=20
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        options="-c search_path=edu,public" # Quan trọng: Trỏ thẳng vào schema 'edu'
    )

    if connection_pool:
        logger.info("✅ Kết nối PostgreSQL thành công (Connection Pool created)")

except (Exception, psycopg2.DatabaseError) as error:
    logger.error(f"❌ Lỗi kết nối PostgreSQL: {error}")

# Dependency Injection: Hàm này sẽ được gọi trong mỗi API request
def get_db_cursor():
    conn = None
    try:
        # Lấy 1 kết nối từ hồ
        conn = connection_pool.getconn()
        
        # Tạo con trỏ (Cursor) trả về Dictionary thay vì Tuple
        # Ví dụ: thay vì (1, 'admin'), nó trả về {'id': 1, 'username': 'admin'}
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        yield cursor # Trả cursor cho hàm xử lý API dùng
        
        # Sau khi API dùng xong, commit transaction
        conn.commit()
        cursor.close()
        
    except Exception as e:
        if conn:
            conn.rollback() # Nếu lỗi thì rollback
        logger.error(f"DB Error: {e}")
        raise e
        
    finally:
        if conn:
            # Trả kết nối về hồ để người khác dùng
            connection_pool.putconn(conn)