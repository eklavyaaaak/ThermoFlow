# ThermoFlow Pro — Liquid-Cooling CDU Engineering Simulator

A transparent, editable, 1-D steady-state thermal-hydraulic study tool built in Python and Streamlit. It demonstrates core calculations relevant to liquid-cooling equipment and coolant distribution units (CDUs).

## Features
- Pump/system curve intersection solved with bisection.
- Darcy–Weisbach pipe pressure drop, minor losses, Reynolds number, velocity and friction factor.
- Estimated pump hydraulic/electrical power and a generic efficiency approximation around BEP.
- Counter-current and parallel-flow heat exchanger performance using effectiveness–NTU.
- Required-UA sizing for a target heat duty.
- Flow sensitivity table and downloadable calculation summary.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Important engineering scope
This is an educational portfolio model, not a certified industrial design tool. The default pump curve is illustrative, not a real manufacturer curve. Replace it with a vendor's tested pump data before making equipment decisions. The model represents one equivalent series loop; it does not solve parallel branch networks. It does not include NPSH/cavitation, transient controls, temperature-dependent fluid properties, two-phase flow, detailed component internals, or CFD.

## Interview explanation
Be ready to explain:
1. Why the pump operating point is the intersection of pump and system curves.
2. Darcy–Weisbach and how Reynolds number/roughness affect friction losses.
3. Hydraulic power `ρ g Q H` and why electrical input is higher due to efficiency.
4. Heat exchanger effectiveness–NTU and the hot/cold-side energy balance.
5. Which inputs are generic assumptions and what vendor data would be needed for validation.

## Suggested validation before claiming design accuracy
- Compare pressure-drop predictions with a measured loop test at several flow rates.
- Enter a real pump manufacturer's Q-H and efficiency curves and compare the predicted intersection.
- Compare HX duty and outlet temperatures with a vendor selection sheet or instrumented test.
- Record measurement uncertainty and residual/error for each validation point.
