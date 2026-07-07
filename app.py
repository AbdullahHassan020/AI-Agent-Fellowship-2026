import time
import json
import streamlit as st

from utils.openrouter import ask_ai
from components.templates import TEMPLATES

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AI Workspace",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Workspace")

st.info("""
### Welcome to AI Workspace

This application allows you to interact with AI models through a clean interface.

### Features

✅ AI Chat

✅ System Prompt

✅ Prompt Templates

✅ Conversation History

✅ Multiple Chat Sessions

✅ Export Chat

✅ Response Time Measurement
""")

# -----------------------------
# Session State
# -----------------------------
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {
        "Chat 1": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("⚙️ AI Workspace")

st.sidebar.markdown("## 💬 Chat Sessions")

chat_names = list(st.session_state.all_chats.keys())

selected_chat = st.sidebar.selectbox(
    "Select Chat",
    chat_names,
    index=chat_names.index(st.session_state.current_chat)
)

st.session_state.current_chat = selected_chat

if st.sidebar.button("➕ New Chat"):
    new_name = f"Chat {len(chat_names)+1}"
    st.session_state.all_chats[new_name] = []
    st.session_state.current_chat = new_name
    st.rerun()

st.session_state.messages = st.session_state.all_chats[
    st.session_state.current_chat
]

st.sidebar.markdown("---")

system_prompt = st.sidebar.text_area(
    "System Prompt",
    value="You are a helpful AI assistant."
)

model = st.sidebar.selectbox(
    "Model",
    [
        "openai/gpt-oss-20b:free",
        "Simulation - GPT-4",
        "Simulation - Claude 4",
        "Simulation - Gemini 2.5"
    ]
)

st.sidebar.caption(f"Current Model: {model}")

template = st.sidebar.selectbox(
    "Prompt Template",
    list(TEMPLATES.keys())
)

# Assignment allows simulated models
real_model = "openai/gpt-oss-20b:free"

# -----------------------------
# Display Chat History
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# User Input
# -----------------------------
prompt = st.chat_input("Ask anything...")

if prompt:

    if prompt.strip() == "":
        st.warning("Prompt cannot be empty.")
        st.stop()

    if template != "None":
        prompt = TEMPLATES[template] + prompt

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(st.session_state.messages)

    start = time.time()

    try:

        answer = ask_ai(
            messages,
            real_model
        )

        elapsed = time.time() - start

        with st.chat_message("assistant"):
            st.markdown(answer)
            st.caption(
                f"⏱ Response Time: {elapsed:.2f} sec"
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

    except Exception as e:
        st.error(f"❌ {e}")

# -----------------------------
# Sidebar Actions
# -----------------------------
st.sidebar.markdown("---")

if st.sidebar.button("🗑 Clear Current Chat"):
    st.session_state.all_chats[
        st.session_state.current_chat
    ] = []
    st.rerun()

# -----------------------------
# Export Chat
# -----------------------------
if st.session_state.messages:

    chat_json = json.dumps(
        st.session_state.messages,
        indent=4
    )

    st.sidebar.download_button(
        "📥 Export Chat",
        data=chat_json,
        file_name=f"{st.session_state.current_chat}.json",
        mime="application/json"
    )

# -----------------------------
# Statistics
# -----------------------------
st.sidebar.markdown("---")

st.sidebar.subheader("📊 Statistics")

st.sidebar.write(
    f"Current Chat Messages: {len(st.session_state.messages)}"
)

st.sidebar.write(
    f"Total Chats: {len(st.session_state.all_chats)}"
)

st.sidebar.markdown("---")

st.sidebar.success("✅ AI Workspace Ready")