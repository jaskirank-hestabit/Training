import json
import os
import time
import uuid

import requests
import streamlit as st

API_URL = os.getenv("STREAMLIT_API_URL", "http://localhost:8000")

# Page config 
st.set_page_config(
    page_title="Local LLM Chat",
    # page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS 
st.markdown("""
<style>
    .stChatMessage { border-radius: 12px; }
    .stat-box {
        background: #1e1e2e;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 0.82em;
        color: #cdd6f4;
        margin-top: 4px;
        border-left: 3px solid #89b4fa;
    }
    .title-area { text-align: center; padding-bottom: 10px; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# Session state init 
def init_state():
    defaults = {
        "chat_history": [],          # List of {role, content}
        "mode": "Chat",
        "last_request_id": None,
        "last_tokens": 0,
        "last_elapsed": 0.0,
        "total_tokens": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# Sidebar 
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bot.png", width=60)
    st.title("LLM Settings")

    mode = st.radio("Mode", ["Chat", "Generate"], horizontal=True)
    st.session_state["mode"] = mode
    st.divider()

    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful, concise, and accurate assistant.",
        height=100,
    )

    st.subheader("Generation Controls")
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.05,
                             help="Higher = more creative. Lower = more deterministic.")
    top_p = st.slider("Top-P", 0.0, 1.0, 0.9, 0.01,
                       help="Nucleus sampling threshold.")
    top_k = st.slider("Top-K", 1, 200, 40,
                       help="Number of top tokens to sample from.")
    max_tokens = st.slider("Max Tokens", 64, 2048, 512, 64)
    repeat_penalty = st.slider("Repeat Penalty", 1.0, 2.0, 1.1, 0.05)
    stream_output = st.toggle("Stream output", value=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state["chat_history"] = []
            st.session_state["total_tokens"] = 0
            st.rerun()
    with col2:
        if st.button("Check API", use_container_width=True):
            try:
                r = requests.get(f"{API_URL}/health", timeout=3)
                if r.status_code == 200:
                    st.success("API")
                else:
                    st.error("API")
            except Exception:
                st.error("Unreachable")

    st.divider()
    st.caption(f"**API:** `{API_URL}`")
    st.caption(f"**Total tokens used:** {st.session_state['total_tokens']}")
    if st.session_state["last_request_id"]:
        st.caption(f"**Last request ID:** `{st.session_state['last_request_id']}`")
        st.caption(f"**Last response:** {st.session_state['last_elapsed']}s · {st.session_state['last_tokens']} tokens")


# ─── Streaming helpers ────────────────────────────────────────────────────────
def stream_generate(prompt: str, sys_prompt: str, params: dict) -> str:
    payload = {
        "prompt": prompt,
        "system_prompt": sys_prompt,
        "stream": True,
        **params,
    }
    full_text = ""
    placeholder = st.empty()
    with requests.post(f"{API_URL}/generate", json=payload, stream=True, timeout=120) as r:
        for line in r.iter_lines():
            if not line:
                continue
            raw = line.decode("utf-8")
            if not raw.startswith("data: "):
                continue
            data = json.loads(raw[6:])
            if data.get("done"):
                st.session_state["last_request_id"] = data.get("request_id")
                st.session_state["last_tokens"] = data.get("tokens_generated", 0)
                st.session_state["total_tokens"] += data.get("tokens_generated", 0)
                break
            full_text += data.get("token", "")
            placeholder.markdown(full_text + "▌")
    placeholder.markdown(full_text)
    return full_text


def generate_sync(prompt: str, sys_prompt: str, params: dict) -> str:
    payload = {
        "prompt": prompt,
        "system_prompt": sys_prompt,
        "stream": False,
        **params,
    }
    r = requests.post(f"{API_URL}/generate", json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    st.session_state["last_request_id"] = data.get("request_id")
    st.session_state["last_tokens"] = data.get("tokens_generated", 0)
    st.session_state["last_elapsed"] = data.get("elapsed_sec", 0)
    st.session_state["total_tokens"] += data.get("tokens_generated", 0)
    return data["response"]


def stream_chat(messages: list, params: dict) -> str:
    payload = {"messages": messages, "stream": True, **params}
    full_text = ""
    placeholder = st.empty()
    with requests.post(f"{API_URL}/chat", json=payload, stream=True, timeout=120) as r:
        for line in r.iter_lines():
            if not line:
                continue
            raw = line.decode("utf-8")
            if not raw.startswith("data: "):
                continue
            data = json.loads(raw[6:])
            if data.get("done"):
                st.session_state["last_request_id"] = data.get("request_id")
                st.session_state["last_tokens"] = data.get("tokens_generated", 0)
                st.session_state["total_tokens"] += data.get("tokens_generated", 0)
                break
            full_text += data.get("token", "")
            placeholder.markdown(full_text + "▌")
    placeholder.markdown(full_text)
    return full_text


def chat_sync(messages: list, params: dict) -> str:
    payload = {"messages": messages, "stream": False, **params}
    r = requests.post(f"{API_URL}/chat", json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    st.session_state["last_request_id"] = data.get("request_id")
    st.session_state["last_tokens"] = data.get("tokens_generated", 0)
    st.session_state["last_elapsed"] = data.get("elapsed_sec", 0)
    st.session_state["total_tokens"] += data.get("tokens_generated", 0)
    return data["response"]


# Main UI 
st.markdown('<div class="title-area"><h1> Local LLM Interface</h1><p>Powered by GGUF · llama.cpp · FastAPI</p></div>', unsafe_allow_html=True)
st.divider()

params = dict(
    max_tokens=max_tokens,
    temperature=temperature,
    top_p=top_p,
    top_k=top_k,
    repeat_penalty=repeat_penalty,
)

# GENERATE MODE 
if st.session_state["mode"] == "Generate":
    st.subheader("Raw Text Generation")
    prompt_input = st.text_area("Enter your prompt:", height=180, placeholder="Write a poem about neural networks...")

    if st.button("⚡ Generate", type="primary", use_container_width=True):
        if not prompt_input.strip():
            st.warning("Please enter a prompt.")
        else:
            t0 = time.perf_counter()
            with st.spinner("Generating..."):
                try:
                    st.subheader("Response")
                    if stream_output:
                        response = stream_generate(prompt_input, system_prompt, params)
                    else:
                        response = generate_sync(prompt_input, system_prompt, params)
                    elapsed = round(time.perf_counter() - t0, 3)
                    st.session_state["last_elapsed"] = elapsed
                    st.markdown(
                        f'<div class="stat-box"> Request ID: <b>{st.session_state["last_request_id"]}</b> &nbsp;|&nbsp; '
                        f'{elapsed}s &nbsp;|&nbsp; {st.session_state["last_tokens"]} tokens</div>',
                        unsafe_allow_html=True,
                    )
                except Exception as e:
                    st.error(f"Error: {e}")

# CHAT MODE 
else:
    st.subheader("Infinite Chat")

    # Render history
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Show user message
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Build messages list with system prompt
        messages = [{"role": "system", "content": system_prompt}] + st.session_state["chat_history"]

        t0 = time.perf_counter()
        with st.chat_message("assistant"):
            try:
                if stream_output:
                    reply = stream_chat(messages, params)
                else:
                    with st.spinner("Thinking..."):
                        reply = chat_sync(messages, params)
                    st.markdown(reply)

                elapsed = round(time.perf_counter() - t0, 3)
                st.session_state["last_elapsed"] = elapsed
                st.markdown(
                    f'<div class="stat-box"> {st.session_state["last_request_id"]} &nbsp;|&nbsp; '
                    f' {elapsed}s &nbsp;|&nbsp; {st.session_state["last_tokens"]} tokens</div>',
                    unsafe_allow_html=True,
                )
            except Exception as e:
                reply = f"Error contacting API: {e}"
                st.error(reply)

        st.session_state["chat_history"].append({"role": "assistant", "content": reply})