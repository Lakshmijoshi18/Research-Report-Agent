"""
STEP 6: The Streamlit Website (v4 - branded look)
------------------------------------------------------
Changes in this version:
  - Replaced the loud purple gradient with a calm, premium earthy palette
  - Added a proper logo mark (R2A) + wordmark in a header, like a real product
  - The whole app now uses FIXED custom colors (not Streamlit's light/dark
    theme) so it always looks intentional and is never affected by the
    viewer's theme setting

SETUP (one-time):
  pip install streamlit markdown2 xhtml2pdf

RUN LOCALLY:
  streamlit run streamlit_app.py
"""

import io
import time
import markdown2
from xhtml2pdf import pisa
import streamlit as st
from planner import plan_research
from search_tool import search_web
from fetch_tool import fetch_article_text
from synthesizer import synthesize_findings
from report_generator import generate_report

st.set_page_config(page_title="R2A · Research & Report Agent", page_icon="🌾", layout="centered")

INCLUDE_SOURCES = False

st.markdown("""
<style>
    :root {
        --bg: #f6f4ef;
        --card: #ffffff;
        --ink: #2b2a26;
        --muted: #7a776d;
        --accent: #4a5d43;
        --accent-dark: #3a4a35;
        --accent-soft: #e7ebe1;
        --border: #e6e2d8;
    }

    .stApp {
        background-color: var(--bg) !important;
    }
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li {
        color: var(--ink);
    }
    .main .block-container {
        max-width: 760px;
        padding-top: 2rem;
    }

    /* Header / navbar */
    .navbar {
        display: flex;
        align-items: center;
        gap: 14px;
        padding-bottom: 1.4rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.8rem;
    }
    .logo-badge {
        width: 50px;
        height: 50px;
        border-radius: 13px;
        background: var(--accent);
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: Georgia, 'Times New Roman', serif;
        font-weight: 700;
        font-size: 1.15rem;
        flex-shrink: 0;
    }
    .logo-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--ink);
        line-height: 1.2;
    }
    .logo-sub {
        font-size: 0.88rem;
        color: var(--muted);
    }

    .tags { margin-top: 0.2rem; }
    .tag {
        display: inline-block;
        background: var(--accent-soft);
        color: var(--accent-dark);
        padding: 0.22rem 0.65rem;
        border-radius: 999px;
        font-size: 0.75rem;
        margin-right: 6px;
        margin-top: 6px;
        font-weight: 600;
    }

    /* How-it-works strip */
    .steps-row {
        display: flex;
        gap: 12px;
        margin-bottom: 1.8rem;
    }
    .step-card {
        flex: 1;
        background: var(--accent-soft);
        border-radius: 12px;
        padding: 0.9rem 1rem;
        text-align: center;
    }
    .step-card .step-icon { font-size: 1.3rem; }
    .step-card .step-label {
        font-weight: 700;
        font-size: 0.85rem;
        color: var(--accent-dark);
        margin-top: 2px;
    }
    .step-card .step-desc {
        font-size: 0.72rem;
        color: var(--muted);
        margin-top: 1px;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 10px;
        padding: 0.7rem 1rem;
        border: 1.5px solid var(--border);
        background: var(--card);
        color: var(--ink);
    }
    div.stButton > button {
        border-radius: 10px;
        padding: 0.55rem 1.4rem;
        font-weight: 600;
        border: none;
        background: var(--accent);
        color: #ffffff !important;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    div.stButton > button:hover {
        background: var(--accent-dark);
        color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(74,93,67,0.35);
    }
    /* Primary button (Generate Report) has its own default styling that
       overrides plain button rules above -- target it explicitly */
    div.stButton > button[kind="primary"],
    div.stButton > button[kind="primary"] p,
    div.stButton > button[kind="primary"] span {
        background: var(--accent) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[kind="primary"]:hover p {
        background: var(--accent-dark) !important;
        color: #ffffff !important;
    }
    div.stDownloadButton > button {
        border-radius: 10px;
        font-weight: 600;
        background: var(--accent);
        color: #ffffff !important;
        border: none;
    }
    div.stDownloadButton > button:hover {
        background: var(--accent-dark);
        color: #ffffff !important;
    }

    .report-card, .report-card * {
        color: var(--ink) !important;
    }
    .report-card {
        background: var(--card) !important;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 2rem 2.2rem;
        margin-top: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    }
    .report-card h1 { font-size: 1.5rem !important; margin-top: 0; }
    .report-card h2 { font-size: 1.2rem !important; margin-top: 1.2rem; color: var(--accent-dark) !important; }
    .report-card h3 { font-size: 1.05rem !important; margin-top: 1rem; }

    section[data-testid="stSidebar"] {
        background-color: #efece3 !important;
        border-right: 2px solid var(--ink) !important;
    }
    section[data-testid="stSidebar"] * {
        color: var(--ink) !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        text-align: left;
        width: 100%;
        margin-bottom: 6px;
        border-radius: 8px;
        background: var(--card) !important;
        color: var(--ink) !important;
        border: 1px solid var(--border) !important;
        font-weight: 500;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent-dark) !important;
    }

    /* Hide Streamlit's default "Press Enter to apply" hint under inputs */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


def markdown_to_pdf_bytes(markdown_text: str) -> bytes:
    html = markdown2.markdown(markdown_text)
    styled_html = f"""
    <html>
    <head>
      <style>
        body {{ font-family: Helvetica, Arial, sans-serif; font-size: 12px; line-height: 1.5; color: #2b2a26; }}
        h1 {{ font-size: 22px; }}
        h2 {{ font-size: 18px; margin-top: 20px; color: #3a4a35; }}
        h3 {{ font-size: 14px; margin-top: 14px; }}
      </style>
    </head>
    <body>{html}</body>
    </html>
    """
    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(styled_html, dest=pdf_buffer)
    return pdf_buffer.getvalue()


def run_agent(topic: str, session_history_titles: list[str]) -> str:
    status = st.status("Running the agent...", expanded=True)

    status.write("Planning research...")
    sub_questions = plan_research(topic, session_history=session_history_titles)

    if not sub_questions:
        status.update(label="Failed to plan research.", state="error")
        return None

    status.write(f"Generated {len(sub_questions)} sub-questions.")

    research_data = []
    for q in sub_questions:
        status.write(f"Searching: {q}")
        results = search_web(q, max_results=3)
        for r in results:
            full_text = fetch_article_text(r["url"])
            r["content"] = full_text if full_text else r["snippet"]
        research_data.append({"question": q, "results": results})
        time.sleep(2)  # small pause to avoid DuckDuckGo rate-limiting

    status.write("Synthesizing findings...")
    findings = synthesize_findings(topic, research_data)

    status.write("Writing final report...")
    sources = None
    if INCLUDE_SOURCES:
        sources = [r["url"] for item in research_data for r in item["results"]]
    report = generate_report(topic, findings, sources=sources)

    status.update(label="Done!", state="complete")
    return report


def render_report(topic: str, report: str):
    st.markdown(f'<div class="report-card">{markdown2.markdown(report)}</div>', unsafe_allow_html=True)
    pdf_bytes = markdown_to_pdf_bytes(report)
    st.download_button(
        label="⬇ Download report (PDF)",
        data=pdf_bytes,
        file_name=f"{topic.replace(' ', '_')}_report.pdf",
        mime="application/pdf",
    )


if "history" not in st.session_state:
    st.session_state.history = []
if "viewing" not in st.session_state:
    st.session_state.viewing = None

with st.sidebar:
    st.subheader("Session history")
    if st.button("+ New research", use_container_width=True):
        st.session_state.viewing = None
    st.divider()
    if st.session_state.history:
        for i, entry in enumerate(st.session_state.history):
            if st.button(entry["topic"], key=f"hist_{i}", use_container_width=True):
                st.session_state.viewing = i
    else:
        st.caption("No topics researched yet this session.")

st.markdown("""
<div class="navbar">
  <div class="logo-badge">R&sup2;A</div>
  <div>
    <div class="logo-title">Research &amp; Report Agent</div>
    <div class="logo-sub">Live web research, synthesized instantly</div>
    <div class="tags">
      <span class="tag">Live web search</span>
      <span class="tag">AI synthesis</span>
      <span class="tag">Instant PDF</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.viewing is None:
    st.markdown("""
    <div class="steps-row">
      <div class="step-card">
        <div class="step-icon">&#129504;</div>
        <div class="step-label">Plan</div>
        <div class="step-desc">Breaks your topic into sub-questions</div>
      </div>
      <div class="step-card">
        <div class="step-icon">&#128269;</div>
        <div class="step-label">Search</div>
        <div class="step-desc">Reads live web results in real time</div>
      </div>
      <div class="step-card">
        <div class="step-icon">&#128196;</div>
        <div class="step-label">Report</div>
        <div class="step-desc">Writes a clean, structured summary</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.viewing is not None:
    entry = st.session_state.history[st.session_state.viewing]
    st.caption(f"Viewing past report · {entry['topic']}")
    render_report(entry["topic"], entry["report"])
else:
    topic = st.text_input("Research topic", placeholder="e.g. AI in healthcare", label_visibility="collapsed")
    generate = st.button("✨ Generate Report", type="primary")

    if generate:
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            past_titles = [e["topic"] for e in st.session_state.history]
            report = run_agent(topic.strip(), session_history_titles=past_titles)

            if report:
                st.session_state.history.append({"topic": topic.strip(), "report": report})
                st.session_state.viewing = len(st.session_state.history) - 1
                st.rerun()
