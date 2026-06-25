# Run 'streamlit run dashboard.py' after activating .venv to start the dashboard
# This URL: https://www.phdata.io/blog/how-to-use-the-gauge-chart-template/ has guage pointer
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time

SIMULATION_DELAY = 0.1  # seconds between play step renders

# 1. Load predicted and actual data from CSV files
pred_df = pd.read_csv('predicted.csv')
actual_df = pd.read_csv('actual.csv')
predicted = pred_df[pred_df.columns[-1]].to_numpy()
actual = actual_df[actual_df.columns[-1]].to_numpy()
dates = pd.to_datetime(pred_df['date'])

# 2. Setup Streamlit Page
st.set_page_config(page_title='Silica Soft Sensor', layout='wide')
st.title('🏭 % Silica Concentrate - Soft Sensor Dashboard')
st.write('Simulating real-time model inference on test data.')

# 3. Create Animation Control States
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'playing' not in st.session_state:
    st.session_state.playing = False

plot_col, gauge_col = st.columns([2, 1])
with plot_col:
    plot_placeholder = st.empty()
with gauge_col:
    gauge_placeholder = st.empty()

caption_col, controls_col, _ = st.columns([1, 1, 1], gap='small')
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

caption_placeholder = caption_col.empty()


def _gauge_number_color(value):
    if value < 0.75: return '#008a7b'
    if value < 1.50: return '#00a86b'
    if value < 2.25: return '#4cd137'
    if value < 3.00: return '#a4e433'
    if value < 3.75: return '#fcd116'
    if value < 4.50: return '#ff9f2a'
    if value < 5.25: return '#ff6f28'
    return '#ff3b30'

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
    gauge_placeholder.plotly_chart(fig, use_container_width=True)

def draw_plot(step):
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
