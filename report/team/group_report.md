# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: ABCD
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: Ollama `qwen2.5:7b`; live chat UI: OpenRouter `nvidia/nemotron-3.5-super-vl:free`

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

> URL: https://catcher-relock-october.ngrok-free.dev

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
| github_search | Tìm repository GitHub theo từ khóa, có thể lọc theo ngôn ngữ và giới hạn số kết quả | Có (`github_search`, CP3) |

### A3. Câu hỏi mẫu để thử

1. "Tìm 3 tin mới nhất về OpenAI trong tuần này, rồi tóm tắt thành digest." — kiểm tra routing `lookup` + `format`.
2. "Xem timeline gần đây của tài khoản sama và chỉ ra 2 bài đăng đáng chú ý." — kiểm tra `timeline`.
3. "Đọc https://openai.com/research/ và tóm tắt 5 điểm chính." — kiểm tra `fetch`.
4. "Tóm tắt giúp tôi bài này với." (không nói URL) — agent phải hỏi lại qua `clarify` thay vì đoán.
5. "Gửi bản tin tóm tắt vừa rồi lên Telegram cho nhóm." — agent phải hỏi xác nhận trước khi gọi `send`, và chỉ gửi khi `confirmed=true`.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

- **v1 — `system_prompt.md`:** bỏ chỉ dẫn starter yêu cầu đoán khi thiếu thông tin, gửi ngay không cần xác nhận và ép xử lý một bước; thêm cách dùng `clarify` và xác nhận trước `send`. Case accuracy tăng từ **0.40 lên 0.50**.
- **v2 — `system_prompt.md`:** thêm quy tắc chọn `timeline`, `social_search`, `lookup`, `fetch`; gọi song song khi cần web và mạng xã hội; giữ chỉ dẫn mới nhất trong hội thoại nhiều lượt. Case accuracy tăng từ **0.50 lên 0.55**.
- **v3 — `tools.yaml`:** viết lại mô tả công cụ, điều kiện dùng/không dùng và quy ước tham số như handle, `topic=news`, timeframe; giữ xác nhận rõ ràng trước `send`. Case accuracy tăng từ **0.55 lên 0.65**.
- **CP3 — `github_search`:** tool mới tìm repository GitHub theo từ khóa, tùy chọn lọc ngôn ngữ và số kết quả; dùng cho yêu cầu tìm code/repo/framework, không dùng cho tin tức, mạng xã hội hoặc bài báo arXiv. Tool đã được đăng ký trong `tools/__init__.py` và `tools.yaml`; có 3 unit test trong `tests/test_tools_todo.py`.
- Các số CP2 trên lấy từ chuỗi run Ollama `qwen2.5:7b` hợp lệ, 20/20 case và 0 provider error; xem B1. v3.1 là lượt tích hợp tool mới, không gộp vào chuỗi CP2 v0–v3.
## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Các run hiện có dưới đây đều hợp lệ theo điều kiện kỹ thuật (`provider_error_cases == 0`, `measured_cases == total_cases`) và đều dùng Ollama `qwen2.5:7b`. Đây là bằng chứng local, chưa phải cloud comparison.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi ban đầu của Ollama `qwen2.5:7b` | — | 0.40 | [v0 run](../../starter_v0/runs/v0_B_base_ollama_20261110T182017764830.json) |
| v1 | `system_prompt.md` (prompt hash `e1bb34ba87e7`; tools hash giữ nguyên) | Bỏ chỉ dẫn xấu, thêm clarify/xác nhận trước send | 0.40 | 0.50 | [v1 canonical run](../../starter_v0/runs/v1_B_base_ollama_20261110T184929994451.json) |
| v2 | `system_prompt.md` (prompt hash `1df0f2c8faae`; tools hash giữ nguyên) | Thêm routing rules, gọi song song khi cần và giữ chỉ dẫn mới nhất ở multi-turn | 0.50 | 0.55 | [v2 canonical run](../../starter_v0/runs/v2_B_base_ollama_20261110T185141794941.json) |
| v3 | `tools.yaml` (prompt hash giữ `1df0f2c8faae`; tools hash `ccdab12edb30`) | Mô tả rõ cách dùng và quy ước args của từng tool | 0.55 | 0.65 | [v3 canonical run](../../starter_v0/runs/v3_B_base_ollama_20261110T185437173292.json) |

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

Lấy từ `starter_v0/transcripts/ui_v3_openrouter_20261111T001056477329.transcript.json` — phiên qua UI Streamlit, provider OpenRouter, model `nvidia/nemotron-3.5-super-vl:free`, artifact `v3+p1df0f2c8faae+t7d687650eba8`. Phiên gồm 6 lượt, đủ 3 kịch bản yêu cầu: research thường, thiếu thông tin/hỏi lại, và yêu cầu gửi có xác nhận.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Hôm nay có tin AI nào đáng chú ý? Tóm tắt giùm mình." | `lookup(query="AI", topic="news", timeframe="day", max_results=8)` → `format(items=8)` | `v3+p1df0f2c8faae+t7d687650eba8` | PASS — trả digest tin AI 10/11/2026 có kèm nguồn |
| 2 | "Twitter/X đang nói gì về OpenAI dạo gần đây?" | `social_search(query="OpenAI", search_type="Latest", limit=10)` | `v3+p1df0f2c8faae+t7d687650eba8` | Tool API X/Twitter trả 403 Forbidden; agent thông báo lỗi trung thực và đề xuất dùng `lookup` web thay thế, không bịa dữ liệu |
| 3 | "Cho mình xin timeline mới nhất của tài khoản sama." | `timeline(screenname="sama", limit=10)` | `v3+p1df0f2c8faae+t7d687650eba8` | 403 tương tự (lỗi API bên ngoài, xem mục 5); agent handle đúng handle không có `@` và đề xuất phương án thay |
| 4 | "Tìm paper arXiv về tool calling của AI agent." | `papers(query="AI agent tool calling", max_results=5, sort_by="submittedDate")` | `v3+p1df0f2c8faae+t7d687650eba8` | PASS — liệt kê 5 paper kèm tác giả, ngày nộp |
| 5 | "Đọc bài tại openai.com/research rồi rút 5 ý chính." | `fetch(url="https://openai.com/research")` | `v3+p1df0f2c8faae+t7d687650eba8` | PASS — rút 5 ý chính có dẫn nguồn |
| 6 | "Đăng bản tin tóm tắt lên Telegram kênh của nhóm nha." | `clarify(response_type="yes_no", question="Bạn có đồng ý gửi bản tin...")` | `v3+p1df0f2c8faae+t7d687650eba8` | PASS boundary — agent KHÔNG gửi ngay, hỏi xác nhận trước (status `waiting_for_user`), chỉ gửi khi user trả lời đồng ý |

Lưu ý: lượt 2 và 3 lỗi 403 là do API Twitter API45 bên ngoài (không phải lỗi routing của agent — model chọn đúng tool, truyền đúng args), đã ghi chi tiết ở mục 5.

**Phiên bổ sung — hành vi khi agent trả lời "không làm được" và user gợi ý hướng khác:** `transcripts/ui_v3_openrouter_20261111T092939065330.transcript.json` (cùng artifact `v3+p1df0f2c8faae+t7d687650eba8`, OpenRouter `nvidia/nemotron-3.5-super-vl:free`).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Cho mình xin timeline mới nhất của tài khoản sama." | `timeline(screenname="sama", limit=10)` | `v3+p1df0f2c8faae+t7d687650eba8` | Tool trả 403 Forbidden → agent trả lời trung thực "không thể lấy lúc này", giải thích nguyên nhân và đề xuất 2 lựa chọn (thử handle khác / tìm trên web), không bịa tweet |
| 2 | "bạn có thể thử lại với 1 tài khoản nào hay tìm kiếm Sam trên web khác" | `lookup(query="Sam Altman", topic="news", timeframe="week", max_results=5)` | `v3+p1df0f2c8faae+t7d687650eba8` | PASS multi-turn recovery — agent hiểu user chọn hướng web, tự chuyển từ `timeline` sang `lookup`, tự điền `topic="news"` và `timeframe="week"` từ ngữ cảnh lượt trước, trả tin Sam Altman có nguồn |

Quan sát: sau khi agent trả lời "không biết/không làm được", chất lượng của lượt reply tiếp theo phụ thuộc vào việc agent có đề xuất lựa chọn rõ ràng hay không — ở đây agent liệt kê 2 hướng nên user chỉ cần chọn bằng một câu tự nhiên, và agent route lại đúng tool với arguments hợp lệ mà không cần user nhắc lại chi tiết.

**Phiên 3 — "Thiếu thông tin rồi bổ sung" (kịch bản C6):** `transcripts/ui_v3_openrouter_20261111T112706061259.transcript.json` (cùng artifact `v3+p1df0f2c8faae+t7d687650eba8`).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Tóm tắt giúp mình một bài báo hay với." (cố ý không kèm URL) | `clarify(response_type="text", question="Bạn muốn tóm tắt bài báo nào? Vui lòng gửi link...")` | `v3+p1df0f2c8faae+t7d687650eba8` | PASS missing_info — agent không đoán URL (khác hẳn hành vi đoán của v0 ở baseline, xem case R11/B2), hỏi lại và dừng chờ user |
| 2 | "Bài này nè mình quên đưa link: https://openai.com/research/" | `fetch(url="https://openai.com/research/")` → `clarify(question="Trang ... là danh sách nhiều bài nghiên cứu... Bạn muốn tóm tắt bài nào cụ thể?")` | `v3+p1df0f2c8faae+t7d687650eba8` | PASS — dùng URL vừa bổ sung để đọc trang; nhận ra trang là danh sách nhiều bài (thông tin vẫn chưa đủ cụ thể) nên hỏi tiếp lượt `clarify` thứ hai thay vì tóm tắt cả trang một cách máy móc |

Quan sát: đây đúng kịch bản "thiếu thông tin rồi bổ sung" mà C6 yêu cầu, và lượt 2 cho thấy thêm một hành vi đáng giá — khi thông tin được bổ sung vẫn còn mập mờ, agent tiếp tục hỏi lại thay vì tự quyết định, nhất quán với boundary đã thiết lập từ v1.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/github_search/`) | `starter_v0/tools/github_search/tool.py`, `TOOL.md` | Tìm kiếm repo GitHub theo từ khóa, lọc theo language, sắp xếp stars giảm dần | Xử lý lỗi trả về error dict thay vì raise crash agent; timeout 30s |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`, `pytest` output (0 failed) | 3 unit tests: happy path (mock fake_http), bad/empty input, failure path 500 pass 100% | Chạy offline qua FakeResponse, không gọi mạng thật |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py`, dependency `streamlit>=1.30.0` trong `requirements.txt` | Chạy: `cd starter_v0 && streamlit run app.py`; sidebar có quick questions, danh sách tool, giới hạn 15 lượt/phiên; mỗi lượt tự ghi transcript JSON vào `transcripts/` cùng format `chat.py` (ví dụ phiên B4 ở trên tạo từ UI) | Public bằng `ngrok http 8501`; cấu hình provider/model nằm trong expander ⚙️ để người demo không đổi lung tung |

Tool unit tests: Đã viết 3 test trong `tests/test_tools_todo.py`. Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: khi model truyền query rỗng (`query="   "`), unit test phát hiện và đảm bảo tool trả về error dict (`ValueError`) an toàn thay vì crash hoặc gửi request rác lên API thật.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | `transcripts/ui_v3_openrouter_20261111T105912755727.transcript.json` | Luồng đủ 2 lượt: lượt 1 agent `lookup` → `format` → `clarify` hỏi xác nhận và dừng chờ (`awaiting_user=true`); lượt 2 sau khi user trả lời "Có, gửi đi", agent gọi `send(confirmed=true)` → `status: sent`, bản tin 5 tin AI có nguồn xuất hiện thật trên channel private "ABCD Research Log" | Guardrail 2 lớp: tool chặn mọi lệnh gửi khi `confirmed != true` (trả `needs_confirmation`); chỉ gửi vào channel private của nhóm, `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` nằm trong `.env`, không commit |
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

| Khó khăn | Hướng giải quyết | Bằng chứng / giới hạn |
|---|---|---|
| Gemini không ổn định cho các lượt đo (terminal ghi nhận 404/429; run Gemini lưu trong repo có 3 case `503 UNAVAILABLE`). Run này chỉ đo được 17/20 case nên không hợp lệ làm baseline. | Nhóm chuyển sang Ollama `qwen2.5:7b` để có chuỗi baseline và tối ưu v0–v3 hợp lệ, không phụ thuộc quota cloud. | [Run Gemini lỗi](../../starter_v0/runs/v0_B_base_gemini_20261110T183955462026.json): 3 provider errors, 17/20 measured; **không dùng làm baseline**. Baseline v0 là [run Ollama](../../starter_v0/runs/v0_B_base_ollama_20261110T182017764830.json); các run Ollama canonical v1–v3 được dẫn ở B1, đều 20/20 và 0 provider error.|
| Quota free tier Gemini `gemini-3.6-flash`/`gemini-3.5-flash` chỉ 20 request/ngày — live chat qua UI liên tục gặp `429 RESOURCE_EXHAUSTED` (retry sau ~19h). | Đổi sang OpenRouter với model free `nvidia/nemotron-3.5-super-vl:free` (giới hạn riêng ~50 req/ngày) cho live chat; giảm Max tool rounds xuống 2 để tiết kiệm request. | Transcript lỗi: `transcripts/ui_v3_gemini_20261110T195255407779.transcript.json` (3 turns 429), `ui_v3_gemini_20261110T195544921562.transcript.json`, `ui_v3_openrouter_20261111T000929525507.transcript.json` (thiếu `OPENROUTER_API_KEY` khi chưa cấu hình). Phiên thành công sau khi đổi: `ui_v3_openrouter_20261111T001056477329.transcript.json` (B4). |
| API Twitter API45 trả `403 Forbidden` cho cả `social_search` lẫn `timeline` trong phiên live chat (model vẫn routing đúng tool + args). | Agent được prompt hướng dẫn thông báo lỗi trung thực và đề xuất tool thay thế (`lookup` web) thay vì bịa tweet; nhóm ghi nhận đây là lỗi dịch vụ bên ngoài, cần kiểm tra lại gói subscribe RapidAPI. | Turns 2–3 trong `transcripts/ui_v3_openrouter_20261111T001056477329.transcript.json`: `social_search(query="OpenAI")` và `timeline(screenname="sama")` đều trả `error=HTTPError` 403. |


## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- `system_prompt.md`: bỏ yêu cầu đoán và gửi ngay; thêm clarify, xác nhận và routing rules. `tools.yaml`: mô tả rõ lúc dùng/không dùng và quy ước tham số.
- Cần review thủ công các case alias handle, chọn `topic=news`/timeframe, hỏi lại khi thiếu dữ kiện và xác nhận trước khi gửi; model có thể trả lời bằng text đúng ý nhưng vẫn không tạo tool call được chấm PASS.
- Nếu có vòng tiếp theo, thử ví dụ ngắn cho handle và `topic=news`, rồi đo lại bằng cùng model và artifacts được version hóa.

## 8. Tài liệu tham khảo

Tài liệu chính thức của các dịch vụ nhóm dùng trong lab:

- OpenRouter API (model provider): https://openrouter.ai/docs
- Google Gemini API & rate limits: https://ai.dev/rate-limit và https://ai.dev/docs
- Ollama (local model provider): https://ollama.com và https://ollama.com/search?c=tools (danh sách model hỗ trợ tool calling)
- Tavily Search API (tool `lookup`): https://docs.tavily.com
- Firecrawl API (tool `fetch`): https://docs.firecrawl.dev
- Twitter API45 trên RapidAPI (tool `timeline`, `social_search`): https://rapidapi.com/alexanderxbx/api/twitter-api45
- arXiv API (tool `papers`, `paper_text`): https://info.arxiv.org/help/api/
- Telegram Bot API (tool `send`): https://core.telegram.org/bots/api
- GitHub REST API (tool `github_search` nhóm tự viết): https://docs.github.com/en/rest
- Streamlit (UI demo, bao gồm `streamlit.testing.v1.AppTest` dùng để tự kiểm tra): https://docs.streamlit.io
- ngrok (expose link public): https://ngrok.com/docs

Đề bài và tiêu chí chấm: README.md, CHECKPOINTS.md, RUBRIC.md, SUBMISSION.md của lab Day 03.
