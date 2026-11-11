# Báo cáo cá nhân — Đỗ Quốc Khánh (2A202603823)

## 1. Thông tin thành viên

- Họ tên: Đỗ Quốc Khánh
- MSSV: 2A202603823
- Email: 26ai.khanhdq2@vinuni.edu.vn
- GitHub: dqk2210
- Vai trò: Xây dựng UI demo, deploy link public, chạy live chat lấy bằng chứng và tổng hợp mục B4 của báo cáo nhóm (CP5).

## 2. Phần việc phụ trách

Mình phụ trách mảng "đưa agent ra cho người khác dùng": dựng giao diện chat chạy được bằng Streamlit, mở link public bằng ngrok để team cùng zone thử, chạy live chat thật để lấy transcript làm bằng chứng, rồi đưa kết quả vào bảng B4 và mục "Khó khăn" của báo cáo nhóm.

## 3. Đóng góp cụ thể

### 3.1. Dựng UI (`starter_v0/app.py`)

Khi bắt đầu, mình đặt ra câu hỏi: UI nên tự gọi API model riêng hay tái dùng đúng vòng lặp của `chat.py`? Nếu viết riêng, UI sẽ "nghe hay" nhưng hành vi agent có thể khác với cái mà nhóm đo bằng eval — bằng chứng trên UI lúc đó không còn ý nghĩa. Nên mình chọn cách giữ nguyên logic: `app.py` import thẳng `run_model_tool_loop`, `trim_history` và `write_transcript` từ `chat.py`. Hệ quả là transcript tạo từ UI có y hệt cấu trúc transcript CLI (đủ `artifact_version`, `prompt_hash`, `tools_hash`, `turns[]`), nên sáu lượt chat live trong B4 dùng làm bằng chứng được luôn mà không cần chỉnh gì.

Về mặt giao diện, mình dựng sidebar gồm: nút cuộc chat mới, mục "Thử nhanh" với các câu hỏi bấm là gửi ngay (có cả câu cố ý thiếu URL để kiểm agent có hỏi lại không), danh sách tool đọc trực tiếp từ `artifacts/tools.yaml`, và bảng "Phiên bản" hiển thị model đang dùng, hash artifact và trạng thái Telegram. Phần danh sách tool đọc từ `tools.yaml` là cố ý: khi Đức Anh merge tool `github_search` vào, UI hiện đúng 11 tool mà mình không phải sửa một dòng nào. Mỗi phiên cũng bị chặn ở 15 lượt, hết lượt thì khóa ô nhập — lý do là khi mở link public, không ai muốn người lạ đốt sạch quota model của nhóm trong một buổi demo.

### 3.2. Những lỗi gặp phải và cách xử lý

Ba lỗi đáng nhớ nhất:

- **`StreamlitWidgetAlreadyInstantiatedError`**: bản Streamlit 1.67 không cho gán tay vào `st.session_state` của widget sau khi widget đó đã tạo. Ban đầu mình gán lại giá trị slider vào session state nên app chết ngay lần đầu mở. Sửa bằng cách bỏ phần gán thừa, để widget tự quản lý state của nó.
- **Chữ trắng trên nền trắng**: máy mình bật dark mode nên Streamlit render nền tối trong khi CSS của app khóa màu sáng, nhìn không đọc được gì. Cách xử lý triệt để là thêm `.streamlit/config.toml` với `base = "light"` để ép theme sáng cố định, kết hợp CSS khóa màu chữ, thay vì thử sửa từng màu trong CSS rồi đón đoán dark mode của từng máy.
- **Chuỗi lỗi provider khi demo**: Gemini `gemini-3.8-flash` trả `503 UNAVAILABLE` (quá tải), đổi sang model khác thì dính `429 RESOURCE_EXHAUSTED` vì free tier của Google chỉ cho 20 request/ngày cho mỗi model, tính theo cả project — nghĩa là tạo key mới trong project cũ cũng vô ích, điều mình phát hiện sau khi mất một lúc chiều. Cuối cùng mình chuyển live chat sang OpenRouter với model free `nvidia/nemotron-3.5-super-vl:free` và phiên chat chạy đủ 6 lượt. Chuỗi lỗi này (kèm transcript) được ghi đầy đủ vào mục 5 của báo cáo nhóm.

### 3.3. Live chat và bằng chứng B4

Mình chạy phiên live chat 6 lượt đủ cả ba kịch bản rubric yêu cầu: yêu cầu research bình thường (lượt 1, 4, 5), yêu cầu thiếu thông tin, và yêu cầu gửi Telegram. Lượt 6 là lượt mình thấy đáng giá nhất: khi yêu cầu "đăng bản tin lên Telegram", agent không gửi ngay mà gọi `clarify` hỏi xác nhận rồi dừng chờ (`waiting_for_user`) — đúng boundary nhóm đã sửa trong v1. Riêng lượt 2 và 3, tool `social_search`/`timeline` bị API Twitter trả 403 Forbidden; model chọn đúng tool và truyền đúng args nên đây là lỗi dịch vụ bên ngoài, agent cũng trả lời trung thực và đề xuất dùng `lookup` thay vì bịa tweet. Toàn bộ được mình điền vào bảng B4 với cột "Version Evidence" trỏ về artifact `v3+p1df0f2c8faae+t7d687650eba8` của từng lượt, cộng thêm hai dòng khó khăn mới (429 quota, 403 Twitter) trong mục 5.

### 3.4. Deploy link public

Máy có sẵn ngrok 3.39 nên mình chỉ cần `ngrok config add-authtoken` rồi `ngrok http 8501`. Vài điều rút ra: link free là URL random mỗi lần chạy nên phải giữ terminal chạy suốt buổi showdown; lần đầu mở link sẽ gặp trang cảnh báo "Visit Site" của ngrok cần bấm qua; và khi dán lệnh có placeholder như `<TOKEN>` vào PowerShell thì dấu `<` bị hiểu là toán tử — lỗi cú pháp nhưng mất vài phút mới nhận ra.

## 4. Bằng chứng

- **Code:** `starter_v0/app.py` (UI), `starter_v0/.streamlit/config.toml` (theme), `starter_v0/requirements.txt` (thêm `streamlit>=1.30.0`).
- **Transcript chính (6 lượt live):** `starter_v0/transcripts/ui_v3_openrouter_20261111T001056477329.transcript.json` — đã phân tích từng lượt trong bảng B4 của [`group_report.md`](group_report.md).
- **Transcript lỗi (giữ lại làm bằng chứng mục 5):** `ui_v3_gemini_20261110T195255407779` và `ui_v3_gemini_20261110T195544921562` (429 RESOURCE_EXHAUSTED), `ui_v3_openrouter_20261111T000929525507` (thiếu `OPENROUTER_API_KEY` khi chưa cấu hình).
- **Commits** (nhánh `doquockhanh`): `23eb062` (dựng UI `app.py`, theme, thêm streamlit vào requirements), `52c5061` (báo cáo cá nhân, cập nhật TEAM.md, bằng chứng B4 + transcripts live chat).
- **AI/công cụ đã dùng:** mình dùng trợ lý AI (opencode) để dựng khung `app.py`, viết CSS và dò lỗi Streamlit; cũng dùng nó để đối chiếu transcript JSON với bảng B4 trước khi điền.
- **Cách tự kiểm tra kết quả AI:** mình không tin chạy-code-then-forget. Cụ thể: (1) dùng `streamlit.testing.v1.AppTest` để chạy app như trình duyệt thật — bắt exception, đổi giá trị slider, bấm nút, và set `turns_used = 15` trong session state để xác nhận ô nhập bị khóa khi hết lượt mà không cần tốn request API nào; (2) chạy `pytest` sau mỗi lần sửa để chắc contract test vẫn xanh; (3) chạy `scripts/preflight_provider.py` cho từng model trước khi chat thật để biết model nào còn quota; (4) đọc lại transcript JSON bằng tay để so tool call thực tế với những gì mình viết vào B4 — đặc biệt là xác nhận lượt 6 thực sự dừng ở `clarify` chứ không gửi message nào ra ngoài Telegram.

## 5. Tự đánh giá

- **Làm tốt:** UI tái dùng nguyên vòng lặp có sẵn nên bằng chứng từ UI và từ CLI nhất quán với nhau; nhờ đọc `tools.yaml` trực tiếp nên việc thêm tool mới của nhóm không phải đụng vào UI; ghi nhận lỗi (429, 403, thiếu key) thành bằng chứng thay vì xóa đi chạy lại cho "đẹp".
- **Chưa tốt:** mình phát hiện giới hạn 20 request/ngày của Gemini hơi muộn, đúng lúc đang demo nên phải đổi provider giữa chừng — lần sau phải preflight cả giới hạn quota trước ngày demo, không chỉ preflight key còn hạn. Luồng `send` Telegram cũng dừng ở lượt `clarify` vì nhóm chưa cấu hình `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID`, nên chưa có transcript hoàn chỉnh "user xác nhận → `send(confirmed=true)` → `status: sent`" để lấy bonus 2 điểm này.
- **Bài học:** giao diện demo dễ nhất để mất điểm là khi nó che lỗi đi. Bản UI của mình cố tình hiển thị cả lỗi provider nguyên văn trong khung đỏ thay vì bắt lỗi im lặng, vì những lỗi đó chính là bằng chứng cần nộp.
