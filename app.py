"""Streamlit UI for Cricket Conversational Agent."""

import os
import streamlit as st
from agent import CricketAgent, OllamaClient

st.set_page_config(
    page_title="Cricket Agent",
    page_icon="🏏",
    layout="wide",
)

# Cricket-themed CSS
st.markdown("""
<style>
    /* Cricket green theme */
    .stApp {
        background: linear-gradient(180deg, #1a472a 0%, #2d5a3d 50%, #1e3d2f 100%);
    }

    /* Main text colors */
    .stApp p, .stApp span, .stApp div, .stApp label {
        color: #e0e0e0 !important;
    }

    .stApp h1, .stApp h2, .stApp h3 {
        color: #ffffff !important;
    }

    /* Title styling */
    h1 {
        background: linear-gradient(90deg, #f0e68c 0%, #daa520 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800 !important;
        text-align: center;
        padding: 1rem 0;
    }

    .subtitle {
        text-align: center;
        color: #a0d0a0 !important;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    /* Chat messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(240, 230, 140, 0.3) !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: rgba(240, 230, 140, 0.15) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a3d2a 0%, #0f2a1a 100%);
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f0e68c !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] div {
        color: #c0d0c0 !important;
    }

    [data-testid="stSidebar"] a {
        color: #f0e68c !important;
    }

    [data-testid="stSidebar"] .stCaption {
        color: #88a088 !important;
    }

    /* Input boxes */
    input, textarea {
        background-color: #2a4a3a !important;
        color: #ffffff !important;
        border: 2px solid #f0e68c !important;
        caret-color: #f0e68c !important;
    }

    .stChatInput textarea,
    .stChatInput input,
    [data-testid="stChatInput"] textarea {
        background-color: #2a4a3a !important;
        color: #ffffff !important;
        border: 2px solid #f0e68c !important;
        border-radius: 25px !important;
    }

    [data-testid="stSidebar"] input {
        background-color: #2a4a3a !important;
        color: #ffffff !important;
        border: 2px solid #f0e68c !important;
    }

    input::placeholder, textarea::placeholder {
        color: #88a088 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #f0e68c 0%, #daa520 100%) !important;
        color: #1a472a !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 25px !important;
    }

    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(240, 230, 140, 0.5) !important;
    }

    /* Status boxes */
    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 12px !important;
    }

    .stSuccess p, .stWarning p, .stError p, .stInfo p,
    [data-testid="stAlert"] p {
        color: #000000 !important;
    }

    [data-testid="stSidebar"] .stSuccess,
    [data-testid="stSidebar"] .stWarning,
    [data-testid="stSidebar"] .stError {
        background-color: rgba(255, 255, 255, 0.9) !important;
    }

    /* Stats bar */
    .stats-bar {
        display: flex;
        justify-content: center;
        gap: 2rem;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 12px;
        margin: 1rem 0;
    }

    .stat-item {
        text-align: center;
    }

    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f0e68c;
    }

    .stat-label {
        font-size: 0.8rem;
        color: #88a088;
    }

    /* Hide branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Floating animation */
    @keyframes bounce {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    .bouncing {
        animation: bounce 1s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1>🏏 Cricket Agent</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Live scores, player stats, and match information at your fingertips</p>", unsafe_allow_html=True)

# Stats bar
st.markdown("""
<div class='stats-bar'>
    <div class='stat-item'>
        <div class='stat-value'>🔴</div>
        <div class='stat-label'>Live Scores</div>
    </div>
    <div class='stat-item'>
        <div class='stat-value'>📊</div>
        <div class='stat-label'>Player Stats</div>
    </div>
    <div class='stat-item'>
        <div class='stat-value'>🏆</div>
        <div class='stat-label'>Series Info</div>
    </div>
    <div class='stat-item'>
        <div class='stat-value'>💰</div>
        <div class='stat-label'>100% Free</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Setup")

    llm = OllamaClient()
    if llm.is_available():
        st.success("✅ Ollama connected")
    else:
        st.error("❌ Ollama not running")
        with st.expander("How to fix"):
            st.code("ollama serve", language="bash")
            st.code("ollama pull llama3.1:8b", language="bash")

    st.divider()

    cricket_key = st.text_input(
        "🔑 Cricket API Key",
        value=os.getenv("CRICKET_API_KEY", ""),
        type="password",
        help="Get free at cricapi.com"
    )
    if cricket_key:
        os.environ["CRICKET_API_KEY"] = cricket_key
        st.success("✅ API key set")
    else:
        st.warning("⚠️ Enter API key")
        st.link_button("Get Free Key", "https://cricapi.com/")

    st.divider()

    st.markdown("## 💡 Try asking...")
    examples = [
        "🔴 What matches are live right now?",
        "🏏 Virat Kohli stats",
        "⚔️ Compare Kohli vs Babar Azam",
        "🏆 Upcoming cricket series",
        "🌟 Tell me about Ben Stokes",
    ]
    for example in examples:
        st.markdown(f"• {example}")

    st.divider()

    st.markdown("### 🛠️ Tech Stack")
    st.caption("**LLM:** Llama 3.1 (Ollama)")
    st.caption("**Data:** CricAPI")
    st.caption("**UI:** Streamlit")

    st.divider()

    st.markdown("### 👩‍💻 Built by")
    st.markdown("[Geetanjali Pramod](https://linkedin.com/in/geetanjalipramod)")
    st.caption("Principal Analytics & AI Strategy")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None

if "cricket_key_used" not in st.session_state:
    st.session_state.cricket_key_used = None

current_key = os.getenv("CRICKET_API_KEY", "")
if current_key and current_key != st.session_state.cricket_key_used:
    st.session_state.agent = None
    st.session_state.cricket_key_used = current_key

# Main chat area
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    if not st.session_state.messages:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; color: #a0d0a0;'>
            <div style='font-size: 4rem;' class='bouncing'>🏏</div>
            <p style='font-size: 1.2rem; margin-top: 1rem;'>
                Ready for cricket action!<br>
                Ask about live matches, player stats, or series.
            </p>
        </div>
        """, unsafe_allow_html=True)

    for message in st.session_state.messages:
        avatar = "🧑" if message["role"] == "user" else "🏏"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

is_ready = llm.is_available() and os.getenv("CRICKET_API_KEY")

if prompt := st.chat_input("🏏 Ask about cricket...", disabled=not is_ready):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with col2:
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

    if st.session_state.agent is None:
        st.session_state.agent = CricketAgent(verbose=True)

    with col2:
        with st.chat_message("assistant", avatar="🏏"):
            with st.spinner("🏏 Checking scores..."):
                try:
                    response = st.session_state.agent.chat(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"❌ Error: {e}")

with col2:
    if st.session_state.messages:
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                if st.session_state.agent:
                    st.session_state.agent.reset()
                st.rerun()

if not is_ready:
    with col2:
        st.warning("👈 Complete setup in the sidebar to start!")
