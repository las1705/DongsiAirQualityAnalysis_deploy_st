import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st
import altair as alt
from urllib.error import URLError
from streamlit_option_menu import option_menu
sns.set(style='dark')

# ===========================================================================================================================
# Perhitungan Data ==========================================================================================================
# ===========================================================================================================================
# Breakpoint setiap polutan
breakpoints = {
    "PM2.5": [(0, 12, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150), 
              (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300), (250.5, 500.4, 301, 500)],
    "PM10": [(0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150), 
             (255, 354, 151, 200), (355, 424, 201, 300), (425, 604, 301, 500)],
    "SO2": [(0, 35, 0, 50), (36, 75, 51, 100), (76, 185, 101, 150), 
            (186, 304, 151, 200), (305, 604, 201, 300), (605, 1004, 301, 500)],
    "NO2": [(0, 53, 0, 50), (54, 100, 51, 100), (101, 360, 101, 150), 
            (361, 649, 151, 200), (650, 1249, 201, 300), (1250, 2049, 301, 500)],
    "CO": [(0, 4.4, 0, 50), (4.5, 9.4, 51, 100), (9.5, 12.4, 101, 150), 
           (12.5, 15.4, 151, 200), (15.5, 30.4, 201, 300), (30.5, 50.4, 301, 500)],
    "O3": [(0, 54, 0, 50), (55, 70, 51, 100), (71, 85, 101, 150), 
           (86, 105, 151, 200), (106, 200, 201, 300), (201, 604, 301, 500)],
} 
#Funct perhitungan AQI setiap polutan
def calculate_aqi(concentration, breakpoints): 
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= concentration <= c_high:
            return ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
    return None  # Jika di luar batas

# Funct menggilir perhitungan AQI setiap Polutan
def compute_aqi_and_dominant_pollutant(row): 
    aqi_values = {}
    for pollutant in breakpoints.keys(): # Menghitungan AQI setiap Polutan
        aqi = calculate_aqi(row[pollutant], breakpoints[pollutant])
        if aqi is not None:
            aqi_values[pollutant] = aqi

    if aqi_values:
        max_aqi_pollutant = max(aqi_values, key=aqi_values.get)  
        return pd.Series([aqi_values[max_aqi_pollutant], max_aqi_pollutant]) # Return nilai dan jenis Polutan dengan AQI tertinggi
    return pd.Series([None, None])

# Skema warna berdasarkan kategori kualitas udara
pollutant_ranges = {
    "PM25": [(0, 12, "Baik", "#00E400"), (12, 35, "Sedang", "#FFFF00"), (35, 55, "Tidak Sehat untuk Kelompok Sensitif", "#FF7E00"),
             (55, 150, "Tidak Sehat", "#FF0000"), (150, 250, "Sangat Tidak Sehat", "#8F3F97"), (250, float("inf"), "Berbahaya", "#7E0023")],
    
    "PM10": [(0, 54, "Baik", "#00E400"), (55, 154, "Sedang", "#FFFF00"), (155, 254, "Tidak Sehat untuk Kelompok Sensitif", "#FF7E00"),
             (255, 354, "Tidak Sehat", "#FF0000"), (355, 424, "Sangat Tidak Sehat", "#8F3F97"), (425, float("inf"), "Berbahaya", "#7E0023")],
    
    "SO2": [(0, 35, "Baik", "#00E400"), (36, 75, "Sedang", "#FFFF00"), (76, 185, "Tidak Sehat untuk Kelompok Sensitif", "#FF7E00"),
            (186, 304, "Tidak Sehat", "#FF0000"), (305, 604, "Sangat Tidak Sehat", "#8F3F97"), (605, float("inf"), "Berbahaya", "#7E0023")],
    
    "NO2": [(0, 53, "Baik", "#00E400"), (54, 100, "Sedang", "#FFFF00"), (101, 360, "Tidak Sehat untuk Kelompok Sensitif", "#FF7E00"),
            (361, 649, "Tidak Sehat", "#FF0000"), (650, 1249, "Sangat Tidak Sehat", "#8F3F97"), (1250, float("inf"), "Berbahaya", "#7E0023")],
    
    "CO": [(0, 4, "Baik", "#00E400"), (4, 9, "Sedang", "#FFFF00"), (9, 12, "Tidak Sehat untuk Kelompok Sensitif", "#FF7E00"),
           (12, 15, "Tidak Sehat", "#FF0000"), (15, 30, "Sangat Tidak Sehat", "#8F3F97"), (30, float("inf"), "Berbahaya", "#7E0023")],
    
    "O3": [(0, 54, "Baik", "#00E400"), (55, 70, "Sedang", "#FFFF00"), (71, 85, "Tidak Sehat untuk Kelompok Sensitif", "#FF7E00"),
           (86, 105, "Tidak Sehat", "#FF0000"), (106, 200, "Sangat Tidak Sehat", "#8F3F97"), (201, float("inf"), "Berbahaya", "#7E0023")],
    
    "AQI": [(0, 50, "Baik", "#00E400"), (51, 100, "Sedang", "#FFFF00"), (101, 150, "Tidak Sehat untuk Kelompok Sensitif", "#FF7E00"),
            (151, 200, "Tidak Sehat", "#FF0000"), (201, 300, "Sangat Tidak Sehat", "#8F3F97"), (301, float("inf"), "Berbahaya", "#7E0023")]
} 

# Derajat dari setiap arah mata angin
wind_directions = {
    "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5, "E": 90, "ESE": 112.5,
    "SE": 135, "SSE": 157.5, "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
    "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
} 
# ===========================================================================================================================
# Perhitungan Data ==========================================================================================================
# ===========================================================================================================================

# ===========================================================================================================================
# Persiapan Dataframe =======================================================================================================
# ===========================================================================================================================
# Dataframe polutan per jam
def create_aqi_hourly_df(all_df): 
    aqi_hourly_df = all_df[["year", "month", "day", "hour", "PM2.5", "PM10", "SO2", "NO2", "CO", "O3","wd"]]
    aqi_hourly_df[["AQI", "Dominant_Pollutant"]] = aqi_hourly_df.apply(compute_aqi_and_dominant_pollutant, axis=1)

    return aqi_hourly_df

# Dataframe polutan per hari
def create_aqi_daily_df(aqi_hourly_df): 
    aqi_daily_df = aqi_hourly_df.groupby(["year", "month", "day"]).agg({
        "PM2.5": "mean",
        "PM10": "mean",
        "SO2": "mean",
        "NO2": "mean",
        "CO": "mean",
        "O3": "mean",
        "AQI": "max", 
        "Dominant_Pollutant": lambda x: x.value_counts().idxmax(),
    })
    aqi_daily_df.reset_index(inplace=True)
    aqi_daily_df.rename(columns={"index": "date"}, inplace=True)

    # Menghitung kembali nilai AQI berdasarkan nilai mean setiap pollutan yang baru
    aqi_daily_df[["AQI", "Dominant_Pollutant"]] = aqi_daily_df.apply(compute_aqi_and_dominant_pollutant, axis=1)
    
    return aqi_daily_df

# Dataframe Polutan per bulan
def create_aqi_monthly_df(aqi_daily_df): 
    aqi_monthly_df = aqi_daily_df.groupby(["year", "month"]).agg({
        "PM2.5": "mean",
        "PM10": "mean",
        "SO2": "mean",
        "NO2": "mean",
        "CO": "mean",
        "O3": "mean",
        "AQI": "mean", # AQI dihitunga dengan rata-rata nilai AQI semua hari di bulan tersebut
    })

    # Ubah index (tanggal) menjadi kolom
    aqi_monthly_df.reset_index(inplace=True)
    aqi_monthly_df.rename(columns={"index": "date"}, inplace=True)

    return aqi_monthly_df

# Dataframe arah angin dengan polutan
def create_aqi_wind_df(aqi_hourly_df):
    aqi_wind_df = aqi_hourly_df.groupby("wd").agg({
        "PM2.5": "mean",
        "PM10": "mean",
        "SO2": "mean",
        "NO2": "mean",
        "CO": "mean",
        "O3": "mean",
        "AQI":"mean",
    })
    aqi_wind_df.reset_index(inplace=True)
    aqi_wind_df.rename(columns={"index": "wd"}, inplace=True)
    
    aqi_wind_df["wd_degree"] = aqi_wind_df["wd"].map(wind_directions)
    
    return aqi_wind_df
# ===========================================================================================================================
# Persiapan Dataframe =======================================================================================================
# ===========================================================================================================================

# ===========================================================================================================================
# Load Dataframe ============================================================================================================
# ===========================================================================================================================
all_df = pd.read_csv("Dongsi_PRSA_DF_Clean.csv") # Datafreme hasil wrangling data
aqi_hourly_df = create_aqi_hourly_df(all_df)
aqi_daily_df = create_aqi_daily_df(aqi_hourly_df)
aqi_monthly_df = create_aqi_monthly_df(aqi_daily_df)
aqi_wind_df = create_aqi_wind_df(aqi_hourly_df)
# ===========================================================================================================================
# Load Dataframe ============================================================================================================
# ===========================================================================================================================
# Fungsi untuk mendapatkan warna berdasarkan nilai polutan
def get_color(value, pollutant):
    for lower, upper, color in pollutant_ranges[pollutant]:
        if lower <= value <= upper:
            return color
    return "#000000"  # Default warna hitam jika tidak ada yang cocok (seharusnya tidak terjadi)

# nav side bar
with st.sidebar:
    selected = option_menu('Kualitas Udara Stasiun Dongsi',['Perubahan Kualitas Udara','Pengaruh Angin Terhadap Kualitas Udara'],default_index=0)
    
# Perubahan Kualitas Udara
if(selected=='Perubahan Kualitas Udara'):
    try:
        st.title("Perubahan Nilai Kualitas Udara Berdasarkan Waktu")
        col1, col2 = st.columns(2)
        
        aqi_daily_v_df = aqi_daily_df # menggunakan dataframe harian
        aqi_daily_v_df = aqi_daily_v_df.rename(columns={"PM2.5": "PM25"}) # mengganti nama kolom PM2.5 agar tidak terjadi error
        aqi_daily_v_df['date'] = pd.to_datetime(aqi_daily_v_df[['year', 'month', 'day']]) # menggabung kolom waktu menjadi satu dengan format datetime
        # aqi_daily_v_df.set_index("date", inplace=True)
        
        # Pilihan rentang waktu
        with col1:
            start_date = st.date_input("Start Date", aqi_daily_v_df["date"].min().date())
            end_date = st.date_input("End Date", aqi_daily_v_df["date"].max().date())
        # Pilihan jenis parameter
        with col2:
            selected_pollutant = st.selectbox("Pilih parameter kualitas udara:", 
                                              ["AQI", "PM25", "PM10", "SO2", "NO2", "CO", "O3"]
            )
    
        if start_date > end_date:
            st.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
        else:
            aqi_daily_v_df = aqi_daily_v_df[(aqi_daily_v_df["date"] >= pd.Timestamp(start_date)) & 
                         (aqi_daily_v_df["date"] <= pd.Timestamp(end_date))] # Rentang waktu
            
            # Tabel polutan dan kualitas udara
            st.subheader("Data Polutan")
            st.dataframe(
                aqi_daily_v_df[[
                    'date',
                    'AQI',
                    'PM25',
                    'PM10', 
                    'SO2',
                    'NO2',
                    'CO',
                    'O3'
                ]].
                rename(columns={
                    'AQI':'AQI',
                    'PM25':'PM2.5 (µg/m³)',
                    'PM10':'PM10 (µg/m³)',
                    'SO2':'SO2 (ppb)',
                    'NO2':'NO2 (ppb)',
                    'CO':'CO (ppm)',
                    'O3':'O3 (ppb)'}).
                sort_values(by='date'),
                hide_index=True
            )         
            
            # DataFrame untuk garis rentang bahaya
            hazard_lines = []
            for lower, upper, category, color in pollutant_ranges[selected_pollutant]:
                hazard_lines.append({"level": lower, "color": color, "keterangan": f"{category} ({lower}-{upper})"})

            hazard_df = pd.DataFrame(hazard_lines)

            # Layer 1: Garis rentang bahaya
            hazard_chart = alt.Chart(hazard_df).mark_rule(strokeWidth=2).encode(
                y="level:Q",
                color=alt.Color(
                    "color:N", 
                    scale=None, legend=
                    alt.Legend(
                        title="keterangan rentang",
                        orient="right",
                        labelFontSize=12,
                        titleFontSize=14 
                    )
                ),
                tooltip=["keterangan:N"]
            )

            # Layer 2: Garis Tren Data
            data_chart = alt.Chart(aqi_daily_v_df).mark_area(opacity=0.8).encode(
                x="date:T",
                y=alt.Y(f"{selected_pollutant}:Q", title=selected_pollutant),
                color=alt.value("#1f77b4"),
            )
            
            # Line Chart gabungan layer 1 + later 2
            final_chart = hazard_chart + data_chart
            st.altair_chart(final_chart, use_container_width=True)
            
            col1, col2 = st.columns([3,1])
            # Keteranan rentang bahaya
            with col1:
                st.markdown("Legenda Rentang Bahaya")
                for lower, upper, category, color in pollutant_ranges[selected_pollutant]:
                    st.markdown(
                        f"<div style='display: flex; align-items: center; margin-bottom: 5px;'>"
                        f"<div style='width: 20px; height: 20px; background-color: {color}; margin-right: 10px;'></div>"
                        f"<span>{lower} - {upper if upper != float('inf') else '>' + str(lower)}: {category}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
            # Analisis parameter
            with col2:
                max_value = aqi_daily_v_df[selected_pollutant].max()
                min_value = aqi_daily_v_df[selected_pollutant].min()
                mean_value = aqi_daily_v_df[selected_pollutant].mean()

                st.markdown(f"Statistik {selected_pollutant} dalam Rentang Waktu yang Dipilih")
                st.metric(f"📈 **Nilai Maksimum**", value = round(max_value, 1))
                st.metric(f"📊 **Nilai Rata-Rata**", value = round(mean_value, 1))
                st.metric(f"📉 **Nilai Minimum**", value = round(min_value, 1)    )
            
            # Dominan polutan
            pollutant_counts = aqi_daily_v_df["Dominant_Pollutant"].value_counts().reset_index() # Dataframe jumlah dominan polutan
            pollutant_counts.columns = ["Pollutant", "Count"]

            # Bar Chart dominan polutan
            bar_chart = alt.Chart(pollutant_counts).mark_bar().encode(
                x=alt.X("Pollutant:N", title="Polutan Dominan"),
                y=alt.Y("Count:Q", title="Jumlah Kemunculan"),
                color=alt.Color("Pollutant:N", scale=alt.Scale(scheme="category10")),
                tooltip=["Pollutant", "Count"]
            ).properties(
                title="Polutan yang Paling Sering Menjadi Breakpoint AQI"
            )
            st.altair_chart(bar_chart, use_container_width=True)
        
    except URLError as e:
        st.error(f"Koneksi internet diperlukan untuk memuat data. Error: {e.reason}")

    
if(selected=='Pengaruh Angin Terhadap Kualitas Udara'):

    # Pilihan parameter polutan
    pollutant_options = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3", "AQI"]
    selected_pollutant_w = st.selectbox("Pilih Parameter Polutan", pollutant_options)

    # Hitung rata-rata polutan berdasarkan arah angin
    pollutant_by_wind = aqi_wind_df.groupby("wd_degree")[selected_pollutant_w].mean().reset_index()

    # Konversi ke bentuk array untuk circular bar chart
    angles = np.radians(pollutant_by_wind["wd_degree"])
    values = pollutant_by_wind[selected_pollutant_w]

    # Normalisasi panjang batang agar proporsional dalam grafik
    values_scaled = values / max(values) * 0.8  # Skala agar tidak terlalu panjang

    # Circular bar chart
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"projection": "polar"})
    fig.patch.set_alpha(0) 
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1) 
    ax.set_facecolor("none") 
    # Warna berdasarkan tingkat polusi
    colors = plt.cm.viridis(values_scaled / max(values_scaled))
    # cmap = plt.get_cmap("RdYlGn_r")
    # norm = mcolors.Normalize(vmin=0, vmax=300)  # AQI rentang 0–300
    # colors=cmap(norm(aqi_values[i]))

    # Plot bar
    bars = ax.bar(angles, values_scaled, width=np.pi/10, bottom=0.2, color=colors, edgecolor="black", alpha=0.8)
    ax.set_xticks(np.radians(list(wind_directions.values()))) # label
    ax.set_xticklabels(list(wind_directions.keys()), fontsize=10, color="white")
    ax.grid(True, color="white", alpha=0.3, linestyle="dashed", linewidth=0.7)
    # ax.spines["polar"].set_visible(False)
    ax.set_title(f"Pengaruh Arah Angin terhadap {selected_pollutant_w}", color="white", fontsize=14)
    ax.tick_params(colors="white")

    # legenda skala polutan
    sm = plt.cm.ScalarMappable(cmap="plasma", norm=plt.Normalize(vmin=min(values), vmax=max(values)))
    cbar = fig.colorbar(sm, ax=ax, orientation="horizontal", pad=0.1)
    cbar.set_label(f"Konsentrasi {selected_pollutant_w}", color="white")
    cbar.ax.xaxis.label.set_color("white")
    cbar.ax.tick_params(colors="white")

    st.pyplot(fig)
    
