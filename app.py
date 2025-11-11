import streamlit as st
import pandas as pd
import numpy as np
import joblib
import boto3
import io
import json
import plotly.express as px

# -----------------------------
# 🎯 PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Car Sales Prediction Dashboard",
    page_icon="🚗",
    layout="centered"
)

st.title("🚗 Smart Enterprise Car Sales Prediction")
st.markdown(""" Welcome to the **Smart Enterprise Modernization Hackathon Demo App**.  
Predict future car sales using the trained Random Forest model from your Databricks ML pipeline.""")

# -----------------------------
# 🔐 LOAD MODEL & METRICS FROM S3
# -----------------------------
@st.cache_resource
def load_model_and_metrics():
    """Load ML model (.pkl) and metrics (JSON) from S3."""
    s3 = boto3.client(
        "s3",
        aws_access_key_id=st.secrets["aws_access_key"],
        aws_secret_access_key=st.secrets["aws_secret_key"],
        region_name=st.secrets["aws_region"]
    )

    # Load model
    model_obj = s3.get_object(
        Bucket=st.secrets["s3_bucket"],
        Key=st.secrets["s3_model_path"]
    )
    model_bytes = io.BytesIO(model_obj["Body"].read())
    model = joblib.load(model_bytes)

    # Load metrics JSON
    metrics = {"rmse": 9000, "mae": None, "r2": None}
    try:
        metrics_obj = s3.get_object(
            Bucket=st.secrets["s3_bucket"],
            Key="ML_Model_Output_2/model_metrics.json"
        )
        metrics = json.loads(metrics_obj["Body"].read())
        st.info(f"📊 Metrics loaded (RMSE: ₹{metrics['rmse']:,.0f}, R²: {metrics['r2']:.3f})")
    except Exception as e:
        st.warning(f"⚠️ Could not load metrics from S3. Using default RMSE = ₹{metrics['rmse']:,.0f}")
        print("Metrics load error:", e)

    return model, metrics


with st.spinner("Loading model & metrics from S3..."):
    model, metrics = load_model_and_metrics()

st.success("✅ Model and metrics successfully loaded from AWS S3")

CONFIDENCE_INTERVAL = metrics.get("rmse", 9000)

# -----------------------------
# 🧮 USER INPUT FORM
# -----------------------------
st.header("📋 Enter Vehicle & Market Details")

with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        vehicle_type = st.selectbox("Vehicle Type", ["SUV", "Sedan", "Hatchback", "Truck"])
        fuel_type = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Electric", "Hybrid"])
        transmission = st.selectbox("Transmission", ["Manual", "Automatic"])
        engine_size = st.number_input("Engine Size (in CC)", min_value=800, max_value=5000, value=1500, step=100)
        mileage = st.number_input("Mileage (km/l)", min_value=5.0, max_value=40.0, value=15.0, step=0.5)

    with col2:
        year = st.slider("Manufacture Year", 2000, 2025, 2022)
        region = st.selectbox("Region", ["North", "South", "East", "West"])
        marketing_spend = st.number_input("Marketing Spend (₹ Lakhs)", min_value=1.0, max_value=100.0, value=10.0, step=0.5)
        previous_sales = st.number_input("Previous Month Sales", min_value=0, max_value=10000, value=2500, step=100)
        competitor_discount = st.number_input("Competitor Discount (%)", min_value=0.0, max_value=50.0, value=10.0, step=1.0)

    submitted = st.form_submit_button("🔮 Predict Sales")

# -----------------------------
# 🚀 PREDICTION LOGIC
# -----------------------------
if submitted:
    st.divider()
    st.subheader("📈 Prediction Results")

    # Create dataframe for model input
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

    # Make prediction
    predicted_sales = model.predict(input_data)[0]

    # Confidence interval bounds
    lower_bound = max(predicted_sales - CONFIDENCE_INTERVAL, 0)
    upper_bound = predicted_sales + CONFIDENCE_INTERVAL

    # Display prediction
    st.markdown(
        f"""
        <div style='text-align:center; font-size:32px; font-weight:700; color:#2E86C1;'>
            🔮 Predicted Monthly Sales: ₹{predicted_sales:,.0f}
        </div>
        <div style='text-align:center; font-size:18px; color:gray;'>
            (Expected range: ₹{lower_bound:,.0f} - ₹{upper_bound:,.0f})
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -----------------------------
    # 📊 BUSINESS VISUALIZATIONS
    # -----------------------------

    # Chart 1: Marketing spend vs predicted sales
    st.markdown("### 📉 Impact of Marketing Spend on Predicted Sales")
    marketing_range = np.linspace(1, 100, 20)
    df_marketing = pd.DataFrame({
        "Marketing Spend (₹ Lakhs)": marketing_range,
        "Predicted Sales": [
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
                "competitor_discount": [competitor_discount]
            }))[0]
            for m in marketing_range
        ]
    })

    fig1 = px.line(
        df_marketing,
        x="Marketing Spend (₹ Lakhs)",
        y="Predicted Sales",
        markers=True,
        template="plotly_white"
    )
    fig1.update_traces(line_color="#2E86C1")
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Competitor discount vs sales
    st.markdown("### 🏷️ Effect of Competitor Discounts on Sales")
    discount_range = np.linspace(0, 50, 15)
    df_discount = pd.DataFrame({
        "Competitor Discount (%)": discount_range,
        "Predicted Sales": [
            model.predict(pd.DataFrame({
                "vehicle_type": [vehicle_type],
                "fuel_type": [fuel_type],
                "transmission": [transmission],
                "engine_size": [engine_size],
                "mileage": [mileage],
                "year": [year],
                "region": [region],
                "marketing_spend": [marketing_spend],
                "previous_sales": [previous_sales],
                "competitor_discount": [d]
            }))[0]
            for d in discount_range
        ]
    })

    fig2 = px.bar(
        df_discount,
        x="Competitor Discount (%)",
        y="Predicted Sales",
        template="plotly_white",
        color="Predicted Sales",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 🧾 FOOTER
# -----------------------------
st.divider()
st.caption("Built with 💙 for the Smart Enterprise Modernization Hackathon | Powered by Streamlit & AWS S3")
