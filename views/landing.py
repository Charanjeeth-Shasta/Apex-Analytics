import streamlit as st



# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hero */
.hero {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 20px;
    padding: 80px 60px;
    text-align: center;
    margin-bottom: 40px;
}
.hero h1 { font-size: 3.5rem; font-weight: 800; color: #ffffff; margin: 0 0 16px; }
.hero p  { font-size: 1.25rem; color: #c9c9e3; margin: 0 0 36px; max-width: 640px; margin-left: auto; margin-right: auto; }

/* Feature cards */
.cards { display: flex; gap: 24px; flex-wrap: wrap; justify-content: center; margin-bottom: 48px; }
.card {
    background: #1a1a2e;
    border: 1px solid #2e2e52;
    border-radius: 16px;
    padding: 32px 28px;
    flex: 1 1 240px;
    max-width: 280px;
    transition: transform .2s, box-shadow .2s;
}
.card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,0.4); }
.card-icon { font-size: 2.4rem; margin-bottom: 12px; }
.card h3 { color: #a78bfa; margin: 0 0 8px; font-size: 1.1rem; }
.card p  { color: #9ca3af; font-size: 0.92rem; margin: 0; line-height: 1.6; }

/* How it works steps */
.steps { display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; margin-bottom: 48px; }
.step {
    text-align: center;
    flex: 1 1 150px;
    max-width: 180px;
    color: #d1d5db;
}
.step-num {
    width: 40px; height: 40px; border-radius: 50%;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white; font-weight: 700; font-size: 1rem;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 10px;
}
.step p { font-size: 0.88rem; color: #9ca3af; margin: 4px 0 0; }
.step-arrow { align-self: center; color: #4f46e5; font-size: 1.4rem; margin-top: -30px; }

/* CTA button wrapper */
.cta-wrapper { text-align: center; margin-top: 8px; }

/* Override Streamlit button */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: white;
    border: none;
    border-radius: 50px;
    padding: 14px 48px;
    font-size: 1.05rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity .2s;
}
div[data-testid="stButton"] > button:hover { opacity: 0.88; }

/* Footer */
.footer { text-align: center; color: #4b5563; font-size: 0.82rem; margin-top: 48px; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>📈 Apex Analytics</h1>
  <p>Turn any CSV into an interactive Business Intelligence dashboard — just by asking a question in plain English. No SQL. No setup.</p>
</div>
""", unsafe_allow_html=True)

# ── CTA ───────────────────────────────────────────────────────
col = st.columns([1, 2, 1])[1]
with col:
    if st.button("🚀  Get Started — It's Free", use_container_width=True):
        st.switch_page("views/auth.py")

st.markdown("---")

# ── Feature cards ────────────────────────────────────────────
st.markdown("""
<div class="cards">
  <div class="card">
    <div class="card-icon">📂</div>
    <h3>Upload Any CSV</h3>
    <p>Drop in any structured dataset — sales data, marketing metrics, HR reports — it just works.</p>
  </div>
  <div class="card">
    <div class="card-icon">💬</div>
    <h3>Ask in Plain English</h3>
    <p>Type questions like "Show revenue by region" and let AI handle the rest. No SQL knowledge needed.</p>
  </div>
  <div class="card">
    <div class="card-icon">📊</div>
    <h3>Instant Dashboards</h3>
    <p>Get interactive Plotly charts with hover, zoom, and legends — generated in seconds.</p>
  </div>
  <div class="card">
    <div class="card-icon">🔁</div>
    <h3>Conversational Editing</h3>
    <p>Follow up with "Now filter for Q3" or "Make it a pie chart" — the AI remembers context.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────────
st.markdown("### ⚡ How It Works")
st.markdown("""
<div class="steps">
  <div class="step">
    <div class="step-num">1</div>
    <strong>Upload</strong>
    <p>Upload your CSV dataset</p>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-num">2</div>
    <strong>Ask</strong>
    <p>Type your question in plain English</p>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-num">3</div>
    <strong>Analyse</strong>
    <p>AI generates SQL and queries your data</p>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-num">4</div>
    <strong>Visualise</strong>
    <p>Interactive chart rendered instantly</p>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
col2 = st.columns([1, 2, 1])[1]
with col2:
    if st.button("Get Started Now →", use_container_width=True, key="cta2"):
        st.switch_page("views/auth.py")

st.markdown('<div class="footer">© 2026 Apex Analytics · Built with Streamlit & Google Gemini</div>', unsafe_allow_html=True)
