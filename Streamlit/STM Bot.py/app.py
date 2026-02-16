import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from Bot import app
import uuid

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LangGraph Chat Bot",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .stMarkdown label {
        color: #e0e0ff !important;
    }

    /* ── Header ── */
    .header-container {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }

    .header-container h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }

    .header-container p {
        color: #888;
        font-size: 0.9rem;
    }

    /* ── Thread badge ── */
    .thread-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea22, #764ba222);
        border: 1px solid #667eea44;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.75rem;
        color: #667eea;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }

    /* ── Chat messages ── */
    .stChatMessage {
        border-radius: 16px !important;
        margin-bottom: 0.5rem !important;
        border: 1px solid rgba(128, 128, 128, 0.1) !important;
    }

    /* ── Sidebar info cards ── */
    .info-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
    }

    .info-card .label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8888cc;
        margin-bottom: 4px;
    }

    .info-card .value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e0e0ff;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #888;
    }

    .empty-state .icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }

    .empty-state h3 {
        color: #aaa;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .empty-state p {
        font-size: 0.85rem;
        line-height: 1.6;
        max-width: 400px;
        margin: 0 auto;
    }

    /* ── Streamlit overrides ── */
    .stChatInput > div {
        border-radius: 12px !important;
    }

    div[data-testid="stStatusWidget"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())[:8]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_counter" not in st.session_state:
    st.session_state.thread_counter = 1

if "all_threads" not in st.session_state:
    st.session_state.all_threads = {
        st.session_state.thread_id: f"Thread {st.session_state.thread_counter}"
    }


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 LangGraph Chat Bot")
    st.markdown("*Short-Term Memory with LangGraph*")
    st.markdown("---")

    # Stats cards
    st.markdown(f"""
    <div class="info-card">
        <div class="label">Active Thread</div>
        <div class="value">🧵 {st.session_state.thread_id}</div>
    </div>
    <div class="info-card">
        <div class="label">Messages in Thread</div>
        <div class="value">💬 {len(st.session_state.chat_history)}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # New thread button
    if st.button("➕  New Conversation", use_container_width=True, type="primary"):
        st.session_state.thread_counter += 1
        new_id = str(uuid.uuid4())[:8]
        st.session_state.thread_id = new_id
        st.session_state.chat_history = []
        st.session_state.all_threads[new_id] = f"Thread {st.session_state.thread_counter}"
        st.rerun()

    # Thread switcher
    if len(st.session_state.all_threads) > 1:
        st.markdown("### 📂 Threads")
        for tid, tname in st.session_state.all_threads.items():
            is_active = tid == st.session_state.thread_id
            label = f"{'🟢' if is_active else '⚪'} {tname}"
            if st.button(label, key=f"thread_{tid}", use_container_width=True, disabled=is_active):
                st.session_state.thread_id = tid
                # Restore chat history from LangGraph checkpoints
                config = {"configurable": {"thread_id": tid}}
                state = app.get_state(config)
                if state and state.values and "messages" in state.values:
                    restored = []
                    for msg in state.values["messages"]:
                        if isinstance(msg, HumanMessage):
                            restored.append({"role": "user", "content": msg.content})
                        elif isinstance(msg, AIMessage):
                            restored.append({"role": "assistant", "content": msg.content})
                    st.session_state.chat_history = restored
                else:
                    st.session_state.chat_history = []
                st.rerun()

    st.markdown("---")

    # How it works
    with st.expander("💡 How it works"):
        st.markdown("""
        **Persistence** saves the graph state across calls.

        - `InMemorySaver` stores checkpoints in RAM
        - `thread_id` links messages to a conversation
        - `add_messages` reducer appends instead of replacing
        - Each `invoke()` auto-saves a new checkpoint

        Try asking *"What's my name?"* after telling it your name!
        """)

    # Tech stack
    with st.expander("⚙️ Tech Stack"):
        st.markdown("""
        - **LLM**: Llama 3.3 70B (Groq)
        - **Framework**: LangGraph
        - **Persistence**: MemorySaver
        - **UI**: Streamlit
        """)


# ─────────────────────────────────────────────
# Main Chat Area
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <h1>🧠 LangGraph Chat Bot</h1>
    <p>Short-Term Memory Chatbot powered by LangGraph Persistence</p>
</div>
""", unsafe_allow_html=True)

# Thread badge
st.markdown(
    f'<div style="text-align:center;"><span class="thread-badge">🧵 THREAD {st.session_state.thread_id}</span></div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Display Chat History
# ─────────────────────────────────────────────
if not st.session_state.chat_history:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">💬</div>
        <h3>Start a conversation</h3>
        <p>
            This bot remembers everything you say within the same thread.
            Try telling it your name, then ask <em>"What's my name?"</em> later!
            <br><br>
            Use <strong>➕ New Conversation</strong> in the sidebar to start a fresh thread — the bot won't remember anything from other threads.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for message in st.session_state.chat_history:
        avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])


# ─────────────────────────────────────────────
# Chat Input
# ─────────────────────────────────────────────
if user_input := st.chat_input("Type your message..."):

    # Show user message immediately
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)

    # Call LangGraph
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            result = app.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
            )
            ai_response = result["messages"][-1].content

        st.markdown(ai_response)

    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
    st.rerun()