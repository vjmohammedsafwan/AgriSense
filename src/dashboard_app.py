import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import dynamic_engine
from weather_service import CITIES_GEO, fetch_live_weather

# Page Configuration
st.set_page_config(
    page_title="AgriSense AI - Adaptive Agro-Intelligence & Irrigation",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .status-badge-urgent {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 10px 18px;
        border-radius: 12px;
        font-weight: 700;
        border: 1px solid #f87171;
    }
    .status-badge-normal {
        background-color: #dcfce7;
        color: #15803d;
        padding: 10px 18px;
        border-radius: 12px;
        font-weight: 700;
        border: 1px solid #86efac;
    }
    .status-badge-moderate {
        background-color: #fef3c7;
        color: #b45309;
        padding: 10px 18px;
        border-radius: 12px;
        font-weight: 700;
        border: 1px solid #fcd34d;
    }
</style>
""", unsafe_allow_html=True)

# 1. Header Section
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("🌱 AgriSense AI")
    st.markdown("### Adaptive Precision Irrigation & Real-World Agro-Intelligence Engine")
    st.caption("Auto-Adapting ML Architecture with Live Atmospheric Telemetry Ingestion")

# 2. Sidebar: Dataset Ingestion (Universal / Any CSV)
st.sidebar.header("📁 Data Source & Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Any Agricultural CSV", type=["csv"], help="Upload any crop or sensor dataset. The system will auto-detect columns, schema, and target variables.")

# Cache the dataset and pipeline build
@st.cache_resource
def get_default_model():
    return dynamic_engine.load_default_pipeline()

if uploaded_file is not None:
    try:
        active_df = pd.read_csv(uploaded_file)
        st.sidebar.success(f"Uploaded: {len(active_df):,} rows")
        # Train dynamically on the newly uploaded dataset
        with st.spinner("Auto-detecting schema & training adaptive model..."):
            pipeline, meta = dynamic_engine.build_dynamic_pipeline(active_df)
    except Exception as e:
        st.sidebar.error(f"Error loading uploaded file: {e}")
        pipeline, meta, active_df = get_default_model()
else:
    pipeline, meta, active_df = get_default_model()
    st.sidebar.info("Using Integrated Agricultural Dataset (16,411 samples)")

with col_head2:
    st.metric("Model Test Accuracy", f"{meta['accuracy']*100:.1f}%", delta=f"{len(active_df):,} rows")

st.divider()

# Sidebar: Live Telemetry
st.sidebar.header("📍 Live Microclimate Telemetry")
selected_region = st.sidebar.selectbox("Region / Agro-Hub", list(CITIES_GEO.keys()))
weather_data = fetch_live_weather(selected_region)

live_temp = float(weather_data["temp"])
live_humidity = float(weather_data["humidity"])

# Sidebar: Dynamic Feature Controls
st.sidebar.header("🎛️ Field & Sensor Inputs")

user_inputs = {}

# Categorical Dropdowns
for cat_col in meta["categorical_cols"]:
    unique_vals = list(active_df[cat_col].dropna().unique())
    user_inputs[cat_col] = st.sidebar.selectbox(f"{cat_col}", unique_vals, index=0)

# Numeric Sliders
for num_col in meta["numeric_cols"]:
    col_min = float(active_df[num_col].min())
    col_max = float(active_df[num_col].max())
    col_mean = float(active_df[num_col].median())
    
    # Sensible defaults matching real sensor values
    if "temp" in num_col.lower():
        default_val = min(max(live_temp, col_min), col_max)
    elif "hum" in num_col.lower():
        default_val = min(max(live_humidity, col_min), col_max)
    elif "moi" in num_col.lower():
        default_val = 30.0 if col_max > 10 else 3.0
    else:
        default_val = col_mean

    step_val = 1.0 if col_max > 20 else 0.1
    user_inputs[num_col] = st.sidebar.slider(
        f"{num_col}",
        min_value=col_min,
        max_value=col_max,
        value=default_val,
        step=step_val
    )

# Two Clean Tabs (Removed Reviewer Defense tab as requested)
tab1, tab2 = st.tabs(["🚀 Real-Time Decision & Advisory", "📊 Data Intelligence & Feature Dynamics"])

with tab1:
    # Telemetry Strip
    st.subheader(f"🌤️ Live Atmospheric Stream: {selected_region}")
    w1, w2, w3, w4 = st.columns(4)
    w1.metric("Live Ambient Temp", f"{live_temp:.1f} °C")
    w2.metric("Live Air Humidity", f"{live_humidity:.0f} %")
    w3.metric("Live Rain", f"{weather_data['precipitation']} mm")
    w4.metric("Live Wind Speed", f"{weather_data['wind_speed']} km/h")

    st.markdown("---")

    # Run Prediction
    input_row = pd.DataFrame([user_inputs])
    pred_val = pipeline.predict(input_row)[0]
    
    # Check if probabilities are available
    has_proba = hasattr(pipeline.named_steps['classifier'], "predict_proba")
    if has_proba:
        probabilities = pipeline.predict_proba(input_row)[0]
    else:
        probabilities = [1.0]

    # Map output status
    # If standard 0, 1, 2 classes:
    # 0 = Adequate Moisture / No Irrigation
    # 1 = Irrigation Recommended (Deficit)
    # 2 = Urgent Critical Irrigation Required (Severe Dehydration)
    pred_str = str(pred_val)
    if pred_str == "0":
        status_badge = "<div class='status-badge-normal'><h3>✅ Adequate Moisture — No Irrigation Needed</h3></div>"
        adv_msg = "Soil and atmospheric moisture are in the optimal biological zone. Irrigating now would risk water-logging and root rot."
        water_rec = 0.0
    elif pred_str == "1":
        status_badge = "<div class='status-badge-moderate'><h3>⚠️ Irrigation Recommended (Moderate Deficit)</h3></div>"
        adv_msg = "Moisture deficit detected under current crop stage and thermal conditions. Apply standard controlled irrigation."
        water_rec = 25.0
    elif pred_str == "2":
        status_badge = "<div class='status-badge-urgent'><h3>🚨 CRITICAL: Urgent Irrigation Required</h3></div>"
        adv_msg = "Severe soil dehydration / high thermal evaporative stress detected! Immediate irrigation required to avoid permanent wilting."
        water_rec = 45.0
    else:
        status_badge = f"<div class='status-badge-moderate'><h3>Predicted Outcome: {pred_str}</h3></div>"
        adv_msg = f"Adaptive decision computed for predicted outcome {pred_str}."
        water_rec = 20.0

    rcol1, rcol2 = st.columns([3, 2])
    with rcol1:
        st.markdown("#### AI Agro-Advisory Output:")
        st.markdown(status_badge, unsafe_allow_html=True)
        st.write("")
        
        st.info(f"""
        **📋 Actionable Advisory:**
        - **{adv_msg}**
        - **Target Irrigation Volume:** **{water_rec:.1f} m³/hectare**
        - **7-Day Cumulative Rain Forecast:** **{sum(weather_data['daily_rain_forecast']):.1f} mm**
        {"*(Alert: Natural precipitation expected within 48h. Adjust scheduled volume accordingly.)*" if sum(weather_data['daily_rain_forecast']) > 8 else "*(Adhere to scheduled water delivery; no significant precipitation anticipated.)*"}
        """)

    with rcol2:
        if has_proba and len(probabilities) > 1:
            classes = pipeline.named_steps['classifier'].classes_
            class_labels = [f"Class {c}" for c in classes]
            colors = ['#22c55e', '#f59e0b', '#ef4444'][:len(classes)]
            fig_p = go.Figure(go.Bar(
                x=class_labels,
                y=probabilities * 100,
                marker_color=colors,
                text=[f"{p*100:.1f}%" for p in probabilities],
                textposition='auto'
            ))
            fig_p.update_layout(
                title="Model Confidence per State (%)",
                xaxis_title="Predicted State",
                yaxis_title="Probability (%)",
                height=260,
                margin=dict(l=10, r=10, t=35, b=10)
            )
            st.plotly_chart(fig_p, width='stretch')

    # 7-Day Rainfall and ETc Forecast
    st.subheader(f"📅 7-Day Weather & Evapotranspiration Balance ({selected_region})")
    
    current_temp_val = user_inputs.get("temp", live_temp)
    current_hum_val = user_inputs.get("humidity", live_humidity)
    
    f_df = pd.DataFrame({
        "Date": weather_data["daily_dates"],
        "Expected Rain (mm)": weather_data["daily_rain_forecast"],
        "Crop Evaporative Demand (ETc mm)": [round(float(current_temp_val) * 0.11 + (100 - float(current_hum_val)) * 0.03, 1)] * len(weather_data["daily_dates"])
    })
    
    fig_f = px.bar(f_df, x="Date", y=["Expected Rain (mm)", "Crop Evaporative Demand (ETc mm)"],
                   barmode="group",
                   color_discrete_sequence=["#3b82f6", "#f97316"])
    st.plotly_chart(fig_f, width='stretch')

    # ROI Cost & Water Savings Calculator
    st.markdown("### 💰 Smart Water & Energy Savings ROI Calculator")
    sc1, sc2, sc3 = st.columns(3)
    farm_size = sc1.number_input("Farm Area (Hectares)", min_value=0.5, max_value=500.0, value=5.0, step=0.5)
    elec_rate = sc2.number_input("Pumping Power Cost ($ or ₹ / kWh)", min_value=1.0, max_value=50.0, value=7.0, step=0.5)
    
    saved_litres = int(farm_size * 26000 * (1 if pred_str == "0" else (0.4 if pred_str == "1" else 0.15)))
    saved_cost = int(saved_litres * 0.00035 * elec_rate)
    
    sc3.metric("Projected Water Saved", f"{saved_litres:,} Litres")
    sc3.metric("Pumping Power Cost Saved", f"₹ {saved_cost:,}")

with tab2:
    st.subheader(f"📊 Dataset Intelligence ({len(active_df):,} Records)")
    
    c1, c2 = st.columns(2)
    with c1:
        if meta["categorical_cols"]:
            first_cat = meta["categorical_cols"][0]
            fig_cat = px.pie(active_df, names=first_cat, title=f"Distribution of {first_cat}", hole=0.35,
                             color_discrete_sequence=px.colors.qualitative.Prism)
            st.plotly_chart(fig_cat, width='stretch')
        else:
            st.write(active_df.head(10))

    with c2:
        if len(meta["numeric_cols"]) >= 2:
            n1 = meta["numeric_cols"][0]
            n2 = meta["numeric_cols"][1]
            sample_size = min(1000, len(active_df))
            fig_sc = px.scatter(active_df.sample(sample_size, random_state=42), x=n1, y=n2, color=meta['target_col'],
                                title=f"{n1} vs {n2} by {meta['target_col']} (Sample {sample_size})",
                                color_continuous_scale="Viridis")
            st.plotly_chart(fig_sc, width='stretch')

    # Top Features
    rf = pipeline.named_steps['classifier']
    pre = pipeline.named_steps['preprocessor']
    
    cat_names = []
    if meta['categorical_cols']:
        cat_names = pre.named_transformers_['cat'].get_feature_names_out(meta['categorical_cols']).tolist()
    
    feat_names = meta['numeric_cols'] + cat_names
    if hasattr(rf, "feature_importances_"):
        imps = rf.feature_importances_
        top_k = min(10, len(imps))
        top_idx = np.argsort(imps)[::-1][:top_k]
        top_f = [feat_names[i] for i in top_idx]
        top_v = [imps[i] for i in top_idx]

        fig_fi = px.bar(x=top_v[::-1], y=top_f[::-1], orientation='h',
                        title=f"Top {top_k} Features Driving the Model Predictions",
                        labels={'x': 'Relative Importance (Gini)', 'y': 'Feature Name'},
                        color=top_v[::-1], color_continuous_scale="Blues")
        st.plotly_chart(fig_fi, width='stretch')
