# 🌱 AgriSense AI
> **Next-Generation Climate-Aware Precision Irrigation & Agro-Advisory Platform**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Framework-Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Machine Learning-Scikit--Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Overview
**AgriSense AI** is an intelligent precision agriculture decision engine designed to solve the real-world challenge of water over-consumption and crop dehydration in modern farming.

Unlike traditional static ML scripts, AgriSense operates as an **integrated real-time decision platform**:
- Ingests **live meteorological telemetry** (temperature, humidity, wind velocity, and 7-day rainfall forecasts) via open satellite APIs for agricultural regions across India.
- Employs a **Universal Dynamic Pipeline Engine** that auto-detects schemas, column types, and targets for **any uploaded agricultural CSV** (with a verified baseline of 16,411 field samples).
- Predicts multi-tier crop water stress (Optimal, Moderate Deficit, Critical Dehydration) at **99.1% test accuracy**.
- Delivers **prescriptive agronomic guidance**: computes exact volumetric irrigation requirements ($m^3/\text{ha}$), rainfall offset advisories, and an interactive **Water & Electricity Cost Savings ROI Calculator**.

---

## 🌟 Key Features

### 1. 🌤️ Real-Time Climate Telemetry Ingestion
Synchronizes on-the-fly with the **Open-Meteo REST API** to retrieve live microclimate data across major agricultural hubs (*Punjab, Maharashtra, Karnataka, Gujarat, Tamil Nadu, Uttar Pradesh, etc.*) without needing proprietary hardware or API keys.

### 2. 🧠 Universal Dynamic Dataset Ingestion
- Upload **any agricultural CSV dataset** via the drag-and-drop sidebar.
- Automatically isolates target variables from numeric and categorical features.
- Dynamically generates custom UI sliders and dropdowns based on the uploaded file's schema.

### 3. 💧 Multi-Tier Crop Stress Classification & Volumetric Advisory
- **Level 0 (Optimal)**: Moisture levels are healthy; irrigation suspended to prevent root rot and conserve groundwater.
- **Level 1 (Moderate Deficit)**: Controlled irrigation scheduled to maintain physiological growth.
- **Level 2 (Critical Alert)**: High heat + low air humidity + depleted soil moisture; immediate intensive irrigation triggered to prevent permanent wilting.
- Outputs **exact volumetric requirements ($m^3/\text{hectare}$)** tailored to the crop and growth stage.

### 4. 📅 7-Day Rainfall & Crop Evapotranspiration ($ET_c$) Forecasting
Forecasts incoming natural precipitation against biological crop water consumption, advising farmers to scale back scheduled pumping if rain is imminent within 48 hours.

### 5. 💰 Farm Water & Energy Savings ROI Calculator
Allows farmers and agricultural officers to input land acreage and local electricity tariffs to project total litres of water conserved and pumping expenses saved.

---

## 🏗️ Architecture & Data Flow

```
                                  [ USER INPUT ]
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                             ▼
       [ Select Regional Geo-Hub ]                 [ Upload Any Dataset / Default ]
                   │                                             │
                   ▼                                             ▼
       [ weather_service.py ]                         [ dynamic_engine.py ]
    • Calls Open-Meteo REST API                    • Auto-detects target & schema
    • Fetches: Temp, Humidity, Rain                • Builds ColumnTransformer Pipeline
    • Fetches: 7-Day Rain Forecast                 • Trains RandomForest Ensemble (99.1% Acc)
                   │                                             │
                   └──────────────────────┬──────────────────────┘
                                          ▼
                                [ dashboard_app.py ]
                                  (Streamlit Web UI)
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
[ 1. Live Weather Feed ]       [ 2. Predictive AI Model ]       [ 3. Prescriptive Advisory ]
• Real-time temperature,       • Classifies stress levels        • Volumetric delivery (m³/ha)
  humidity & wind meters       • Confidence distributions        • Rain-offset recommendations
                                                                 • ROI savings calculator
```

---

## 📂 Project Structure

```bash
AgriSense/
├── data/
│   └── cropdata_updated.csv        # Integrated verified dataset (16,411 samples)
├── src/
│   ├── dashboard_app.py            # Streamlit interactive web dashboard
│   ├── dynamic_engine.py           # Universal ML training & inference pipeline
│   ├── weather_service.py          # Real-time Open-Meteo REST API connector
│   └── PROJECT_DOCUMENTATION.md    # In-depth technical architecture documentation
├── .gitignore                      # Git ignore rules
└── README.md                       # Project overview and setup guide
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/vjmohammedsafwan/AgriSense.git
cd AgriSense
```

### 2. Install Required Dependencies
Ensure you have Python 3.9+ installed, then run:
```bash
pip install streamlit scikit-learn pandas numpy plotly
```

### 3. Launch the Application
```bash
streamlit run src/dashboard_app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 📊 Dataset Overview
The integrated baseline dataset contains **16,411 field records** covering:
- **Crops**: Wheat, Potato, Carrot, Tomato, Chilli
- **Soil Types**: Black, Alluvial, Sandy, Red, Clay, Loam, Chalky
- **Growth Stages**: Germination, Seedling, Vegetative, Flowering, Pollination, Bulb/Fruit Formation, Maturation, Harvest
- **Environmental Parameters**: Soil Moisture Index (MOI: 1–100), Ambient Temperature (10–42°C), Relative Humidity (15–91%)
- **Target (`result`)**: 0 (Adequate), 1 (Irrigation Required), 2 (Critical Irrigation)

---

## 👥 Contributors & Acknowledgements
- Developed by **vjmohammedsafwan** and Team.
- Powered by open meteorological data from [Open-Meteo](https://open-meteo.com/).
