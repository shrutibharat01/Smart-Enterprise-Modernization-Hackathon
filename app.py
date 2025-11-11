import streamlit as st
import pandas as pd
import numpy as np
import joblib, boto3, io, json
import plotly.graph_objects as go
import plotly.express as px

# -----------------------------
# 🎯 PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Car Sales Prediction Dashboard",
    page_icon="🚗",
    layout="wide"
)

st.markdown(
    "<h1 style='text-align:center;color:#1A5276;'>🚗 Smart Enterprise Car Sales Prediction</h1>",
    unsafe_allow_html=True,
)
st.write(
    "Welcome to the **Smart Enterprise Modernization Hackathon Demo App** — "
    "predict monthly car sales and visualize key business drivers."
)

# -----------------------------
# 🔐 LOAD MODEL & METRICS FROM S3
# -----------------------------
@st.cache_resource
def load_model_and_metrics():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=st.secrets["aws_access_key"],
        aws_secret_access_key=st.secrets["aws_secret_key"],
        region_name=st.secrets["aws_region"]
    )

    # Load model
    obj = s3.get_object(
        Bucket=st.secrets["s3_bucket"],
        Key=st.secrets["s3_model_path"]
    )
    model = joblib.load(io.BytesIO(obj["Body"].read()))

    # Load metrics
    metrics = {"rmse": 9000, "r2": 0.85}
    try:
        mobj = s3.get_object(
            Bucket=st.secrets["s3_bucket"],
            Key="ML_Model_Output_2/model_metrics.json"
        )
        metrics = json.loads(mobj["Body"].read())
    except Exception:
        st.warning("⚠️ Metrics file not found; using defaults.")

    return model, metrics


with st.spinner("Loading model & metrics from S3 …"):
    model, metrics = load_model_and_metrics()
st.success("✅ Model and metrics successfully loaded from AWS S3")
CONFIDENCE_INTERVAL = metrics.get("rmse", 9000)

# -----------------------------
# 🎛️ SIDEBAR USER INPUTS
# -----------------------------
st.sidebar.header("📋 Input Vehicle & Market Details")

vehicle_type = st.sidebar.selectbox("Vehicle Type", ["SUV", "Sedan", "Hatchback", "Truck"])
fuel_type = st.sidebar.selectbox("Fuel Type", ["Petrol", "Diesel", "Electric", "Hybrid"])
transmission = st.sidebar.selectbox("Transmission", ["Manual", "Automatic"])
engine_size = st.sidebar.number_input("Engine Size (CC)", 800, 5000, 1500, step=100)
mileage = st.sidebar.number_input("Mileage (km/l)", 5.0, 40.0, 15.0, step=0.5)
year = st.sidebar.slider("Manufacture Year", 2000, 2025, 2022)
region = st.sidebar.selectbox("Region", ["North", "South", "East", "West"])
marketing_spend = st.sidebar.number_input("Marketing Spend (₹ Lakhs)", 1.0, 100.0, 10.0, step=0.5)
previous_sales = st.sidebar.number_input("Previous Month Sales", 0, 10000, 2500, step=100)
competitor_discount = st.sidebar.number_input("Competitor Discount (%)", 0.0, 50.0, 10.0, step=1.0)

predict_button = st.sidebar.button("🔮 Predict Sales")

# -----------------------------
# 🚀 PREDICTION
# -----------------------------
if predict_button:
    st.divider()
    st.subheader("📈 Prediction Results")

    input_data = pd.DataFrame({
        "vehicle_type": [vehicle_type],
        "fuel_type": [fuel_type],
        "transmission": [transmission],
        "engine_size": [engine_size],
        "mileage": [mileage],
        "year": [year],
        "region": [region],
        "marketing_spend": [marketing_spend],
        "previous_sales": [previous_sales],
        "competitor_discount": [competitor_discount]
    })

    # Align columns with model
    if hasattr(model, "feature_names_in_"):
        exp_cols = list(model.feature_names_in_)
        for c in exp_cols:
            if c not in input_data.columns:
                input_data[c] = np.nan
        input_data = input_data[exp_cols]

    pred = model.predict(input_data)[0]
    lower, upper = max(pred - CONFIDENCE_INTERVAL, 0), pred + CONFIDENCE_INTERVAL

    # --- Central KPI gauge ---
    colA, colB, colC = st.columns([1, 2, 1])
    with colB:
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=pred,
                delta={'reference': (lower + upper) / 2, 'increasing': {'color': "#2E86C1"}},
                gauge={
                    'axis': {'range': [0, upper * 1.2]},
                    'bar': {'color': "#1F618D"},
                    'steps': [
                        {'range': [0, lower], 'color': "#AED6F1"},
                        {'range': [lower, upper], 'color': "#5DADE2"}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': upper}
                },
                title={'text': "Predicted Monthly Sales (₹)"}
            )
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown(
        f"<p style='text-align:center;font-size:20px;color:gray;'>Expected range: ₹{lower:,.0f} – ₹{upper:,.0f}</p>",
        unsafe_allow_html=True
    )

    # -----------------------------
    # 🌈 BUSINESS VISUALS
    # -----------------------------
    st.subheader("📊 Business Impact Simulations")

    # Marketing Spend & Discount Impact – dual axis line
    m_range = np.linspace(1, 100, 20)
    d_range = np.linspace(0, 50, 20)

    df = pd.DataFrame({
        "Marketing Spend (₹ Lakhs)": m_range,
        "Competitor Discount (%)": d_range
    })
    df["Predicted Sales"] = [
        model.predict(pd.DataFrame({
            "vehicle_type": [vehicle_type],
            "fuel_type": [fuel_type],
            "transmission": [transmission],
            "engine_size": [engine_size],
            "mileage": [mileage],
            "year": [year],
            "region": [region],
            "marketing_spend": [m],
            "previous_sales": [previous_sales],
            "competitor_discount": [d]
        }).reindex(columns=exp_cols, fill_value=np.nan))[0]
        for m, d in zip(m_range, d_range)
    ]

    fig_line = px.scatter_3d(
        df,
        x="Marketing Spend (₹ Lakhs)",
        y="Competitor Discount (%)",
        z="Predicted Sales",
        color="Predicted Sales",
        color_continuous_scale="Viridis",
        title="Predicted Sales vs Marketing Spend & Competitor Discount"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Heatmap for quick business overview
    st.markdown("### 🔥 Sales Sensitivity Heatmap")
    m_vals = np.linspace(5, 100, 10)
    d_vals = np.linspace(0, 50, 10)
    heat_data = np.zeros((len(m_vals), len(d_vals)))

    for i, m in enumerate(m_vals):
        for j, d in enumerate(d_vals):
            heat_data[i, j] = model.predict(pd.DataFrame({
                "vehicle_type": [vehicle_type],
                "fuel_type": [fuel_type],
                "transmission": [transmission],
                "engine_size": [engine_size],
                "mileage": [mileage],
                "year": [year],
                "region": [region],
                "marketing_spend": [m],
                "previous_sales": [previous_sales],
                "competitor_discount": [d]
            }).reindex(columns=exp_cols, fill_value=np.nan))[0]

    fig_heat = px.imshow(
        heat_data,
        x=[f"{d:.0f}%" for d in d_vals],
        y=[f"₹ {m:.0f} L" for m in m_vals],
        color_continuous_scale="Tealrose",
        labels=dict(x="Competitor Discount", y="Marketing Spend", color="Predicted Sales"),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

st.divider()
st.caption("Built with 💙 for the Smart Enterprise Modernization Hackathon | Powered by Streamlit & AWS S3")
