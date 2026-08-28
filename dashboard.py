"""Streamlit UI for the Modus Enterprise AI Intelligence Engine.

Run with:
    streamlit run dashboard.py

All data and actions come from the FastAPI backend over HTTP. The dashboard
does not contain research, AI, or database business logic.
"""

from __future__ import annotations

import os
import time
from typing import Any

import requests
import streamlit as st


API_BASE = os.getenv("MODUS_API_URL", "http://127.0.0.1:8000").rstrip("/")
HTTP_TIMEOUT = float(os.getenv("DASHBOARD_HTTP_TIMEOUT", "12"))
POLL_SECONDS = max(2.0, float(os.getenv("DASHBOARD_POLL_SECONDS", "3")))

st.set_page_config(
    page_title="Modus Enterprise Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .hero { padding: 1.25rem 1.5rem; border-radius: 0.8rem; background: linear-gradient(110deg, #102a43, #1f4e79); color: white; margin-bottom: 1.25rem; }
    .hero h1 { margin: 0; font-size: 2rem; }
    .hero p { margin: .35rem 0 0; color: #d9ecff; }
    .status-chip { font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_request(method: str, path: str, **kwargs: Any) -> Any:
    response = requests.request(method, f"{API_BASE}{path}", timeout=HTTP_TIMEOUT, **kwargs)
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(f"Backend returned {response.status_code}: {detail}")
    return response.json()


def show_record_detail(record: dict[str, Any], title: str = "Process Intelligence") -> None:
    st.subheader(title)
    status_label = record.get("display_status", record.get("status", "Unknown"))
    st.caption(f"Record ID {record.get('id')} · status: {status_label} · stage: {record.get('stage') or '—'}")
    fields = [
        ("Business Purpose", "business_purpose"),
        ("Key Activities", "key_activities"),
        ("Current Challenges", "current_challenges"),
        ("AI Opportunity", "ai_opportunity"),
        ("Automation Potential", "automation_potential"),
        ("Human Involvement", "human_involvement"),
        ("Technologies", "technologies"),
        ("Business Benefit", "business_benefit"),
        ("Risks", "risks"),
        ("Evidence", "evidence"),
    ]
    left, right = st.columns(2)
    for index, (label, key) in enumerate(fields):
        column = left if index % 2 == 0 else right
        with column:
            value = record.get(key)
            st.markdown(f"**{label}**")
            st.write(value if value else "Not available until analysis completes.")
    st.markdown("**Evidence URL**")
    evidence_url = record.get("evidence_url")
    if evidence_url:
        st.markdown(f"[Open verifiable Wikipedia source]({evidence_url})")
    else:
        st.write("Not available until analysis completes.")


def render_live_analysis() -> None:
    st.header("Live Process Analysis")
    st.write("Submit any new enterprise process. The API accepts it immediately, then the worker researches and analyses it in the background.")
    with st.form("surprise_record_form"):
        process_name = st.text_input(
            "Enter a New Enterprise Process",
            value="Drone-Assisted Core Audit",
            max_chars=200,
        )
        submitted = st.form_submit_button("Submit for background analysis", type="primary")
    if submitted:
        if not process_name.strip():
            st.error("Enter a process name.")
        else:
            try:
                accepted = api_request("POST", "/processes", json={"name": process_name.strip()})
                process = accepted["process"]
                st.session_state["watch_process_id"] = process["id"]
                st.success(f"Accepted immediately with status {process['status']} (record ID {process['id']}).")
            except Exception as exc:
                st.error(str(exc))

    watch_id = st.session_state.get("watch_process_id")
    if watch_id:
        try:
            record = api_request("GET", f"/processes/{watch_id}")
            status_label = record.get("display_status", record.get("status"))
            if status_label == "Processing":
                st.info(f"Live worker status: **Processing** — {record.get('stage') or 'queued'}")
                st.progress(0.5, text="Real backend job is active; progress is based on worker state.")
                time.sleep(POLL_SECONDS)
                st.rerun()
            elif record.get("status") == "Pending":
                st.info("Live worker status: **Pending** — waiting in the async queue")
                time.sleep(POLL_SECONDS)
                st.rerun()
            elif record.get("status") == "Analyzed":
                st.success("Live worker status: **Analyzed**")
                show_record_detail(record, "Completed Surprise Record")
            else:
                st.error("Live worker status: **Failed**. Retry from the process detail section or API.")
                if st.button("Retry surprise record", key="retry_surprise"):
                    try:
                        api_request("POST", f"/processes/{watch_id}/retry")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
        except Exception as exc:
            st.error(f"Could not poll surprise record: {exc}")


def render_advisory_console() -> None:
    st.header("Executive Advisory Console")
    st.caption("Each answer is grounded in the local BM25 retrieval of persisted process intelligence before Gemini synthesis.")
    with st.form("advisory_form"):
        question = st.text_input(
            "Executive question",
            placeholder="Which processes should be transformed first?",
        )
        ask = st.form_submit_button("Ask grounded advisor", type="primary")
    if ask:
        if not question.strip():
            st.warning("Enter an executive question.")
            return
        try:
            result = api_request("POST", "/chat", json={"question": question.strip(), "limit": 5})
            st.markdown("#### Answer")
            st.write(result["answer"])
            st.markdown("#### Retrieved persisted records")
            st.dataframe(result.get("retrieved_processes", []), use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(str(exc))


def render_matrix() -> None:
    st.header("Process Intelligence Matrix")
    filter_col, search_col, refresh_col = st.columns([1, 2, 1])
    with filter_col:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "Analyzed", "Failed"])
    with search_col:
        name_query = st.text_input("Search by process name", placeholder="e.g. invoice, risk, routing")
    with refresh_col:
        st.write("")
        st.write("")
        refresh = st.button("Refresh table")
    if refresh:
        st.rerun()

    params: dict[str, Any] = {"limit": 1000, "offset": 0}
    if status_filter != "All":
        params["status"] = status_filter
    if name_query.strip():
        params["name"] = name_query.strip()
    try:
        payload = api_request("GET", "/processes", params=params)
        items = payload.get("items", [])
    except Exception as exc:
        st.error(str(exc))
        return

    display_rows = [
        {
            "ID": item["id"],
            "Process name": item["name"],
            "Status": item.get("display_status", item["status"]),
            "Automation potential": item.get("automation_potential") or "—",
            "AI opportunity": item.get("ai_opportunity") or "—",
            "Evidence": "Yes" if item.get("evidence_url") else "Pending",
        }
        for item in items
    ]
    st.caption(f"Showing {len(display_rows)} persisted records")
    st.dataframe(display_rows, use_container_width=True, hide_index=True)

    if not items:
        st.info("No records match the current filters.")
        return
    options = {f"{item['id']} · {item['name']}": item["id"] for item in items}
    selected_label = st.selectbox("Select a process to inspect all intelligence dimensions", list(options))
    selected_id = options[selected_label]
    try:
        detail = api_request("GET", f"/processes/{selected_id}")
        show_record_detail(detail)
        if detail.get("status") == "Failed":
            if st.button("Retry selected process", key=f"retry_{selected_id}"):
                api_request("POST", f"/processes/{selected_id}/retry")
                st.success("Process re-queued.")
                st.rerun()
    except Exception as exc:
        st.error(str(exc))


def main() -> None:
    st.markdown(
        "<div class='hero'><h1>Modus Enterprise AI Intelligence Engine</h1><p>100-process research, analysis, retrieval, and executive decision support</p></div>",
        unsafe_allow_html=True,
    )
    with st.sidebar:
        st.title("Control Plane")
        st.caption(f"Backend: {API_BASE}")
        try:
            health = api_request("GET", "/health")
            st.success("FastAPI connected")
            st.caption(
                f"Workers: {health.get('workers', 0)} (active {health.get('active_workers', 0)}) · "
                f"Queue depth: {health.get('queue_depth', 0)} · "
                f"AI concurrency: {health.get('configured_concurrency', 0)}"
            )
            if not health.get("gemini_configured"):
                st.warning("GEMINI_API_KEY is not configured")
        except Exception as exc:
            st.error(f"Backend unavailable: {exc}")
            st.stop()
        st.divider()
        st.markdown("**Seed control**")
        st.caption("Seed records are intentionally Pending until queued; no static AI results are created.")
        seed_batch = st.number_input("Queue pending records", min_value=1, max_value=1000, value=10, step=10)
        if st.button("Queue pending work"):
            try:
                result = api_request("POST", "/processes/queue-pending", params={"limit": int(seed_batch)})
                st.success(f"Queued {result['accepted']} records.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    try:
        stats = api_request("GET", "/stats")
    except Exception as exc:
        st.error(str(exc))
        return

    st.header("Executive Overview")
    metric_cols = st.columns(5)
    metric_cols[0].metric("Total processes", stats.get("total", 0))
    metric_cols[1].metric("Analyzed", stats.get("analyzed", 0))
    metric_cols[2].metric("Pending", stats.get("pending", 0))
    metric_cols[3].metric("Processing", stats.get("processing", 0))
    metric_cols[4].metric("Failed", stats.get("failed", 0))
    total = max(int(stats.get("total", 0)), 1)
    st.progress(min(int(stats.get("analyzed", 0)) / total, 1.0), text=f"Analyzed: {stats.get('analyzed', 0)} / {stats.get('total', 0)}")

    render_live_analysis()
    st.divider()
    render_matrix()
    st.divider()
    render_advisory_console()


if __name__ == "__main__":
    main()
