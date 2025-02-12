import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import numpy as np
import datetime
from PIL import Image

# Load Mitsubishi logo
# Ensure that "mitsubishi_logo2.png" is in the same folder as this script or update the path accordingly.
mitsubishi_logo = Image.open("mitsubishi_logo3.png")

# ---------------------------
# Page configuration and custom CSS
st.set_page_config(
    page_title="Mitsubishi",
    page_icon=mitsubishi_logo,  # Set Mitsubishi logo as the page icon
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        /* Button styling */
        .stButton > button {
            transition: all 0.3s ease;
            border-radius: 8px;
        }
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-image: linear-gradient(#2e7bcf, #1e5aa7);
            color: white;
            font-size: 16px;
        }
        /* Force images in the sidebar to have transparent background */
        .sidebar .sidebar-content img {
            background-color: transparent !important;
        }
        /* Summary Card: transparent background so it matches the dashboard */
        .summary-card {
            background-color: transparent;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        /* Force any iframe (e.g. the folium map) to take full width */
        iframe {
            width: 100% !important;
            max-width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# Flotta: Map with 13 example heatpumps
def flotta():
    st.header("Flotta")

    # ---------------------------
    # Create a DataFrame for 13 devices with coordinates.
    data = {
        "City": ["Rome", "Milan", "Naples", "Turin", "Palermo", "Bologna",
                 "Florence", "Genoa", "Bari", "Catania", "Verona", "Trieste", "Messina"],
        "Latitude": [41.9028, 45.4642, 40.8518, 45.0703, 38.1157, 44.4949,
                     43.7696, 44.4056, 41.1171, 37.5079, 45.4384, 45.6495, 38.1938],
        "Longitude": [12.4964, 9.1900, 14.2681, 7.6869, 13.3615, 11.3426,
                      11.2558, 8.9463, 16.8719, 15.0830, 10.9916, 13.7768, 15.5540]
    }
    fleet_data = pd.DataFrame(data)

    # ---------------------------
    # Assign one of the three main statuses to each device.
    # The statuses will be assigned in a repeating order.
    main_statuses = ["Disponibile", "Occupata", "Rientro da verificare"]
    fleet_data["MainStatus"] = [main_statuses[i % 3] for i in range(len(fleet_data))]

    # Randomly flag 3 devices as needing maintenance ("Manutenzione necessaria")
    fleet_data["Maintenance"] = False
    np.random.seed(42)  # Ensure reproducibility
    maintenance_indices = np.random.choice(fleet_data.index, 3, replace=False)
    fleet_data.loc[maintenance_indices, "Maintenance"] = True

    # ---------------------------
    # Create a Folium map centered on Italy.
    m = folium.Map(location=[41.87194, 17.89938], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(m)

    # Mapping of main status to colors (used for marker color)
    color_mapping = {
        "Disponibile": "green",
        "Occupata": "blue",
        "Rientro da verificare": "red"
    }

    # Add markers for each device.
    # The marker color is based on the main status.
    # If a device is flagged for maintenance, we change its icon (using a wrench).
    for idx, row in fleet_data.iterrows():
        color = color_mapping.get(row["MainStatus"], "gray")
        if row["Maintenance"]:
            popup_text = f"{row['City']} - {row['MainStatus']} (Manutenzione necessaria)"
            marker_icon = folium.Icon(color=color, icon="wrench", prefix="fa")
        else:
            popup_text = f"{row['City']} - {row['MainStatus']}"
            marker_icon = folium.Icon(color=color)
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=popup_text,
            tooltip=row["City"],
            icon=marker_icon
        ).add_to(marker_cluster)

    #st.subheader("Fleet Localization")
    st_folium(m, width=1400, height=500)

    # ---------------------------
    # Summary Metrics: Count devices per main status and maintenance flag.
    total_devices = len(fleet_data)
    disponibile_count = len(fleet_data[fleet_data["MainStatus"] == "Disponibile"])
    occupata_count = len(fleet_data[fleet_data["MainStatus"] == "Occupata"])
    rientro_count = len(fleet_data[fleet_data["MainStatus"] == "Rientro da verificare"])
    maintenance_count = len(fleet_data[fleet_data["Maintenance"]])

    st.write(f"### Parco Macchine: {total_devices}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Disponibile", disponibile_count)
    col2.metric("Occupata", occupata_count)
    col3.metric("Rientro da verificare", rientro_count)
    col4.metric("Manutenzione necessaria", maintenance_count)

# ---------------------------
# Analytics: Charts for Power Consumption, Temperatura and Anomaly Detection
def analytics():
    st.header("Analytics")
    
    # Device selection for Analytics
    devices = ["Rome", "Milan", "Naples", "Turin", "Palermo", "Bologna",
               "Florence", "Genoa", "Bari", "Catania", "Verona", "Trieste", "Messina"]
    device = st.selectbox("Select Device", devices)
    #st.write(f"Analytics for device: {device}")
    device_seed = hash(device) % 2**32
    
    # Date range selection
    date_range = st.date_input("Select Date Range", 
                               [datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()])
    
    # Generate time series data for the selected date range using device-specific seeds
    np.random.seed(device_seed)
    time_range = pd.date_range(start=date_range[0], end=date_range[1], freq='h')
    
    # --- Power Consumption (kW) dummy data ---
    power_values = 10 + 2 * np.sin(np.linspace(0, 2*np.pi, len(time_range))) + np.random.normal(scale=1, size=len(time_range))
    df_power = pd.DataFrame({
        "Time": time_range,
        "Power Consumption (kW)": power_values
    })
    
    # --- Temperatura (°C) dummy data ---
    np.random.seed(device_seed + 1)
    temp_mandata = 60 + np.random.normal(scale=2, size=len(time_range))
    temp_ritorno = 50 + np.random.normal(scale=2, size=len(time_range))
    df_temp = pd.DataFrame({
        "Time": time_range,
        "Temperatura di mandata": temp_mandata,
        "Temperatura di ritorno": temp_ritorno
    })
    df_temp_melt = df_temp.melt(id_vars="Time", var_name="Tipo", value_name="Temperatura (°C)")
    
    # --- Anomaly Detection (m/s) dummy data ---
    np.random.seed(device_seed + 2)
    anomaly_values = 3 + np.random.normal(scale=0.3, size=len(time_range))
    df_anomaly = pd.DataFrame({
        "Time": time_range,
        "Anomaly Detection (m/s)": anomaly_values
    })
    
    # --- Monthly Data Aggregation ---
    # Add a 'Month' column to each DataFrame
    df_power["Month"] = df_power["Time"].dt.to_period("M").astype(str)
    df_temp["Month"] = df_temp["Time"].dt.to_period("M").astype(str)
    df_anomaly["Month"] = df_anomaly["Time"].dt.to_period("M").astype(str)
    
    # Aggregate monthly data (using mean as an example aggregation)
    monthly_power = df_power.groupby("Month", as_index=False).agg({"Power Consumption (kW)": "mean"})
    monthly_temp = df_temp.groupby("Month", as_index=False).agg({
        "Temperatura di mandata": "mean",
        "Temperatura di ritorno": "mean"
    })
    monthly_anomaly = df_anomaly.groupby("Month", as_index=False).agg({"Anomaly Detection (m/s)": "mean"})
    
    # Merge the monthly aggregated data
    monthly_data = pd.merge(monthly_power, monthly_temp, on="Month", how="outer")
    monthly_data = pd.merge(monthly_data, monthly_anomaly, on="Month", how="outer")
    
    # Create a CSV from the monthly_data DataFrame
    csv_data = monthly_data.to_csv(index=False).encode('utf-8')
    
    # --- CSV Download Button ---
    st.download_button(
        label="Download Monthly Data CSV",
        data=csv_data,
        file_name="monthly_data.csv",
        mime="text/csv"
    )
    
    # --- Plotting ---
    st.subheader("Power Consumption (kWh)")
    fig_power = px.line(df_power, x="Time", y="Power Consumption (kW)", title="Power Consumption (kWh)")
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
    st.write(f"### {device}:")

    kpi = get_device_kpi(device)
    
    # Compute additional KPI values
    giorni_utilizzo = round(kpi["Total hours of work"] / 24, 1)  # Total days of usage
    ore_utilizzo = kpi["Total hours of work"]                     # Total hours of usage
    consumi_totali = kpi["Total consumption (kWh)"]               # Total consumption (kWh)
    alerts = kpi["Alerts"]

    if st.button("Generate PDF Report"):
        from fpdf import FPDF

        # Create a PDF instance and add a page
        pdf = FPDF()
        pdf.add_page()
        
        # Set title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Report for {device}", ln=True)
        pdf.ln(10)
        
        # Set content font
        pdf.set_font("Arial", "", 12)
        
        # Stato Generale Macchina
        pdf.cell(0, 10, "Stato Generale Macchina", ln=True)
        pdf.cell(0, 10, f"Giorni di utilizzo Totali: {giorni_utilizzo}", ln=True)
        pdf.cell(0, 10, f"Ore di utilizzo Totali: {ore_utilizzo}", ln=True)
        pdf.cell(0, 10, f"Consumi Totali: {consumi_totali} kWh", ln=True)
        pdf.cell(0, 10, f"Alert Totali: {alerts}", ln=True)
        pdf.ln(10)
        
        # Consumi Elettrici
        pdf.cell(0, 10, "Consumi Elettrici", ln=True)
        pdf.cell(0, 10, f"Consumi Totali Orari (kW): {kpi['Daily total consumption (kWh)']}", ln=True)
        pdf.cell(0, 10, f"Consumi Totali Giornalieri (kWh): {kpi['Daily total consumption (kWh)']}", ln=True)
        pdf.cell(0, 10, f"Consumi Totali Settimanali (kWh): {kpi['Weekly total consumption (kWh)']}", ln=True)
        pdf.cell(0, 10, f"Consumi Totali Mensili (kWh): {kpi['Monthly total consumption (kWh)']}", ln=True)
        pdf.ln(10)
        
        # Dati Ultimo Noleggio
        pdf.cell(0, 10, "Dati Ultimo Noleggio", ln=True)
        pdf.cell(0, 10, f"Giorni di utilizzo: {giorni_utilizzo}", ln=True)
        pdf.cell(0, 10, f"Ore di utilizzo: {ore_utilizzo}", ln=True)
        pdf.cell(0, 10, f"Consumi Totali (kWh): {consumi_totali} kWh", ln=True)
        pdf.cell(0, 10, f"Alerts: {alerts}", ln=True)
        pdf.ln(10)
        
        # Temperatura di Mandata
        pdf.cell(0, 10, "Temperatura di Mandata", ln=True)
        pdf.cell(0, 10, f"Max: {kpi['Max Temperatura di mandata']} °C", ln=True)
        pdf.cell(0, 10, f"Min: {kpi['Min Temperatura di mandata']} °C", ln=True)
        pdf.cell(0, 10, f"Avg: {kpi['Avg Temperatura di mandata']} °C", ln=True)
        pdf.ln(10)
        
        # Temperatura di Ritorno
        pdf.cell(0, 10, "Temperatura di Ritorno", ln=True)
        pdf.cell(0, 10, f"Max: {kpi['Max Temperatura di ritorno']} °C", ln=True)
        pdf.cell(0, 10, f"Min: {kpi['Min Temperatura di ritorno']} °C", ln=True)
        pdf.cell(0, 10, f"Avg: {kpi['Avg Temperatura di ritorno']} °C", ln=True)
        
        # Instead of using a BytesIO buffer, get the PDF as a string and encode it.
        pdf_data = pdf.output(dest="S").encode("latin-1")
        
        # Provide a download button for the PDF
        st.download_button(
            label="Download PDF Report",
            data=pdf_data,
            file_name=f"report_{device}.pdf",
            mime="application/pdf"
        )

    # Combined Summary Card: "Stato Generale Macchina" (left) and "Consumi Elettrici" (right)
    st.markdown(f"""
        <div class="summary-card" style="
                background-color: rgba(255, 255, 255, 0.08);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                display: flex;
                flex-wrap: wrap;
            ">
            <div style="flex: 1; min-width: 250px; padding-right: 20px; border-right: 1px solid rgba(255,255,255,0.3);">
                <h3>Stato Generale Macchina</h3>
                <p>Giorni di utilizzo Totali: <strong>{giorni_utilizzo}</strong></p>
                <p>Ore di utilizzo Totali: <strong>{ore_utilizzo}</strong></p>
                <p>Consumi Totali: <strong>{consumi_totali} kWh</strong></p>
                <p>Alert Totali: <strong>{alerts}</strong></p>
            </div>
            <div style="flex: 1; min-width: 250px; padding-left: 20px;">
                <h3>Consumi Elettrici</h3>
                <p>Consumi Totali Orari (kW): <strong>{kpi["Daily total consumption (kWh)"]}</strong></p>
                <p>Consumi Totali Giornalieri (kWh): <strong>{kpi["Daily total consumption (kWh)"]}</strong></p>
                <p>Consumi Totali Settimanali (kWh): <strong>{kpi["Weekly total consumption (kWh)"]}</strong></p>
                <p>Consumi Totali Mensili (kWh): <strong>{kpi["Monthly total consumption (kWh)"]}</strong></p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Combined Card for "Dati Ultimo Noleggio" and Temperature Metrics
    st.markdown(f"""
        <div class="summary-card" style="
                background-color: rgba(255, 255, 255, 0.08);
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            ">
            <h3>Dati Ultimo Noleggio</h3>
            <p>Giorni di utilizzo: <strong>{giorni_utilizzo}</strong></p>
            <p>Ore di utilizzo: <strong>{ore_utilizzo}</strong></p>
            <p>Consumi Totali (kWh): <strong>{consumi_totali} kWh</strong></p>
            <p>Alerts: <strong>{alerts}</strong></p>
            
        <div style="margin-top: 20px; display: flex; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 250px; padding-right: 20px; border-right: 1px solid rgba(255,255,255,0.3);">
                <h3>Temperatura di Mandata</h3>
                <p>Max: <strong>{kpi["Max Temperatura di mandata"]} °C</strong></p>
                <p>Min: <strong>{kpi["Min Temperatura di mandata"]} °C</strong></p>
                    <p>Avg: <strong>{kpi["Avg Temperatura di mandata"]} °C</strong></p>
            </div>
            <div style="flex: 1; min-width: 250px; padding-left: 20px;">
                <h3>Temperatura di Ritorno</h3>
                <p>Max: <strong>{kpi["Max Temperatura di ritorno"]} °C</strong></p>
                <p>Min: <strong>{kpi["Min Temperatura di ritorno"]} °C</strong></p>
                <p>Avg: <strong>{kpi["Avg Temperatura di ritorno"]} °C</strong></p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- PDF Report Generation Section ---
    


# ---------------------------
# Main function with sidebar navigation
def main():
    # Display the Mitsubishi logo at full width in the sidebar
    st.sidebar.image(mitsubishi_logo, use_container_width=True)
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
