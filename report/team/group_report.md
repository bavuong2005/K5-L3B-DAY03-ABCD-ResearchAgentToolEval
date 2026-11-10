# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: <!-- ĐIỀN -->
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: Gemini — `gemini-3.5-flash` <!-- xác nhận lại model/provider thật mà team dùng cho các run v0–v3, sửa lại dòng này cho khớp -->

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent: nhận yêu cầu của người dùng, tự chọn tool phù hợp (tìm tin theo từ khóa, xem bài đăng gần đây của một tài khoản, đọc URL, tra chính sách nội bộ, tìm paper arXiv), biết hỏi lại khi thiếu thông tin, tổng hợp kết quả thành digest markdown, và chỉ gửi bản tin lên Telegram sau khi người dùng xác nhận rõ ràng.

**Cách chạy UI:**

```powershell
cd starter_v0
pip install -r requirements.txt   # đã thêm streamlit>=1.30.0
streamlit run app.py              # mở http://localhost:8501
```

UI ghi transcript JSON vào `starter_v0/transcripts/` cùng format với `chat.py`, nên lượt chat từ UI dùng làm bằng chứng mục B4. Cấu hình provider/model ở sidebar (mục ⚙️ Cấu hình), mỗi phiên giới hạn 15 lượt để tránh tốn quota.

Expose link public — chọn một trong hai cách:

```powershell
# Cách 1: Cloudflare Tunnel (không cần tài khoản)
cloudflared tunnel --url http://localhost:8501

# Cách 2: ngrok (cần tài khoản free + authtoken)
winget install ngrok.ngrok
ngrok config add-authtoken <TOKEN_TU_DASHBOARD>
ngrok http 8501
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
| G01_github_search_python | Tìm repo GitHub với từ khóa và filter language=python, limit=3 | `github_search(query='agent eval', language='python', limit=3)` | PASS |
| G02_github_search_general | Tìm repo trên GitHub không chỉ định ngôn ngữ | `github_search(query='langchain')` | PASS (model tự thêm language=python, không bị chấm vì expect chỉ kiểm query) |
| G03_policy_internal_routing | Hỏi quy định nội bộ công ty -> route tới policy thay vì web search | `policy(policy_area='ai_research')` | PASS |
| G04_missing_github_query | Yêu cầu tìm repo nhưng không có từ khóa -> hỏi lại người dùng | `clarify(response_type='text')` | FAIL `missing_info`: gọi `github_search(query="hay ho", language=python)` thay vì `clarify` (bịa query) |
| G05_out_of_scope_creative | Sáng tác thơ ngoài phạm vi research agent -> từ chối, không gọi tool | `no_tool=true (refuse)` | PASS (từ chối bằng text, không gọi tool) |
| G06_multiturn_github_refine_lang | 2 turns: carry query DeepSeek từ turn 1, thêm language=typescript ở turn 2 | `github_search(query='DeepSeek', language='typescript')` | PASS |
| G07_multiturn_clarify_then_github | 2 turns: user bổ sung query và language ở turn 2 sau khi thiếu ở turn 1 | `github_search(query='RAG evaluation', language='python')` | PASS |
| G08_multiturn_switch_web_to_github | 2 turns: chuyển hướng từ web search sang tìm kiếm repo GitHub cho Llama 3 | `github_search(query='Llama 3')` | PASS |
| G09_multiturn_confirm_send_flow | 2 turns: lượt 1 yêu cầu gửi, lượt 2 user xác nhận -> gọi send | `send(confirmed=true)` | PASS |
| G10_multiturn_paper_then_repo | 2 turns: tìm paper xong chuyển sang tìm repo GitHub triển khai LoRA | `github_search(query='LoRA', language='python')` | FAIL `wrong_arg_value`: route đúng nhưng `query="LoRA Python"` (nhét ngôn ngữ vào query) |

Run: `starter_v0/runs/v3.1_B_group_ollama_20261110T194253447355.json` (ollama qwen2.5:7b, artifact `v3.1+p1df0f2c8faae+t7d687650eba8`, provider_error_cases=0, measured 10/10). Kết quả: **8/10 PASS**, case_accuracy 0.80, tool_routing_accuracy 0.90, multiturn_accuracy 0.80.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/github_search/`) | `starter_v0/tools/github_search/tool.py`, `TOOL.md` | Tìm kiếm repo GitHub theo từ khóa, lọc theo language, sắp xếp stars giảm dần | Xử lý lỗi trả về error dict thay vì raise crash agent; timeout 30s |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`, `pytest` output (0 failed) | 3 unit tests: happy path (mock fake_http), bad/empty input, failure path 500 pass 100% | Chạy offline qua FakeResponse, không gọi mạng thật |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: Đã viết 3 test trong `tests/test_tools_todo.py`. Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: khi model truyền query rỗng (`query="   "`), unit test phát hiện và đảm bảo tool trả về error dict (`ValueError`) an toàn thay vì crash hoặc gửi request rác lên API thật.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `starter_v0/tests/test_tools_todo.py`, `pytest` output (84 passed, 0 skipped) | Đạt 84 passed, 0 failed, 0 skipped toàn bộ suite pytest. Hoàn thành đầy đủ 14 unit tests cho toàn bộ tools hệ thống (clarify, format, send, lookup, fetch, timeline, social_search, policy) + 3 tests cho tool mới github_search | Đảm bảo 100% test chạy offline bằng FakeResponse, không gọi mạng thật |

Test challenge: Toàn bộ suite đạt 84 passed, 0 skipped, 0 failed. Đã kiểm thử đầy đủ các nhánh biên: format rỗng không crash, fetch cắt chuỗi đúng 4000 ký tự, send bắt buộc phải có xác nhận confirmed=true và kiểm tra biến môi trường, timeline bỏ qua item thiếu ID, policy tách biệt dòng chỉ dẫn nguy hiểm (prompt injection) vào untrusted_text thay vì đưa vào facts.

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
