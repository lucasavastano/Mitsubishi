import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium  # Using st_folium to render the map
import pandas as pd
import plotly.express as px
import numpy as np
import datetime

# ---------------------------
# Page configuration and custom CSS
st.set_page_config(
    page_title="Mitsubishi",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .stButton > button {
            transition: all 0.3s ease;
            border-radius: 8px;
        }
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        .sidebar .sidebar-content {
            background-image: linear-gradient(#2e7bcf, #2e7bcf);
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# Flotta: Map with 13 example heatpumps
def flotta():
    st.header("Flotta")
    # Example data for 13 heatpumps across Italy
    data = {
        "City": ["Rome", "Milan", "Naples", "Turin", "Palermo", "Bologna",
                 "Florence", "Genoa", "Bari", "Catania", "Verona", "Trieste", "Messina"],
        "Latitude": [41.9028, 45.4642, 40.8518, 45.0703, 38.1157, 44.4949,
                     43.7696, 44.4056, 41.1171, 37.5079, 45.4384, 45.6495, 38.1938],
        "Longitude": [12.4964, 9.1900, 14.2681, 7.6869, 13.3615, 11.3426,
                      11.2558, 8.9463, 16.8719, 15.0830, 10.9916, 13.7768, 15.5540],
        "Status": ["Active", "Maintenance", "Active", "Inactive", "Active",
                   "Active", "Maintenance", "Active", "Inactive", "Active", "Active", "Active", "Maintenance"]
    }
    fleet_data = pd.DataFrame(data)
    
    # Create a Folium map centered on Italy
    m = folium.Map(location=[41.87194, 12.56738], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for each heatpump
    for idx, row in fleet_data.iterrows():
        popup_text = f"{row['City']} - {row['Status']}"
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=popup_text,
            tooltip=row["City"]
        ).add_to(marker_cluster)
    
    st.subheader("Flotta Localization")
    st_folium(m, width=700, height=500)

# ---------------------------
# Analytics: Charts for Power Consumption, Temperatura and Anomaly Detection
def analytics():
    st.header("Analytics")
    
    # Device selection for Analytics
    devices = ["Rome", "Milan", "Naples", "Turin", "Palermo", "Bologna",
               "Florence", "Genoa", "Bari", "Catania", "Verona", "Trieste", "Messina"]
    device = st.selectbox("Select Device", devices)
    st.write(f"Analytics for device: {device}")
    device_seed = hash(device) % 2**32
    
    # Generate time series data for the past 24 hours using device-specific seeds
    np.random.seed(device_seed)
    time_range = pd.date_range(end=datetime.datetime.now(), periods=24, freq='h')
    
    # --- Power Consumption (kW) dummy data ---
    power_values = 10 + 2 * np.sin(np.linspace(0, 2*np.pi, 24)) + np.random.normal(scale=1, size=24)
    df_power = pd.DataFrame({
        "Time": time_range,
        "Power Consumption (kW)": power_values
    })
    
    # --- Temperatura (°C) dummy data ---
    np.random.seed(device_seed + 1)
    temp_mandata = 60 + np.random.normal(scale=2, size=24)
    temp_ritorno = 50 + np.random.normal(scale=2, size=24)
    df_temp = pd.DataFrame({
        "Time": time_range,
        "Temperatura di mandata": temp_mandata,
        "Temperatura di ritorno": temp_ritorno
    })
    df_temp_melt = df_temp.melt(id_vars="Time", var_name="Tipo", value_name="Temperatura (°C)")
    
    # --- Anomaly Detection (m/s) dummy data ---
    np.random.seed(device_seed + 2)
    anomaly_values = 3 + np.random.normal(scale=0.3, size=24)
    df_anomaly = pd.DataFrame({
        "Time": time_range,
        "Anomaly Detection (m/s)": anomaly_values
    })
    
    # --- Plotting ---
    st.subheader("Power Consumption (kW)")
    fig_power = px.line(df_power, x="Time", y="Power Consumption (kW)", title="Power Consumption (kW)")
    st.plotly_chart(fig_power, use_container_width=True)
    
    st.subheader("Temperatura (°C)")
    fig_temp = px.line(df_temp_melt, x="Time", y="Temperatura (°C)", color="Tipo", title="Temperatura (°C)")
    st.plotly_chart(fig_temp, use_container_width=True)
    
    st.subheader("Anomaly Detection (m/s)")
    fig_anomaly = px.line(df_anomaly, x="Time", y="Anomaly Detection (m/s)", title="Anomaly Detection (m/s)")
    st.plotly_chart(fig_anomaly, use_container_width=True)

# ---------------------------
# Utility: Generate dummy KPI data for a device
def get_device_kpi(device):
    # Seed the random generator using the device name for consistency
    np.random.seed(hash(device) % 2**32)
    total_hours = np.random.randint(1000, 5000)
    alerts = np.random.randint(0, 100)
    total_consumption = round(np.random.uniform(5000, 10000), 1)
    daily_consumption = round(np.random.uniform(100, 500), 1)
    weekly_consumption = round(np.random.uniform(700, 3500), 1)
    monthly_consumption = round(np.random.uniform(3000, 15000), 1)
    
    max_mandata = round(np.random.uniform(70, 80), 1)
    min_mandata = round(np.random.uniform(50, 60), 1)
    avg_mandata = round((max_mandata + min_mandata) / 2, 1)
    
    max_ritorno = round(np.random.uniform(60, 70), 1)
    min_ritorno = round(np.random.uniform(40, 50), 1)
    avg_ritorno = round((max_ritorno + min_ritorno) / 2, 1)
    
    return {
        "Total hours of work": total_hours,
        "Alerts": alerts,
        "Total consumption (kWh)": total_consumption,
        "Daily total consumption (kWh)": daily_consumption,
        "Weekly total consumption (kWh)": weekly_consumption,
        "Monthly total consumption (kWh)": monthly_consumption,
        "Max Temperatura di mandata": max_mandata,
        "Min Temperatura di mandata": min_mandata,
        "Avg Temperatura di mandata": avg_mandata,
        "Max Temperatura di ritorno": max_ritorno,
        "Min Temperatura di ritorno": min_ritorno,
        "Avg Temperatura di ritorno": avg_ritorno,
    }

# ---------------------------
# Report: Select a single device and view its KPIs
def report():
    st.header("Report")
    devices = ["Rome", "Milan", "Naples", "Turin", "Palermo", "Bologna",
               "Florence", "Genoa", "Bari", "Catania", "Verona", "Trieste", "Messina"]
    device = st.selectbox("Select Device", devices)
    st.write(f"### KPIs for {device}:")
    
    kpi = get_device_kpi(device)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total hours of work", kpi["Total hours of work"])
    col2.metric("Alerts", kpi["Alerts"])
    col3.metric("Total consumption (kWh)", kpi["Total consumption (kWh)"])
    
    col4, col5, col6 = st.columns(3)
    col4.metric("Daily total consumption (kWh)", kpi["Daily total consumption (kWh)"])
    col5.metric("Weekly total consumption (kWh)", kpi["Weekly total consumption (kWh)"])
    col6.metric("Monthly total consumption (kWh)", kpi["Monthly total consumption (kWh)"])
    
    st.write("### Temperatura di Mandata")
    col_mandata1, col_mandata2, col_mandata3 = st.columns(3)
    col_mandata1.metric("Max Temperatura di mandata (°C)", kpi["Max Temperatura di mandata"])
    col_mandata2.metric("Min Temperatura di mandata (°C)", kpi["Min Temperatura di mandata"])
    col_mandata3.metric("Avg Temperatura di mandata (°C)", kpi["Avg Temperatura di mandata"])
    
    st.write("### Temperatura di Ritorno")
    col_ritorno1, col_ritorno2, col_ritorno3 = st.columns(3)
    col_ritorno1.metric("Max Temperatura di ritorno (°C)", kpi["Max Temperatura di ritorno"])
    col_ritorno2.metric("Min Temperatura di ritorno (°C)", kpi["Min Temperatura di ritorno"])
    col_ritorno3.metric("Avg Temperatura di ritorno (°C)", kpi["Avg Temperatura di ritorno"])

# ---------------------------
# Main function with sidebar navigation
def main():
    st.sidebar.title("Mitsubishi - PDC Tracking")
    section = st.sidebar.radio("Select Section", ["Flotta", "Analytics", "Report"])
    
    st.write(f"Selected Section: {section}")  # Debug message
    
    if section == "Flotta":
        flotta()
    elif section == "Analytics":
        analytics()
    elif section == "Report":
        report()

if __name__ == "__main__":
    main()
