"""ThermoFlow Pro: transparent 1-D steady-state thermal-hydraulic calculations.

Educational engineering tool. Generic pump curve and component inputs are user-editable.
Not a certified design package. Validate all inputs against manufacturer data and standards.
"""
from dataclasses import dataclass, asdict
from math import pi, log, sqrt
from typing import List, Dict, Any

G = 9.80665

@dataclass
class Coolant:
    rho: float = 997.0          # kg/m3, water near 25 C
    cp: float = 4180.0          # J/kg-K
    mu: float = 0.00089         # Pa.s
    roughness: float = 4.5e-5   # m, commercial steel illustrative

@dataclass
class Pipe:
    length_m: float = 25.0
    diameter_m: float = 0.032
    roughness_m: float = 4.5e-5
    minor_loss_k: float = 12.0
    static_head_m: float = 0.0

@dataclass
class PumpCurve:
    shutoff_head_m: float = 28.0
    free_delivery_m3h: float = 12.0
    bep_flow_m3h: float = 7.0
    max_efficiency: float = 0.68

@dataclass
class HXInputs:
    hot_in_c: float = 40.0
    cold_in_c: float = 20.0
    hot_mass_flow_kg_s: float = 1.0
    cold_mass_flow_kg_s: float = 1.2
    ua_kw_k: float = 8.0
    arrangement: str = "Counter-current"

def friction_factor(re: float, rel_rough: float) -> float:
    if re <= 0:
        return 0.0
    if re < 2300:
        return 64.0 / re
    # Haaland explicit approximation to Colebrook-White
    turbulent = (-1.8 * log((rel_rough / 3.7)**1.11 + 6.9 / re, 10))**-2
    if re < 4000:
        # Smooth interpolation over the transitional range
        lam = 64.0 / 2300.0
        w = (re - 2300.0) / 1700.0
        return lam*(1-w) + turbulent*w
    return turbulent

def hydraulic_state(flow_m3h: float, coolant: Coolant, pipe: Pipe) -> Dict[str, float]:
    q = max(flow_m3h, 0.0) / 3600.0
    area = pi * pipe.diameter_m**2 / 4.0
    velocity = q / area if area else 0.0
    re = coolant.rho * velocity * pipe.diameter_m / coolant.mu if velocity else 0.0
    rr = pipe.roughness_m / pipe.diameter_m
    f = friction_factor(re, rr)
    dynamic = coolant.rho * velocity**2 / 2.0
    major = f * (pipe.length_m / pipe.diameter_m) * dynamic if velocity else 0.0
    minor = pipe.minor_loss_k * dynamic
    dp = major + minor
    head = dp / (coolant.rho * G) + pipe.static_head_m
    return {"flow_m3h": flow_m3h, "velocity_m_s": velocity, "reynolds": re,
            "friction_factor": f, "major_dp_pa": major, "minor_dp_pa": minor,
            "total_dp_pa": dp, "system_head_m": head}

def pump_head_m(flow_m3h: float, curve: PumpCurve) -> float:
    qmax = max(curve.free_delivery_m3h, 1e-9)
    return curve.shutoff_head_m * max(0.0, 1.0 - (max(flow_m3h, 0.0)/qmax)**2)

def pump_efficiency(flow_m3h: float, curve: PumpCurve) -> float:
    # Generic parabolic approximation around BEP; replace with vendor curve.
    span = max(curve.free_delivery_m3h, 1e-6)
    penalty = 0.30 * ((flow_m3h - curve.bep_flow_m3h)/span)**2
    return max(0.15, min(curve.max_efficiency, curve.max_efficiency*(1.0-penalty)))

def solve_operating_point(coolant: Coolant, pipe: Pipe, curve: PumpCurve) -> Dict[str, float]:
    """Bisection on pump head - system head; returns first positive intersection."""
    lo, hi = 0.0, max(curve.free_delivery_m3h, 0.1)
    def residual(q):
        return pump_head_m(q, curve) - hydraulic_state(q, coolant, pipe)["system_head_m"]
    if residual(lo) <= 0:
        raise ValueError("Pump shutoff head does not overcome the specified static/system head.")
    if residual(hi) > 0:
        hi *= 2
        for _ in range(30):
            if residual(hi) <= 0: break
            hi *= 2
        else:
            raise ValueError("Could not bracket pump/system intersection; check pump curve.")
    for _ in range(100):
        mid=(lo+hi)/2
        if residual(mid)>0: lo=mid
        else: hi=mid
    q=(lo+hi)/2
    state=hydraulic_state(q,coolant,pipe)
    h=pump_head_m(q,curve)
    eta=pump_efficiency(q,curve)
    hydraulic_power=coolant.rho*G*(q/3600)*h
    return {**state, "pump_head_m":h, "pump_efficiency":eta,
            "hydraulic_power_w":hydraulic_power,
            "electrical_power_w":hydraulic_power/eta,
            "bep_flow_m3h":curve.bep_flow_m3h,
            "flow_vs_bep_pct":100*(q-curve.bep_flow_m3h)/curve.bep_flow_m3h}

def hx_effectiveness(ntu: float, cr: float, arrangement: str) -> float:
    if ntu <= 0: return 0.0
    if abs(1-cr) < 1e-8:
        return ntu/(1+ntu) if arrangement == "Parallel-flow" else ntu/(1+ntu)
    if arrangement == "Parallel-flow":
        return (1 - __import__("math").exp(-ntu*(1+cr)))/(1+cr)
    e=__import__("math").exp(-ntu*(1-cr))
    return (1-e)/(1-cr*e)

def heat_exchanger(hx: HXInputs, cp: float = 4180.0) -> Dict[str, float]:
    if min(hx.hot_mass_flow_kg_s, hx.cold_mass_flow_kg_s, hx.ua_kw_k) <= 0:
        raise ValueError("Both mass flow rates and UA must be greater than zero.")
    if hx.hot_in_c <= hx.cold_in_c:
        raise ValueError("Hot-side inlet temperature must exceed cold-side inlet temperature.")
    ch=hx.hot_mass_flow_kg_s*cp
    cc=hx.cold_mass_flow_kg_s*cp
    cmin=min(ch,cc); cmax=max(ch,cc); cr=cmin/cmax
    ntu=hx.ua_kw_k*1000/cmin
    eps=hx_effectiveness(ntu,cr,hx.arrangement)
    qmax=cmin*(hx.hot_in_c-hx.cold_in_c)
    duty=eps*qmax
    hot_out=hx.hot_in_c-duty/ch
    cold_out=hx.cold_in_c+duty/cc
    return {"ntu":ntu,"capacity_ratio":cr,"effectiveness":eps,
            "maximum_possible_duty_kw":qmax/1000,"duty_kw":duty/1000,
            "hot_out_c":hot_out,"cold_out_c":cold_out,
            "hot_capacity_rate_w_k":ch,"cold_capacity_rate_w_k":cc}

def required_ua_for_duty(duty_kw: float, hx: HXInputs, cp: float=4180.0) -> Dict[str,float]:
    ch=hx.hot_mass_flow_kg_s*cp; cc=hx.cold_mass_flow_kg_s*cp
    cmin=min(ch,cc); cmax=max(ch,cc); cr=cmin/cmax
    qmax=cmin*(hx.hot_in_c-hx.cold_in_c)
    target=duty_kw*1000/qmax
    if target <= 0 or target >= 1:
        raise ValueError("Target duty must be greater than zero and below the thermodynamic maximum.")
    lo,hi=0.0,1.0
    while hx_effectiveness(hi,cr,hx.arrangement)<target: hi*=2
    for _ in range(100):
        mid=(lo+hi)/2
        if hx_effectiveness(mid,cr,hx.arrangement)<target: lo=mid
        else: hi=mid
    ntu=(lo+hi)/2
    return {"target_effectiveness":target,"required_ntu":ntu,"required_ua_kw_k":ntu*cmin/1000}

def flow_sweep(coolant: Coolant, pipe: Pipe, curve: PumpCurve, count: int=50) -> List[Dict[str,float]]:
    maxq=curve.free_delivery_m3h
    rows=[]
    for i in range(count):
        q=maxq*i/(count-1)
        st=hydraulic_state(q,coolant,pipe)
        rows.append({"flow_m3h":q,"pump_head_m":pump_head_m(q,curve),
                     "system_head_m":st["system_head_m"],"pressure_drop_kpa":st["total_dp_pa"]/1000})
    return rows
