import streamlit as st
import requests
import pandas as pd
import uuid
import threading
from utils.chart_generator import generate_chart

API_URL = "http://localhost:5001"

# ── Auth guard ────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.warning("Please log in to access the dashboard.")
    if st.button("Go to Login"):
        st.switch_page("views/auth.py")
    st.stop()

username = st.session_state.get("username", "user")


# ─────────────────────────────────────────────────────────────
# Persistence helpers
# ─────────────────────────────────────────────────────────────

def _slim_history(history: list) -> list:
    """Strip large data arrays before saving to keep JSON small."""
    slim = []
    for msg in history:
        entry = dict(msg)
        # Keep only first 200 rows of data to bound file size
        if "data" in entry and isinstance(entry["data"], list):
            entry["data"] = entry["data"][:200]
        slim.append(entry)
    return slim

def _save_chats():
    try:
        payload = {
            cid: {**c, "history": _slim_history(c["history"])}
            for cid, c in st.session_state["chats"].items()
        }
        requests.post(f"{API_URL}/chats/{username}", json=payload, timeout=3)
    except Exception:
        pass   # never block the user for a save failure

def _load_chats() -> dict:
    try:
        r = requests.get(f"{API_URL}/chats/{username}", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}

def _delete_chat_remote(chat_id: str):
    """Fire-and-forget: delete from backend in a background thread."""
    def _do():
        try:
            requests.delete(f"{API_URL}/chats/{username}/{chat_id}", timeout=5)
        except Exception:
            pass
    threading.Thread(target=_do, daemon=True).start()


# ─────────────────────────────────────────────────────────────
# Session-state init
# ─────────────────────────────────────────────────────────────

def _new_chat_id() -> str:
    return str(uuid.uuid4())

def _make_chat(title="New Chat") -> dict:
    return {
        "title":      title,
        "history":    [],
        "schema":     "",
        "data_loaded": False,
        "chat_id":    _new_chat_id(),
        "name_set":   False,
    }

# Load persisted chats once per login session
if "chats" not in st.session_state:
    loaded = _load_chats()
    if loaded:
        st.session_state["chats"] = loaded
        st.session_state["current_chat_id"] = next(iter(loaded))
    else:
        first = _make_chat()
        st.session_state["chats"] = {first["chat_id"]: first}
        st.session_state["current_chat_id"] = first["chat_id"]

# Safety: ensure current_chat_id is valid
if st.session_state.get("current_chat_id") not in st.session_state["chats"]:
    st.session_state["current_chat_id"] = next(iter(st.session_state["chats"]))

# Show delete success toast (set during dialog, consumed here)
if "_last_deleted_name" in st.session_state:
    _deleted_name = st.session_state.pop("_last_deleted_name")
    st.toast(f"🗑️ Chat \u201c{_deleted_name}\u201d deleted successfully.", icon="✅")

def current() -> dict:
    return st.session_state["chats"][st.session_state["current_chat_id"]]

def switch_to(cid: str):
    st.session_state["current_chat_id"] = cid


# ─────────────────────────────────────────────────────────────
# Delete confirmation dialog
# ─────────────────────────────────────────────────────────────

@st.dialog("⚠️ Delete Chat")
def confirm_delete_dialog():
    cid   = st.session_state.get("_pending_delete_id", "")
    chats = st.session_state["chats"]
    if not cid or cid not in chats:
        st.rerun()
        return

    title = chats[cid]["title"]
    st.markdown(f"Are you sure you want to permanently delete **\"{title}\"**?")
    st.error("This action is **irreversible** and **cannot be undone**.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Yes, Delete", type="primary", use_container_width=True):
            # Save name BEFORE deleting so toast can reference it
            st.session_state["_last_deleted_name"] = title
            # Update local state immediately
            del st.session_state["chats"][cid]
            st.session_state.pop("_pending_delete_id", None)
            remaining = st.session_state["chats"]
            if not remaining:
                new = _make_chat()
                remaining[new["chat_id"]] = new
            if st.session_state.get("current_chat_id") == cid:
                st.session_state["current_chat_id"] = next(iter(remaining))
            # Fire backend delete + save in background (non-blocking)
            _delete_chat_remote(cid)
            threading.Thread(target=_save_chats, daemon=True).start()
            st.rerun()   # closes dialog instantly
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.pop("_pending_delete_id", None)
            st.rerun()


# ── Styles ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

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

.welcome-card {
    background: linear-gradient(135deg, #f5f3ff, #ede9fe);
    border: 1px solid #c4b5fd;
    border-radius: 20px;
    padding: 40px 48px;
    text-align: center;
    margin-top: 32px;
}
.welcome-card h2 { color: #6d28d9; font-size: 1.6rem; margin: 0 0 8px; }
.welcome-card p  { color: #7c3aed; font-size: 1rem; margin: 6px 0; }
.welcome-card .hint { color: #9ca3af; font-size: 0.88rem; margin-top: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────
col_brand, col_user, col_logout = st.columns([5, 3, 2])
with col_brand:
    st.markdown('<div style="font-size:1.4rem;font-weight:800;color:#7c3aed;">📈 Apex Analytics</div>',
                unsafe_allow_html=True)
with col_user:
    st.markdown(f'<div style="color:#9ca3af;padding-top:8px;">👤 {username}</div>', unsafe_allow_html=True)
with col_logout:
    if st.button("Logout", key="logout"):
        _save_chats()
        for key in ["logged_in", "username", "token", "chats", "current_chat_id"]:
            st.session_state.pop(key, None)
        st.switch_page("views/landing.py")

st.markdown("---")

# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────
with st.sidebar:

    # ── New Chat ──────────────────────────────────────────────
    if st.button("✏️  New Chat", use_container_width=True, type="primary"):
        new = _make_chat()
        st.session_state["chats"][new["chat_id"]] = new
        st.session_state["current_chat_id"] = new["chat_id"]
        _save_chats()
        st.rerun()

    # ── Dataset Upload ────────────────────────────────────────
    st.markdown("#### 📂 Dataset")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    if uploaded_file and st.button("Load Dataset", type="primary"):
        with st.spinner("Processing dataset…"):
            try:
                new_cid = _new_chat_id()
                files   = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
                resp    = requests.post(f"{API_URL}/upload", files=files, data={"chat_id": new_cid})
                if resp.status_code == 200:
                    backend_cid = resp.json().get("chat_id", new_cid)
                    cur = current()
                    cur["chat_id"]    = backend_cid
                    cur["data_loaded"] = True
                    cur["schema"]     = resp.json().get("schema", "")
                    cur["history"]    = []
                    cur["name_set"]   = False
                    cur["title"]      = "New Chat"
                    st.success(f"✅ {uploaded_file.name} loaded!")
                    _save_chats()
                    st.rerun()
                else:
                    st.error(f"Upload failed: {resp.json().get('error', 'Unknown')}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach backend. Is Flask running?")

    if current().get("data_loaded") and current().get("schema"):
        with st.expander("📋 Dataset Schema"):
            st.code(current()["schema"], language="text")

    st.markdown("---")

    # ── Recent Chats ──────────────────────────────────────────
    st.markdown("#### 🕒 Recent Chats")
    chats     = st.session_state["chats"]
    active_id = st.session_state["current_chat_id"]

    for cid in reversed(list(chats.keys())):
        chat_item = chats[cid]
        label     = chat_item["title"]
        display   = f"{'💬' if cid != active_id else '▶'} {label[:24]}…" if len(label) > 24 \
                    else f"{'💬' if cid != active_id else '▶'} {label}"

        col_btn, col_menu = st.columns([5, 1])
        with col_btn:
            disabled = (cid == active_id)
            if st.button(display, key=f"chat_btn_{cid}", use_container_width=True, disabled=disabled):
                switch_to(cid)
                st.rerun()
        with col_menu:
            with st.popover("⋯", use_container_width=True):
                if st.button("🗑️ Delete", key=f"del_{cid}", use_container_width=True):
                    st.session_state["_pending_delete_id"] = cid
                    st.rerun()

# Show modal if a delete is pending
if st.session_state.get("_pending_delete_id"):
    confirm_delete_dialog()


# ─────────────────────────────────────────────────────────────
# Main area
# ─────────────────────────────────────────────────────────────
chat = current()

# ── No data loaded ────────────────────────────────────────────
if not chat.get("data_loaded"):
    st.markdown(f"""
    <div class="welcome-card">
      <h2>👋 Hi, {username.title()}!</h2>
      <p>I'm <strong>Apex</strong>, your AI analytics assistant.</p>
      <p>I can turn your CSV data into interactive dashboards — just by chatting.</p>
      <p class="hint">👈 Upload a CSV from the sidebar to get started.</p>
    </div>
    """, unsafe_allow_html=True)

# ── Data loaded but no name set ───────────────────────────────
elif not chat.get("name_set"):
    st.markdown("""
    <div class="welcome-card">
      <h2>📁 Dataset Ready!</h2>
      <p>Give this chat a unique name so you can find it later.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    chat_name_input = st.text_input(
        "Chat name",
        placeholder="e.g. Q1 Sales Analysis, Marketing ROI…",
        key="chat_name_input",
    )
    if st.button("Start Chat →", type="primary"):
        name = chat_name_input.strip()
        if not name:
            st.error("Please enter a chat name.")
        else:
            chat["title"]    = name
            chat["name_set"] = True
            _save_chats()
            st.rerun()

# ── Active chat ───────────────────────────────────────────────
else:
    # Collect prompt BEFORE deciding what to render
    prompt = st.chat_input(f"Ask about {chat['title']}…")

    if prompt:
        chat["history"].append({"role": "user", "content": prompt})

    if not chat["history"]:
        st.markdown(f"""
        <div style="text-align:center;margin-top:60px;color:#9ca3af;">
          <div style="font-size:2.5rem;">💬</div>
          <p>Ask your first question about <strong style="color:#7c3aed;">{chat['title']}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Render history
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

        # Backend call for new prompt
        if prompt:
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Analysing…"):
                    try:
                        resp   = requests.post(f"{API_URL}/chat", json={
                            "prompt":  prompt,
                            "chat_id": chat["chat_id"]
                        })
                        result = resp.json()

                        if resp.status_code == 200:
                            if result.get("status") == "clarification":
                                question = result.get("question", "Could you clarify?")
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
                            err = result.get("error", "Unknown error.")
                            st.error(err)
                            chat["history"].append({
                                "role": "assistant",
                                "explanation": f"❌ {err}",
                                "data": [], "chart_config": {}, "generated_sql": "",
                            })

                        _save_chats()   # persist after every exchange

                    except requests.exceptions.ConnectionError:
                        st.error("Cannot reach backend. Is Flask running?")
