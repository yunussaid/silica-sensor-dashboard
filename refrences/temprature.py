import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time

# 1. Page Configuration
st.set_page_config(page_title="Industrial Telemetry Simulation", layout="centered")
st.title("🌡️ Real-Time Temperature Monitoring")
st.write("Simulating a continuous 500-minute time-series stream.")

# 2. Generate 500 Minutes of Synthetic Temperature Data
@st.cache_data
def get_temperature_data():
    np.random.seed(42)
    # Generate 500 consecutive minutes starting from now
    times = pd.date_range(start=pd.Timestamp.now(), periods=500, freq='min')
    
    # Create a realistic drifting industrial temperature curve (random walk)
    base_temp = 75.0  # Starting target degrees Celsius
    drifts = np.random.normal(loc=0.0, scale=0.3, size=500)
    temperatures = base_temp + np.cumsum(drifts)
    
    return pd.DataFrame({"Timestamp": times, "Temperature": temperatures})

df = get_temperature_data()

# 3. Handle Animation Control States
if "anim_index" not in st.session_state:
    st.session_state.anim_index = 10  # Start with an initial historical window of 10 points
if "playing" not in st.session_state:
    st.session_state.playing = False

# 4. Continuous Fixed Placeholder for Chart Injection
chart_placeholder = st.empty()

# 5. Control Buttons Layout
# Using the 5-column trick to center-align the controls
pad_l, btn_play, btn_pause, btn_reset, pad_r = st.columns([1.5, 1, 1, 1, 1.5])

with btn_play:
    if st.button("▶️ Play", use_container_width=True):
        st.session_state.playing = True

with btn_pause:
    if st.button("⏸️ Pause", use_container_width=True):
        st.session_state.playing = False

with btn_reset:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.anim_index = 10
        st.session_state.playing = False
        st.rerun()

# 6. Main Rendering Loop
while True:
    idx = st.session_state.anim_index
    # Slice the historical data up to the current simulated minute
    current_slice = df.iloc[:idx]
    
    # Build a clean Plotly Line Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=current_slice["Timestamp"],
        y=current_slice["Temperature"],
        mode="lines",                 # Pure line, explicitly NO DOTS/MARKERS
        line=dict(color="#2ca02c", width=2),
        name="Process Temp"
    ))
    
    # Standard industrial layout configurations
    fig.update_layout(
        xaxis_title="Time Line (Minutes)",
        yaxis_title="Temperature (°C)",
        xaxis=dict(range=[df["Timestamp"].min(), df["Timestamp"].max()]), # Keep X-axis static so it doesn't jitter
        yaxis=dict(range=[df["Temperature"].min() - 2, df["Temperature"].max() + 2]),
        margin=dict(l=40, r=20, t=20, b=40),
        height=400,
        showlegend=False
    )
    
    # Render (or update) the figure directly inside the fixed placeholder block
    chart_placeholder.plotly_chart(fig, use_container_width=True)
    
    # Check if we should increment and advance the animation
    if st.session_state.playing and idx < len(df):
        st.session_state.anim_index += 1
        time.sleep(0.05)  # Controls animation speed (50ms interval between points)
    else:
        # Stop looping if we've reached the end or if the user hit Pause
        break