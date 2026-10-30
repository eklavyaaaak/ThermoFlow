import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from engineering_model import Inputs, calculate, sweep_flow

st.set_page_config(page_title="ThermoFlow | Thermal-Hydraulic Lab", page_icon="🌡️", layout="wide")

st.markdown("""
<style>
.stApp {background: radial-gradient(circle at 12% 0%, #16243a 0%, #0b1220 45%, #080d17 100%); color:#e8eef7;}
[data-testid="stMetric"] {background:linear-gradient(135deg,#17263b,#101a2a); border:1px solid #2a3d58; padding:16px; border-radius:14px;}
section[data-testid="stSidebar"] {background:#101a2a;}
div[data-testid="stExpander"] {border:1px solid #2b405d; border-radius:12px;}
h1,h2,h3 {letter-spacing:-.03em;}
.small-muted {color:#9db0c9; font-size:.88rem;}
.hero {padding:22px 26px; border:1px solid #29415f; border-radius:18px; background:linear-gradient(115deg,rgba(22,49,77,.95),rgba(16,28,46,.75)); margin-bottom:18px;}
.pill {display:inline-block; border:1px solid #3c648d; color:#a9d7ff; padding:4px 10px; border-radius:99px; font-size:12px; margin-right:6px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div><span class="pill">ENGINEERING WORKBENCH</span><span class="pill">STEADY-STATE MODEL</span><span class="pill">REV 1.0</span></div>
  <h1 style="font-size:2.55rem;margin:12px 0 4px;">THERMO<span style="color:#56c7e8;">FLOW</span></h1>
  <div style="font-size:1.12rem;color:#c3d4e8;">Thermal-hydraulic analysis & operating-point exploration</div>
  <p class="small-muted">A conceptual liquid-cooling loop model for exploring heat removal, hydraulic losses and pump energy trade-offs.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Design inputs")
    st.caption("Adjust the conceptual loop. SI properties are used internally.")
    heat = st.slider("Thermal load (kW)", 5.0, 100.0, 30.0, 1.0)
    tin = st.slider("Coolant inlet temperature (°C)", 10.0, 45.0, 25.0, 1.0)
    flow = st.slider("Coolant flow rate (L/min)", 10.0, 180.0, 60.0, 2.0)
    diameter = st.select_slider("Pipe internal diameter (mm)", options=[16,20,25,32,40,50,63], value=32)
    length = st.slider("Equivalent straight pipe length (m)", 5.0, 100.0, 25.0, 5.0)
    fittings = st.slider("Fittings loss coefficient, ΣK", 0.0, 40.0, 12.0, 1.0)
    eff = st.slider("Pump efficiency (%)", 30, 85, 65, 1)/100
    st.divider()
    st.subheader("Heat exchanger assumptions")
    ua = st.slider("Overall UA (kW/K)", 1.0, 30.0, 8.0, 0.5)
    sec_in = st.slider("Secondary-side inlet (°C)", 5.0, 35.0, 20.0, 1.0)
    st.caption("Water-like coolant properties are assumed. Edit the model file to change fluid properties.")

x = Inputs(heat_kw=heat, tin_c=tin, flow_l_min=flow, pipe_id_mm=float(diameter),
           pipe_length_m=length, fittings_k=fittings, pump_eff=eff,
           hx_ua_kw_k=ua, secondary_in_c=sec_in)
r = calculate(x)

st.subheader("Live system snapshot")
cols = st.columns(4)
cols[0].metric("Coolant outlet", f'{r["coolant_out_c"]:.1f} °C', f'ΔT {r["coolant_delta_t_c"]:.1f} °C')
cols[1].metric("Loop pressure drop", f'{r["total_pressure_drop_kpa"]:.1f} kPa')
cols[2].metric("Estimated pump input", f'{r["pump_electric_kw"]:.2f} kW')
cols[3].metric("Heat exchanger screen", f'{r["hx_screening_capacity_kw"]:.1f} kW', f'margin {r["hx_margin_kw"]:.1f} kW')

if r["hx_margin_kw"] < 0:
    st.warning("The simplified heat-exchanger screening capacity is below the specified thermal load. Increase UA or review terminal temperatures.")
if r["coolant_out_c"] > 40:
    st.warning("Predicted coolant outlet temperature is above 40 °C. Review flow rate, heat load and allowable component temperatures.")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance", "🔬 Flow sweep", "🧰 Engineering details", "📘 Model notes"])

with tab1:
    a,b = st.columns([1.2,1])
    with a:
        st.markdown("#### Thermal duty")
        fig = go.Figure(go.Indicator(mode="gauge+number", value=heat,
            title={"text":"Specified heat load (kW)"},
            gauge={"axis":{"range":[0,100]}, "bar":{"color":"#56c7e8"},
                   "steps":[{"range":[0,50],"color":"#19334b"},{"range":[50,100],"color":"#3b2632"}]}))
        fig.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", font_color="#e8eef7", margin=dict(l=20,r=20,t=50,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with b:
        st.markdown("#### Hydraulic breakdown")
        dfp = pd.DataFrame({"Component":["Straight pipe","Fittings"],"Pressure drop (kPa)":[r["pipe_pressure_drop_kpa"],r["fittings_pressure_drop_kpa"]]})
        fig2 = px.bar(dfp, x="Component", y="Pressure drop (kPa)", color="Component",
                      color_discrete_sequence=["#56c7e8","#f5a65b"])
        fig2.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e8eef7", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown("#### Flow path — conceptual arrangement")
    st.markdown("""
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
    <div style="background:#17314a;border:1px solid #3b6388;border-radius:12px;padding:15px;flex:1;text-align:center;">♨️ Heat source<br><small>Server / equipment load</small></div>
    <div style="color:#56c7e8;font-size:24px;">→</div>
    <div style="background:#17314a;border:1px solid #3b6388;border-radius:12px;padding:15px;flex:1;text-align:center;">❄️ Heat exchanger<br><small>Heat rejection</small></div>
    <div style="color:#56c7e8;font-size:24px;">→</div>
    <div style="background:#17314a;border:1px solid #3b6388;border-radius:12px;padding:15px;flex:1;text-align:center;">⚙️ Pump<br><small>Circulation</small></div>
    <div style="color:#56c7e8;font-size:24px;">→</div>
    <div style="background:#17314a;border:1px solid #3b6388;border-radius:12px;padding:15px;flex:1;text-align:center;">🔁 Return loop<br><small>Repeat cycle</small></div>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("#### How does changing flow rate affect the loop?")
    flows = np.linspace(20,160,29)
    sweep = pd.DataFrame(sweep_flow(x, flows))
    c1,c2 = st.columns(2)
    with c1:
        f = px.line(sweep, x="Flow (L/min)", y="Coolant ΔT (°C)", markers=True, title="Coolant temperature rise")
        f.update_traces(line_color="#56c7e8")
        f.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#e8eef7")
        st.plotly_chart(f,use_container_width=True)
    with c2:
        f = px.line(sweep, x="Flow (L/min)", y="Pressure drop (kPa)", markers=True, title="Hydraulic penalty")
        f.update_traces(line_color="#f5a65b")
        f.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#e8eef7")
        st.plotly_chart(f,use_container_width=True)
    f = px.line(sweep, x="Flow (L/min)", y="Pump input (kW)", markers=True, title="Estimated pump electrical input")
    f.update_traces(line_color="#a88cf0")
    f.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#e8eef7")
    st.plotly_chart(f,use_container_width=True)
    st.dataframe(sweep.round(3), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download flow-sweep CSV", sweep.to_csv(index=False), "thermoflow_flow_sweep.csv", "text/csv")

with tab3:
    st.markdown("#### Calculated engineering quantities")
    rows = [
        ("Mass flow rate",r["mass_flow_kg_s"],"kg/s"),
        ("Mean pipe velocity",r["velocity_m_s"],"m/s"),
        ("Reynolds number",r["reynolds"],"—"),
        ("Darcy friction factor",r["friction_factor"],"—"),
        ("Straight-pipe pressure loss",r["pipe_pressure_drop_kpa"],"kPa"),
        ("Fittings pressure loss",r["fittings_pressure_drop_kpa"],"kPa"),
        ("Total modelled pressure loss",r["total_pressure_drop_kpa"],"kPa"),
        ("Hydraulic pump power",r["pump_hydraulic_kw"],"kW"),
        ("Estimated electrical input",r["pump_electric_kw"],"kW"),
        ("LMTD screening value",r["lmtd_k"],"K"),
    ]
    st.dataframe(pd.DataFrame(rows,columns=["Quantity","Value","Unit"]).round(4), use_container_width=True, hide_index=True)
    st.info(f'Flow regime estimate: **{r["flow_regime"]}**. Reynolds number = {r["reynolds"]:.0f}.')
    st.caption("Pump input is calculated from modelled loop pressure loss × volumetric flow / assumed efficiency. It is not a pump-curve selection.")

with tab4:
    st.markdown("""
    #### Model boundary and assumptions
    - Steady-state, incompressible, single-phase flow.
    - Water-like constant properties: density 997 kg/m³, specific heat 4180 J/kg·K, dynamic viscosity 0.00089 Pa·s.
    - Darcy-Weisbach pressure loss with Swamee–Jain friction-factor approximation in turbulent flow; laminar relation below Re 2300.
    - Minor losses represented by a user-entered aggregate ΣK.
    - Pump electrical input estimated from pressure loss and assumed efficiency.
    - Heat exchanger capacity is a screening estimate using an assumed UA and a simplified terminal-temperature approach.

    #### Important limitations
    This is not a detailed counter-current heat-exchanger rating model, network solver, pump curve intersection, transient thermal model, CFD model or safety-certified design. The heat-exchanger estimate is intentionally a screening calculation and should be replaced with a full effectiveness-NTU or manufacturer-rating method for design release.

    #### Suggested next validation steps
    1. Compare pipe pressure loss against a trusted Darcy-Weisbach worked example.
    2. Add a real pump curve and solve its intersection with the system curve.
    3. Implement a full counter-current effectiveness-NTU model.
    4. Verify selected operating points with a physical test loop before making hardware claims.
    """)
    st.download_button("⬇️ Download current input summary", pd.Series(x.__dict__).to_csv(), "thermoflow_inputs.csv", "text/csv")

st.markdown("---")
st.caption("THERMOFLOW • Student engineering concept • Results are model outputs, not experimental measurements.")
