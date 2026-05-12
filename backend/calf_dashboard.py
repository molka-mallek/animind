"""
calf_dashboard.py — AniMind Real-Time Calf Monitoring Dashboard
================================================================
Run order:
  1. cd backend
  2. uvicorn main:app --reload --port 8000   (start FastAPI backend)
  3. streamlit run calf_dashboard.py          (start this dashboard)

Architecture:
  This file is the DISPLAY layer only.
  - Generates simulated accelerometer data (or receives real ESP32 data)
  - Sends raw accX/accY/accZ to FastAPI /predict-calf endpoint
  - FastAPI runs feature engineering + model inference (in ai_pipeline.py)
  - This file reads the prediction and renders the dashboard

Do NOT:
  - Load model files in this file
  - Call model.predict() in this file
  - Import from ai_pipeline.py in this file
  - Reimplement feature engineering here

All inference logic lives in backend/modules/calf_behavior/ai_pipeline.py
"""

import streamlit as st
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS — copied exactly from the Kaggle notebook
# ══════════════════════════════════════════════════════════════════════════════

CALVES       = ['calf_1', 'calf_2', 'calf_3', 'calf_4', 'calf_5', 'calf_6']
CLASSES      = ['lying', 'standing', 'eating_drinking', 'active', 'social', 'abnormal']
NUM_CLASSES  = 6
WINDOW_SIZE  = 100    # 4 seconds at 25 Hz
SAMPLING_HZ  = 25
FEATURE_COLS = ['accX', 'accY', 'accZ', 'magnitude', 'ODBA', 'VeDBA', 'pitch', 'roll']

CLASS_EMOJI = {
    'lying':           '😴',
    'standing':        '🧍',
    'eating_drinking': '🍼',
    'active':          '🏃',
    'social':          '🤝',
    'abnormal':        '⚠️',
}

CLASS_COLORS = {
    'lying':           '#3498db',
    'standing':        '#2ecc71',
    'eating_drinking': '#f39c12',
    'active':          '#e74c3c',
    'social':          '#9b59b6',
    'abnormal':        '#e67e22',
}

# Alert thresholds matching the notebook's app logic
ABNORMAL_CONF_THRESHOLD = 0.60   # fire alert only above this
LYING_STREAK_ALERT      = 360    # windows = 6 hours (360 × 4s = 1440s)

BACKEND_URL = "http://localhost:8000"

# ══════════════════════════════════════════════════════════════════════════════
# SIMULATED SENSOR — exact Gaussian profiles per behaviour
# ══════════════════════════════════════════════════════════════════════════════

PROFILES = {
    'lying':           {'mean': [0.95, -0.10,  0.05], 'std': [0.04, 0.03, 0.03]},
    'standing':        {'mean': [0.80, -0.12,  0.10], 'std': [0.06, 0.05, 0.05]},
    'eating_drinking': {'mean': [0.60, -0.25,  0.15], 'std': [0.12, 0.10, 0.09]},
    'active':          {'mean': [0.50, -0.10,  0.10], 'std': [0.30, 0.28, 0.25]},
    'social':          {'mean': [0.75, -0.15,  0.12], 'std': [0.18, 0.13, 0.11]},
    'abnormal':        {'mean': [0.70, -0.20,  0.08], 'std': [0.22, 0.20, 0.17]},
}

def generate_reading(behaviour: str):
    """Generate a single accelerometer reading (one sample at 25 Hz)."""
    p = PROFILES[behaviour]
    accX = float(np.random.normal(p['mean'][0], p['std'][0]))
    accY = float(np.random.normal(p['mean'][1], p['std'][1]))
    accZ = float(np.random.normal(p['mean'][2], p['std'][2]))
    return accX, accY, accZ

# ══════════════════════════════════════════════════════════════════════════════
# BACKEND COMMUNICATION
# ══════════════════════════════════════════════════════════════════════════════

def check_backend_health():
    """Check if backend is online."""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=1)
        return response.status_code == 200
    except:
        return False

def call_predict(calf_id: str, accX: float, accY: float, accZ: float):
    """
    Send single accelerometer reading to FastAPI backend.
    Backend maintains the 100-sample buffer internally.
    Returns result dict or None if backend is unreachable.
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/predict-calf",
            json={"id": calf_id, "accX": accX, "accY": accY, "accZ": accZ},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.sidebar.error(f"System error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.sidebar.error("System offline — please contact support")
    except requests.exceptions.Timeout:
        st.sidebar.warning("System busy — please wait")
    return None

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title='AniMind — Calf Monitoring',
    page_icon='🐄',
    layout='wide'
)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════

for calf in CALVES:
    if f'{calf}_history' not in st.session_state:
        st.session_state[f'{calf}_history'] = []
    if f'{calf}_lying_streak' not in st.session_state:
        st.session_state[f'{calf}_lying_streak'] = 0
    if f'{calf}_abnormal_count' not in st.session_state:
        st.session_state[f'{calf}_abnormal_count'] = 0
    if f'{calf}_accX' not in st.session_state:
        st.session_state[f'{calf}_accX'] = [0.0] * 50
        st.session_state[f'{calf}_accY'] = [0.0] * 50
        st.session_state[f'{calf}_accZ'] = [0.0] * 50
    if f'{calf}_last_result' not in st.session_state:
        st.session_state[f'{calf}_last_result'] = None
    if f'{calf}_alerts' not in st.session_state:
        st.session_state[f'{calf}_alerts'] = []

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

st.sidebar.title("🐄 AniMind")
st.sidebar.caption("Real-Time Calf Monitoring")

# Simulation controls
simulate_sensor = st.sidebar.toggle("Demo mode", value=True)

if simulate_sensor:
    simulated_behaviour = st.sidebar.selectbox(
        "Demo behavior",
        CLASSES,
        help="Choose a behavior to simulate"
    )
else:
    simulated_behaviour = None
    st.sidebar.info("Live sensor mode — waiting for real data")

# Calf selection
selected_calf = st.sidebar.selectbox("Select calf", CALVES)

st.sidebar.markdown("---")

# Backend status
backend_online = check_backend_health()
if backend_online:
    st.sidebar.markdown("🟢 **System online**")
else:
    st.sidebar.markdown("🔴 **System offline**")
    st.sidebar.error("Please contact technical support")

# ══════════════════════════════════════════════════════════════════════════════
# TOP METRICS ROW
# ══════════════════════════════════════════════════════════════════════════════

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Active calves", len(CALVES))

with col2:
    total_alerts = sum(st.session_state[f'{c}_abnormal_count'] for c in CALVES)
    st.metric("Alerts today", total_alerts)

with col3:
    last_result = st.session_state[f'{selected_calf}_last_result']
    if last_result and last_result.get('status') == 'success':
        conf = last_result['result']['confidence']
        st.metric("Certainty", f"{conf:.0%}")
    else:
        st.metric("Certainty", "—")

with col4:
    lying_streak = st.session_state[f'{selected_calf}_lying_streak']
    lying_hours = lying_streak * 4 / 3600
    st.metric("Lying streak", f"{lying_hours:.1f}h")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA — TWO COLUMNS
# ══════════════════════════════════════════════════════════════════════════════

left_col, right_col = st.columns([0.6, 0.4])

# ──────────────────────────────────────────────────────────────────────────────
# LEFT COLUMN
# ──────────────────────────────────────────────────────────────────────────────

with left_col:
    # Live sensor stream
    st.markdown(f"### 📡 Live sensor stream — {selected_calf.replace('_', ' ').title()}")
    
    chart_data = pd.DataFrame({
        'accX': st.session_state[f'{selected_calf}_accX'],
        'accY': st.session_state[f'{selected_calf}_accY'],
        'accZ': st.session_state[f'{selected_calf}_accZ'],
    })
    
    st.line_chart(chart_data, color=['#e74c3c', '#2ecc71', '#3498db'], height=200)
    
    # Activity timeline
    st.markdown("### 📊 Activity timeline — today")
    
    history = st.session_state[f'{selected_calf}_history']
    
    if history:
        # Count occurrences of each class
        class_counts = {cls: 0 for cls in CLASSES}
        for entry in history:
            cls = entry['class']
            if cls in class_counts:
                class_counts[cls] += 1
        
        total = sum(class_counts.values())
        class_percentages = {cls: (count / total * 100) if total > 0 else 0 
                           for cls, count in class_counts.items()}
    else:
        # Placeholder values
        class_percentages = {cls: 100 / NUM_CLASSES for cls in CLASSES}
    
    # Create stacked horizontal bar
    fig, ax = plt.subplots(figsize=(10, 1))
    
    left = 0
    for cls in CLASSES:
        width = class_percentages[cls]
        ax.barh(0, width, left=left, color=CLASS_COLORS[cls], height=0.5)
        left += width
    
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 0.5)
    ax.axis('off')
    
    st.pyplot(fig, use_container_width=True)
    
    # Legend row
    legend_cols = st.columns(NUM_CLASSES)
    for i, cls in enumerate(CLASSES):
        with legend_cols[i]:
            st.markdown(
                f"<span style='color:{CLASS_COLORS[cls]}'>●</span> {cls.replace('_', ' ')}",
                unsafe_allow_html=True
            )
    
    # Stat cards
    s1, s2 = st.columns(2)
    
    with s1:
        lying_count = sum(1 for entry in history if entry['class'] == 'lying')
        lying_hours_total = lying_count * 4 / 3600
        st.metric("🛏️ Lying today", f"{lying_hours_total:.1f}h")
    
    with s2:
        abnormal_count = st.session_state[f'{selected_calf}_abnormal_count']
        st.metric("⚠️ Abnormal events", abnormal_count)

# ──────────────────────────────────────────────────────────────────────────────
# RIGHT COLUMN
# ──────────────────────────────────────────────────────────────────────────────

with right_col:
    # All calves status grid
    st.markdown("### 🐄 All calves")
    
    grid_cols = st.columns(3)
    
    for idx, calf in enumerate(CALVES):
        with grid_cols[idx % 3]:
            last_res = st.session_state[f'{calf}_last_result']
            
            if last_res and last_res.get('status') == 'success':
                behavior = last_res['result']['behavior']
                emoji = CLASS_EMOJI.get(behavior, '❓')
                color = CLASS_COLORS.get(behavior, '#95a5a6')
                display_text = f"{emoji} {behavior.replace('_', ' ')}"
            else:
                display_text = "❓ unknown"
                color = '#95a5a6'
            
            # Highlight selected calf
            if calf == selected_calf:
                st.success(f"**{calf.replace('_', ' ').title()}**\n\n{display_text}")
            else:
                st.markdown(
                    f"<div style='padding:10px; border:1px solid #ddd; border-radius:5px;'>"
                    f"<strong>{calf.replace('_', ' ').title()}</strong><br>"
                    f"<span style='color:{color}'>{display_text}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
    
    st.markdown("---")
    
    # Current behaviour card
    st.markdown(f"### Current behaviour — {selected_calf.replace('_', ' ').title()}")
    
    result = st.session_state[f'{selected_calf}_last_result']
    
    if result and result.get('status') == 'warming_up':
        progress = result.get('progress', 0)
        required = result.get('required', WINDOW_SIZE)
        st.info(f"⏳ Starting up — collecting initial data")
        st.progress(progress / required, text=f"Loading... ({progress}/{required})")
    
    elif result and result.get('status') == 'success':
        res_data = result['result']
        cls = res_data['behavior']
        conf = res_data['confidence']
        emoji = CLASS_EMOJI.get(cls, '❓')
        
        # Large emoji + class name
        st.markdown(f"## {emoji} {cls.replace('_', ' ').title()}")
        
        # Confidence bar
        st.progress(conf)
        st.caption(f"Certainty: {conf:.0%}")
        
        # Probability breakdown
        if res_data.get('probabilities'):
            st.markdown("**Behavior likelihood**")
            for cls_name in CLASSES:
                prob = res_data['probabilities'].get(cls_name, 0)
                # Only show progress bar, no percentage text
                st.progress(prob, text=cls_name.replace('_', ' ').title())
        
        # Alert section — read from backend response
        if res_data.get('alert'):
            alert_type = res_data.get('alert_type', 'unknown')
            if alert_type == 'instability':
                st.error(f"⚠️ Behavior instability detected — {selected_calf}")
            elif alert_type not in ['low_confidence']:
                st.error(f"⚠️ Alert: {alert_type}")
        
        # Event detection
        if res_data.get('event') and res_data['event'].get('type') != 'none':
            event_type = res_data['event']['type']
            duration = res_data['event']['duration']
            duration_seconds = duration * 4  # Convert windows to seconds
            st.info(f"📌 Event: {event_type.replace('_', ' ').title()} ({duration_seconds}s)")
        
        # Lying streak alert
        lying_streak = st.session_state[f'{selected_calf}_lying_streak']
        if lying_streak > LYING_STREAK_ALERT:
            hours = round(lying_streak * 4 / 3600, 1)
            st.warning(
                f"🛏️ {selected_calf.replace('_', ' ').title()} has been lying "
                f"for {hours}h — check health"
            )
    
    else:
        st.info("Waiting for data…")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN INFERENCE LOOP
# ══════════════════════════════════════════════════════════════════════════════

if simulate_sensor and backend_online:
    # ── 1. Generate simulated reading ──────────────────────────────────────────
    accX, accY, accZ = generate_reading(simulated_behaviour)
    
    # ── 2. Update rolling chart buffer (last 50 points) ───────────────────────
    st.session_state[f'{selected_calf}_accX'].append(accX)
    st.session_state[f'{selected_calf}_accX'] = st.session_state[f'{selected_calf}_accX'][-50:]
    
    st.session_state[f'{selected_calf}_accY'].append(accY)
    st.session_state[f'{selected_calf}_accY'] = st.session_state[f'{selected_calf}_accY'][-50:]
    
    st.session_state[f'{selected_calf}_accZ'].append(accZ)
    st.session_state[f'{selected_calf}_accZ'] = st.session_state[f'{selected_calf}_accZ'][-50:]
    
    # ── 3. Call backend ────────────────────────────────────────────────────────
    result = call_predict(selected_calf, accX, accY, accZ)
    
    # ── 4. Process result ──────────────────────────────────────────────────────
    if result:
        st.session_state[f'{selected_calf}_last_result'] = result
        
        if result.get('status') == 'success':
            res_data = result['result']
            cls_name = res_data['behavior']
            conf = res_data['confidence']
            
            # Append to history
            st.session_state[f'{selected_calf}_history'].append({
                'class': cls_name,
                'confidence': conf,
                'probs': res_data.get('probabilities', {}),
            })
            
            # Update lying streak counter
            if cls_name == 'lying':
                st.session_state[f'{selected_calf}_lying_streak'] += 1
            else:
                st.session_state[f'{selected_calf}_lying_streak'] = 0
            
            # Count abnormal events (based on backend alert)
            if res_data.get('alert'):
                st.session_state[f'{selected_calf}_abnormal_count'] += 1
                st.session_state[f'{selected_calf}_alerts'].append({
                    'time': time.strftime('%H:%M:%S'),
                    'class': cls_name,
                    'conf': conf,
                    'alert_type': res_data.get('alert_type', 'unknown'),
                })
    
    # ── 5. Wait then rerun ─────────────────────────────────────────────────────
    time.sleep(0.05)  # Faster sampling for demo (~20 Hz)
    st.rerun()
