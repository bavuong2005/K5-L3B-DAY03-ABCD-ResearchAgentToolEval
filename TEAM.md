# Team

## Thông tin nhóm

- Tên nhóm: ABCD
- Lớp: L3B
- Repo nhóm: [K5-L3B-DAY03-ABCD-ResearchAgentToolEval](https://github.com/bavuong2005/K5-L3B-DAY03-ABCD-ResearchAgentToolEval)
- URL repo, nhánh nộp, commit chốt: https://github.com/bavuong2005/K5-L3B-DAY03-ABCD-ResearchAgentToolEval

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Cung Đức Anh | 2A202603814 | 26ai.anhcd2@vinuni.edu.vn | cungducanh2712 | Tool mới & Unit Test (CP3) |
| 2 | Mai Lê Bá Vương | 2A202603872 | 26ai.vuongmlb@vinuni.edu.vn | bavuong2005 |baseline, tối ưu prompt/tool declaration (CP1–CP2); đồng bộ báo cáo và tích hợp nhánh |
| 3 | Phạm Thanh An | 2A202603913 | 26ai.anpt3@vinuni.edu.vn | thanhanbk02 | Phân công công việc; chạy eval, tối ưu prompt/tool declaration (CP1, CP2, CP4); tích hợp tool và nhánh |
| 4 | Đỗ Quốc Khánh | 2A202603823 | 26ai.khanhdq2@vinuni.edu.vn | dqk2210 | UI demo, deploy link public, live chat & bằng chứng B4 (CP5) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/team/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

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

## MaiLeBaVuong-2A202603872

### Phần việc phụ trách

- Điều phối nhóm và chia việc theo checkpoint; phụ trách chạy baseline, phân tích lỗi và cải thiện prompt/tool declaration cho CP1–CP2; tổng hợp bằng chứng, đồng bộ báo cáo và tích hợp các nhánh vào nhánh `MaiLeBaVuong`.

### Đóng góp cụ thể

- Dựng môi trường eval và chạy chuỗi Ollama `qwen2.5:7b` nhất quán: baseline v0 đạt 0.40; v1 đạt 0.50; v2 đạt 0.55; v3 đạt 0.65 case accuracy.
- Cập nhật `system_prompt.md` qua v1–v2 và `tools.yaml` ở v3 theo từng giả thuyết; ghi thay đổi, hash, metric và đường dẫn run trong `artifacts/version_log.csv`.
- Đọc `actual_tool_calls` và kết quả từng case để ghi nhận lỗi còn lại, phân biệt kết quả đo hợp lệ với run có provider error.
- Tích hợp đóng góp của thành viên vào nhánh nhóm; đồng bộ B1/B2 và CP2–CP3 trong group report theo run canonical, giữ riêng CP4 để thành viên kiểm tra.
- Đối chiếu các run trùng/mislabel với hash artifact và kết quả; loại hai file gắn nhãn v1/v2 nhưng không phải run canonical, giữ các run có giá trị làm bằng chứng.

### Bằng chứng

- Run hợp lệ: `starter_v0/runs/v0_B_base_ollama_20261110T182017764830.json`, `v1_B_base_ollama_20261110T184929994451.json`, `v2_B_base_ollama_20261110T185141794941.json`, `v3_B_base_ollama_20261110T185437173292.json`.
- Version log: `starter_v0/artifacts/version_log.csv`; báo cáo kết quả: `report/team/group_report.md` (B1, B2 và phần CP3 tương ứng).
- Commits trên nhánh `MaiLeBaVuong`: `d89fa72` (ghi kết quả CP1/CP2), `62c76ed` (đồng bộ báo cáo với run canonical), `3f317be` (dọn hai run gắn nhãn sai).
- GitHub: [bavuong2005/K5-L3B-DAY03-ABCD-ResearchAgentToolEval](https://github.com/bavuong2005/K5-L3B-DAY03-ABCD-ResearchAgentToolEval), nhánh `MaiLeBaVuong`.
- Tự kiểm tra: so metric và `provider_error_cases` trong JSON với version log; xác nhận hash artifact/đường dẫn run; kiểm tra diff và trạng thái Git sau khi tích hợp.

## PhamThanhAn-2A202603913

### Phần việc phụ trách

- Đọc yêu cầu, chia việc theo checkpoint và phân công cho 4 thành viên.
- Dựng môi trường eval Ollama `qwen2.5:7b`; là người duy nhất chạy chuỗi eval v0 → v3 để giữ cùng model và provider.
- Chạy baseline, tối ưu prompt/tool declaration cho CP1–CP2; kiểm tra bộ eval nhóm CP4 và tích hợp tool `github_search`.

### Đóng góp và kết quả

- Chạy các phiên bản trên cùng model: v0 `case_acc=0.40`; v1 `0.50`; v2 `0.55`; v3 `0.65` (`routing_acc=0.85`). Sau khi thêm `github_search`, v3.1 đạt `case_acc=0.60`, `routing_acc=0.85` trên base.
- Ghi giả thuyết, thay đổi artifact, hash và metric vào `starter_v0/artifacts/version_log.csv`; phân tích lỗi từ `actual_tool_calls` và `actual_text` trong run JSON.
- Tích hợp `github_search`, kiểm tra khai báo 10 case group (5 single, 5 multi) và chạy group eval v3.1 đạt **8/10** (case accuracy 0.80, routing 0.90; còn lỗi G04 và G10).
- Xử lý sai lệch hash do LF/CRLF trên Windows bằng `.gitattributes`, chuẩn hóa artifact và chạy lại eval để bảo đảm run khớp hash.

### Bằng chứng

- Run canonical v0–v3 và v3.1: `starter_v0/runs/`; version log: `starter_v0/artifacts/version_log.csv`.
- File thay đổi: `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `.gitattributes`; kết quả CP4 tại bảng B3 của `report/team/group_report.md`.
- Báo cáo cá nhân: `report/team/2A202603913_PhamThanhAn.md`.
- Tự kiểm tra: loại run có provider error hoặc hash artifact không khớp; xem từng case lỗi và chạy lại cùng artifact để xác nhận kết quả có thể tái lập.

## DoQuocKhanh-2A202603823

### Phần việc phụ trách

- Xây dựng UI demo (CP5), deploy link public, chạy live chat và tổng hợp bằng chứng B4 + mục "Khó khăn" của báo cáo nhóm.

### Đóng góp cụ thể

- Dựng `starter_v0/app.py` (Streamlit) tái dùng đúng vòng lặp `chat.py`, transcript từ UI cùng format với CLI để dùng làm bằng chứng.
- Xử lý chuỗi lỗi provider (Gemini 503/429, thiếu key OpenRouter) và chuyển live chat sang OpenRouter model free; deploy ngrok.
- Chạy phiên live chat 6 lượt đủ 3 kịch bản rubric; điền bảng B4, dòng UI ở B5a và 2 dòng khó khăn mới ở mục 5 của `group_report.md`.

### Bằng chứng

- Chi tiết đầy đủ: `report/team/2A202603823_DoQuocKhanh.md`; transcript `starter_v0/transcripts/ui_v3_openrouter_20261111T001056477329.transcript.json` (phiên 6 lượt) và các transcript lỗi 429/403 làm bằng chứng mục 5.
