import streamlit as st
import requests
import pandas as pd
import uuid
from utils.chart_generator import generate_chart

API_URL = "http://localhost:5001"

# ── Auth guard ────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.warning("Please log in to access the dashboard.")
    if st.button("Go to Login"):
        st.switch_page("views/auth.py")
    st.stop()


# ─────────────────────────────────────────────────────────────
# Session-state helpers
# ─────────────────────────────────────────────────────────────

def _new_chat_id() -> str:
    return str(uuid.uuid4())

def _make_chat(title="New Chat"):
    return {
        "title": title,
        "history": [],
        "schema": "",
        "data_loaded": False,
        "chat_id": _new_chat_id(),
        "name_set": False,      # whether user has confirmed a chat name
    }

if "chats" not in st.session_state:
    first = _make_chat()
    st.session_state["chats"] = {first["chat_id"]: first}
    st.session_state["current_chat_id"] = first["chat_id"]

if st.session_state.get("current_chat_id") not in st.session_state["chats"]:
    cid = next(iter(st.session_state["chats"]))
    st.session_state["current_chat_id"] = cid

def current() -> dict:
    return st.session_state["chats"][st.session_state["current_chat_id"]]

def switch_to(cid: str):
    st.session_state["current_chat_id"] = cid


# ── Styles ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Make chat input white */
div[data-testid="stChatInput"] textarea {
    border-radius: 12px !important;
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
}
div[data-testid="stChatInput"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    border: 1px solid #e5e7eb !important;
}

/* Welcome card */
.welcome-card {
    background: linear-gradient(135deg, #f5f3ff, #ede9fe);
    border: 1px solid #c4b5fd;
    border-radius: 20px;
    padding: 40px 48px;
    text-align: center;
    margin-top: 32px;
}
.welcome-card h2 { color: #6d28d9; font-size: 1.6rem; margin: 0 0 8px; }
.welcome-card p  { color: #7c3aed; font-size: 1rem; margin: 0; }
.welcome-card .hint { color: #9ca3af; font-size: 0.88rem; margin-top: 12px; }

/* Name chat box */
.name-chat-box {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────
username = st.session_state.get("username", "user")
col_brand, col_user, col_logout = st.columns([5, 3, 2])
with col_brand:
    st.markdown('<div style="font-size:1.4rem;font-weight:800;color:#7c3aed;">📈 Apex Analytics</div>', unsafe_allow_html=True)
with col_user:
    st.markdown(f'<div style="color:#9ca3af;padding-top:8px;">👤 {username}</div>', unsafe_allow_html=True)
with col_logout:
    if st.button("Logout", key="logout"):
        for key in ["logged_in", "username", "token", "chats", "current_chat_id"]:
            st.session_state.pop(key, None)
        st.switch_page("views/landing.py")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────
with st.sidebar:

    # ── 1. New Chat + Dataset upload (TOP) ───────────────────
    if st.button("✏️  New Chat", use_container_width=True, type="primary"):
        new = _make_chat()
        st.session_state["chats"][new["chat_id"]] = new
        st.session_state["current_chat_id"] = new["chat_id"]
        st.rerun()

    st.markdown("#### 📂 Dataset")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    if uploaded_file and st.button("Load Dataset", type="primary"):
        with st.spinner("Processing dataset…"):
            try:
                new_chat_id = _new_chat_id()
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
                resp = requests.post(
                    f"{API_URL}/upload",
                    files=files,
                    data={"chat_id": new_chat_id}
                )
                if resp.status_code == 200:
                    backend_chat_id = resp.json().get("chat_id", new_chat_id)
                    cur = current()
                    cur["chat_id"]     = backend_chat_id
                    cur["data_loaded"] = True
                    cur["schema"]      = resp.json().get("schema", "")
                    cur["history"]     = []
                    cur["name_set"]    = False   # prompt for name
                    cur["title"]       = "New Chat"
                    st.success(f"✅ {uploaded_file.name} loaded!")
                    st.rerun()
                else:
                    st.error(f"Upload failed: {resp.json().get('error', 'Unknown error')}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach backend. Is Flask running?")

    if current().get("data_loaded") and current().get("schema"):
        with st.expander("📋 Dataset Schema"):
            st.code(current()["schema"], language="text")

    st.markdown("---")

    # ── 2. Recent Chats list (BELOW dataset) ─────────────────
    st.markdown("#### 🕒 Recent Chats")
    chats    = st.session_state["chats"]
    active_id = st.session_state["current_chat_id"]

    for cid in reversed(list(chats.keys())):
        chat      = chats[cid]
        label     = chat["title"]
        is_active = cid == active_id
        display   = f"💬 {label[:26]}…" if len(label) > 26 else f"💬 {label}"

        col_btn, col_del = st.columns([5, 1])
        with col_btn:
            btn_label = f"**{display}**" if is_active else display
            if st.button(display, key=f"chat_btn_{cid}", use_container_width=True):
                switch_to(cid)
                st.rerun()
        with col_del:
            if len(chats) > 1:
                if st.button("🗑", key=f"del_{cid}"):
                    del st.session_state["chats"][cid]
                    if active_id == cid:
                        st.session_state["current_chat_id"] = next(iter(st.session_state["chats"]))
                    st.rerun()


# ─────────────────────────────────────────────────────────────
# Main area
# ─────────────────────────────────────────────────────────────
chat = current()

# ── STATE A: No data loaded — welcome screen ──────────────────
if not chat.get("data_loaded"):
    st.markdown(f"""
    <div class="welcome-card">
      <h2>👋 Hi, {username.title()}!</h2>
      <p>I'm <strong>Apex</strong>, your AI analytics assistant.</p>
      <p>I can turn your CSV data into interactive dashboards — just by chatting.</p>
      <p class="hint">👈 Upload a CSV from the sidebar to get started.</p>
    </div>
    """, unsafe_allow_html=True)

# ── STATE B: Data loaded, but chat not yet named ──────────────
elif not chat.get("name_set"):
    st.markdown(f"""
    <div class="welcome-card">
      <h2>📁 Dataset Ready!</h2>
      <p>Give this chat a unique name before you start asking questions.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    with st.container():
        chat_name_input = st.text_input(
            "Chat name",
            placeholder="e.g. Q1 Sales Analysis, Marketing ROI…",
            key="chat_name_input",
            label_visibility="visible",
        )
        if st.button("Start Chat →", type="primary"):
            name = chat_name_input.strip()
            if not name:
                st.error("Please enter a chat name.")
            else:
                chat["title"]    = name
                chat["name_set"] = True
                st.rerun()

# ── STATE C: Active chat ──────────────────────────────────────
else:
    # Render history
    if not chat["history"]:
        st.markdown(f"""
        <div style="text-align:center;margin-top:60px;color:#9ca3af;">
          <div style="font-size:2.5rem;">💬</div>
          <p style="font-size:1rem;">Ask your first question about <strong style="color:#7c3aed;">{chat['title']}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    for msg in chat["history"]:
        role = msg["role"]
        with st.chat_message(role, avatar="🧑" if role == "user" else "🤖"):
            if role == "user":
                st.markdown(msg["content"])
            else:
                st.markdown(f"**{msg.get('explanation', '')}**")
                chart_data   = msg.get("data")
                chart_config = msg.get("chart_config", {})
                if chart_data:
                    fig = generate_chart(chart_data, chart_config)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    with st.expander("📄 View Data Table", expanded=False):
                        st.dataframe(pd.DataFrame(chart_data), use_container_width=True)
                sql = msg.get("generated_sql", "")
                if sql:
                    with st.expander("🔍 Generated SQL", expanded=False):
                        st.code(sql, language="sql")

    # Chat input
    prompt = st.chat_input(f"Ask about {chat['title']}…")

    if prompt:
        chat["history"].append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analysing…"):
                try:
                    resp = requests.post(f"{API_URL}/chat", json={
                        "prompt":  prompt,
                        "chat_id": chat["chat_id"]
                    })
                    result = resp.json()

                    if resp.status_code == 200:
                        if result.get("status") == "clarification":
                            question = result.get("question", "Could you clarify your question?")
                            st.markdown(f"💬 **I need a bit more detail:**\n\n{question}")
                            chat["history"].append({
                                "role": "assistant",
                                "explanation": f"💬 **I need a bit more detail:**\n\n{question}",
                                "data": [], "chart_config": {}, "generated_sql": "",
                            })
                        else:
                            data         = result.get("data", [])
                            chart_config = result.get("chart_config", {})
                            details      = result.get("query_details", {})
                            explanation  = details.get("explanation", "Here are your results.")
                            sql          = details.get("generated_sql", "")

                            st.markdown(f"**{explanation}**")
                            if data:
                                fig = generate_chart(data, chart_config)
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                                with st.expander("📄 View Data Table", expanded=False):
                                    st.dataframe(pd.DataFrame(data), use_container_width=True)
                            if sql:
                                with st.expander("🔍 Generated SQL", expanded=False):
                                    st.code(sql, language="sql")

                            chat["history"].append({
                                "role": "assistant",
                                "explanation": explanation,
                                "data": data,
                                "chart_config": chart_config,
                                "generated_sql": sql,
                            })
                    else:
                        err = result.get("error", "An error occurred.")
                        st.error(err)
                        chat["history"].append({
                            "role": "assistant",
                            "explanation": f"❌ {err}",
                            "data": [], "chart_config": {}, "generated_sql": "",
                        })

                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach backend. Is Flask running?")
