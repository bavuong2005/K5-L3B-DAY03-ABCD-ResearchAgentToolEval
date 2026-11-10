from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


GITHUB_API_URL = "https://api.github.com/search/repositories"


def search_github(
    query: str,
    language: str | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """Tìm kiếm repository trên GitHub theo từ khóa và ngôn ngữ lập trình.

    Args:
        query: Từ khóa tìm kiếm (bắt buộc).
        language: Ngôn ngữ lập trình để lọc repo (tùy chọn, vd: python, typescript).
        limit: Số lượng repository trả về (mặc định 5, tối đa 30).

    Returns:
        Dict chứa danh sách các repository hoặc thông tin lỗi.
    """
    clean_query = (query or "").strip()
    if not clean_query:
        return {
            "tool": "github_search",
            "error": "ValueError",
            "message": "query is required and cannot be empty",
            "count": 0,
            "items": [],
        }

    q = clean_query
    if language and language.strip():
        q = f"{clean_query} language:{language.strip()}"

    max_items = min(max(1, limit or 5), 30)
    params: dict[str, Any] = {
        "q": q,
        "sort": "stars",
        "order": "desc",
        "per_page": max_items,
    }
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AI20k-Day03-Research-Agent/1.0 (educational lab; contact: local)",
    }

    try:
        response = requests.get(GITHUB_API_URL, params=params, headers=headers, timeout=TIMEOUT)
        if response.status_code != 200:
            return {
                "tool": "github_search",
                "error": f"HTTP {response.status_code}",
                "message": response.text[:200],
                "count": 0,
                "items": [],
            }
        data = response.json()
        raw_items = data.get("items", []) if isinstance(data, dict) else []
        items = []
        for repo in raw_items[:max_items]:
            if not isinstance(repo, dict):
                continue
            items.append({
                "name": repo.get("full_name") or repo.get("name") or "",
                "url": repo.get("html_url") or "",
                "description": repo.get("description") or "",
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language") or "",
            })
        return {
            "tool": "github_search",
            "query": clean_query,
            "count": len(items),
            "items": items,
        }
    except Exception as exc:
        res = err("github_search", exc)
        res["count"] = 0
        res["items"] = []
        return res

