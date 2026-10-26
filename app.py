import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from scanner import (
    DETECTOR_LABELS,
    GeminiAnalysisFailure,
    RiskAssessment,
    analyze_with_gemini,
    scan_prompt,
)


load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)


st.set_page_config(
    page_title="ContextGuard - AI Prompt Security",
    page_icon="🛡️",
    layout="wide",
)


def clear_scan_results() -> None:
    had_results = st.session_state.get("scan_result") is not None
    st.session_state["scan_result"] = None
    st.session_state["gemini_analysis"] = None
    st.session_state["gemini_error"] = None
    if had_results:
        st.session_state["rescan_notice"] = True


def hide_gemini_analysis_when_disabled() -> None:
    if not st.session_state["gemini_enabled"]:
        st.session_state["gemini_analysis"] = None
        st.session_state["gemini_error"] = None


def reset_prompt_and_results() -> None:
    st.session_state["prompt_input"] = ""
    st.session_state["scan_result"] = None
    st.session_state["gemini_analysis"] = None
    st.session_state["gemini_error"] = None
    st.session_state["rescan_notice"] = False


st.session_state.setdefault("prompt_input", "")
st.session_state.setdefault("scan_result", None)
st.session_state.setdefault("gemini_analysis", None)
st.session_state.setdefault("gemini_error", None)
st.session_state.setdefault("gemini_enabled", False)
st.session_state.setdefault("rescan_notice", False)
for detector_id in DETECTOR_LABELS:
    st.session_state.setdefault(f"detector_{detector_id}", True)

st.title("🛡️ ContextGuard - AI Prompt Security")
st.caption("Local-First Privacy Guard for Developers")

gemini_enabled = st.toggle(
    "Enable Gemini Deep Context Analysis",
    key="gemini_enabled",
    on_change=hide_gemini_analysis_when_disabled,
)
st.warning(
    "⚠️ Local regex redaction is pattern-based and best-effort. When enabled, "
    "ContextGuard sends only the redacted prompt to Google Gemini; unsupported "
    "secrets or other sensitive details may remain. Review the redacted prompt "
    "before enabling Deep Scan."
)
if gemini_enabled:
    st.warning("🛡️ Mode: Hybrid (Local Redaction + Gemini Context Analysis)")
else:
    st.info("🔒 Mode: 100% Local Regex Scan (Zero External Network Calls)")

with st.sidebar:
    st.text_input(
        "Gemini API key",
        type="password",
        key="gemini_api_key_input",
        help="Optional. If blank, ContextGuard uses GEMINI_API_KEY from the project .env file.",
    )
    st.subheader("Active Regex Detectors")
    for detector_id, label in DETECTOR_LABELS.items():
        st.checkbox(label, key=f"detector_{detector_id}", on_change=clear_scan_results)

    st.divider()
    st.button(
        "Reset",
        use_container_width=True,
        on_click=reset_prompt_and_results,
    )

prompt_input = st.text_area(
    "Paste your AI Prompt or Code Snippet here",
    height=220,
    placeholder="Paste text to scan locally. Use synthetic examples when testing.",
    key="prompt_input",
    on_change=clear_scan_results,
)

if st.session_state["rescan_notice"]:
    st.info("✏️ Input or detector settings modified. Click '🛡️ Scan & Mask Prompt' again to update results.")

if st.button("🛡️ Scan & Mask Prompt", type="primary", use_container_width=True):
    if not prompt_input.strip():
        st.warning("⚠️ Please enter or paste a prompt or code snippet before running the scan.")
    else:
        enabled_detectors = {
            detector_id
            for detector_id in DETECTOR_LABELS
            if st.session_state[f"detector_{detector_id}"]
        }
        st.session_state["scan_result"] = scan_prompt(
            prompt_input,
            enabled_detectors=enabled_detectors,
        )
        st.session_state["gemini_analysis"] = None
        st.session_state["gemini_error"] = None
        st.session_state["rescan_notice"] = False
        if gemini_enabled:
            api_key = (
                st.session_state["gemini_api_key_input"].strip()
                or os.getenv("GEMINI_API_KEY", "").strip()
            )
            with st.spinner("Analyzing the locally redacted prompt with Gemini..."):
                analysis_result = analyze_with_gemini(
                    st.session_state["scan_result"].redacted_text,
                    api_key,
                )
            if isinstance(analysis_result, GeminiAnalysisFailure):
                st.session_state["gemini_error"] = analysis_result
            else:
                st.session_state["gemini_analysis"] = analysis_result

scan_result = st.session_state["scan_result"]
if scan_result is not None:
    metric_columns = st.columns(3)
    metric_columns[0].metric("Total Characters", scan_result.raw_character_count)
    metric_columns[1].metric("Secrets Masked Count", scan_result.total_redactions)
    metric_columns[2].metric(
        "Privacy Shield Status",
        "Hybrid" if gemini_enabled else "100% Local",
    )

    st.divider()
    breakdown_column, prompt_column = st.columns(2)

    with breakdown_column:
        st.subheader("🔴 Redactions Breakdown")
        if scan_result.counts_by_category:
            for detector_id, count in scan_result.counts_by_category.items():
                st.error(f"{DETECTOR_LABELS[detector_id]}: {count}")
        else:
            st.success("No supported patterns found.")
            st.caption("This does not guarantee the prompt is safe.")

    with prompt_column:
        st.subheader("🟢 Cleaned Prompt")
        st.code(scan_result.redacted_text, language="text")
        st.caption("Regex redaction is pattern-based and best-effort. Review the cleaned text before copying.")

    if gemini_enabled:
        gemini_error = st.session_state["gemini_error"]
        if isinstance(gemini_error, GeminiAnalysisFailure):
            if gemini_error.kind == "missing_key":
                st.warning(
                    "⚠️ Gemini Deep Scan is enabled, but no Google Gemini API Key "
                    "was found in your .env or sidebar. Please enter your API key "
                    "to enable context analysis, or copy your locally redacted "
                    "prompt above."
                )
            else:
                st.warning(
                    "⚠️ Gemini contextual analysis could not be completed "
                    "(Network/API Error). Your locally redacted prompt remains "
                    "available to review and copy."
                )
        else:
            analysis = st.session_state["gemini_analysis"]
            if isinstance(analysis, RiskAssessment):
                st.divider()
                st.subheader("Gemini Deep Context Analysis")
                risk_colors = {
                    "LOW": "#10B981",
                    "MEDIUM": "#F59E0B",
                    "HIGH": "#EF4444",
                }
                risk_color = risk_colors[analysis.risk_level]
                st.html(
                    f"""
                    <div>
                      <label for="gemini-risk-score">Risk score: {analysis.risk_score} out of 100</label>
                      <progress id="gemini-risk-score" value="{analysis.risk_score}" max="100"
                        aria-label="Gemini risk score: {analysis.risk_score} out of 100"
                        style="width: 100%; height: 1.25rem; accent-color: {risk_color};">
                        {analysis.risk_score}%
                      </progress>
                      <span role="status" aria-label="Risk level: {analysis.risk_level}"
                        style="display: inline-block; color: {risk_color}; border: 1px solid {risk_color};
                        border-radius: 0.35rem; padding: 0.15rem 0.5rem; margin-top: 0.5rem;">
                        Risk level: {analysis.risk_level}
                      </span>
                    </div>
                    """
                )
                st.markdown("**Contextual findings**")
                for finding in analysis.analysis_summary:
                    st.text(f"• {finding}")
