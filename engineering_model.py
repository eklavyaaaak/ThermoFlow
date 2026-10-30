"""ThermoFlow engineering calculations.

A steady-state, single-phase liquid-cooling loop screening model.
This is an educational conceptual model, not a certified equipment sizing tool.
"""
from dataclasses import dataclass
import math

@dataclass
class Inputs:
    heat_kw: float = 30.0
    tin_c: float = 25.0
    flow_l_min: float = 60.0
    pipe_id_mm: float = 32.0
    pipe_length_m: float = 25.0
    roughness_mm: float = 0.045
    fittings_k: float = 12.0
    pump_eff: float = 0.65
    rho: float = 997.0
    cp: float = 4180.0
    mu: float = 0.00089
    hx_ua_kw_k: float = 8.0
    secondary_in_c: float = 20.0

def calculate(x: Inputs):
    q_w = x.heat_kw * 1000
    vdot = x.flow_l_min / 60000.0
    area = math.pi * (x.pipe_id_mm / 1000.0)**2 / 4
    velocity = vdot / area
    mdot = x.rho * vdot
    delta_t = q_w / (mdot * x.cp) if mdot > 0 else float("nan")
    tout = x.tin_c + delta_t

    reynolds = x.rho * velocity * (x.pipe_id_mm/1000) / x.mu
    rel_rough = (x.roughness_mm/1000) / (x.pipe_id_mm/1000)
    if reynolds < 2300:
        friction = 64 / reynolds if reynolds > 0 else float("nan")
        regime = "Laminar"
    else:
        # Swamee-Jain explicit approximation
        friction = 0.25 / (math.log10(rel_rough/3.7 + 5.74/(reynolds**0.9))**2)
        regime = "Turbulent / transitional estimate"

    dynamic = x.rho * velocity**2 / 2
    dp_pipe = friction * (x.pipe_length_m/(x.pipe_id_mm/1000)) * dynamic
    dp_fittings = x.fittings_k * dynamic
    dp_total = dp_pipe + dp_fittings
    pump_hydraulic_w = dp_total * vdot
    pump_electric_w = pump_hydraulic_w / max(x.pump_eff, 0.01)

    # Simple counter-current LMTD screening estimate, using terminal differences
    # Treat hot stream as the primary coolant and assume secondary inlet given.
    dt1 = max(tout - x.secondary_in_c, 0.01)
    dt2 = max(x.tin_c - x.secondary_in_c, 0.01)
    if abs(dt1-dt2) < 1e-9:
        lmtd = dt1
    else:
        lmtd = (dt1-dt2) / math.log(dt1/dt2) if dt1/dt2 > 0 else float("nan")
    ua_w_k = x.hx_ua_kw_k * 1000
    hx_capacity_kw = ua_w_k * lmtd / 1000

    return {
        "mass_flow_kg_s": mdot,
        "velocity_m_s": velocity,
        "reynolds": reynolds,
        "flow_regime": regime,
        "friction_factor": friction,
        "coolant_delta_t_c": delta_t,
        "coolant_out_c": tout,
        "pipe_pressure_drop_kpa": dp_pipe/1000,
        "fittings_pressure_drop_kpa": dp_fittings/1000,
        "total_pressure_drop_kpa": dp_total/1000,
        "pump_hydraulic_kw": pump_hydraulic_w/1000,
        "pump_electric_kw": pump_electric_w/1000,
        "lmtd_k": lmtd,
        "hx_screening_capacity_kw": hx_capacity_kw,
        "hx_margin_kw": hx_capacity_kw - x.heat_kw,
    }

def sweep_flow(x: Inputs, values):
    rows = []
    for flow in values:
        y = Inputs(**{**x.__dict__, "flow_l_min": float(flow)})
        r = calculate(y)
        rows.append({"Flow (L/min)": flow, "Coolant ΔT (°C)": r["coolant_delta_t_c"],
                     "Pressure drop (kPa)": r["total_pressure_drop_kpa"],
                     "Pump input (kW)": r["pump_electric_kw"],
                     "Velocity (m/s)": r["velocity_m_s"]})
    return rows
