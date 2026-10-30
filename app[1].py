import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from engineering_model import (Coolant, Pipe, PumpCurve, HXInputs, solve_operating_point,
                               hydraulic_state, heat_exchanger, required_ua_for_duty, flow_sweep)

st.set_page_config(page_title="ThermoFlow Pro | CDU Engineering", page_icon="💧", layout="wide")
st.markdown("""
<style>
.stApp{background:linear-gradient(145deg,#071426 0%,#0b1d33 55%,#10243b 100%);color:#edf4fb}
.block-container{padding-top:1.5rem;max-width:1500px}
[data-testid="stMetric"]{background:#112943;border:1px solid #24435f;padding:15px;border-radius:12px}
section[data-testid="stSidebar"]{background:#0b1b2d}
h1,h2,h3{color:#eaf4ff}
.small{color:#9bb4ca}
</style>
""",unsafe_allow_html=True)

st.title("💧 ThermoFlow Pro")
st.caption("Liquid-cooling CDU | 1-D thermal-hydraulic engineering simulator")
st.warning("Engineering study tool only. Pump curve defaults are illustrative, not manufacturer data. Verify all results before design or hardware use.")

with st.sidebar:
    st.header("1 · Coolant & loop")
    rho=st.number_input("Density (kg/m³)",850.0,1200.0,997.0,1.0)
    cp=st.number_input("Specific heat (J/kg·K)",3000.0,5000.0,4180.0,10.0)
    mu=st.number_input("Dynamic viscosity (Pa·s)",0.0001,0.01,0.00089,0.00001,format="%.5f")
    length=st.number_input("Equivalent pipe length (m)",1.0,500.0,25.0)
    diameter=st.number_input("Pipe inside diameter (mm)",8.0,150.0,32.0)
    rough=st.number_input("Pipe roughness (mm)",0.001,1.0,0.045,0.001)
    k=st.number_input("Total minor-loss coefficient ΣK",0.0,200.0,12.0)
    static=st.number_input("Static head (m)",0.0,100.0,0.0)
    st.header("2 · Pump curve")
    h0=st.number_input("Shutoff head H₀ (m)",1.0,100.0,28.0)
    qmax=st.number_input("Free-delivery flow (m³/h)",1.0,100.0,12.0)
    bep=st.number_input("BEP flow (m³/h)",0.1,100.0,7.0)
    eta=st.slider("Maximum pump efficiency (%)",15,90,68)
    st.header("3 · Heat exchanger")
    th=st.number_input("Hot-side inlet (°C)",21.0,100.0,40.0)
    tc=st.number_input("Cold-side inlet (°C)",0.0,th-0.1,20.0)
    mh=st.number_input("Hot-side mass flow (kg/s)",0.05,20.0,1.0)
    mc=st.number_input("Cold-side mass flow (kg/s)",0.05,20.0,1.2)
    ua=st.number_input("HX UA (kW/K)",0.1,200.0,8.0)
    arrangement=st.selectbox("HX arrangement",["Counter-current","Parallel-flow"])

cool=Coolant(rho,cp,mu,rough/1000)
pipe=Pipe(length,diameter/1000,rough/1000,k,static)
pump=PumpCurve(h0,qmax,bep,eta/100)
hx=HXInputs(th,tc,mh,mc,ua,arrangement)

st.markdown("### Operating point")
try:
    op=solve_operating_point(cool,pipe,pump)
    a,b,c,d=st.columns(4)
    a.metric("Operating flow",f"{op['flow_m3h']:.2f} m³/h")
    b.metric("Pump head",f"{op['pump_head_m']:.2f} m")
    c.metric("Loop pressure drop",f"{op['total_dp_pa']/1000:.1f} kPa")
    d.metric("Electrical pump input",f"{op['electrical_power_w']/1000:.2f} kW")
    e,f,g,h=st.columns(4)
    e.metric("Pipe velocity",f"{op['velocity_m_s']:.2f} m/s")
    f.metric("Reynolds number",f"{op['reynolds']:,.0f}")
    g.metric("Pump efficiency estimate",f"{op['pump_efficiency']*100:.1f}%")
    h.metric("Flow deviation from BEP",f"{op['flow_vs_bep_pct']:+.1f}%")
except Exception as ex:
    st.error(f"Operating point could not be solved: {ex}")
    op=None

tab1,tab2,tab3,tab4=st.tabs(["Pump & system curves","Heat exchanger","Design sensitivity","Calculation report"])
with tab1:
    rows=flow_sweep(cool,pipe,pump)
    df=pd.DataFrame(rows)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df.flow_m3h,y=df.pump_head_m,name="Pump curve",line=dict(width=3)))
    fig.add_trace(go.Scatter(x=df.flow_m3h,y=df.system_head_m,name="System curve",line=dict(width=3)))
    if op: fig.add_vline(x=op["flow_m3h"],line_dash="dash",annotation_text="Operating point")
    fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(10,25,42,.7)",
                      xaxis_title="Flow (m³/h)",yaxis_title="Head (m)",legend=dict(orientation="h"))
    st.plotly_chart(fig,use_container_width=True)
    if op:
        st.write("The operating point is the intersection of the entered pump curve and calculated system-resistance curve.")
        st.dataframe(pd.DataFrame([{"Parameter":k,"Value":v} for k,v in op.items()]),hide_index=True,use_container_width=True)
with tab2:
    try:
        result=heat_exchanger(hx,cp)
        x1,x2,x3=st.columns(3)
        x1.metric("Heat-transfer duty",f"{result['duty_kw']:.2f} kW")
        x2.metric("Effectiveness",f"{result['effectiveness']*100:.1f}%")
        x3.metric("NTU",f"{result['ntu']:.2f}")
        y1,y2=st.columns(2)
        y1.metric("Hot outlet",f"{result['hot_out_c']:.2f} °C")
        y2.metric("Cold outlet",f"{result['cold_out_c']:.2f} °C")
        st.markdown("#### Thermal balance")
        st.write(f"Hot-side heat loss = {(mh*cp*(th-result['hot_out_c'])/1000):.3f} kW")
        st.write(f"Cold-side heat gain = {(mc*cp*(result['cold_out_c']-tc)/1000):.3f} kW")
        st.caption("Both sides are calculated from the same heat duty; temperature changes satisfy the steady-state energy balance.")
        target=st.number_input("Required duty for UA sizing (kW)",0.1,float(result["maximum_possible_duty_kw"]*0.99),float(min(20,result["maximum_possible_duty_kw"]*0.7)))
        sizing=required_ua_for_duty(target,hx,cp)
        st.success(f"Required UA for this target duty: {sizing['required_ua_kw_k']:.3f} kW/K")
    except Exception as ex: st.error(str(ex))
with tab3:
    st.markdown("#### Flow sensitivity")
    flows=st.slider("Compare design flow range (m³/h)",1.0,float(qmax),min(10.0,float(qmax)),0.5)
    vals=[]
    for q in [flows*i/20 for i in range(1,21)]:
        s=hydraulic_state(q,cool,pipe)
        vals.append({"Flow (m³/h)":q,"Velocity (m/s)":s["velocity_m_s"],"Δp (kPa)":s["total_dp_pa"]/1000,
                     "System head (m)":s["system_head_m"]})
    st.dataframe(pd.DataFrame(vals),hide_index=True,use_container_width=True)
with tab4:
    st.markdown("#### Assumptions and model boundaries")
    st.write("- Single equivalent series loop; no parallel branch balancing.")
    st.write("- Darcy–Weisbach pressure loss with Haaland turbulent friction-factor approximation.")
    st.write("- Generic quadratic pump curve; efficiency is an illustrative BEP-centred approximation.")
    st.write("- Heat exchanger uses ε–NTU relations for the selected flow arrangement.")
    st.write("- Constant coolant properties; no temperature-dependent property lookup.")
    st.write("- No cavitation/NPSH, transient controls, two-phase flow, detailed component internals, or CFD.")
    st.write("Use manufacturer pump and heat-exchanger data for an actual design.")
    report={"operating_point":op,"heat_exchanger":heat_exchanger(hx,cp)}
    st.download_button("Download calculation summary (JSON)",json.dumps(report,indent=2,default=str),
                       file_name="thermoflow_calculation_summary.json",mime="application/json")
