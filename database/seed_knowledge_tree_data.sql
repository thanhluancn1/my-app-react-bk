-- =================================================================
-- SEED DATA: 3. CÂY KIẾN THỨC
-- Schema: edu
-- =================================================================

SET search_path TO edu, public;

-- 1. Insert Grade Levels (dùng grade_level_name)
INSERT INTO edu.grade_levels (grade_level_name, value) VALUES
('Khối 6', 6),
('Khối 7', 7),
('Khối 8', 8),
('Khối 9', 9),
('Khối 10', 10),
('Khối 11', 11),
('Khối 12', 12)
ON CONFLICT DO NOTHING;

-- 2. Insert Subjects (dùng subject_name)
INSERT INTO edu.subjects (grade_level_id, subject_name)
SELECT grade_level_id, unnest(ARRAY['Toán', 'Vật lí', 'Hóa học', 'Sinh học', 'Lịch sử', 'Địa lí'])
FROM edu.grade_levels
WHERE value BETWEEN 6 AND 12;

-- 3. Insert Sách giáo khoa mẫu (dùng book_name)
INSERT INTO edu.books (subject_id, book_name)
SELECT s.subject_id, 'Kết nối tri thức'
FROM edu.subjects s
JOIN edu.grade_levels g ON s.grade_level_id = g.grade_level_id
WHERE g.value = 10; 

-- 4. Insert Chương mẫu (dùng chapter_name)
INSERT INTO edu.chapters (book_id, chapter_name, order_number)
SELECT b.book_id, 'Chương 1: Mệnh đề và Tập hợp', 1
FROM edu.books b
JOIN edu.subjects s ON b.subject_id = s.subject_id
JOIN edu.grade_levels g ON s.grade_level_id = g.grade_level_id
WHERE g.value = 10 AND s.subject_name = 'Toán';

INSERT INTO edu.chapters (book_id, chapter_name, order_number)
SELECT b.book_id, 'Chương 2: Bất phương trình', 2
FROM edu.books b
JOIN edu.subjects s ON b.subject_id = s.subject_id
JOIN edu.grade_levels g ON s.grade_level_id = g.grade_level_id
WHERE g.value = 10 AND s.subject_name = 'Toán';