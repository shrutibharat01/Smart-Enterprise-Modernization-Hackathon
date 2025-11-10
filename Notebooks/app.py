import streamlit as st
import pandas as pd
import pickle

# -----------------------------
# 🎯 App Title and Description
# -----------------------------
st.set_page_config(page_title="Vehicle Sales Prediction", page_icon="🚗", layout="centered")

st.title("🚗 Vehicle Sales Prediction App")
st.markdown("""
Enter the vehicle details below to predict its expected sales value.  
This model uses a trained **Random Forest Regressor** saved locally as a `.pkl` file.
""")

# -----------------------------
# 🔧 Load Local Pickle Model
# -----------------------------
@st.cache_resource
def load_model():
    model_path = "D:\Python\model.pkl"  # <- your local model file
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model

try:
    model = load_model()
except Exception as e:
    st.error(f"❌ Failed to load local model file: {e}")
    st.stop()

# -----------------------------
# 🧾 User Input Section
# -----------------------------
st.header("🔢 Input Features")

col1, col2 = st.columns(2)
with col1:
    price = st.number_input("Vehicle Price", min_value=0.0, format="%.2f", value=25000.0)
    mileage = st.number_input("Mileage (km/l)", min_value=0.0, format="%.2f", value=15.0)
    avg_odometer = st.number_input("Average Odometer Reading (km)", min_value=0.0, format="%.2f", value=20000.0)
with col2:
    engine_size = st.number_input("Engine Size (cc)", min_value=0.0, format="%.2f", value=1500.0)
    fault_count = st.number_input("Fault Count", min_value=0, format="%d", value=1)

# Convert input to DataFrame for model
input_data = pd.DataFrame([{
    "price": price,
    "engine_size": engine_size,
    "mileage": mileage,
    "fault_count": fault_count,
    "avg_odometer": avg_odometer
}])

# -----------------------------
# 🎛️ Buttons and Prediction Logic
# -----------------------------
col_pred, col_clear = st.columns([1, 1])

if col_pred.button("🔮 Predict Sales"):
    try:
        prediction = model.predict(input_data)
        st.success(f"### ✅ Predicted Sales: {prediction[0]:,.2f}")
    except Exception as e:
        st.error(f"Prediction failed: {e}")

if col_clear.button("🧹 Clear / Reset"):
    st.experimental_rerun()

# -----------------------------
# 📊 Optional Debug Info
# -----------------------------
with st.expander("🔍 View Input DataFrame"):
    st.write(input_data)
