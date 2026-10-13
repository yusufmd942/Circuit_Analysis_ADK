"""
Offline Test Script for MCP Tools
Runs math checks locally without requiring a Gemini API key.
"""
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

def run_tests():
    print("=" * 60)
    print("  Offline Verification of EE MCP Math Tools")
    print("=" * 60 + "\n")

    # 1. Test RC Cutoff
    rc = calculate_rc_cutoff(1000.0, 1e-7)
    print(f"[TEST 1] RC Cutoff (1k Ohm, 100nF):\n  -> {rc}\n")
    assert rc["cutoff_frequency_hz"] == 1591.55, f"Unexpected cutoff: {rc}"

    # 2. Test RLC Resonance
    rlc = calculate_rlc_resonance(10.0, 1e-3, 1e-6)
    print(f"[TEST 2] RLC Resonance (10 Ohm, 1mH, 1uF):\n  -> {rlc}\n")
    assert rlc["resonant_frequency_hz"] == 5032.92

    # 3. Test Bode Analysis
    bode = analyze_bode_transfer_function([1000.0], [1.0, 1000.0])
    print(f"[TEST 3] Bode Transfer Function num=[1000], den=[1, 1000]:\n  -> {bode}\n")

    # 4. Test Symbolic Transfer Function
    sym = solve_symbolic_transfer_function("lowpass", 1000.0, 1e-6)
    print(f"[TEST 4] SymPy Symbolic Lowpass (1k Ohm, 1uF):\n  -> {sym}\n")

    # 5. Test E24 Matching
    e24 = match_e24_component(4730.0, "resistor")
    print(f"[TEST 5] E24 Standard Resistor Matching (4730 Ohm target):\n  -> {e24}\n")
    assert e24["standard_e24_value"] == 4700.0

    # 6. Test DC Load Calculation
    load = calculate_resistive_load(12.0, 100.0, 10.0)
    print(f"[TEST 6] DC Load (12V, 100 Ohm load, 10 Ohm source):\n  -> {load}\n")
    assert load["load_current_a"] == 0.109091
    assert load["load_power_w"] == 1.190083

    # 7. Test Feedback Stability Metric
    stability = analyze_feedback_stability([10000.0], [1.0, 1000.0])
    print(f"[TEST 7] Feedback Stability Review:\n  -> {stability}\n")
    assert stability["phase_margin_deg"] is not None

    # 8. Test Automated Reports
    rc_report = generate_rc_design_report(1000.0, 1e-7)
    load_report = generate_load_design_report(12.0, 100.0, 10.0)
    print(f"[TEST 8] Automated Design Reports:\n  -> {rc_report['report_type']}, {load_report['report_type']}\n")
    assert "RC Low-Pass Filter Design Report" in rc_report["report_markdown"]
    assert "DC Resistive Load Design Report" in load_report["report_markdown"]

    # 9. Test Combined Schematic Review Report
    review = generate_schematic_review_report(12.0, 100.0, 10.0, [10000.0], [1.0, 1000.0])
    print(f"[TEST 9] Schematic Review Report:\n  -> {review['report_type']}\n")
    assert "Feedback stability review" in review["report_markdown"]

    print("=" * 60)
    print("  SUCCESS: All MCP math tools verified cleanly!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
