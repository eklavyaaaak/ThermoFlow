# ThermoFlow — Thermal-Hydraulic Analysis Workbench

**Project type:** Student engineering concept / steady-state simulation  
**Version:** 1.0

## What it does
ThermoFlow explores the interaction between thermal load, coolant flow rate, pipe geometry, pressure loss and estimated pump input in a conceptual liquid-cooling loop.

The app provides:
- Coolant temperature-rise calculation from an energy balance
- Pipe velocity and Reynolds number
- Darcy-Weisbach straight-pipe loss
- Aggregate minor losses using a user-entered K value
- First-pass pump input estimate
- Simplified heat-exchanger UA/LMTD screening estimate
- Flow-rate sweep plots and CSV export

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create a virtual environment (recommended):
   - Windows: `python -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install packages: `pip install -r requirements.txt`
5. Launch: `streamlit run app.py`

## Files
- `app.py` — interactive Streamlit dashboard
- `engineering_model.py` — calculation engine
- `requirements.txt` — Python dependencies
- `engineering_note.md` — project scope, equations, assumptions and limitations

## Engineering equations
Energy balance:
`Q = m_dot * cp * (Tout - Tin)`

Pipe velocity:
`V = V_dot / A`

Reynolds number:
`Re = rho * V * D / mu`

Darcy-Weisbach:
`deltaP_pipe = f * (L/D) * (rho*V^2/2)`

Minor losses:
`deltaP_minor = sum(K) * (rho*V^2/2)`

Pump input estimate:
`P_electric = deltaP_total * V_dot / eta_pump`

## Important scope statement
This is an educational, steady-state screening model using constant water-like properties. It is not a certified equipment sizing package and does not represent a physically tested product. The heat-exchanger calculation is a simplified screening estimate, not a full manufacturer rating. A real design requires validated component data, pump curves, a complete hydraulic network, fluid-property variation, controls, safety review and physical testing.

## How to present it honestly
Describe your actual contribution, explain the assumptions, show how you checked the equations, and be ready to discuss limitations and next validation steps. Do not claim physical testing or measured performance unless you perform it.
