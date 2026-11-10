# Báo cáo cá nhân — Cung Đức Anh (2A202603814)

## 1. Thông tin thành viên

- Họ tên: Cung Đức Anh
- MSSV: 2A202603814
- Email: 26ai.anhcd2@vinuni.edu.vn
- Vai trò: Phụ trách Xây dựng Tool mới & Unit Test (Checkpoint 3)

## 2. Phần việc phụ trách

- Thiết kế và phát triển tool mới cho Research Agent (`github_search`).
- Định nghĩa contract kỹ thuật (`TOOL.md`) và khai báo tool schema trong `artifacts/tools.yaml`.
- Đăng ký tool vào hệ thống (`tools/__init__.py`).
- Viết 3 unit test hoàn chỉnh (happy path, bad input, failure path) trong `tests/test_tools_todo.py` đảm bảo chạy offline và tuân thủ contract.
- Phối hợp với mảng Eval & Phân tích lỗi của nhóm để cung cấp định dạng tool name và args chuẩn cho bộ test case trong `data/eval_group.json`.

## 3. Đóng góp cụ thể

1. **Xây dựng module `github_search` (`tools/github_search/tool.py`)**:
   - Sử dụng GitHub REST API công khai (`/search/repositories`) để tìm kiếm mã nguồn mở, framework, thư viện theo từ khóa và bộ lọc ngôn ngữ.
   - Cơ chế sắp xếp theo `stars` giảm dần, giới hạn kết quả an toàn.
   - Xử lý lỗi nghiêm ngặt: kiểm tra input rỗng, bắt toàn bộ ngoại lệ mạng/HTTP và trả về error dict (`err()`) thay vì raise crash hệ thống agent.
2. **Khai báo và đồng bộ contract (`tools/github_search/TOOL.md` & `artifacts/tools.yaml`)**:
   - Định nghĩa frontmatter đầy đủ (`track: bonus`, `kind: live_api`, `provider: GitHub REST API`).
   - Cung cấp description chi tiết hướng dẫn rõ ràng: *khi nào dùng* (tìm kiếm code, repo, framework) và *khi nào không dùng* (tìm tin tức, bài báo khoa học).
3. **Hiện thực trọn vẹn Unit Tests cho toàn bộ hệ thống Tool (`tests/test_tools_todo.py`)**:
   - `test_my_new_tool_*` (3 tests): happy path (mock `fake_http`), bad/empty input (`ValueError`), failure path 500 cho tool mới `github_search`.
   - **Hoàn thành 14 tests cho các tool có sẵn trong hệ thống (Đạt Bonus Test Challenge)**:
     - `clarify`: kiểm thử `response_type="choice"` và `awaiting_user=True`.
     - `format`: kiểm thử gom nhóm `sections`, đánh số `thread` (`1/`, `2/`), xử lý `items=None` và `items=[]` không crash.
     - `send`: kiểm thử guardrail bảo vệ (chỉ gửi khi `confirmed=True`), kiểm tra bắt buộc có biến môi trường token/chat_id.
     - `lookup`: kiểm thử tự động lược bỏ `time_range` khi `timeframe=None`.
     - `fetch`: kiểm thử mapping dữ liệu từ Firecrawl và cắt độ dài tóm tắt chính xác 4000 ký tự.
     - `timeline` & `social_search`: kiểm thử giới hạn `limit`, loại bỏ tweet thiếu ID, truyền đúng `search_type` (Top/Latest).
     - `policy`: kiểm thử query rỗng, bộ lọc `policy_area`, và cơ chế bóc tách prompt injection vào `untrusted_text` thay vì `facts`.
4. **Đóng góp xây dựng bộ Eval nhóm (Checkpoint 4)**:
   - Soạn trọn vẹn 10 case chuẩn (5 single-turn, 5 multi-turn) vào `data/eval_group.json`, bao gồm 6 case kiểm thử tool mới `github_search` (cả đơn lượt và đa lượt chuyển đổi ngữ cảnh).
   - Điền sẵn bảng B3 và bảng B5 (Bonus Test Challenge) trong `report/team/group_report.md`.

## 4. Bằng chứng

- **File đã tạo/chỉnh sửa**:
  - `starter_v0/tools/github_search/tool.py`
  - `starter_v0/tools/github_search/TOOL.md`
  - `starter_v0/tools/__init__.py`
  - `starter_v0/artifacts/tools.yaml`
  - `starter_v0/tests/test_tools_todo.py`
  - `starter_v0/data/eval_group.json`
  - `report/team/group_report.md` (Bảng B3, B5a, B5)
  - `TEAM.md`
- **Kết quả kiểm thử (`pytest -v`)**:
  - Toàn bộ test suite đạt **84 passed, 0 skipped, 0 failed** (100% xanh, đạt chuẩn Test Challenge Bonus).
- **AI/công cụ đã dùng**: Antigravity Pair-Programming Assistant, pytest test runner, PowerShell CLI.

## 5. Tự đánh giá

- Hoàn thành xuất sắc 100% mục tiêu của Checkpoint 3 theo Rubric tiêu chí C4 (15/15 điểm).
- Đạt thêm **1 điểm Bonus Test Challenge** (suite 0 skipped, 0 failed) nhờ hoàn thành trọn bộ unit tests cho tất cả tools hệ thống.
- Mã nguồn tuân thủ nguyên tắc thiết kế sạch, an toàn, không rò rỉ network call trong test và đồng bộ hoàn hảo với schema của hệ thống.
