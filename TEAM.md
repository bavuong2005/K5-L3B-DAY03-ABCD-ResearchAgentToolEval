# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A / L3B
- Repo nhóm: `K5-L3A-DAY03-TenNhom-ResearchAgentToolEval` hoặc `K5-L3B-DAY03-TenNhom-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Cung Đức Anh | 2A202603814 | 26ai.anhcd2@vinuni.edu.vn | | Tool mới & Unit Test (CP3) |
|   2 |        |      |       |        |         |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## CungDucAnh-2A202603814

### Phần việc phụ trách

- Xây dựng Tool mới (`github_search`), đăng ký hệ thống, viết tài liệu `TOOL.md` và 3 unit test (CP3).

### Đóng góp cụ thể

- Tạo module `tools/github_search/tool.py` kết nối GitHub REST API công khai, sort theo stars, lọc theo ngôn ngữ, xử lý lỗi an toàn trả về error dict.
- Định nghĩa contract `tools/github_search/TOOL.md` và khai báo schema trong `artifacts/tools.yaml`.
- Đăng ký tool trong `tools/__init__.py`.
- Hiện thực toàn bộ unit tests trong `tests/test_tools_todo.py` (bao gồm 3 test tool mới + 14 test cho các tool có sẵn), đưa test suite về 84 passed, 0 failed, 0 skipped (đạt điểm Bonus Test Challenge).
- Soạn trọn bộ 10 case eval nhóm vào `data/eval_group.json` và cập nhật bảng B3, B5 trong `report/team/group_report.md`.

### Bằng chứng

- File code: `tools/github_search/tool.py`, `tools/github_search/TOOL.md`, `artifacts/tools.yaml`, `tests/test_tools_todo.py`, `data/eval_group.json`.
- `pytest` kết quả: **84 passed, 0 skipped, 0 failed** (100% xanh).
- Báo cáo chi tiết: `report/team/2A202603814_CungDucAnh.md`.
