import streamlit as st
from app import app, get_all_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid

st.set_page_config(
    page_title="LangGraph DB Bot",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded",
)


# **************************************** utility functions *************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'][thread_id] = f'Chat {len(st.session_state["chat_threads"]) + 1}'

def load_conversation(thread_id):
    state = app.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])


# **************************************** Session Setup ******************************
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    existing_threads = get_all_threads()
    st.session_state['chat_threads'] = {
        tid: f'Chat {i}' for i, tid in enumerate(existing_threads, start=1)
    }

add_thread(st.session_state['thread_id'])


# **************************************** Custom CSS **********************************

st.markdown("""
<style>
    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    /* Sidebar title */
    section[data-testid="stSidebar"] h1 {
        color: #e2e8f0 !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    /* New Chat button — prominent gradient */
    section[data-testid="stSidebar"] div[data-testid="stButton"]:first-of-type button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        margin-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"]:first-of-type button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
    }

    /* Conversation header */
    section[data-testid="stSidebar"] h3 {
        color: #94a3b8 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Chat thread buttons */
    section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        padding: 0.55rem 1rem !important;
        font-size: 0.88rem !important;
        font-weight: 400 !important;
        width: 100% !important;
        text-align: left !important;
        transition: all 0.25s ease !important;
        margin-bottom: 0.25rem !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"]:not(:first-of-type) button:hover {
        background: rgba(102, 126, 234, 0.15) !important;
        border-color: rgba(102, 126, 234, 0.3) !important;
        color: #e2e8f0 !important;
        transform: translateX(4px) !important;
    }
</style>
""", unsafe_allow_html=True)


# **************************************** Sidebar UI *********************************

st.sidebar.title('🤖 LangGraph Chatbot')

if st.sidebar.button('✨ New Chat'):
    reset_chat()

st.sidebar.subheader('Conversations')

for thread_id, thread_name in reversed(list(st.session_state['chat_threads'].items())):
    if st.sidebar.button(thread_name, key=str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages


# **************************************** Main UI ************************************

st.markdown("""
<div class="header-container">
    <h1>⚡ Welcome to LangGraph Chatbot</h1>
    <p>Real-time token streaming with LangGraph Persistence</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Display Chat History
# ─────────────────────────────────────────────
if not st.session_state['message_history']:
    st.markdown("""
    <div class="empty-state">
        <h3>🚀 Start a conversation</h3>
        <p>
            This bot <strong>streams</strong> responses token by token — just like ChatGPT!
            It also remembers everything within the same thread.
            <br><br>
            Use <strong>✨ New Chat</strong> in the sidebar to start a fresh thread.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for message in st.session_state['message_history']:
        avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

     # first add the message to message_history
    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in app.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    # yield only assistant tokens
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})