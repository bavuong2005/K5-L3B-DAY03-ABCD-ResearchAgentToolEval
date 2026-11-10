from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
DEFAULT_PROVIDER = "gemini" if os.getenv("GEMINI_API_KEY") else "openrouter"
DEFAULT_MODEL_HINTS = {
    "openrouter": "openai/gpt-4o-mini",
    "gemini": "gemini-3.5-flash",
    "ollama": "qwen2.5:7b",
}
SESSION_TURN_LIMIT = 15

QUICK_QUESTIONS = [
    "Hôm nay có tin AI nào đáng chú ý? Tóm tắt giùm mình.",
    "Twitter/X đang nói gì về OpenAI dạo gần đây?",
    "Cho mình xin timeline mới nhất của tài khoản sama.",
    "Đọc bài tại openai.com/research rồi rút 5 ý chính.",
    "Tìm paper arXiv về tool calling của AI agent.",
    "Đăng bản tin tóm tắt lên Telegram kênh của nhóm nha.",
]

CSS = """
<style>
section[data-testid="stSidebar"] { background: #f6f7fb; border-right: 1px solid #e4e6f0; }
section[data-testid="stSidebar"] .stButton > button {
    width: 100%; text-align: left; justify-content: flex-start;
    border-radius: 10px; border: 1px solid #e0e2ee; background: #ffffff; color: #1f2337;
}
section[data-testid="stSidebar"] .stButton > button:hover { border-color: #6366f1; color: #4338ca; }
.brand-title { font-weight: 800; font-size: 1.35rem; margin-bottom: 0; }
.brand-sub { color: #6b7280; font-size: 0.85rem; margin-top: 2px; }
.quota-pill {
    display: inline-block; padding: 3px 12px; border-radius: 999px;
    background: #eef2ff; color: #4338ca; font-size: 0.85rem; font-weight: 600;
    border: 1px solid #c7d2fe; white-space: nowrap;
}
.hero { text-align: center; padding: 56px 16px 24px; }
.hero h1 {
    font-size: 2.3rem; font-weight: 800;
    background: linear-gradient(90deg, #4f46e5, #0ea5e9);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p { color: #6b7280; font-size: 1.02rem; max-width: 640px; margin: 10px auto 0; }
[data-testid="stChatMessage"] {
    border: 1px solid #e4e6f0; border-radius: 14px; background: #ffffff; padding: 6px 10px;
}
[data-testid="stChatMessage"], [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {
    color: #1f2337;
}
.stApp { background: #ffffff; color: #1f2337; }
section[data-testid="stSidebar"] { color: #1f2337; }
.tool-line { margin: 4px 0; }
.tool-name { color: #0e7490; font-family: monospace; font-weight: 600; }
.tool-desc { color: #4b5563; font-size: 0.82rem; }
.ver-table { font-size: 0.82rem; color: #4b5563; }
.ver-table code { color: #4338ca; }
</style>
"""

st.set_page_config(page_title="Research Agent — Day 03", page_icon="🔍", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


def tool_catalog() -> list[dict[str, str]]:
    declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    return [{"name": item["name"], "description": item.get("description", "")} for item in declarations]


def short_desc(text: str, limit: int = 90) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def telegram_status() -> str:
    if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        return "bật (send có thể gửi thật sau xác nhận)"
    return "tắt (send chỉ trả lời, không gửi)"


def ensure_transcript() -> None:
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    cfg = (
        st.session_state.provider,
        st.session_state.model,
        st.session_state.version,
        st.session_state.history_window,
        st.session_state.max_tool_rounds,
    )
    if st.session_state.get("transcript_config") == cfg:
        return
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([
        "ui",
        safe_slug(st.session_state.version),
        safe_slug(st.session_state.provider),
        timestamp,
    ])
    artifact_version = build_artifact_version(st.session_state.version, system_prompt_path, tools_path)
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": st.session_state.provider,
        "model": st.session_state.model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": st.session_state.history_window,
        "max_tool_rounds": st.session_state.max_tool_rounds,
        "ui": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript_config = cfg


def append_turn_record(result: dict[str, Any], user_text: str) -> None:
    transcript: dict[str, Any] = st.session_state.transcript
    turn_record: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    turn_record.update(result)
    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, transcript)


def current_artifact_version() -> str:
    try:
        av = build_artifact_version(
            st.session_state.version,
            ARTIFACTS_DIR / "system_prompt.md",
            ARTIFACTS_DIR / "tools.yaml",
        )
        return av.artifact_version
    except Exception:
        return "n/a"


def tool_events_md(events: list[dict[str, Any]]) -> str:
    lines = []
    for event in events:
        tool = event.get("tool", "?")
        args = json.dumps(event.get("args", {}), ensure_ascii=False, sort_keys=True)
        result = json.dumps(event.get("result", {}), ensure_ascii=False, default=str)
        if len(result) > 800:
            result = result[:800] + " ...<truncated>"
        lines.append(f"**`{tool}({args})`**\n\n```json\n{result}\n```")
    return "\n\n".join(lines) if lines else ""


if "display" not in st.session_state:
    st.session_state.display = []
if "model_history" not in st.session_state:
    st.session_state.model_history = []
if "turns_used" not in st.session_state:
    st.session_state.turns_used = 0

with st.sidebar:
    st.markdown('<p class="brand-title">🔍 Research Agent</p>', unsafe_allow_html=True)
    st.markdown('<p class="brand-sub">Day 03 · Research Agent Tool Eval</p>', unsafe_allow_html=True)

    if st.button("➕ Cuộc chat mới", use_container_width=True):
        for key in ["display", "model_history", "transcript", "transcript_path", "transcript_config"]:
            st.session_state.pop(key, None)
        st.session_state.turns_used = 0
        st.rerun()

    st.caption("THỬ NHANH")
    for question in QUICK_QUESTIONS:
        if st.button(question, key=f"quick_{hash(question)}", use_container_width=True):
            st.session_state.pending_question = question
            st.rerun()

    st.caption(f"TOOL ({len(tool_catalog())})")
    for tool in tool_catalog():
        st.markdown(
            f'<div class="tool-line"><span class="tool-name">{tool["name"]}</span><br>'
            f'<span class="tool-desc">{short_desc(tool["description"])}</span></div>',
            unsafe_allow_html=True,
        )

    with st.expander("⚙️ Cấu hình"):
        provider = st.selectbox("Provider", PROVIDERS, index=PROVIDERS.index(DEFAULT_PROVIDER))
        hint = DEFAULT_MODEL_HINTS.get(provider, "mặc định của provider")
        model = st.text_input(
            f"Model (bỏ trống = {hint})",
            value=st.session_state.get("model_input", ""),
            key="model_input",
        )
        version = st.text_input("Version label", value=st.session_state.get("version_input", "v3"), key="version_input")
        history_window = st.slider("History window", 0, 10, 5, key="history_window")
        max_tool_rounds = st.slider("Max tool rounds", 1, 8, 4, key="max_tool_rounds")
        st.session_state.provider = provider
        st.session_state.model = model.strip() or None
        st.session_state.version = version.strip() or "v0"

    st.caption("PHIÊN BẢN")
    st.markdown(
        f'<div class="ver-table">'
        f'Model<br><code>{st.session_state.provider} / {st.session_state.model or DEFAULT_MODEL_HINTS.get(st.session_state.provider, "default")}</code><br>'
        f'Artifact<br><code>{current_artifact_version()}</code><br>'
        f'Telegram<br>{telegram_status()}'
        f'</div>',
        unsafe_allow_html=True,
    )

    transcript_path = st.session_state.get("transcript_path")
    if transcript_path is not None and Path(transcript_path).exists():
        st.download_button(
            "⬇️ Tải transcript JSON",
            data=Path(transcript_path).read_text(encoding="utf-8"),
            file_name=Path(transcript_path).name,
            mime="application/json",
            use_container_width=True,
        )


header_l, header_r = st.columns([0.85, 0.15])
with header_l:
    st.markdown("#### Chat với Research Agent")
with header_r:
    turns_left = SESSION_TURN_LIMIT - st.session_state.turns_used
    st.markdown(f'<span class="quota-pill">còn {max(turns_left, 0)}/{SESSION_TURN_LIMIT} lượt</span>', unsafe_allow_html=True)

if not st.session_state.display:
    st.markdown(
        '<div class="hero"><h1>Hỏi agent một câu research</h1>'
        '<p>Agent tìm tin web, xem tweet theo chủ đề hoặc theo tài khoản, đọc URL, tra policy nội bộ '
        'và tìm paper arXiv. Thiếu thông tin thì agent sẽ hỏi lại; muốn gửi Telegram thì agent xin xác nhận trước.</p>'
        '<p>Mỗi câu trả lời kèm tool đã gọi, arguments và kết quả thô — bấm vào để xem.</p></div>',
        unsafe_allow_html=True,
    )

for message in st.session_state.display:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])
        md = tool_events_md(message.get("tool_events", []))
        if md:
            with st.expander("Tool calls & results"):
                st.markdown(md)
        if message.get("error"):
            st.error(message["error"])


quota_exhausted = st.session_state.turns_used >= SESSION_TURN_LIMIT
if quota_exhausted:
    st.warning(f"Đã hết {SESSION_TURN_LIMIT} lượt của phiên này. Bấm “➕ Cuộc chat mới” để tiếp tục (một transcript mới sẽ được tạo).")

pending = st.session_state.pop("pending_question", None)
user_text = pending or st.chat_input("Nhập yêu cầu cho agent...", disabled=quota_exhausted)
if user_text:
    ensure_transcript()
    st.session_state.display.append({"role": "user", "text": user_text})
    st.session_state.turns_used += 1
    with st.chat_message("user"):
        st.markdown(user_text)

    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    openai_tools = to_openai_tools(tool_declarations)
    provider_obj = make_provider(st.session_state.provider)
    selected_model = st.session_state.model or getattr(provider_obj, "default_model", None)
    st.session_state.transcript["model"] = selected_model

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.model_history, st.session_state.history_window),
        {"role": "user", "content": user_text},
    ]

    try:
        with st.chat_message("assistant"):
            with st.spinner("Agent đang chọn tool và chạy..."):
                result = run_model_tool_loop(
                    provider=provider_obj,
                    messages=messages,
                    tools=openai_tools,
                    model=selected_model,
                    max_tool_rounds=st.session_state.max_tool_rounds,
                )
        append_turn_record(result, user_text)
        assistant_text = result.get("assistant_text") or "(không có phản hồi)"
        st.session_state.display.append({
            "role": "assistant",
            "text": assistant_text,
            "tool_events": result.get("tool_events", []),
            "status": result.get("status"),
        })
        st.session_state.model_history.append({"role": "user", "content": user_text})
        st.session_state.model_history.append({"role": "assistant", "content": assistant_text})
    except Exception as exc:
        error_text = f"{type(exc).__name__}: {str(exc)}"
        append_turn_record({"status": "provider_error", "error": error_text, "rounds": [], "tool_events": []}, user_text)
        st.session_state.display.append({"role": "assistant", "text": "Có lỗi khi chạy agent.", "error": error_text})

    st.rerun()
