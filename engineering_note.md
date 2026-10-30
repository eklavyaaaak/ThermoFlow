# ThermoFlow — Engineering Note

## 1. Problem statement
Liquid-cooling loops must remove a specified thermal load while maintaining acceptable coolant temperatures and avoiding excessive hydraulic losses. Increasing flow generally reduces coolant temperature rise for a fixed heat load, but it also increases velocity and pressure losses. The design task is therefore a thermal-hydraulic trade-off rather than simply maximising flow.

## 2. Objective
Build a transparent, parameter-driven model to investigate:
- coolant temperature rise for a specified thermal duty;
- flow velocity and Reynolds number;
- pressure losses through straight pipe and fittings;
- first-pass pump electrical input;
- a simplified heat-exchanger capacity screen;
- sensitivity to coolant flow rate.

## 3. Baseline case
The default demonstration case uses:
- Heat load: 30 kW
- Coolant inlet temperature: 25 °C
- Flow rate: 60 L/min
- Pipe internal diameter: 32 mm
- Equivalent straight length: 25 m
- Aggregate fitting coefficient: 12
- Pump efficiency: 65%
- Water-like fluid properties at a representative condition

These are illustrative assumptions selected for demonstration, not manufacturer specifications or a recommended design point.

## 4. Method
The heat balance is calculated using Q = m_dot cp ΔT. Flow velocity is determined from volumetric flow and pipe cross-sectional area. Reynolds number identifies the flow regime. The Darcy-Weisbach equation estimates straight-pipe loss, while a lumped K coefficient estimates fitting losses. The pump input is estimated by dividing hydraulic power by assumed efficiency.

The heat-exchanger tab uses a simplified UA/LMTD screening approach. It should not be interpreted as a detailed heat-exchanger rating because terminal temperatures and stream capacity rates are not solved as a coupled counter-current exchanger model.

## 5. Engineering interpretation
For a fixed heat load, increasing mass flow reduces coolant temperature rise. However, higher velocity increases dynamic pressure and usually increases hydraulic losses. This raises the estimated pump input. A practical design seeks an acceptable compromise among thermal margin, pressure loss, pump energy, component limits, controllability and cost.

## 6. Validation plan
1. Independently hand-calculate the baseline mass flow, velocity, Reynolds number and energy-balance temperature rise.
2. Check the friction-factor and pressure-loss implementation against a worked Darcy-Weisbach reference case.
3. Replace assumed ΣK with a component-by-component fitting schedule.
4. Add actual pump head-flow and efficiency curves and solve the system operating point.
5. Replace the simplified heat-exchanger screen with effectiveness-NTU or manufacturer-rating calculations.
6. Conduct a controlled test-loop experiment with calibrated flow, pressure and temperature sensors before reporting measured performance.

## 7. Limitations
The model is steady-state, single-phase and incompressible. Fluid properties are constant. It does not include elevation changes, parallel branches, transient warm-up, heat loss to ambient, pump curves, cavitation/NPSH, control-valve behaviour, fouling, detailed heat-exchanger geometry or uncertainty propagation. It is a learning and screening tool only.

## 8. Further development
- Pump/system curve intersection and NPSH screening
- Effectiveness-NTU heat-exchanger model
- Coolant property selection and temperature-dependent properties
- Branch network pressure balancing
- Sensor uncertainty and alarm thresholds
- Experimental validation using a benchtop loop
