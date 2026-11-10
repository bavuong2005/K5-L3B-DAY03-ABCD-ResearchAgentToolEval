# Báo cáo cá nhân — Mai Lê Bá Vương (2A202603872)

## 1. Thông tin thành viên

- Họ tên: Mai Lê Bá Vương
- MSSV: 2A202603872
- Email: 26ai.vuongmlb@vinuni.edu.vn
- GitHub: noobpyno
- Vai trò: Điều phối; baseline và tối ưu prompt/tool declaration (CP1–CP2); đồng bộ báo cáo và tích hợp nhánh.

## 2. Phần việc phụ trách

- Chia việc ban đầu theo checkpoint cho nhóm A/B/C/D và theo dõi bằng chứng cần có trong báo cáo.
- Dựng môi trường và chạy chuỗi eval baseline v0, các phiên bản v1–v3 bằng cùng một model Ollama `qwen2.5:7b` để số liệu có thể so sánh.
- Phân tích lỗi từ run JSON, đề xuất thay đổi prompt/tool declaration theo từng vòng và cập nhật version log.
- Tích hợp nhánh thành viên vào `MaiLeBaVuong`, rà soát run và đồng bộ báo cáo với bằng chứng thực tế.

## 3. Đóng góp cụ thể

### 3.1. Baseline và tối ưu (CP1–CP2)

| Version | Thay đổi | Case accuracy | Kết quả |
|---|---|---:|---|
| v0 | Baseline Ollama `qwen2.5:7b` | 0.40 | Mốc so sánh ban đầu |
| v1 | Sửa `system_prompt.md`: bỏ chỉ dẫn đoán khi thiếu dữ kiện/gửi chưa xác nhận; thêm clarify và xác nhận trước send | 0.50 | Tăng 0.10 |
| v2 | Thêm quy tắc routing cho timeline, social search, web lookup, fetch và ngữ cảnh nhiều lượt | 0.55 | Tăng 0.05 |
| v3 | Viết rõ mô tả tool, trường hợp nên/không nên dùng và quy ước tham số trong `tools.yaml` | 0.65 | Tăng 0.10 |

Toàn bộ chuỗi dùng Ollama `qwen2.5:7b`; các run canonical đo đủ 20/20 case và không có provider error. Những lỗi còn lại ở v3 được giữ trong B2 để phản ánh giới hạn quan sát được, gồm nhầm handle, chưa hỏi `clarify` ở một số yêu cầu thiếu dữ kiện và chưa luôn chọn `topic=news`.

### 3.2. Quản lý bằng chứng và tích hợp

- Ghi version, artifact, hash, giả thuyết, metric trước/sau và run file vào `starter_v0/artifacts/version_log.csv`.
- Cập nhật group report để B1 khớp run canonical và B2 nêu lỗi dựa trên tool call thực tế.
- Kiểm tra các file run trùng/gắn nhãn sai bằng hash và kết quả. Hai file gắn nhãn v1/v2 nhưng nội dung không tương ứng với canonical version đã được loại bỏ; các run có giá trị lặp lại vẫn được giữ làm bằng chứng tái lập.
- Tích hợp nhánh các thành viên vào `MaiLeBaVuong` để review chung trước khi nộp.

## 4. Bằng chứng

- **Run JSON:**
  - v0: [`v0_B_base_ollama_20261110T182017764830.json`](../../starter_v0/runs/v0_B_base_ollama_20261110T182017764830.json)
  - v1: [`v1_B_base_ollama_20261110T184929994451.json`](../../starter_v0/runs/v1_B_base_ollama_20261110T184929994451.json)
  - v2: [`v2_B_base_ollama_20261110T185141794941.json`](../../starter_v0/runs/v2_B_base_ollama_20261110T185141794941.json)
  - v3: [`v3_B_base_ollama_20261110T185437173292.json`](../../starter_v0/runs/v3_B_base_ollama_20261110T185437173292.json)
- **Version log:** [`version_log.csv`](../../starter_v0/artifacts/version_log.csv)
- **Báo cáo nhóm:** [`group_report.md`](group_report.md), B1/B2 và phần tóm tắt CP3.
- **Commits:** `d89fa72` (ghi kết quả CP1/CP2), `62c76ed` (đồng bộ báo cáo với run canonical), `3f317be` (loại hai run gắn nhãn sai).
- **Repo/nhánh:** [K5-L3B-DAY03-ABCD-ResearchAgentToolEval](https://github.com/bavuong2005/K5-L3B-DAY03-ABCD-ResearchAgentToolEval), `MaiLeBaVuong`.
- **Tự kiểm tra:** so khớp metric và số case đo được với run JSON, xác nhận `provider_error_cases=0` cho chuỗi canonical, đối chiếu version/hash với `version_log.csv`, kiểm tra diff Git.
- **Công cụ:** Python eval runner, Ollama `qwen2.5:7b`, Git/PowerShell và trợ lý AI để rà soát; kết quả được đối chiếu trực tiếp với run JSON và artifact trong repo.

## 5. Tự đánh giá

- Làm tốt: dùng cùng provider/model cho chuỗi baseline và cải tiến; mỗi phiên bản có giả thuyết, hash và run riêng; sửa báo cáo theo bằng chứng thay vì suy luận từ điểm tổng.
- Cần cải thiện: nên thống nhất quy tắc đặt tên run và lưu log ngay từ đầu để tránh file chạy lại bị gắn nhãn nhầm; một số lỗi routing và tham số vẫn còn ở v3, cần thêm vòng prompt/few-shot và đo lại nếu có thời gian.
