# EE Circuit Analysis Assistant

An electrical-engineering circuit-analysis application that combines deterministic Python tools with an optional Google ADK/Gemini natural-language interface.

The core analysis runs locally with Python. Gemini is used only to interpret chat requests and present results; it does not perform the engineering calculations.

## Features

- RC low-pass cutoff frequency and time-constant analysis
- Series RLC resonance, Q factor, and bandwidth calculations
- Bode-response summaries for transfer functions
- Symbolic RC transfer-function derivation
- E24 standard component matching
- DC resistive-load current, voltage, power, loss, and efficiency calculations
- Open-loop feedback stability review using gain and phase margins
- Automated Markdown reports for RC filters, loads, and schematic reviews
- Streamlit interface with offline calculators that require no API key

## Architecture

```text
User interface (Streamlit, CLI, or ADK web UI)
                 |
                 +-- Optional: Google ADK + Gemini for natural-language chat
                 |
                 +-- Deterministic EE tools
                       |- NumPy: numerical calculations
                       |- SciPy: transfer functions and Bode analysis
                       |- SymPy: symbolic transfer functions
                       `- FastMCP-decorated tool definitions
```

`mcp_server.py` defines FastMCP-decorated engineering tools. In the current application, the ADK agent imports and calls those Python functions locally; the project does not require a separate MCP server process for normal use.

## Requirements

- Python 3.10 or later
- A Gemini API key only if you want to use the optional AI chat features

## Setup

```powershell
git clone https://github.com/yusufmd942/Circuit_Analysis_ADK.git
cd Circuit_Analysis_ADK
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, use the virtual environment executables directly in the commands below.

### Optional Gemini API key

Copy the template, then add your own key:

```powershell
Copy-Item .env.template .env
```

Edit `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Never commit `.env` or a real API key.

## Run the project

### Offline verification

Runs all deterministic engineering-tool tests. No API key or internet connection is required.

```powershell
.\venv\Scripts\python.exe test_tools.py
```

### Streamlit interface (recommended)

```powershell
.\venv\Scripts\streamlit.exe run app.py
```

Open the local address printed by Streamlit, normally `http://localhost:8501`. The **Offline calculators ($0)** tab works without Gemini.

### Terminal chat interface

Requires a configured Gemini API key.

```powershell
.\venv\Scripts\python.exe main.py
```

### Google ADK web UI

Run this command from the parent directory of the repository:

```powershell
.\Circut_Analysis_Agent\venv\Scripts\adk.exe web
```

## Testing

`test_tools.py` validates the deterministic tools against known RC, RLC, E24, load, stability, and report-generation results.

## Limitations

- Gemini API availability and free-tier quotas can limit the optional AI chat interface.
- Feedback stability results are open-loop design-review metrics, not a complete substitute for validating a physical closed-loop circuit, including parasitics, layout, loading, and component tolerances.

## License

Released under the [MIT License](LICENSE).
