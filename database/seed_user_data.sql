-- =============================================
-- SEED DATA: 1. QUẢN TRỊ HỆ THỐNG & NGƯỜI DÙNG
-- Schema: edu
-- =============================================

SET search_path TO edu, public;

-- Lưu ý: 'password_hash' ở đây chỉ là chuỗi giả lập để demo.
-- Trong thực tế backend (NodeJS/Go/Java), bạn phải dùng thư viện (như bcrypt) 
-- để hash mật khẩu "123456" thật rồi mới insert vào đây.

INSERT INTO edu.users (username, password_hash, full_name, email, phone, avatar_url, role, status) VALUES
-- 1. Admin (Quản trị viên)
('admin', '$2b$10$ExampleHashStringFor123456...', 'Quản Trị Viên Chính', 'admin@aronedu.com', '0901234567', 'https://ui-avatars.com/api/?name=Admin&background=0D8ABC&color=fff', 'admin', 'Hoạt động'),

-- 2. Teachers (Giáo viên bộ môn)
('gv_toan', '$2b$10$ExampleHashStringFor123456...', 'Nguyễn Thầy Toán', 'toan.ng@aronedu.com', '0911112222', 'https://ui-avatars.com/api/?name=Thay+Toan&background=random', 'giáo viên', 'Hoạt động'),
('gv_ly', '$2b$10$ExampleHashStringFor123456...', 'Trần Cô Lý', 'ly.tr@aronedu.com', '0922223333', 'https://ui-avatars.com/api/?name=Co+Ly&background=random', 'giáo viên', 'Hoạt động'),
('gv_hoa', '$2b$10$ExampleHashStringFor123456...', 'Lê Thầy Hóa', 'hoa.le@aronedu.com', '0933334444', 'https://ui-avatars.com/api/?name=Thay+Hoa&background=random', 'giáo viên', 'Hoạt động'),
('gv_anh', '$2b$10$ExampleHashStringFor123456...', 'Phạm Cô Anh', 'anh.ph@aronedu.com', '0944445555', 'https://ui-avatars.com/api/?name=Co+Anh&background=random', 'giáo viên', 'Hoạt động'),

-- 3. Students (Học sinh test)
-- Lưu ý: Thông thường tài khoản học sinh sẽ sinh ra từ mã học sinh, đây là user test đăng nhập
('hs_an', '$2b$10$ExampleHashStringFor123456...', 'Nguyễn Văn An', 'an.nv@example.com', '0988777666', 'https://ui-avatars.com/api/?name=Van+An&background=random', 'học sinh', 'Hoạt động'),
('hs_bich', '$2b$10$ExampleHashStringFor123456...', 'Trần Thị Bích', 'bich.tt@example.com', '0912345678', 'https://ui-avatars.com/api/?name=Thi+Bich&background=random', 'học sinh', 'Hoạt động');

-- 4. User bị khóa (Demo trạng thái)
('gv_cu', '$2b$10$ExampleHashStringFor123456...', 'Giáo Viên Đã Nghỉ', 'old.teacher@aronedu.com', '0999999999', NULL, 'giáo viên', 'Không hoạt động');