# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: <!-- ĐIỀN -->
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: OpenRouter — `openai/gpt-4o-mini` <!-- sửa nếu nhóm đổi provider/model -->

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent: nhận yêu cầu của người dùng, tự chọn tool phù hợp (tìm tin theo từ khóa, xem bài đăng gần đây của một tài khoản, đọc URL, tra chính sách nội bộ, tìm paper arXiv), biết hỏi lại khi thiếu thông tin, tổng hợp kết quả thành digest markdown, và chỉ gửi bản tin lên Telegram sau khi người dùng xác nhận rõ ràng.

**Cách chạy UI:**

```powershell
cd starter_v0
pip install -r requirements.txt   # đã thêm streamlit>=1.30.0
streamlit run app.py              # mở http://localhost:8501
```

UI ghi transcript JSON vào `starter_v0/transcripts/` cùng format với `chat.py`, nên lượt chat từ UI dùng làm bằng chứng mục B4. Cấu hình provider/model/version ở sidebar. Expose link public bằng Cloudflare Tunnel:

```powershell
cloudflared tunnel --url http://localhost:8501
```

**Link dùng thử (deploy):**

> URL: <!-- DÁN LINK sau khi mở tunnel hoặc deploy -->

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin, dừng chờ lượt trả lời tiếp theo | không |
| timeline | lấy bài đăng gần đây của một tài khoản X (`screenname`) | không |
| social_search | tìm bài đăng theo từ khóa (`search_type`: Top/Latest) | không |
| lookup | tìm trên web qua Tavily (`topic` general/news, có `timeframe`) | không |
| fetch | đọc nội dung một URL qua Firecrawl | không |
| format | trình bày các item đã có thành markdown digest | không |
| send | gửi text lên Telegram channel, chỉ gửi khi `confirmed=true` | không |
| policy | tìm trong company policy markdown nội bộ | không |
| papers | tìm paper trên arXiv | không |
| paper_text | tải PDF arXiv và trích text cục bộ | không |
| <!-- tool mới --> | <!-- điền khi nhóm viết xong --> | có |

### A3. Câu hỏi mẫu để thử

1. "Tìm 3 tin mới nhất về OpenAI trong tuần này, rồi tóm tắt thành digest." — kiểm tra routing `lookup` + `format`.
2. "Xem timeline gần đây của tài khoản sama và chỉ ra 2 bài đăng đáng chú ý." — kiểm tra `timeline`.
3. "Đọc https://openai.com/research/ và tóm tắt 5 điểm chính." — kiểm tra `fetch`.
4. "Tóm tắt giúp tôi bài này với." (không nói URL) — agent phải hỏi lại qua `clarify` thay vì đoán.
5. "Gửi bản tin tóm tắt vừa rồi lên Telegram cho nhóm." — agent phải hỏi xác nhận trước khi gọi `send`, và chỉ gửi khi `confirmed=true`.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
