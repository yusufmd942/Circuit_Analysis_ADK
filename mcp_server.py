"""
MCP Tool Server for Electrical Engineering Computations
Exposes deterministic engineering math tools using FastMCP, SciPy, SymPy, and NumPy.
"""
from fastmcp import FastMCP
import scipy.signal as signal
import sympy as sp
import numpy as np

# Initialize FastMCP server
mcp = FastMCP("EE-Math-Tools")

@mcp.tool()
def calculate_rc_cutoff(r_ohms: float, c_farads: float) -> dict:
    """Calculates cutoff frequency (Hz) and time constant (seconds) for an RC filter."""
    if r_ohms <= 0 or c_farads <= 0:
        return {"error": "Resistor and capacitor values must be strictly positive."}
    
    tau = r_ohms * c_farads
    fc = 1.0 / (2.0 * np.pi * tau)
    return {
        "cutoff_frequency_hz": round(float(fc), 2),
        "time_constant_sec": float(tau),
        "r_ohms": r_ohms,
        "c_farads": c_farads
    }

@mcp.tool()
def calculate_rlc_resonance(r_ohms: float, l_henries: float, c_farads: float) -> dict:
    """Calculates resonant frequency (Hz), Q factor, and 3dB bandwidth for a series RLC circuit."""
    if r_ohms <= 0 or l_henries <= 0 or c_farads <= 0:
        return {"error": "All component values (R, L, C) must be strictly positive."}
    
    w0 = 1.0 / np.sqrt(l_henries * c_farads)
    f0 = w0 / (2.0 * np.pi)
    q = (1.0 / r_ohms) * np.sqrt(l_henries / c_farads)
    bw = f0 / q
    return {
        "resonant_frequency_hz": round(float(f0), 2),
        "q_factor": round(float(q), 2),
        "bandwidth_hz": round(float(bw), 2),
        "r_ohms": r_ohms,
        "l_henries": l_henries,
        "c_farads": c_farads
    }

@mcp.tool()
def analyze_bode_transfer_function(num: list[float], den: list[float]) -> dict:
    """Computes peak gain (dB) and -3dB cutoff frequency for transfer function numerator/denominator coefficients."""
    try:
        sys = signal.TransferFunction(num, den)
        w, mag, phase = signal.bode(sys)
        max_gain = float(np.max(mag))
        cutoff_idx = np.argmin(np.abs(mag - (max_gain - 3.0)))
        cutoff_w = float(w[cutoff_idx])
        return {
            "max_gain_db": round(max_gain, 2),
            "cutoff_freq_rad_s": round(cutoff_w, 2),
            "cutoff_freq_hz": round(cutoff_w / (2.0 * np.pi), 2)
        }
    except Exception as e:
        return {"error": f"Failed to compute Bode analysis: {str(e)}"}

@mcp.tool()
def solve_symbolic_transfer_function(circuit_type: str, r_val: float, c_val: float) -> dict:
    """Derives the symbolic Laplace transfer function H(s) for a lowpass or highpass RC filter using SymPy."""
    s, R, C = sp.symbols('s R C')
    if circuit_type.lower() in ["lowpass", "lp"]:
        H_sym = 1 / (1 + s * R * C)
        mode = "lowpass"
    else:
        H_sym = (s * R * C) / (1 + s * R * C)
        mode = "highpass"
    
    H_numeric = H_sym.subs({R: r_val, C: c_val})
    return {
        "symbolic_expression": str(H_sym),
        "numeric_expression": str(sp.simplify(H_numeric)),
        "circuit_type": mode
    }

@mcp.tool()
def match_e24_component(value: float, component_type: str = "resistor") -> dict:
    """Finds the nearest standard E24 series component value for a target resistor (ohms) or capacitor (farads)."""
    e24_base = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
                3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
    
    if value <= 0:
        return {"error": "Component value must be positive"}
    
    decade = 10 ** np.floor(np.log10(value))
    normalized = value / decade
    closest_base = min(e24_base, key=lambda x: abs(x - normalized))
    standard_value = round(closest_base * decade, 9)
    error_pct = round(abs((standard_value - value) / value) * 100, 2)
    
    return {
        "target_value": value,
        "standard_e24_value": standard_value,
        "error_percentage": error_pct,
        "component_type": component_type
    }

@mcp.tool()
def calculate_resistive_load(
    supply_voltage_volts: float,
    load_resistance_ohms: float,
    source_resistance_ohms: float = 0.0,
) -> dict:
    """Calculates DC load current, load voltage, load power, source loss, and efficiency."""
    if supply_voltage_volts < 0 or load_resistance_ohms <= 0 or source_resistance_ohms < 0:
        return {"error": "Supply voltage and source resistance must be non-negative; load resistance must be positive."}

    total_resistance = load_resistance_ohms + source_resistance_ohms
    current = supply_voltage_volts / total_resistance
    load_voltage = current * load_resistance_ohms
    load_power = current ** 2 * load_resistance_ohms
    source_loss = current ** 2 * source_resistance_ohms
    input_power = supply_voltage_volts * current
    efficiency = (load_power / input_power * 100) if input_power else 100.0
    return {
        "supply_voltage_v": supply_voltage_volts,
        "load_resistance_ohms": load_resistance_ohms,
        "source_resistance_ohms": source_resistance_ohms,
        "load_current_a": round(float(current), 6),
        "load_voltage_v": round(float(load_voltage), 6),
        "load_power_w": round(float(load_power), 6),
        "source_loss_w": round(float(source_loss), 6),
        "efficiency_percent": round(float(efficiency), 2),
    }

@mcp.tool()
def analyze_feedback_stability(num: list[float], den: list[float]) -> dict:
    """Estimates gain/phase margins from an open-loop transfer function for feedback stability review."""
    try:
        system = signal.TransferFunction(num, den)
        poles = np.asarray(system.poles, dtype=complex)
        characteristic_frequencies = np.abs(poles[np.abs(poles) > 0])
        center = float(np.median(characteristic_frequencies)) if characteristic_frequencies.size else 1.0
        w = np.logspace(np.log10(center) - 4, np.log10(center) + 4, 4000)
        _, response = signal.freqresp(system, w)
        magnitude_db = 20 * np.log10(np.maximum(np.abs(response), 1e-300))
        phase_deg = np.unwrap(np.angle(response)) * 180 / np.pi

        gain_crossings = np.where(np.diff(np.signbit(magnitude_db)))[0]
        phase_crossings = np.where(np.diff(np.signbit(phase_deg + 180)))[0]
        result = {"review_note": "Margins are computed from the supplied open-loop transfer function; they are a design-review metric, not a complete proof of closed-loop stability."}

        if gain_crossings.size:
            index = gain_crossings[0]
            gain_crossover = float(np.exp(np.interp(0.0, magnitude_db[index:index + 2][::-1], np.log(w[index:index + 2][::-1]))))
            phase_at_crossover = float(np.interp(np.log(gain_crossover), np.log(w), phase_deg))
            phase_margin = 180 + phase_at_crossover
            result.update({
                "gain_crossover_hz": round(gain_crossover / (2 * np.pi), 3),
                "phase_margin_deg": round(phase_margin, 2),
                "stability_assessment": "acceptable margin" if phase_margin >= 45 else "marginal margin" if phase_margin >= 0 else "negative phase margin",
            })
        else:
            result["phase_margin_deg"] = None
            result["stability_assessment"] = "no 0 dB gain crossover found in analysis range"

        if phase_crossings.size:
            index = phase_crossings[0]
            phase_crossover = float(np.exp(np.interp(-180.0, phase_deg[index:index + 2], np.log(w[index:index + 2]))))
            gain_at_crossover = float(np.interp(np.log(phase_crossover), np.log(w), magnitude_db))
            result["phase_crossover_hz"] = round(phase_crossover / (2 * np.pi), 3)
            result["gain_margin_db"] = round(-gain_at_crossover, 2)
        else:
            result["gain_margin_db"] = None
        return result
    except Exception as exc:
        return {"error": f"Failed to analyze feedback stability: {str(exc)}"}

@mcp.tool()
def generate_rc_design_report(r_ohms: float, c_farads: float) -> dict:
    """Generates a concise Markdown design report for a first-order RC low-pass filter."""
    analysis = calculate_rc_cutoff(r_ohms, c_farads)
    if "error" in analysis:
        return analysis
    report = (
        "# RC Low-Pass Filter Design Report\n\n"
        "## Design inputs\n"
        f"- Resistance: {r_ohms:,.6g} Ω\n"
        f"- Capacitance: {c_farads:,.6g} F\n\n"
        "## Calculated performance\n\n"
        "| Metric | Result |\n|---|---:|\n"
        f"| Cutoff frequency | {analysis['cutoff_frequency_hz']:,.2f} Hz |\n"
        f"| Time constant | {analysis['time_constant_sec']:.6g} s |\n\n"
        "## Review note\n"
        "This first-order passive network has transfer function `H(s) = 1 / (RCs + 1)`. "
        "Confirm component voltage, tolerance, and loading requirements before release."
    )
    return {"report_type": "rc_lowpass", "report_markdown": report, "analysis": analysis}

@mcp.tool()
def generate_load_design_report(
    supply_voltage_volts: float,
    load_resistance_ohms: float,
    source_resistance_ohms: float = 0.0,
) -> dict:
    """Generates a concise Markdown load-calculation report for schematic review."""
    analysis = calculate_resistive_load(supply_voltage_volts, load_resistance_ohms, source_resistance_ohms)
    if "error" in analysis:
        return analysis
    report = (
        "# DC Resistive Load Design Report\n\n"
        "## Calculated performance\n\n"
        "| Metric | Result |\n|---|---:|\n"
        f"| Load current | {analysis['load_current_a']:,.6f} A |\n"
        f"| Load voltage | {analysis['load_voltage_v']:,.6f} V |\n"
        f"| Load power | {analysis['load_power_w']:,.6f} W |\n"
        f"| Source loss | {analysis['source_loss_w']:,.6f} W |\n"
        f"| Efficiency | {analysis['efficiency_percent']:.2f}% |\n\n"
        "## Review note\n"
        "Verify resistor power ratings, supply-current capability, thermal margin, and load transients before release."
    )
    return {"report_type": "dc_resistive_load", "report_markdown": report, "analysis": analysis}

@mcp.tool()
def generate_schematic_review_report(
    supply_voltage_volts: float,
    load_resistance_ohms: float,
    source_resistance_ohms: float,
    open_loop_num: list[float],
    open_loop_den: list[float],
) -> dict:
    """Generates a combined load and open-loop stability review report for a schematic."""
    load = calculate_resistive_load(supply_voltage_volts, load_resistance_ohms, source_resistance_ohms)
    stability = analyze_feedback_stability(open_loop_num, open_loop_den)
    if "error" in load:
        return load
    if "error" in stability:
        return stability

    phase_margin = "Not available" if stability["phase_margin_deg"] is None else f"{stability['phase_margin_deg']:.2f}°"
    gain_margin = "Not available" if stability["gain_margin_db"] is None else f"{stability['gain_margin_db']:.2f} dB"
    report = (
        "# Schematic Review Report\n\n"
        "## Load calculation\n\n"
        "| Metric | Result |\n|---|---:|\n"
        f"| Load current | {load['load_current_a']:.6f} A |\n"
        f"| Load voltage | {load['load_voltage_v']:.6f} V |\n"
        f"| Load power | {load['load_power_w']:.6f} W |\n"
        f"| Source loss | {load['source_loss_w']:.6f} W |\n"
        f"| Efficiency | {load['efficiency_percent']:.2f}% |\n\n"
        "## Feedback stability review\n\n"
        "| Metric | Result |\n|---|---:|\n"
        f"| Assessment | {stability['stability_assessment']} |\n"
        f"| Phase margin | {phase_margin} |\n"
        f"| Gain margin | {gain_margin} |\n\n"
        "## Release checklist\n"
        "- Confirm component voltage and power ratings.\n"
        "- Confirm supply-current and thermal margins.\n"
        "- Review feedback compensation against the complete closed-loop implementation.\n"
    )
    return {
        "report_type": "schematic_review",
        "report_markdown": report,
        "load_analysis": load,
        "stability_analysis": stability,
    }

if __name__ == "__main__":
    mcp.run()
