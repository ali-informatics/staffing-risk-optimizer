import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Staffing Risk Dashboard", layout="wide")
st.title("Healthcare Labor-Load Optimizer")

with st.sidebar:
    st.header("Operational Inputs")
    inflow = st.slider('Expected Daily Admissions', 0, 100, 50)
    discharges = st.slider('Expected Daily Discharges', 0, 100, 45)
    current_staff = st.slider('Total Staff on Duty', 5, 50, 15)
    st.divider()
    # Industrial Standard: 1 Nurse per 4 Patients (Adjustable)
    ratio_target = st.number_input("Target Patient-to-Staff Ratio", value=4)

@st.cache_data
def run_staffing_sim(inflow, discharges, variance_seed=42):
    np.random.seed(variance_seed)
    # Volatility: Real-world "Surges"
    noise = np.random.normal(0, 8, 7) 
    return [max(0, (inflow + n) - discharges) for n in noise]

daily_net = run_staffing_sim(inflow, discharges)

# Assuming a starting census of 40 patients
total_patients = np.cumsum(daily_net) + 40 
staff_capacity = current_staff * ratio_target

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Avg Patient Load", f"{int(np.mean(total_patients))}")

with col2:
    staff_needed = int(max(total_patients) / ratio_target)
    st.metric("Required Staff (Peak)", staff_needed)

with col3:
    gap = staff_needed - current_staff
    # Force the color logic: Red for shortage (gap > 0), Green for surplus/even
    if gap > 0:
        st.metric("Staffing Gap", gap, delta=-gap, delta_color="normal")
    else:
        st.metric("Staffing Gap", gap, delta=abs(gap), delta_color="normal")

# --- FIXED CHRONOLOGICAL CHART LOGIC ---
days_list = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

chart_data = pd.DataFrame({
    "Day": days_list,
    "Patient Demand": total_patients,
    "Current Staff Capacity": [staff_capacity] * 7
})

# Explicitly define 'Day' as a Categorical type with a fixed order to prevent alphabetical sorting
chart_data['Day'] = pd.Categorical(chart_data['Day'], categories=days_list, ordered=True)
chart_data = chart_data.sort_values("Day").set_index("Day")

st.subheader("Labor Stress Test: Demand vs. Capacity")
st.area_chart(chart_data)

if gap > 0:
    st.error(f"⚠️ **Risk Detected:** You are understaffed by {gap} personnel for peak demand. Suggested action: Authorize overtime or hire temporary staff.")
else:
    st.success("✅ **System Stable:** Current staffing levels meet the safety ratio for the projected week.")