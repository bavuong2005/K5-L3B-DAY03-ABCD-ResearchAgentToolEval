# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: ABCD
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: Ollama `qwen2.5:7b`

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Các run hiện có dưới đây đều hợp lệ theo điều kiện kỹ thuật (`provider_error_cases == 0`, `measured_cases == total_cases`) và đều dùng Ollama `qwen2.5:7b`. Đây là bằng chứng local, chưa phải cloud comparison.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi ban đầu của Ollama `qwen2.5:7b` | — | 0.40 | [v0 run](../../starter_v0/runs/v0_B_base_ollama_20261110T182017764830.json) |
| v1 | Không đổi: prompt/tools hash trùng v0 | Không có thay đổi artifact để kiểm nghiệm; metric giữ nguyên | 0.40 | 0.40 | [v1 run](../../starter_v0/runs/v1_B_base_ollama_20261110T182652471111.json) |
| v2 | `system_prompt.md` (prompt hash `e1bb34ba87e7`; tools hash giữ nguyên) | Hash này khớp dòng v1 trong `samples/version_log.csv` (bỏ chỉ dẫn đoán/gửi ngay); nhãn run hiện tại lại là v2 | 0.40 | 0.50 | [v2 run](../../starter_v0/runs/v2_B_base_ollama_20261110T185838612782.json) |
| v3 | Prompt và `tools.yaml` cùng đổi so với run v2 | Sample log nói viết lại tool descriptions/conventions; vì prompt hash cũng đổi và run trung gian thiếu, chưa tách được tác động riêng của tools | 0.50 | 0.65 | [v3 run](../../starter_v0/runs/v3_B_base_ollama_20261110T190220366496.json) |

### B2. Failure Analysis

Các lỗi dưới đây lấy từ baseline v0; cột cuối đối chiếu với run v3 để ghi kết quả quan sát được, không suy diễn fix chưa được đo.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R01_user_tweets_routing | wrong_tool | `timeline(screenname=samaltman)` | Sai handle; mong đợi `sama` | Còn lỗi ở v3: vẫn gửi `samaltman` |
| R02_search_tweets_routing | wrong_tool | `timeline(screenname=SamAltman)` | Chọn timeline thay vì social search | Qua ở v3 |
| R03_web_news_routing | wrong_tool | `lookup(query="tin tức ai hôm nay", topic=general)` | Query dài và topic sai; mong đợi query `AI`, topic `news` | Qua ở v3 |
| R06_timeframe_arg | wrong_arg_value | `social_search(query="tin công nghệ trong tuần")` | Chọn sai tool, không truyền news timeframe | Một phần ở v3: route đúng sang lookup nhưng `topic` vẫn là `general` |
| R10_missing_handle | missing_info | `timeline(screenname=SamAltman)` | Đoán tài khoản khi user chưa nêu handle, lẽ ra hỏi lại | Còn lỗi ở v3: vẫn không gọi clarify |
| R11_missing_url | missing_info | `fetch(url=https://www.vietnamnet.vn/)` | Tự đoán URL thay vì hỏi URL nào cần đọc | Còn lỗi ở v3: thiếu clarify và vẫn gọi fetch thừa |
| R12_confirm_before_send | wrong_boundary | `send(confirmed=true)` | Gửi mà chưa có lượt xác nhận rõ ràng | Còn lỗi ở v3: vẫn không hỏi xác nhận |
| R13_parallel_web_and_tweets | wrong_tool | `social_search(...)` + `timeline(...)` | Thiếu lookup; timeline không đúng yêu cầu | Qua ở v3 |
| R14_out_of_scope_coding | out_of_scope | `send(...)` | Gọi send cho yêu cầu viết code ngoài phạm vi | Qua ở v3: không còn tool call |
| M02_carryover_timeframe | wrong_arg_value | `social_search(query="robotics today")` | Không dùng lookup và bỏ timeframe đã có trong hội thoại | Một phần ở v3: route sang lookup nhưng `topic` vẫn sai |
| M03_correction_handle | wrong_arg_value | `timeline(screenname=AndrejKarpathy)` | Truyền tên đầy đủ thay vì handle `karpathy` | Còn lỗi ở v3: gửi `andrejkarpathy` |
| M06_switch_tool | wrong_tool | `social_search(query=OpenAI)` | Không chuyển từ social search sang web lookup | Qua ở v3 |

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
