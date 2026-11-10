---
name: github_search
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [query, language, limit]
outputs: [tool, query, count, items]
side_effect: false
---
# github_search

Tìm kiếm các repository mã nguồn mở trên GitHub theo từ khóa và ngôn ngữ lập trình.
Sắp xếp theo số lượt gắn sao (stars) giảm dần.

