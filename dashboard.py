# Run 'streamlit run dashboard.py' after activating .venv to start the dashboard
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import altair as alt

SIMULATION_DELAY = 0.1  # seconds between play step renders

# 1. Load predicted and actual data from CSV files
pred_df = pd.read_csv('predicted.csv')
actual_df = pd.read_csv('actual.csv')
predicted = pred_df[pred_df.columns[-1]].to_numpy()
actual = actual_df[actual_df.columns[-1]].to_numpy()
dates = pd.to_datetime(pred_df['date'])

# Setup Streamlit Page
st.set_page_config(page_title='Silica Soft Sensor', layout='wide')
st.title('🏭 % Silica Concentrate - Soft Sensor Dashboard')
st.write("""
**Simulating real-time model inference on test data.** Sped up for demonstration convenience. Listed below are the controls:
* **▶️ Play:** Starts streaming the test timeline. The line chart draws all historical trends and the gauge displays what real-time ML % Silica predictions look like.
* **⏸️ Pause:** Freezes the simulation instantly at any moment so you can inspect anomalous spikes or specific data transitions.
* **🔄 Reset:** Restores the pipeline to its initial state (t=0) and clears the timeline canvas.
---""")

# Create Animation States
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'playing' not in st.session_state:
    st.session_state.playing = False

# Render Placeholders
plot_col, gauge_col = st.columns([2, 1])
with plot_col:
    plot_placeholder = st.empty()
with gauge_col:
    gauge_placeholder = st.empty()

# Render Control Buttons
caption_col, controls_col, _ = st.columns([1, 1, 1], gap='small')
caption_placeholder = caption_col.empty()
with controls_col:
    btn_play, btn_pause, btn_reset = st.columns([1, 1, 1], gap='medium')
    with btn_play:
        if st.button('▶️ Play', use_container_width=True):
            st.session_state.playing = True
    with btn_pause:
        if st.button('⏸️ Pause', use_container_width=True):
            st.session_state.playing = False
    with btn_reset:
        if st.button('🔄 Reset', use_container_width=True):
            st.session_state.step = 0
            st.session_state.playing = False
            st.rerun()

# Draw Plot with Altair (Altair does not flicker)
def draw_plot(step):
    chart_data = pd.DataFrame({
        'Date': dates[:step + 1],
        'Predicted': predicted[:step + 1],
        'Actual': actual[:step + 1]
    })
    chart_data = chart_data.melt(id_vars='Date', value_vars=['Predicted', 'Actual'], 
                                 var_name='Type', value_name='% Silica')
    chart = alt.Chart(chart_data, title='Predicted vs Actual % Silica Plot').mark_line().encode(
        x=alt.X('Date:T',
            title='Date',
            scale=alt.Scale(domain=[dates.iloc[0], dates.iloc[-1]]),
            axis=alt.Axis(format='%Y-%m-%d', grid=True)),
        y=alt.Y('% Silica:Q',
            title='% Silica',
            scale=alt.Scale(domain=[0, 6])),
        color=alt.Color('Type:N',
            scale=alt.Scale(domain=['Predicted', 'Actual'], range=['#1f77b4', '#ff7f0e']),
            legend=alt.Legend(title=None, orient='none', legendX=0, legendY=-15, direction='vertical'))
    ).properties(height=440)
    plot_placeholder.altair_chart(chart, use_container_width=True)

# Draw Plot with Plotly (Plotly flickers)
def draw_plot_2(step):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates[:step + 1],
        y=predicted[:step + 1],
        mode='lines',
        name='Predicted',
        line={'color': '#1f77b4'}
    ))
    fig.add_trace(go.Scatter(
        x=dates[:step + 1],
        y=actual[:step + 1],
        mode='lines',
        name='Actual',
        line={'color': '#ff7f0e'}
    ))
    fig.update_layout(
        title='Predicted vs Actual % Silica Plot',
        xaxis_title='Date',
        yaxis_title='% Silica',
        xaxis=dict(
            type='date',
            range=[dates.iloc[0], dates.iloc[-1]],
            tickformat='%Y-%m-%d',
            nticks=10,
            showgrid=False
        ),
        yaxis=dict(range=[0, 6]),
        legend=dict(yanchor='top', y=0.95, xanchor='left', x=0.02)
    )
    plot_placeholder.plotly_chart(fig, use_container_width=True)

# Draw Gauge with Plotly
def draw_gauge(value):
    number_color = _gauge_number_color(value)
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=value,
        number={'suffix': '%', 'font': {'color': number_color}},
        domain={'x': [0.03, 0.97], 'y': [0, 1]},
        title={'text': '% Silica Gauge'},
        gauge={
            'axis': {'range': [0, 6], 'tickwidth': 3, 'tickcolor': 'gray'},
            'bar': {'color': 'white'},
            'borderwidth': 3,
            'bordercolor': 'gray',
            'steps': [
                {'range': [0.0, 0.75], 'color': '#008a7b'},
                {'range': [0.75, 1.5], 'color': '#00a86b'},
                {'range': [1.5, 2.25], 'color': '#4cd137'},
                {'range': [2.25, 3.0], 'color': '#a4e433'},
                {'range': [3.0, 3.75], 'color': '#fcd116'},
                {'range': [3.75, 4.5], 'color': '#ff9f2a'},
                {'range': [4.5, 5.25], 'color': '#ff6f28'},
                {'range': [5.25, 6.0], 'color': '#ff3b30'},
            ]
        }
    ))
    fig.update_layout()
    gauge_placeholder.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}) # displayModeBar = floating toolbar

# Helper method for drawing Gauge
def _gauge_number_color(value):
    if value < 0.75: return '#008a7b'
    if value < 1.50: return '#00a86b'
    if value < 2.25: return '#4cd137'
    if value < 3.00: return '#a4e433'
    if value < 3.75: return '#fcd116'
    if value < 4.50: return '#ff9f2a'
    if value < 5.25: return '#ff6f28'
    return '#ff3b30'


# Main Render Loop
while True:
    draw_gauge(predicted[st.session_state.step])
    draw_plot(st.session_state.step)

    progress_pct = int((st.session_state.step + 1) / len(predicted) * 100)
    caption_placeholder.caption(f'Progress: {progress_pct}%', text_alignment="center")

    if st.session_state.playing and st.session_state.step < len(predicted) - 1:
        st.session_state.step += 1
        time.sleep(SIMULATION_DELAY)
        continue

    if st.session_state.step >= len(predicted) - 1:
        st.session_state.playing = False

    break
