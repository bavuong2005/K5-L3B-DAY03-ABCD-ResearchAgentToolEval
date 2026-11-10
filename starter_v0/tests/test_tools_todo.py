"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    tool = TOOL_FUNCTIONS["clarify"]
    opts = ["Lựa chọn 1", "Lựa chọn 2"]
    res = tool(question="Bạn chọn cái nào?", response_type="choice", options=opts)
    assert res["options"] == opts
    assert res["awaiting_user"] is True
    assert res["response_type"] == "choice"
    assert res["question"] == "Bạn chọn cái nào?"


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    tool = TOOL_FUNCTIONS["format"]
    items = [
        {"title": "Mục 1", "section": "Nhóm A"},
        {"title": "Mục 2", "section": "Nhóm B"},
        {"title": "Mục 3", "section": "Nhóm A"},
    ]
    res = tool(items=items, template="sections")
    md = res["markdown"]
    assert md.count("## Nhóm A") == 1
    assert md.count("## Nhóm B") == 1
    assert res["item_count"] == 3


def test_format_thread_numbers_items() -> None:
    tool = TOOL_FUNCTIONS["format"]
    items = [
        {"title": "Tweet thứ nhất", "url": "https://x.com/1"},
        {"title": "Tweet thứ hai", "url": "https://x.com/2"},
        {"title": "Tweet thứ ba", "url": "https://x.com/3"},
    ]
    res = tool(items=items, template="thread")
    md = res["markdown"]
    assert "1/ Tweet thứ nhất" in md
    assert "2/ Tweet thứ hai" in md
    assert "3/ Tweet thứ ba" in md


def test_format_empty_items_does_not_crash() -> None:
    tool = TOOL_FUNCTIONS["format"]
    res_none = tool(items=None)
    assert res_none["item_count"] == 0
    assert res_none["markdown"] == ""

    res_empty = tool(items=[])
    assert res_empty["item_count"] == 0
    assert res_empty["markdown"] == ""


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")
    calls = fake_http(FakeResponse({"ok": True}))
    tool = TOOL_FUNCTIONS["send"]
    res = tool(text="Bản tin", confirmed=True)
    assert len(calls) == 1
    assert "fake-token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "123456"
    assert calls[0]["json"]["text"] == "Bản tin"
    assert res["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    tool = TOOL_FUNCTIONS["send"]
    res = tool(text="Bản tin", confirmed=True)
    assert calls == []
    assert "error" in res
    assert res["error"] == "RuntimeError"


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))
    tool = TOOL_FUNCTIONS["lookup"]
    res = tool(query="AI news", timeframe=None)
    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]
    assert res["timeframe"] is None


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "Nội dung bài viết",
            "metadata": {"title": "Tiêu đề bài viết", "sourceURL": "https://example.com/article"},
        }
    }))
    tool = TOOL_FUNCTIONS["fetch"]
    res = tool(url="https://example.com/article")
    assert res["tool"] == "read_url"
    assert len(res["items"]) == 1
    item = res["items"][0]
    assert item["title"] == "Tiêu đề bài viết"
    assert item["url"] == "https://example.com/article"
    assert item["source"] == "example.com"
    assert item["summary"] == "Nội dung bài viết"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "x" * 5000,
            "metadata": {"title": "Long page"},
        }
    }))
    tool = TOOL_FUNCTIONS["fetch"]
    res = tool(url="https://example.com/long")
    summary = res["items"][0]["summary"]
    assert len(summary) == 4000
    assert summary == "x" * 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    raw_timeline = [{"text": "no id"}] + [
        {"id": f"id_{i}", "screen_name": "sama", "text": f"tweet {i}"}
        for i in range(6)
    ]
    fake_http(FakeResponse({"timeline": raw_timeline}))
    tool = TOOL_FUNCTIONS["timeline"]
    res = tool(screenname="sama", limit=3)
    assert len(res["items"]) == 3
    for i, it in enumerate(res["items"]):
        assert it["url"] == f"https://x.com/sama/status/id_{i}"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse({"timeline": []}))
    tool = TOOL_FUNCTIONS["social_search"]
    res = tool(query="AGI", search_type="Top")
    assert len(calls) == 1
    assert calls[0]["params"]["query"] == "AGI"
    assert calls[0]["params"]["search_type"] == "Top"
    assert res["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    tool = TOOL_FUNCTIONS["policy"]
    res = tool(query="")
    assert res["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    tool = TOOL_FUNCTIONS["policy"]
    res = tool(query="data privacy user personal", policy_area="data_privacy")
    assert len(res["results"]) > 0
    for it in res["results"]:
        assert it["policy_area"] == "data_privacy"


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    tool = TOOL_FUNCTIONS["policy"]
    res = tool(query="injection probe citation", policy_area="source_citation")
    assert len(res["results"]) > 0
    target_section = next(r for r in res["results"] if r["section"] == "Injection probe")
    assert any("ignore the citation policy" in line for line in target_section["untrusted_text"])
    assert "ignore the citation policy" not in target_section["facts"]


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_my_new_tool_happy_path(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "items": [
            {
                "full_name": "google/agent-eval",
                "html_url": "https://github.com/google/agent-eval",
                "description": "Evaluation framework for AI agents",
                "stargazers_count": 2500,
                "language": "Python",
            },
            {
                "full_name": "meta/llama-tools",
                "html_url": "https://github.com/meta/llama-tools",
                "description": "Tool calling repo",
                "stargazers_count": 1200,
                "language": "Python",
            },
        ]
    }))
    tool = TOOL_FUNCTIONS["github_search"]
    result = tool(query="agent eval", language="python", limit=2)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"]["q"] == "agent eval language:python"
    assert calls[0]["params"]["per_page"] == 2
    assert result["count"] == 2
    assert result["items"][0]["name"] == "google/agent-eval"
    assert result["items"][0]["stars"] == 2500
    assert result["items"][0]["language"] == "Python"
    assert result["items"][0]["url"] == "https://github.com/google/agent-eval"


def test_my_new_tool_bad_input_from_model() -> None:
    tool = TOOL_FUNCTIONS["github_search"]
    result = tool(query="   ", language="", limit=5)
    assert result["count"] == 0
    assert result["items"] == []
    assert "error" in result
    assert result["error"] == "ValueError"


def test_my_new_tool_failure_returns_error_dict(fake_http) -> None:
    calls = fake_http(FakeResponse(status_code=500, text="GitHub API rate limit exceeded"))
    tool = TOOL_FUNCTIONS["github_search"]
    result = tool(query="vllm", language="python")
    assert len(calls) == 1
    assert "error" in result
    assert "500" in result["error"]
    assert result["count"] == 0
    assert result["items"] == []
