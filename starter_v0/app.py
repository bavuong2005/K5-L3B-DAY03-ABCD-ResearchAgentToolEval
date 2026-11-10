from __future__ import annotations

import json
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
DEFAULT_MODEL_HINTS = {
    "openrouter": "openai/gpt-4o-mini",
    "ollama": "qwen2.5:7b",
}

SAMPLE_QUESTIONS = [
    "Tìm 3 tin mới nhất về OpenAI trong tuần này, rồi tóm tắt thành digest.",
    "Xem timeline gần đây của tài khoản sama và chỉ ra 2 bài đăng đáng chú ý.",
    "Đọc https://openai.com/research/ và tóm tắt 5 điểm chính.",
    "Tóm tắt giúp tôi bài này với (cố ý không nói URL — agent nên hỏi lại).",
    "Gửi bản tin tóm tắt vừa rồi lên Telegram cho nhóm.",
    "Chính sách công ty về chia sẻ dữ liệu khách hàng ra sao?",
]


st.set_page_config(page_title="Research Agent — Day 03", page_icon=":mag:", layout="centered")
st.title("Research Agent")
st.caption(
    "Chat nhiều lượt với agent. Mỗi lượt được ghi vào `starter_v0/transcripts/*.transcript.json` "
    "cùng format với `chat.py` để dùng làm bằng chứng báo cáo."
)


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


with st.sidebar:
    st.header("Cấu hình")

    provider = st.selectbox("Provider", PROVIDERS, index=0)
    hint = DEFAULT_MODEL_HINTS.get(provider, "mặc định của provider")
    model = st.text_input(
        f"Model (bỏ trống = mặc định: {hint})",
        value=st.session_state.get("model_input", ""),
        key="model_input",
    )
    version = st.text_input("Version label", value=st.session_state.get("version_input", "v3"), key="version_input")
    history_window = st.slider("History window (lượt giữ trong context)", 0, 10, 5, key="history_window")
    max_tool_rounds = st.slider("Max tool rounds", 1, 8, 4, key="max_tool_rounds")

    st.session_state.provider = provider
    st.session_state.model = model.strip() or None
    st.session_state.version = version.strip() or "v0"

    if st.button("Bắt đầu phiên mới", use_container_width=True):
        for key in ["display", "model_history", "transcript", "transcript_path", "transcript_config"]:
            st.session_state.pop(key, None)
        st.rerun()

    st.divider()
    st.subheader("Câu hỏi mẫu")
    for question in SAMPLE_QUESTIONS:
        if st.button(question, key=f"sample_{hash(question)}", use_container_width=True):
            st.session_state.pending_question = question
            st.rerun()

    st.divider()
    transcript_path = st.session_state.get("transcript_path")
    if transcript_path is not None:
        st.caption(f"Transcript: `transcripts/{Path(transcript_path).name}`")
        st.download_button(
            "Tải transcript JSON",
            data=Path(transcript_path).read_text(encoding="utf-8"),
            file_name=Path(transcript_path).name,
            mime="application/json",
            use_container_width=True,
        )


if "display" not in st.session_state:
    st.session_state.display = []
if "model_history" not in st.session_state:
    st.session_state.model_history = []


for message in st.session_state.display:
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["text"])
        md = tool_events_md(message.get("tool_events", []))
        if md:
            with st.expander("Tool calls & results"):
                st.markdown(md)
        if message.get("error"):
            st.error(message["error"])


pending = st.session_state.pop("pending_question", None)
user_text = pending or st.chat_input("Nhập yêu cầu cho agent...")
if user_text:
    ensure_transcript()
    st.session_state.display.append({"role": "user", "text": user_text})
    with st.chat_message("user", avatar="🧑‍💻"):
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
        with st.chat_message("assistant", avatar="🤖"):
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
