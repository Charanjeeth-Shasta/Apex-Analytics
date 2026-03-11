import streamlit as st
import requests



API_URL = "http://localhost:5001"

# ── If already logged in, skip straight to dashboard ─────────
if st.session_state.get("logged_in"):
    st.switch_page("views/dashboard.py")

# ── Styles ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #0f0c29; }

.auth-header { text-align: center; margin-bottom: 8px; }
.auth-header h1 { font-size: 2rem; font-weight: 800; color: #fff; margin: 0; }
.auth-header p  { color: #9ca3af; font-size: 0.95rem; margin: 4px 0 24px; }

.rule { font-size: 0.8rem; color: #6b7280; margin-top: -10px; margin-bottom: 12px; line-height: 1.5; }
.rule span { display: block; }
.rule .ok   { color: #34d399; }
.rule .fail { color: #f87171; }

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white; border: none; border-radius: 50px;
    padding: 12px 36px; font-size: 1rem; font-weight: 600;
    width: 100%; transition: opacity .2s;
}
div[data-testid="stButton"] > button:hover { opacity: 0.85; }

.back-link { text-align: center; margin-top: 16px; }
.back-link a { color: #a78bfa; text-decoration: none; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="auth-header">
  <h1>📈 <span style="color:#a78bfa;font-weight:800;">Apex Analytics</span></h1>
  <p>Sign in or create an account to get started</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────
tab_login, tab_signup = st.tabs(["🔑  Login", "✨  Sign Up"])

# ── Helpers ───────────────────────────────────────────────────
import re

def check_username(u):
    rules = {
        "len":   (5 <= len(u) <= 20,       "5–20 characters"),
        "chars": (bool(re.match(r'^[A-Za-z0-9_]+$', u)), "Letters, numbers, underscores only"),
    }
    return rules

def check_password(p):
    rules = {
        "len":   (len(p) >= 8,                                 "At least 8 characters"),
        "upper": (bool(re.search(r'[A-Z]', p)),                "At least one uppercase letter (A-Z)"),
        "num":   (bool(re.search(r'[0-9]', p)),                "At least one number (0-9)"),
        "spec":  (bool(re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>?/\\|`~]', p)),
                  "At least one special character (!@#$…)"),
    }
    return rules

def rules_html(rules: dict) -> str:
    lines = []
    for _, (ok, label) in rules.items():
        cls = "ok" if ok else "fail"
        icon = "✔" if ok else "✘"
        lines.append(f'<span class="{cls}">{icon} {label}</span>')
    return '<div class="rule">' + "".join(lines) + "</div>"

# ═══════════════════════════════════════════════
# LOGIN TAB
# ═══════════════════════════════════════════════
with tab_login:
    st.markdown("#### Welcome back")
    l_user = st.text_input("Username", key="login_user", placeholder="your_username")
    l_pass = st.text_input("Password", key="login_pass", type="password", placeholder="••••••••")

    if st.button("Login", key="btn_login"):
        if not l_user or not l_pass:
            st.error("Please fill in both fields.")
        else:
            try:
                resp = requests.post(f"{API_URL}/login", json={"username": l_user, "password": l_pass})
                data = resp.json()
                if resp.status_code == 200:
                    st.session_state["logged_in"] = True
                    st.session_state["username"]  = data["username"]
                    st.session_state["token"]     = data["token"]
                    st.session_state["session_id"] = data["token"]
                    st.success("Logged in! Redirecting…")
                    st.switch_page("views/dashboard.py")
                else:
                    st.error(data.get("message", "Login failed."))
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach backend. Is Flask running?")

# ═══════════════════════════════════════════════
# SIGNUP TAB
# ═══════════════════════════════════════════════
with tab_signup:
    st.markdown("#### Create your account")
    s_user = st.text_input("Username", key="signup_user", placeholder="choose_username")
    u_rules = check_username(s_user)
    st.markdown(rules_html(u_rules), unsafe_allow_html=True)

    s_pass = st.text_input("Password", key="signup_pass", type="password", placeholder="••••••••")
    p_rules = check_password(s_pass)
    st.markdown(rules_html(p_rules), unsafe_allow_html=True)

    s_pass2 = st.text_input("Confirm Password", key="signup_pass2", type="password", placeholder="••••••••")

    if st.button("Create Account", key="btn_signup"):
        if not s_user or not s_pass or not s_pass2:
            st.error("Please fill in all fields.")
        elif s_pass != s_pass2:
            st.error("Passwords do not match.")
        elif not all(ok for ok, _ in u_rules.values()):
            st.error("Please fix the username issues highlighted above.")
        elif not all(ok for ok, _ in p_rules.values()):
            st.error("Please fix the password issues highlighted above.")
        else:
            try:
                resp = requests.post(f"{API_URL}/register", json={"username": s_user, "password": s_pass})
                data = resp.json()
                if resp.status_code == 200:
                    st.success(data.get("message", "Account created! Please log in."))
                else:
                    st.error(data.get("message", "Registration failed."))
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach backend. Is Flask running?")

# Back to home
st.markdown('<div class="back-link"><a href="/">← Back to Home</a></div>', unsafe_allow_html=True)
