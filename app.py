"""Streamlit interfaces for the EE Circuit Analysis project."""
import asyncio
import uuid

import streamlit as st
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import ee_agent
from mcp_server import (
    analyze_bode_transfer_function,
    calculate_rc_cutoff,
    calculate_rlc_resonance,
    match_e24_component,
    solve_symbolic_transfer_function,
)


SAMPLE_PROMPTS = [
    "Calculate the cutoff frequency and time constant for a low-pass RC filter with R = 4.7 kOhm and C = 100 nF.",
    "Find the resonance frequency, Q factor, and bandwidth for a series RLC circuit with R = 10 Ohm, L = 1 mH, and C = 1 uF.",
    "Match a target resistor value of 4.73 kOhm to the nearest E24 value and show the percentage error.",
]


def run_agent(prompt: str) -> str:
    """Run one AI chat turn while retaining this browser session's conversation."""
    async def _run() -> str:
        session_service = st.session_state.session_service
        if not st.session_state.session_created:
            await session_service.create_session(
                app_name="ee_app", user_id="streamlit_user", session_id=st.session_state.session_id
            )
            st.session_state.session_created = True

        runner = Runner(app_name="ee_app", agent=ee_agent, session_service=session_service)
        message = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        response_parts = []
        async for event in runner.run_async(
            user_id="streamlit_user", session_id=st.session_state.session_id, new_message=message
        ):
            if event.content:
                response_parts.extend(
                    part.text for part in event.content.parts if getattr(part, "text", None)
                )
        return "".join(response_parts) or "The calculation completed, but no text response was returned."

    return asyncio.run(_run())


def parse_coefficients(raw: str) -> list[float]:
    """Parse comma-separated transfer-function coefficients."""
    return [float(value.strip()) for value in raw.split(",") if value.strip()]


def render_rc_calculator() -> None:
    st.subheader("RC filter analysis")
    left, right = st.columns(2)
    with left:
        resistance = st.number_input("Resistance (Ω)", min_value=0.001, value=4700.0, key="rc_r")
    with right:
        capacitance = st.number_input("Capacitance (F)", min_value=1e-15, value=100e-9, format="%.9g", key="rc_c")
    result = calculate_rc_cutoff(resistance, capacitance)
    a, b, c = st.columns(3)
    a.metric("Cutoff frequency", f"{result['cutoff_frequency_hz']:,.2f} Hz")
    b.metric("Time constant", f"{result['time_constant_sec'] * 1e6:,.2f} µs")
    c.metric("Transfer function", "Low-pass")
    st.caption("H(s) = 1 / (RCs + 1)")


def render_rlc_calculator() -> None:
    st.subheader("Series RLC resonance")
    col1, col2, col3 = st.columns(3)
    with col1:
        resistance = st.number_input("Resistance (Ω)", min_value=0.001, value=10.0, key="rlc_r")
    with col2:
        inductance = st.number_input("Inductance (H)", min_value=1e-15, value=1e-3, format="%.9g", key="rlc_l")
    with col3:
        capacitance = st.number_input("Capacitance (F)", min_value=1e-15, value=1e-6, format="%.9g", key="rlc_c")
    result = calculate_rlc_resonance(resistance, inductance, capacitance)
    a, b, c = st.columns(3)
    a.metric("Resonant frequency", f"{result['resonant_frequency_hz']:,.2f} Hz")
    b.metric("Q factor", result["q_factor"])
    c.metric("3 dB bandwidth", f"{result['bandwidth_hz']:,.2f} Hz")


def render_e24_calculator() -> None:
    st.subheader("E24 component matcher")
    left, right = st.columns(2)
    with left:
        value = st.number_input("Target value", min_value=1e-15, value=4730.0, format="%.9g", key="e24_value")
    with right:
        component_type = st.selectbox("Component type", ["resistor", "capacitor"], key="e24_type")
    result = match_e24_component(value, component_type)
    a, b, c = st.columns(3)
    a.metric("Target", f"{result['target_value']:,.6g}")
    b.metric("Nearest E24 value", f"{result['standard_e24_value']:,.6g}")
    c.metric("Absolute error", f"{result['error_percentage']:.2f}%")


def render_transfer_calculators() -> None:
    st.subheader("Transfer-function tools")
    bode_tab, symbolic_tab = st.tabs(["Bode summary", "Symbolic RC transfer function"])
    with bode_tab:
        numerator = st.text_input("Numerator coefficients", "1000")
        denominator = st.text_input("Denominator coefficients", "1, 1000")
        if st.button("Analyze Bode response", use_container_width=True):
            try:
                result = analyze_bode_transfer_function(parse_coefficients(numerator), parse_coefficients(denominator))
                if "error" in result:
                    st.error(result["error"])
                else:
                    a, b, c = st.columns(3)
                    a.metric("Peak gain", f"{result['max_gain_db']:.2f} dB")
                    b.metric("Cutoff", f"{result['cutoff_freq_hz']:.2f} Hz")
                    c.metric("Angular cutoff", f"{result['cutoff_freq_rad_s']:.2f} rad/s")
            except ValueError:
                st.error("Enter comma-separated numeric coefficients, such as `1, 1000`.")
    with symbolic_tab:
        circuit_type = st.selectbox("Filter type", ["lowpass", "highpass"])
        r_value = st.number_input("R (Ω)", min_value=0.001, value=1000.0, key="symbolic_r")
        c_value = st.number_input("C (F)", min_value=1e-15, value=1e-6, format="%.9g", key="symbolic_c")
        if st.button("Derive transfer function", use_container_width=True):
            result = solve_symbolic_transfer_function(circuit_type, r_value, c_value)
            st.code(result["symbolic_expression"], language="text")
            st.caption(f"With your component values: {result['numeric_expression']}")


st.set_page_config(page_title="EE Circuit Assistant", page_icon="⚡", layout="wide")
st.markdown(
    """<style>
    .stApp { background: #0b1120; }
    .hero { padding: 0.8rem 0 1.2rem; }
    .hero h1 { margin-bottom: 0.15rem; }
    .hero p { color: #a8b5cc; font-size: 1.05rem; }
    [data-testid="stSidebar"] { background: #101a2d; }
    </style>""",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.session_service = InMemorySessionService()
    st.session_state.session_created = False

with st.sidebar:
    st.header("EE Circuit Assistant")
    st.success("Offline calculators run locally at $0 cost.")
    st.caption("AI chat is optional and uses Gemini API quota.")
    if st.button("Clear AI conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.session_service = InMemorySessionService()
        st.session_state.session_created = False
        st.rerun()

st.markdown(
    """<div class="hero"><h1>⚡ EE Circuit Assistant</h1>
    <p>Run deterministic circuit calculations locally, or use Gemini chat when API quota is available.</p></div>""",
    unsafe_allow_html=True,
)

chat_tab, calculator_tab = st.tabs(["AI chat", "Offline calculators ($0)"])

with chat_tab:
    st.info("The chat uses Gemini and may be rate-limited. The Offline calculators tab never calls an AI API.")
    with st.expander("Example prompts"):
        for sample in SAMPLE_PROMPTS:
            st.code(sample, language="text")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Ask an electrical-engineering question…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Running engineering tools…"):
                try:
                    response = run_agent(prompt)
                except Exception as exc:
                    if "RESOURCE_EXHAUSTED" in str(exc) or "429" in str(exc):
                        response = (
                            "### Gemini quota reached\n\n"
                            "The AI chat is unavailable for this API project right now. Use the "
                            "**Offline calculators ($0)** tab for RC, RLC, E24, Bode, and symbolic "
                            "transfer-function calculations without any API calls."
                        )
                    else:
                        response = f"**Unable to run the agent:** `{exc}`"
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

with calculator_tab:
    st.success("These calculators execute locally with NumPy, SciPy, and SymPy. No Gemini key or internet connection is required.")
    rc_tab, rlc_tab, e24_tab, transfer_tab = st.tabs(["RC filter", "RLC resonance", "E24 matcher", "Transfer functions"])
    with rc_tab:
        render_rc_calculator()
    with rlc_tab:
        render_rlc_calculator()
    with e24_tab:
        render_e24_calculator()
    with transfer_tab:
        render_transfer_calculators()
