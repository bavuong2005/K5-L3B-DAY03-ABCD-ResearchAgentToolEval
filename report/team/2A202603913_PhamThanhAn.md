# Báo cáo cá nhân — Phạm Thanh An (2A202603913)

## 1. Thông tin thành viên

- Họ tên: Phạm Thanh An
- MSSV: 2A202603913
- Email: 26ai.anpt3@vinuni.edu.vn
- GitHub: thanhanbk02
- Vai trò: Phân công công việc · Chạy eval & tối ưu prompt/tool declaration (CP1, CP2, CP4)

## 2. Phần việc phụ trách

- Đọc đề (README, CHECKPOINTS, RUBRIC, SUBMISSION), chia nhỏ công việc theo 5 checkpoint và phân công cho 4 thành viên.
- Dựng môi trường chạy agent bằng model local (Ollama `qwen2.5:7b`); là người **duy nhất chạy eval** của nhóm để mọi số liệu v0 → v3 đo trên cùng một model.
- Chạy baseline v0, tối ưu v1 → v3 (mỗi version một giả thuyết) và ghi `artifacts/version_log.csv`.
- Tích hợp tool mới `github_search` (merge nhánh của Cung Đức Anh), chạy lại base + group eval trên artifact mới (v3.1).
- Merge các nhánh thành viên vào nhánh `PhamThanhAn`, giữ repo nhất quán.

## 3. Đóng góp cụ thể

### 3.1. Chia nhỏ và phân công công việc

Chia lab thành 4 mảng theo lượng công việc hợp lý, mỗi người một nhiệm vụ, phối hợp nhịp nhàng để đẩy nhanh tiến độ nhất có thể.

### 3.2. Dựng môi trường và quyết định provider

- Tạo `.venv`, cài `requirements.txt`, cấu hình `.env` (Tavily, Firecrawl, RapidAPI).
- Thử Gemini trước: model mặc định `gemini-3.8-flash` trả **503 UNAVAILABLE**, run v0 đầu tiên có `provider_error_cases = 20/20` → không hợp lệ, đã loại bỏ.
- Chuyển sang **Ollama local** (`OLLAMA_BASE_URL`, `OLLAMA_MODEL=qwen2.5:7b`), preflight pass (`tool=timeline`).
- Thống nhất với nhóm: **chỉ một người, một model** chạy chuỗi v0 → v3, vì trộn provider giữa các version làm `metric_before/after` không so sánh được (RUBRIC C3).

### 3.3. Baseline v0 và vòng lặp tối ưu v1 → v3 (CP1, CP2)

| Version | File sửa | Giả thuyết | case_acc | routing_acc |
|---|---|---|---:|---:|
| v0 | — (starter) | Đo hành vi chưa tối ưu | 0.40 | 0.55 |
| v1 | `system_prompt.md` | Prompt starter ép model *đoán thay vì hỏi* và *gửi không cần xác nhận* → bỏ 3 chỉ dẫn xấu, thêm rule `clarify` + xác nhận trước `send` | 0.50 | 0.65 |
| v2 | `system_prompt.md` | Model nhầm `social_search` ↔ `lookup` vì prompt không có rule routing → thêm mục *Routing rules* | 0.55 | 0.80 |
| v3 | `tools.yaml` | Description tool quá mơ hồ → viết lại mỗi tool: làm gì / khi nào dùng / khi nào không + convention args (handle không `@`, query ngắn không chứa từ thời gian, `topic=news` cho tin tức, `send` chỉ khi `confirmed=true`) | **0.65** | **0.85** |
| v3.1 | `tools.yaml` | Thêm khai báo `github_search` (CP3), prompt giữ nguyên v3 | 0.60 | 0.85 |

Các quan sát rút ra từ run JSON (không phải cảm giác):

- **v1:** giả thuyết chỉ đúng một phần. R10/R11/R12 vẫn FAIL, nhưng đọc `actual_text` thấy model đã **hỏi lại bằng text** và **không còn tự gửi Telegram** — hành vi đúng hơn, nhưng `qwen2.5:7b` không gọi tool `clarify` nên eval vẫn chấm FAIL. Đây là giới hạn của model nhỏ (Ollama có thể bỏ qua `tool_choice="required"`).
- **v2:** sửa được R13, M06 (routing tăng 0.65 → 0.80), nhưng R08 tụt (model gọi `clarify` cho câu hỏi toán ngoài phạm vi).
- **v3:** sửa R03 (query + topic) và R08 (ghi rõ "ngoài phạm vi thì không gọi tool" trong description `clarify`). Với convention handle, tôi **cố ý dùng ví dụ không có trong eval** (`ylecun`) để tránh học thuộc đáp án; vì vậy R01/M03 vẫn FAIL do model không biết handle thật (`samaltman` thay vì `sama`).
- **v3.1:** thêm `github_search` làm base giảm 1 case (M06: `lookup` đúng tool nhưng `topic=general`) — cùng điểm yếu `topic=news` có sẵn ở R06/M02, không phải nhầm sang tool mới. Ghi trung thực trong `version_log.csv`.
- **Độ ổn định:** chạy lại cùng artifact cho kết quả giống hệt (v0 chạy 2 lần cùng 8/20; group v3.1 chạy 2 lần cùng 8/10, cùng FAIL G04/G10) → `qwen2.5:7b` ở `temperature=0` đủ ổn định để so sánh giữa các version.

### 3.4. Tích hợp tool mới và eval nhóm (CP3, CP4)

- Merge nhánh `CungDucAnh` (tool `github_search`, 10 case `eval_group.json`), kiểm tra `pytest`: **84 passed, 0 skipped**.
- Kiểm tra `eval_group.json` theo yêu cầu CP4: 10 case (5 single + 5 multi), `failure_type` hợp lệ, mọi tool/arg trong `expect` đều được khai báo, 6 case route tới `github_search`.
- Chạy `--suite group`: **8/10 PASS** (case_accuracy 0.80, routing 0.90). Hai case FAIL: G04 (bịa `query="hay ho"` thay vì `clarify`), G10 (route đúng nhưng `query="LoRA Python"`).
- Điền kết quả vào bảng B3 của `group_report.md`.

### 3.5. Sửa lỗi hash do line ending trên Windows

- Sau khi merge, `prompt_hash` đổi dù nội dung `system_prompt.md` không đổi chữ nào. Nguyên nhân: `core.autocrlf=true` đổi LF → CRLF, mà `versioning.py` hash trên raw bytes.
- Thêm `.gitattributes` ép `starter_v0/artifacts/*` dùng LF, chuẩn hoá file → `prompt_hash` trở lại `1df0f2c8faae`. Loại bỏ run group chạy trên file CRLF (hash sai) và chạy lại.

## 4. Bằng chứng

- **Commit kỹ thuật** (nhánh `PhamThanhAn`):
  - `0f6fbf4` — Run checkpoint 2: `system_prompt.md`, `tools.yaml`, `version_log.csv`, run v0–v3
  - `21ad315` — CP4: run group eval (v3.1), `.gitattributes`, bảng B3
  - `54d1b4c` — Run checkpoint 4: run group chạy tay
  - `8eca430`, `650c35e` — merge nhánh `CungDucAnh`, `doquockhanh`
- **Run JSON** (`starter_v0/runs/`, tất cả `provider_error_cases = 0`, `measured_cases = total_cases`):
  - v0: `v0_B_base_ollama_20261110T182017764830.json` (0.40)
  - v1: `v1_B_base_ollama_20261110T184929994451.json` (0.50)
  - v2: `v2_B_base_ollama_20261110T185141794941.json` (0.55)
  - v3: `v3_B_base_ollama_20261110T185437173292.json` (0.65)
  - v3.1 base: `v3.1_B_base_ollama_20261110T194213771032.json` (0.60)
  - v3.1 group: `v3.1_B_group_ollama_20261110T194253447355.json`, `v3.1_B_group_ollama_20261110T195039725271.json` (0.80)
- **File đã sửa:** `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`, `.gitattributes`, `report/team/group_report.md` (B3).
- **AI/công cụ đã dùng:** Claude Code (VS Code) phân tích lỗi tìm hướng fix khi chạy test; Ollama `qwen2.5:7b`; pytest; PowerShell.
- **Cách tự kiểm tra kết quả AI:**
  - Mỗi version kiểm tra `Artifact version` trong output: hash của file vừa sửa phải đổi, file không sửa phải giữ nguyên (phát hiện được run "v1" đầu tiên chỉ đổi nhãn, hash trùng v0 → không dùng làm v1).
  - Chỉ dùng run có `provider_error_cases = 0` và `measured_cases = total_cases` (loại run Gemini 20/20 lỗi).
  - Đọc `actual_tool_calls` / `actual_text` của từng case FAIL trong run JSON trước khi đặt giả thuyết tiếp theo, không dựa vào tóm tắt của AI.
  - Chạy lại tay cùng artifact để xác nhận kết quả tái lập được.
  - Chạy `pytest` (contract test) sau mỗi lần sửa `tools.yaml`.
  - Quét run JSON trước khi commit để chắc không chứa API key trong `.env`.

## 5. Tự đánh giá

- **Làm tốt:** chia việc rõ ràng theo checkpoint và quyền sở hữu file nên các nhánh merge không conflict; giữ được chuỗi v0 → v3 trên cùng một model, mỗi version một giả thuyết, có hash và metric trước/sau; phát hiện và xử lý hai vấn đề làm hỏng bằng chứng (run chỉ đổi nhãn, hash đổi do line ending).
- **Chưa tốt:**
  - Giả thuyết v1 chỉ đúng một phần: mục tiêu R10/R11/R12 chưa PASS vì model nhỏ hỏi lại bằng text thay vì gọi `clarify`. Chưa thử few-shot hoặc prompt riêng cho model local để khắc phục.
  - `topic=news` vẫn không ổn định (R06, M02, M06) dù đã ghi rõ trong description.
  - Lúc đầu thử nhiều provider làm mất thời gian và để lại vài run thừa trong `runs/` (run "v1" chỉ đổi nhãn, các run chạy lại) — cần dọn bằng commit mới.
- **Bài học:** với model nhỏ, eval chấm *tool call* chứ không chấm *ý định*; một hành vi "đúng" bằng text vẫn là FAIL. Và bằng chứng chỉ có giá trị khi artifact được version hoá chính xác đến từng byte.
