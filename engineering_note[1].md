# Engineering Note — ThermoFlow Pro

## 1. Hydraulic model
For a single equivalent loop, the total pressure loss is represented by Darcy–Weisbach major loss plus aggregate minor losses:

`Δp = [ f (L/D) + ΣK ] ρv²/2`

`v = Q/A`, `Re = ρvD/μ`, and pump head corresponding to pressure rise is `H = Δp/(ρg)` (plus static head).

The pump curve is an editable generic quadratic approximation:
`H_p = H_0 [1 - (Q/Q_free)^2]`, bounded at zero.
The system operating point is where pump head equals system head. A bisection root solver finds that intersection.

## 2. Pump power
`P_hyd = ρgQH`; estimated electrical input is `P_e = P_hyd/η`.
The included efficiency curve is a placeholder approximation around the entered best-efficiency-point flow. Replace it with vendor data.

## 3. Heat exchanger
The ε–NTU method is used:
`C_h = ṁ_h cp`, `C_c = ṁ_c cp`, `C_min = min(C_h,C_c)`,
`NTU = UA/C_min`, `C_r = C_min/C_max`,
`Q = ε C_min (T_h,in - T_c,in)`.
Outlet temperatures follow each stream's energy balance. The inverse sizing function solves for NTU and UA needed to meet a specified duty below the thermodynamic maximum.

## 4. Model limitations
Single-series loop, constant properties, generic pump model, no NPSH/cavitation, no branched network, no transient controls, no two-phase flow, no detailed component models, no CFD. Results are for learning and portfolio demonstration only.
