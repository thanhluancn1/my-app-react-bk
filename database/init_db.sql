-- ==========================================
-- 0. KHỞI TẠO SCHEMA
-- ==========================================
CREATE SCHEMA IF NOT EXISTS edu;

SET search_path TO edu, public;

-- ==========================================
-- 1. QUẢN TRỊ HỆ THỐNG & NGƯỜI DÙNG
-- ==========================================

CREATE TABLE edu.users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  email VARCHAR(255),
  phone VARCHAR(50),
  avatar_url TEXT,
  role VARCHAR(50), -- VD: 'admin', 'giáo viên', 'học sinh'
  subject_id INT REFERENCES edu.subjects(id),
  status VARCHAR(50) DEFAULT 'Hoạt động', -- VD: 'Hoạt động', 'Đã khóa'
  created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 2. QUẢN LÝ TRƯỜNG HỌC, LỚP, HỌC SINH
-- ==========================================

CREATE TABLE edu.schools (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  address TEXT,
  phone VARCHAR(50)
);

CREATE TABLE edu.classes (
  id SERIAL PRIMARY KEY,
  school_id INT REFERENCES edu.schools(id),
  class_name VARCHAR(100) NOT NULL,
  subject_name VARCHAR(100),
  grade_level INT,
  start_year INT,
  end_year INT,
  teacher_id INT REFERENCES edu.users(id),
  status VARCHAR(50) DEFAULT 'Hoạt động',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE edu.students (
  id SERIAL PRIMARY KEY,
  class_id INT REFERENCES edu.classes(id),
  full_name VARCHAR(255) NOT NULL,
  date_of_birth DATE,
  email VARCHAR(255),
  phone_number VARCHAR(50),
  status VARCHAR(50) DEFAULT 'Hoạt động', -- 'Hoạt động', 'Bảo lưu', 'Thôi học'
  created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 3. CÂY KIẾN THỨC (KNOWLEDGE TREE)
-- ==========================================

DROP TABLE IF EXISTS edu.grade_levels CASCADE;
CREATE TABLE edu.grade_levels (
  grade_level_id SERIAL PRIMARY KEY,
  grade_level_name VARCHAR(100) NOT NULL, -- Đổi từ name
  value INT
);

DROP TABLE IF EXISTS edu.subjects CASCADE;
CREATE TABLE edu.subjects (
  subject_id SERIAL PRIMARY KEY,
  grade_level_id INT,
  subject_name VARCHAR(100) NOT NULL -- Đổi từ name
);

DROP TABLE IF EXISTS edu.books CASCADE;
CREATE TABLE edu.books (
  book_id SERIAL PRIMARY KEY,
  subject_id INT,
  book_name VARCHAR(255) NOT NULL -- Đổi từ name
);

DROP TABLE IF EXISTS edu.chapters CASCADE;
CREATE TABLE edu.chapters (
  chapter_id SERIAL PRIMARY KEY,
  book_id INT,
  chapter_name VARCHAR(255) NOT NULL, -- Đổi từ name
  order_number INT
);

DROP TABLE IF EXISTS edu.lessons CASCADE;
CREATE TABLE edu.lessons (
  lesson_id SERIAL PRIMARY KEY,
  chapter_id INT,
  lesson_name VARCHAR(255) NOT NULL, -- Đổi từ name
  description TEXT,
  order_number INT
);

DROP TABLE IF EXISTS edu.knowledge_units CASCADE;
CREATE TABLE edu.knowledge_units (
  knowledge_unit_id SERIAL PRIMARY KEY,
  lesson_id INT,
  content TEXT NOT NULL,
  knowledge_type VARCHAR(50) -- Đổi từ type -> knowledge_type
);

-- ==========================================
-- 4. NGÂN HÀNG CÂU HỎI (QUESTION BANK)
-- ==========================================

CREATE TABLE edu.questions (
  id SERIAL PRIMARY KEY,
  knowledge_unit_id INT REFERENCES edu.knowledge_units(id),
  lesson_id INT REFERENCES edu.lessons(id),
  
  content TEXT NOT NULL,
  type VARCHAR(50) NOT NULL,  -- VD: 'Trắc nghiệm', 'Tự luận', 'Đúng/Sai'
  level VARCHAR(50),          -- VD: 'Nhận biết', 'Thông hiểu', 'Vận dụng', 'Vận dụng cao'
  
  default_score FLOAT DEFAULT 1.0,
  solution_guide TEXT,
  
  created_by INT REFERENCES edu.users(id),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE edu.question_options (
  id SERIAL PRIMARY KEY,
  question_id INT REFERENCES edu.questions(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  is_correct BOOLEAN DEFAULT FALSE,
  order_index INT
);

CREATE TABLE edu.question_images (
  id SERIAL PRIMARY KEY,
  question_id INT REFERENCES edu.questions(id) ON DELETE CASCADE,
  image_key VARCHAR(100),
  image_url TEXT
);

-- ==========================================
-- 5. QUẢN LÝ ĐỀ THI & GIAO BÀI (EXAMS)
-- ==========================================

CREATE TABLE edu.exam_batches (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  creator_id INT REFERENCES edu.users(id),
  subject_id INT REFERENCES edu.subjects(id),
  
  duration_minutes INT,
  total_points FLOAT,
  
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  
  status VARCHAR(50) DEFAULT 'Bản nháp', -- VD: 'Bản nháp', 'Đang diễn ra', 'Đã kết thúc'
  
  -- Cấu hình hiển thị
  allow_view_score BOOLEAN DEFAULT FALSE,
  allow_view_solution BOOLEAN DEFAULT FALSE,
  min_score_to_view FLOAT,
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- 6. MA TRẬN ĐỀ THI (EXAM MATRICES)
-- ==========================================

CREATE TABLE edu.exam_matrices (
  id SERIAL PRIMARY KEY,
  exam_batch_id INT REFERENCES edu.exam_batches(id) ON DELETE CASCADE,
  
  chapter_id INT REFERENCES edu.chapters(id),
  lesson_id INT REFERENCES edu.lessons(id),
  knowledge_unit_id INT REFERENCES edu.knowledge_units(id),
  
  level_recognition INT DEFAULT 0,    -- Nhận biết
  level_understanding INT DEFAULT 0,  -- Thông hiểu
  level_application INT DEFAULT 0,    -- Vận dụng
  level_high_application INT DEFAULT 0, -- Vận dụng cao
  
  type_multiple_choice INT DEFAULT 0, -- Trắc nghiệm
  type_essay INT DEFAULT 0,           -- Tự luận
  type_true_false INT DEFAULT 0,      -- Đúng/Sai
  type_fill_blank INT DEFAULT 0,      -- Điền khuyết
  
  total_points FLOAT DEFAULT 0,

  CONSTRAINT check_knowledge_target CHECK (
    (chapter_id IS NOT NULL) OR (lesson_id IS NOT NULL) OR (knowledge_unit_id IS NOT NULL)
  )
);

-- ==========================================
-- 7. LIÊN KẾT ĐỀ THI
-- ==========================================

CREATE TABLE edu.exam_class_assignments (
  id SERIAL PRIMARY KEY,
  exam_batch_id INT REFERENCES edu.exam_batches(id) ON DELETE CASCADE,
  class_id INT REFERENCES edu.classes(id),
  assigned_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE edu.exam_questions (
  id SERIAL PRIMARY KEY,
  exam_batch_id INT REFERENCES edu.exam_batches(id) ON DELETE CASCADE,
  question_id INT REFERENCES edu.questions(id),
  score_in_exam FLOAT,
  order_index INT
);

-- ==========================================
-- 8. LỊCH DẠY (SCHEDULE)
-- ==========================================

CREATE TABLE edu.schedules (
  id SERIAL PRIMARY KEY,
  class_id INT REFERENCES edu.classes(id),
  lesson_id INT REFERENCES edu.lessons(id),
  teacher_id INT REFERENCES edu.users(id),
  
  date DATE NOT NULL,
  week_day VARCHAR(20), -- Lưu string tiếng Việt: 'Thứ Hai', 'Thứ Ba'...
  
  start_period INT,
  end_period INT,
  
  note TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);