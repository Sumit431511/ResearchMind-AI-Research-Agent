import streamlit as st
import time
from orchestrator import run_research_pipeline

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    color: #f0ebe0;
    margin: 0 0 1rem;
}
.hero h1 span {
    color: #ff8c32;
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: #a09890;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.65;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent);
    margin: 2rem 0;
}

/* ── Input card ── */
.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,140,50,0.15);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(8px);
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,140,50,0.25) !important;
    border-radius: 10px !important;
    color: #f0ebe0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 0 3px rgba(255,140,50,0.12) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #ff8c32 !important;
    font-weight: 500 !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2.2rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
    box-shadow: 0 4px 20px rgba(255,140,50,0.3) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(255,140,50,0.4) !important;
    opacity: 0.95 !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Pipeline step cards ── */
.step-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.step-card.active {
    border-color: rgba(255,140,50,0.4);
    background: rgba(255,140,50,0.04);
}
.step-card.done {
    border-color: rgba(80,200,120,0.3);
    background: rgba(80,200,120,0.03);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 14px 0 0 14px;
    background: rgba(255,255,255,0.05);
    transition: background 0.3s;
}
.step-card.active::before { background: #ff8c32; }
.step-card.done::before   { background: #50c878; }

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.3rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #ff8c32;
    opacity: 0.7;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #f0ebe0;
}
.step-status {
    margin-left: auto;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
}
.status-waiting  { color: #555; }
.status-running  { color: #ff8c32; }
.status-done     { color: #50c878; }

/* ── Result panels ── */
.result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(255,140,50,0.15);
}
.result-content {
    font-size: 0.92rem;
    line-height: 1.8;
    color: #cdc8bf;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

/* ── Report & feedback panels ── */
.report-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,140,50,0.2);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
}
.feedback-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(80,200,120,0.2);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
}
.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
}
.panel-label.orange {
    color: #ff8c32;
    border-bottom: 1px solid rgba(255,140,50,0.15);
}
.panel-label.green {
    color: #50c878;
    border-bottom: 1px solid rgba(80,200,120,0.15);
}

/* ── Progress text ── */
.stSpinner > div { color: #ff8c32 !important; }

/* ── Expander ── */
details summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #a09890 !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #f0ebe0;
    margin: 2rem 0 1rem;
}

/* ── Toast-style notice ── */
.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #605850;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.82rem;color:#706860;margin-top:0.3rem;'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = {}
if "running" not in st.session_state:
    st.session_state.running = False
if "done" not in st.session_state:
    st.session_state.done = False
if "error" not in st.session_state:
    st.session_state.error = None
if "status_log" not in st.session_state:
    st.session_state.status_log = []


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    #st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <span style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#605850;letter-spacing:0.1em;">TRY →</span>
    """, unsafe_allow_html=True)
    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]
    for ex in examples:
        st.markdown(f"""
        <span style="
            background:rgba(255,255,255,0.04);
            border:1px solid rgba(255,255,255,0.08);
            border-radius:6px;
            padding:0.25rem 0.7rem;
            font-size:0.75rem;
            color:#a09890;
            font-family:'DM Sans',sans-serif;
            cursor:default;
        ">{ex}</span>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    r = st.session_state.results

    def s(step):
        if not r:
            return "waiting"
        completed_map = {
            "search": bool(r.get("search_results")),
            "reader": bool(r.get("scraped_sources")),
            "writer": bool(r.get("report")),
            "critic": bool(r.get("critique")),
        }
        if completed_map.get(step):
            return "done"
        if st.session_state.running:
            step_order = ["search", "reader", "writer", "critic"]
            for item in step_order:
                if not completed_map[item]:
                    return "running" if item == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent",  s("search"), "Gathers recent web information")
    step_card("02", "Reader Agent",  s("reader"), "Scrapes & extracts deep content")
    step_card("03", "Writer Chain",  s("writer"), "Drafts the full research report")
    step_card("04", "Critic Chain",  s("critic"), "Reviews & scores the report")


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.session_state.error = None
        st.session_state.status_log = []

        try:
            with st.status("Running research pipeline...", expanded=True) as status:
                def on_progress(step: str, message: str) -> None:
                    st.session_state.status_log.append((step, message))
                    status.write(f"{step.title()}: {message}")

                pipeline_state = run_research_pipeline(topic.strip(), progress_callback=on_progress)
                st.session_state.results = pipeline_state.model_dump()
                status.update(label="Pipeline completed", state="complete", expanded=False)
            st.session_state.done = True
        except Exception as exc:
            st.session_state.error = str(exc)
            st.session_state.done = False
        finally:
            st.session_state.running = False
        st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if st.session_state.error:
    st.error(st.session_state.error)

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    metrics = st.columns(3)
    metrics[0].metric("Sources Found", len(r.get("search_results", [])))
    metrics[1].metric("Pages Scraped", len(r.get("scraped_sources", [])))
    metrics[2].metric("Revision Rounds", r.get("revision_count", 0))

    if r.get("search_results"):
        with st.expander("🔍 Search Results", expanded=False):
            for item in r["search_results"]:
                st.markdown(
                    f"**{item['title']}**\n\n"
                    f"{item['snippet']}\n\n"
                    f"[Open source]({item['url']})"
                )
                st.markdown("---")

    if r.get("scraped_sources"):
        with st.expander("📄 Scraped Source Previews", expanded=False):
            for item in r["scraped_sources"]:
                title = item.get("title") or "Untitled page"
                if item.get("success"):
                    st.markdown(f"**{title}**")
                    st.caption(item["url"])
                    st.write(item.get("content", "")[:700] + "...")
                else:
                    st.markdown(f"**{title}**")
                    st.caption(item["url"])
                    st.error(item.get("error", "Scrape failed."))
                st.markdown("---")

    if r.get("report"):
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["report"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["report"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if st.session_state.status_log:
        with st.expander("Pipeline Log", expanded=False):
            for step, message in st.session_state.status_log:
                st.write(f"{step.title()}: {message}")

    if r.get("critique"):
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label green">🧐 Critic Feedback</div>
        """, unsafe_allow_html=True)
        critique = r["critique"]
        if critique.get("score") is not None:
            st.markdown(f"**Score:** {critique['score']}/10")
        st.markdown(critique.get("raw", "No critique generated."))
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)
