-- ==========================================
-- 0. KHỞI TẠO SCHEMA
-- ==========================================
CREATE SCHEMA IF NOT EXISTS edu;

SET search_path TO edu, public;

-- ==========================================
-- 1. QUẢN TRỊ HỆ THỐNG & NGƯỜI DÙNG
-- ==========================================

DROP TABLE IF EXISTS edu.users CASCADE;
CREATE TABLE edu.users (
  user_id SERIAL PRIMARY KEY, -- Đổi từ id -> user_id
  username VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  email VARCHAR(255),
  phone VARCHAR(50),
  avatar_url TEXT,
  role VARCHAR(50), -- 'admin', 'giáo viên', 'học sinh'
  
  subject_id INT, -- No FK: Liên kết môn học (nếu là giáo viên)
  
  status VARCHAR(50) DEFAULT 'Hoạt động',
  created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 2. QUẢN LÝ TRƯỜNG HỌC, LỚP, HỌC SINH
-- ==========================================

DROP TABLE IF EXISTS edu.schools CASCADE;
CREATE TABLE edu.schools (
  school_id SERIAL PRIMARY KEY, -- Đổi từ id -> school_id
  name VARCHAR(255) NOT NULL,
  address TEXT,
  phone VARCHAR(50)
);

DROP TABLE IF EXISTS edu.classes CASCADE;
CREATE TABLE edu.classes (
  class_id SERIAL PRIMARY KEY, -- Đổi từ id -> class_id
  school_id INT, -- No FK
  class_name VARCHAR(100) NOT NULL,
  subject_name VARCHAR(100),
  
  grade_level INT, -- Mới thêm: Khối lớp (10, 11, 12...)
  
  start_year INT,
  end_year INT,
  
  teacher_id INT, -- No FK: Giáo viên chủ nhiệm/phụ trách
  
  status VARCHAR(50) DEFAULT 'Hoạt động',
  created_at TIMESTAMP DEFAULT NOW()
);

DROP TABLE IF EXISTS edu.students CASCADE;
CREATE TABLE edu.students (
  student_id SERIAL PRIMARY KEY, -- Đổi từ id -> student_id
  class_id INT, -- No FK
  full_name VARCHAR(255) NOT NULL,
  date_of_birth DATE,
  email VARCHAR(255),
  phone_number VARCHAR(50),
  status VARCHAR(50) DEFAULT 'Hoạt động',
  created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 3. CÂY KIẾN THỨC (KNOWLEDGE TREE)
-- ==========================================

DROP TABLE IF EXISTS edu.grade_levels CASCADE;
CREATE TABLE edu.grade_levels (
  grade_level_id SERIAL PRIMARY KEY, -- Đổi từ id -> grade_level_id
  grade_level_name VARCHAR(100) NOT NULL, -- Đổi từ name -> grade_level_name
  value INT
);

DROP TABLE IF EXISTS edu.subjects CASCADE;
CREATE TABLE edu.subjects (
  subject_id SERIAL PRIMARY KEY, -- Đổi từ id -> subject_id
  grade_level_id INT, -- No FK
  subject_name VARCHAR(100) NOT NULL -- Đổi từ name -> subject_name
);

DROP TABLE IF EXISTS edu.books CASCADE;
CREATE TABLE edu.books (
  book_id SERIAL PRIMARY KEY, -- Đổi từ id -> book_id
  subject_id INT, -- No FK
  book_name VARCHAR(255) NOT NULL -- Đổi từ name -> book_name
);

DROP TABLE IF EXISTS edu.chapters CASCADE;
CREATE TABLE edu.chapters (
  chapter_id SERIAL PRIMARY KEY, -- Đổi từ id -> chapter_id
  book_id INT, -- No FK
  chapter_name VARCHAR(255) NOT NULL, -- Đổi từ name -> chapter_name
  order_number INT
);

DROP TABLE IF EXISTS edu.lessons CASCADE;
CREATE TABLE edu.lessons (
  lesson_id SERIAL PRIMARY KEY, -- Đổi từ id -> lesson_id
  chapter_id INT, -- No FK
  lesson_name VARCHAR(255) NOT NULL, -- Đổi từ name -> lesson_name
  description TEXT,
  order_number INT
);

DROP TABLE IF EXISTS edu.knowledge_units CASCADE;
CREATE TABLE edu.knowledge_units (
  knowledge_unit_id SERIAL PRIMARY KEY, -- Đổi từ id -> knowledge_unit_id
  lesson_id INT, -- No FK
  content TEXT NOT NULL,
  knowledge_type VARCHAR(50) -- Đổi từ type -> knowledge_type
);

-- ==========================================
-- 4. NGÂN HÀNG CÂU HỎI (QUESTION BANK)
-- ==========================================

DROP TABLE IF EXISTS edu.questions CASCADE;
CREATE TABLE edu.questions (
  question_id SERIAL PRIMARY KEY, -- Đổi từ id -> question_id
  knowledge_unit_id INT, -- No FK
  lesson_id INT, -- No FK
  
  content TEXT NOT NULL,
  type VARCHAR(50) NOT NULL, -- 'Trắc nghiệm', 'Tự luận'
  level VARCHAR(50), -- 'Nhận biết', 'Thông hiểu', 'Vận dụng'
  
  default_score FLOAT DEFAULT 1.0,
  solution_guide TEXT,
  
  created_by INT, -- No FK
  created_at TIMESTAMP DEFAULT NOW()
);

DROP TABLE IF EXISTS edu.question_options CASCADE;
CREATE TABLE edu.question_options (
  question_option_id SERIAL PRIMARY KEY, -- Đổi từ id -> question_option_id
  question_id INT, -- No FK
  content TEXT NOT NULL,
  is_correct BOOLEAN DEFAULT FALSE,
  order_index INT
);

DROP TABLE IF EXISTS edu.question_images CASCADE;
CREATE TABLE edu.question_images (
  question_image_id SERIAL PRIMARY KEY, -- Đổi từ id -> question_image_id
  question_id INT, -- No FK
  image_key VARCHAR(100),
  image_url TEXT
);

-- ==========================================
-- 5. QUẢN LÝ ĐỀ THI & GIAO BÀI (EXAMS)
-- ==========================================

DROP TABLE IF EXISTS edu.exam_batches CASCADE;
CREATE TABLE edu.exam_batches (
  exam_batch_id SERIAL PRIMARY KEY, -- Đổi từ id -> exam_batch_id
  name VARCHAR(255) NOT NULL,
  creator_id INT, -- No FK
  subject_id INT, -- No FK
  
  duration_minutes INT,
  total_points FLOAT,
  
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  
  status VARCHAR(50) DEFAULT 'Bản nháp',
  
  allow_view_score BOOLEAN DEFAULT FALSE,
  allow_view_solution BOOLEAN DEFAULT FALSE,
  min_score_to_view FLOAT,
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 6. MA TRẬN ĐỀ THI (EXAM MATRICES)
-- ==========================================

DROP TABLE IF EXISTS edu.exam_matrices CASCADE;
CREATE TABLE edu.exam_matrices (
  exam_matrix_id SERIAL PRIMARY KEY, -- Đổi từ id -> exam_matrix_id
  
  exam_batch_id INT, -- No FK
  
  chapter_id INT, -- No FK
  lesson_id INT, -- No FK
  knowledge_unit_id INT, -- No FK
  
  level_recognition INT DEFAULT 0,
  level_understanding INT DEFAULT 0,
  level_application INT DEFAULT 0,
  level_high_application INT DEFAULT 0,
  
  type_multiple_choice INT DEFAULT 0,
  type_essay INT DEFAULT 0,
  type_true_false INT DEFAULT 0,
  type_fill_blank INT DEFAULT 0,
  
  total_points FLOAT DEFAULT 0,

  -- Vẫn giữ Check Constraint để đảm bảo logic dữ liệu đúng
  CONSTRAINT check_knowledge_target CHECK (
    (chapter_id IS NOT NULL) OR (lesson_id IS NOT NULL) OR (knowledge_unit_id IS NOT NULL)
  )
);

-- ==========================================
-- 7. LIÊN KẾT ĐỀ THI (ASSIGNMENTS & QUESTIONS)
-- ==========================================

DROP TABLE IF EXISTS edu.exam_class_assignments CASCADE;
CREATE TABLE edu.exam_class_assignments (
  assignment_id SERIAL PRIMARY KEY, -- Đổi từ id -> assignment_id
  exam_batch_id INT, -- No FK
  class_id INT, -- No FK
  assigned_at TIMESTAMP DEFAULT NOW()
);

DROP TABLE IF EXISTS edu.exam_questions CASCADE;
CREATE TABLE edu.exam_questions (
  exam_question_id SERIAL PRIMARY KEY, -- Đổi từ id -> exam_question_id
  exam_batch_id INT, -- No FK
  question_id INT, -- No FK
  score_in_exam FLOAT,
  order_index INT
);

-- ==========================================
-- 8. LỊCH DẠY (SCHEDULE)
-- ==========================================

DROP TABLE IF EXISTS edu.schedules CASCADE;
CREATE TABLE edu.schedules (
  schedule_id SERIAL PRIMARY KEY, -- Đổi từ id -> schedule_id
  class_id INT, -- No FK
  lesson_id INT, -- No FK
  teacher_id INT, -- No FK
  
  schedule_date DATE NOT NULL,
  week_day VARCHAR(20),
  
  start_period INT,
  end_period INT,
  
  note TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);