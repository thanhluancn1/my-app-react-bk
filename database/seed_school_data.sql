-- =============================================
-- SEED DATA: 2. QUẢN LÝ TRƯỜNG HỌC, LỚP, HỌC SINH
-- Schema: edu
-- =============================================

-- Set search_path để đảm bảo insert đúng schema
SET search_path TO edu, public;

-- 1. Insert Schools (Trường học)
INSERT INTO edu.schools (name, address, phone) VALUES
('THPT Chu Văn An', '10 Thụy Khuê, Tây Hồ, Hà Nội', '02438233139'),
('THPT Chuyên Hà Nội - Amsterdam', '1 Hoàng Minh Giám, Cầu Giấy, Hà Nội', '02438463096'),
('THPT Yên Hòa', '251 Nguyễn Khang, Cầu Giấy, Hà Nội', '02438333721');

-- 2. Insert Classes (Lớp học)
INSERT INTO edu.classes (school_id, class_name, subject_name, start_year, end_year, status) VALUES
-- Trường Chu Văn An (ID: 1)
(1, '10A1', 'Toán', 2024, 2025, 'Hoạt động'),
(1, '10A2', 'Văn', 2024, 2025, 'Hoạt động'),
(1, '11A1', 'Lý', 2023, 2024, 'Hoạt động'),
-- Trường Amsterdam (ID: 2)
(2, '10 Toán 1', 'Toán', 2024, 2025, 'Hoạt động'),
(2, '11 Anh 1', 'Tiếng Anh', 2023, 2024, 'Hoạt động'),
-- Trường Yên Hòa (ID: 3)
(3, '12D1', 'Toán', 2022, 2023, 'Hoạt động');

-- 3. Insert Students (Học sinh)
INSERT INTO edu.students (class_id, full_name, date_of_birth, email, phone_number, status) VALUES
-- Học sinh lớp 10A1 (Class ID: 1)
(1, 'Nguyễn Văn An', '2009-05-15', 'an.nv@example.com', '0988777666', 'Hoạt động'),
(1, 'Trần Thị Bích', '2009-08-20', 'bich.tt@example.com', '0912345678', 'Hoạt động'),
(1, 'Lê Hoàng Nam', '2009-01-10', 'nam.lh@example.com', '0909000111', 'Hoạt động'),
(1, 'Phạm Thu Trang', '2009-12-05', 'trang.pt@example.com', '0988111222', 'Hoạt động'),

-- Học sinh lớp 10A2 (Class ID: 2)
(2, 'Đỗ Minh Tuấn', '2009-03-25', 'tuan.dm@example.com', '0922333444', 'Hoạt động'),
(2, 'Vũ Thị Mai', '2009-11-02', 'mai.vt@example.com', '0933444555', 'Hoạt động'),

-- Học sinh lớp 10 Toán 1 Am (Class ID: 4)
(4, 'Hoàng Đức Thắng', '2009-06-12', 'thang.hd@example.com', '0944555666', 'Hoạt động'),
(4, 'Ngô Phương Lan', '2009-09-30', 'lan.np@example.com', '0955666777', 'Hoạt động'),
(4, 'Đặng Nhật Minh', '2009-02-14', 'minh.dn@example.com', '0966777888', 'Hoạt động'),

-- Học sinh lớp 12D1 Yên Hòa (Class ID: 6)
(6, 'Bùi Văn Hùng', '2007-04-14', 'hung.bv@example.com', '0977888999', 'Hoạt động');