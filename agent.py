"""
Google ADK Agent Setup for EE Circuit Analysis
Connects Gemini with custom MCP tools for deterministic calculations.
"""
import os
from dotenv import load_dotenv
from google.adk import Agent

try:
    from mcp_server import (
        calculate_rc_cutoff,
        calculate_rlc_resonance,
        analyze_bode_transfer_function,
        solve_symbolic_transfer_function,
        match_e24_component,
        calculate_resistive_load,
        analyze_feedback_stability,
        generate_rc_design_report,
        generate_load_design_report,
        generate_schematic_review_report,
    )
except ImportError:
    from .mcp_server import (
        calculate_rc_cutoff,
        calculate_rlc_resonance,
        analyze_bode_transfer_function,
        solve_symbolic_transfer_function,
        match_e24_component,
        calculate_resistive_load,
        analyze_feedback_stability,
        generate_rc_design_report,
        generate_load_design_report,
        generate_schematic_review_report,
    )

load_dotenv()

# Ensure API Key is available
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key == "your_actual_gemini_api_key_here":
    print("\n[WARNING] GOOGLE_API_KEY is not set in your .env file!")

# Instantiate the Google ADK Agent
ee_agent = Agent(
    name="CircuitAnalysisAgent",
    model="gemini-3.6-flash",
    instruction=(
        "You are an expert Electrical Engineering assistant. Analyze analog circuits, "
        "calculate filter cutoffs, analyze transfer functions, compute RLC resonance, "
        "select standard E24 series components, calculate DC resistive loads, evaluate "
        "open-loop feedback stability margins, and generate automated design reports. "
        "CRITICAL: Always use your provided tools to execute numerical and symbolic "
        "calculations. Never guess math values or estimate frequencies manually. "
        "Present every response clearly in Markdown for a chat interface. Begin with a "
        "one-sentence conclusion, then use short descriptive headings. Put key numerical "
        "results in a compact Markdown table with units. Use bullets only for assumptions, "
        "alternatives, or next steps. Keep paragraphs short and avoid repeating information. "
        "Prefer inline math and plain-text units (for example, `1.54 kHz`) over display "
        "equations; include a detailed derivation only when the user requests it. "
        "When recommending components, show the target, selected E24 values, actual result, "
        "and percentage error together in a table. End by offering one relevant follow-up."
    ),
    tools=[
        calculate_rc_cutoff,
        calculate_rlc_resonance,
        analyze_bode_transfer_function,
        solve_symbolic_transfer_function,
        match_e24_component,
        calculate_resistive_load,
        analyze_feedback_stability,
        generate_rc_design_report,
        generate_load_design_report,
        generate_schematic_review_report,
    ]
)

# Export root_agent for adk web UI discovery
root_agent = ee_agent
