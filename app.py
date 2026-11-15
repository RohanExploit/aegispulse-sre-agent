"""AegisPulse — Dark Ops Mission Control UI for Autonomous Multi-Agent SRE."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from agents.orchestrator import AegisPulseCommander

st.set_page_config(
    page_title="AegisPulse | Autonomous SRE Incident Commander",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}
code, pre, .mono {
    font-family: 'JetBrains Mono', monospace !important;
}
.stApp {
    background: radial-gradient(circle at 12% 10%, #101c33 0%, #090e17 55%, #060910 100%);
}
.hero-banner {
    border: 1px solid rgba(0, 245, 212, 0.28);
    background: linear-gradient(135deg, rgba(17, 26, 43, 0.92), rgba(9, 14, 23, 0.96));
    border-radius: 14px;
    padding: 1.35rem 1.6rem;
    margin-bottom: 1.1rem;
    box-shadow: 0 12px 34px rgba(0, 0, 0, 0.38);
}
.hero-title {
    font-size: 1.85rem;
    font-weight: 700;
    color: #F1F5F9;
    margin: 0;
    letter-spacing: -0.02em;
}
.hero-sub {
    color: #94A3B8;
    font-size: 0.96rem;
    margin-top: 0.35rem;
}
.kpi-card {
    background: rgba(17, 26, 43, 0.85);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 12px;
    padding: 1rem 1.1rem;
}
.kpi-label {
    color: #94A3B8;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.kpi-val {
    color: #F8FAFC;
    font-size: 1.55rem;
    font-weight: 700;
    margin-top: 0.2rem;
}
.msg-row {
    border-left: 3px solid #00F5D4;
    background: rgba(15, 23, 42, 0.78);
    padding: 0.75rem 1rem;
    border-radius: 0 10px 10px 0;
    margin-bottom: 0.6rem;
}
.badge {
    display: inline-block;
    padding: 0.2rem 0.58rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}
.badge-crit { background: rgba(255, 77, 109, 0.18); color: #FF4D6D; border: 1px solid #FF4D6D; }
.badge-warn { background: rgba(255, 183, 3, 0.18); color: #FFB703; border: 1px solid #FFB703; }
.badge-ok { background: rgba(0, 245, 212, 0.15); color: #00F5D4; border: 1px solid #00F5D4; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DEFAULT_ENDPOINTS_TEXT = "\n".join(
    [
        "https://api.github.com",
        "https://pypi.org/pypi/streamlit/json",
        "https://httpbin.org/status/200",
    ]
)

with st.sidebar:
    st.markdown("### Control Plane")
    endpoints_raw = st.text_area("Monitored Endpoints (1 per line)", value=DEFAULT_ENDPOINTS_TEXT, height=110)
    target_repo = st.text_input("Correlated GitHub Repo (owner/repo)", value="streamlit/streamlit")
    service_kw = st.text_input("HN Outage Signal Keyword", value="github")

    with st.expander("AI Brain Keys (Optional — 90% Keyless)"):
        gemini_override = st.text_input("Gemini API Key Override", type="password", placeholder="Uses Streamlit Secrets if blank")
        groq_override = st.text_input("Groq API Key Override", type="password", placeholder="Auto-fallback if Gemini errors")

    run_btn = st.button("Execute Autonomous SRE Sweep", type="primary", use_container_width=True)
    st.caption("Built by Prathamesh Linge | BTCOC701 CAS Activity-I")

if "aegis_result" not in st.session_state or run_btn:
    endpoints_list = [line.strip() for line in endpoints_raw.splitlines() if line.strip()]
    with st.spinner("AegisPulse Lead Agent coordinating 4 sub-agents..."):
        commander = AegisPulseCommander()
        st.session_state.aegis_result = commander.run_cycle(
            endpoints=endpoints_list,
            target_repo=target_repo,
            service_keyword=service_kw,
            gemini_key=gemini_override,
            groq_key=groq_override,
        )

res = st.session_state.aegis_result
verdict = res["verdict"]
sev = verdict["severity"]
badge_cls = "badge-crit" if "SEV-1" in sev else ("badge-warn" if "SEV-2" in sev else "badge-ok")

st.markdown(
    f"""
<div class="hero-banner">
  <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.8rem;">
    <div>
      <div class="hero-title">AegisPulse — Autonomous SRE Incident Commander</div>
      <div class="hero-sub">Goal-Based + Utility-Based + Model-Based Multi-Agent System correlating HTTP Probes, DoH DNS, GitHub Commits &amp; HN Signals</div>
    </div>
    <div><span class="badge {badge_cls}">{sev} · RISK {verdict['risk_score']}/100</span></div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
avg_lat = round(sum(p["latency_ms"] for p in res["probes"]) / max(len(res["probes"]), 1), 1)
healthy_cnt = sum(1 for p in res["probes"] if p["ok"])
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Endpoint Health</div><div class="kpi-val">{healthy_cnt}/{len(res["probes"])} UP</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Mean Latency</div><div class="kpi-val">{avg_lat} ms</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Autonomous Runs</div><div class="kpi-val">{res["memory"]["total_autonomous_runs"]}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">10% AI Tier</div><div class="kpi-val" style="font-size:1.05rem;">{res["synthesis"]["provider"]}</div></div>', unsafe_allow_html=True)

st.markdown("")
tab1, tab2, tab3 = st.tabs(["War-Room Telemetry & Topology", "Sub-Agent Message Bus", "PEAS & Persistent Memory"])

with tab1:
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Live Endpoint Latency vs EWMA Baseline")
        probe_df = pd.DataFrame(res["probes"])
        if not probe_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Current Latency (ms)", x=probe_df["host"], y=probe_df["latency_ms"], marker_color="#00F5D4"))
            fig.add_trace(go.Bar(name="Model Baseline (ms)", x=probe_df["host"], y=probe_df["baseline_ms"], marker_color="#334155"))
            fig.update_layout(
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(17,26,43,0.5)",
                font=dict(color="#E2E8F0"),
                height=310,
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Top Suspect GitHub Commits")
        commits_df = pd.DataFrame(res["suspect_commits"])
        if not commits_df.empty:
            st.dataframe(
                commits_df[["sha", "author", "suspicion_score", "message"]],
                use_container_width=True,
                hide_index=True,
            )

    with right:
        st.subheader("Lead Agent Executive Briefing")
        st.info(res["synthesis"]["text"])
        st.caption(f"Model: `{res['synthesis']['model']}` | Latency: `{res['synthesis']['latency_ms']} ms` | {res['synthesis']['notes']}")

        st.subheader("Utility-Ranked Remediation Runbook")
        for step in res["runbook"]["actions"]:
            st.markdown(f"**[{step['priority']}]** {step['action']} — *Utility: {step['utility']}*")

        if res["hn_signals"]:
            st.subheader("Live Hacker News Outage Chatter")
            for sig in res["hn_signals"][:3]:
                st.markdown(f"- [{sig['title']}]({sig['url']}) (`{sig['points']} pts`)")

with tab2:
    st.subheader("Multi-Agent Execution Graph & Inter-Agent Bus")
    topo = go.Figure(
        go.Scatter(
            x=[0, 1, 2, 3, 4],
            y=[0, 0.35, -0.35, 0.35, 0],
            mode="markers+text",
            marker=dict(size=[38, 30, 30, 30, 32], color=["#00F5D4", "#38BDF8", "#818CF8", "#FFB703", "#22C55E"]),
            text=["Lead Commander", "1. TelemetryProbe", "2. CommitCorrelator", "3. HypothesisCritic", "4. RunbookStrategist"],
            textposition="top center",
            textfont=dict(color="#F8FAFC", size=12),
        )
    )
    topo.add_trace(
        go.Scatter(
            x=[0, 1, 2, 3, 4],
            y=[0, 0.35, -0.35, 0.35, 0],
            mode="lines",
            line=dict(color="rgba(0,245,212,0.4)", width=2, dash="dot"),
            hoverinfo="none",
            showlegend=False,
        )
    )
    topo.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,26,43,0.45)",
        xaxis=dict(visible=False, range=[-0.6, 4.6]),
        yaxis=dict(visible=False, range=[-0.8, 0.9]),
        height=240,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
    )
    st.plotly_chart(topo, use_container_width=True)

    for m in res["messages"]:
        st.markdown(
            f"""
<div class="msg-row">
  <div class="mono" style="font-size:0.78rem; color:#00F5D4;">[{m['phase']}] {m['sender']} → {m['recipient']} (conf={m['confidence']})</div>
  <div style="margin-top:0.25rem; color:#E2E8F0;">{m['content']}</div>
</div>
""",
            unsafe_allow_html=True,
        )

with tab3:
    st.subheader("PEAS Agent Architecture Matrix")
    peas_rows = [
        {"Component": "P — Performance Measure", "Definition": "MTTR reduction, zero false-positive escalations, latency drift detection accuracy, safe human-gated rollbacks."},
        {"Component": "E — Environment", "Definition": "Production HTTP APIs, Google DoH DNS resolvers, GitHub repositories, Hacker News stream, Streamlit & GitHub Actions."},
        {"Component": "A — Actuators", "Definition": "Multi-agent war-room UI, prioritized P0/P1/P2 runbook emitter, persistent EWMA baseline updater."},
        {"Component": "S — Sensors", "Definition": "Live HTTP probe timings, DNS A-records, GitHub commit feed, HN Algolia JSON API, state/incident_memory.json."},
    ]
    st.table(pd.DataFrame(peas_rows))

    st.subheader("Persistent Incident Memory (`state/incident_memory.json`)")
    hist = res["memory"].get("incident_history", [])
    if hist:
        hist_df = pd.DataFrame(hist)
        fig_hist = px.line(hist_df, x="timestamp_utc", y="risk_score", markers=True, title="Historical Risk Trajectory")
        fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(17,26,43,0.5)", font=dict(color="#E2E8F0"), height=250)
        st.plotly_chart(fig_hist, use_container_width=True)
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
