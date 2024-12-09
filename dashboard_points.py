import streamlit as st
import pandas as pd
import altair as alt
from api_utils import authenticate, list_data
from datetime import timedelta

def process_point_data(raw_data):
    date_values = []
    point_codes = []
    energy_values = []

    for entry in raw_data:
        date_val = entry.get("date")
        point_code = entry.get("point.code")
        energy_val = entry.get("value")

        if date_val is None:
            st.warning("Warning: Boş tarih verisi tespit edildi ve atlandı.")
        elif point_code is None:
            st.warning("Warning: Boş point code verisi tespit edildi ve atlandı.")
        elif energy_val is None:
            st.warning("Warning: Boş enerji verisi tespit edildi ve atlandı.")
        else:
            date_values.append(date_val)
            point_codes.append(point_code)
            energy_values.append(energy_val)

    data = {
        "date": date_values,
        "point": point_codes,
        "energy": energy_values,
    }
    df = pd.DataFrame(data)

    try:
        df["date"] = pd.to_datetime(df["date"], infer_datetime_format=True, errors="coerce")
    except ValueError as e:
        st.error(f"Tarih dönüştürme hatası: {e}")

    if df["date"].isnull().any():
        df["energy"] = pd.to_numeric(df["energy"], errors="coerce")

    return df

def show_points_dashboard():
    st.title("Enerji Tüketimi")

    connection_id = authenticate()
    if not connection_id:
        st.error("Kimlik doğrulama başarısız.")
        return

    with st.spinner("Veri getiriliyor..."):
        raw_data = list_data(connection_id)
    if not raw_data:
        st.error("Veri çekme işlemi başarısız.")
        return

    df = process_point_data(raw_data)

    if df.empty:
        st.error("Dönen veri seti boş.")
        return

    st.subheader("Enerji Tüketiminin Zaman İçinde Dağılımı")

    # Tarih aralığı seçimi
    start_date = st.date_input("Başlangıç Tarihi", df["date"].min())
    end_date = st.date_input("Bitiş Tarihi", df["date"].max())

    if start_date > end_date:
        st.error("Başlangıç tarihi bitiş tarihinden büyük olamaz.")
        return

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    filtered_df["year"] = filtered_df["date"].dt.year
    filtered_df["month"] = filtered_df["date"].dt.to_period("M")

    weekly_df = filtered_df.resample("W-Mon", on="date")["energy"].sum().reset_index().sort_values(by="date")

    weekly_bar_chart = alt.Chart(weekly_df).mark_bar(size=20).encode(
        x=alt.X("yearweek(date):T", title="Hafta"),
        y=alt.Y("energy:Q", title="Enerji Tüketimi"),
        tooltip=["date:T", "energy:Q"],
    ).properties(
        width=700,
        height=400,
    ).interactive()

    st.altair_chart(weekly_bar_chart, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)  

    with st.container():
        st.subheader("Enerji Tüketimi Detayları")
        icon_style = """
        <style>
        .metric-card {
            background: #ffffff;
            padding: 20px;
            border-radius: 10px;
            margin: 10px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .metric-title {
            font-size: 18px;
            color: #6b6b6b;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #000000;
        }
        .metric-icon {
            width: 32px;
            height: 32px;
        }
        .chart-card {
            background: none;
            padding: 0px;
            border-radius: 10px;
            margin: 10px;
            text-align: center;
            box-shadow: none;
        }
        </style>
        """
        st.markdown(icon_style, unsafe_allow_html=True)

        col1, _, col2 = st.columns([1, 0.1, 1])

        current_sum = filtered_df["energy"].sum()
        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div>
                        <img src="https://img.icons8.com/fluency/48/000000/electricity.png" class="metric-icon"/>
                    </div>
                    <div class="metric-title">Total Energy Consumption</div>
                    <div class="metric-value">{current_sum:.2f} kWh</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        weekly_average = weekly_df["energy"].mean()
        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div>
                        <img src="https://img.icons8.com/fluent/48/000000/calendar.png" class="metric-icon"/>
                    </div>
                    <div class="metric-title">Weekly Average</div>
                    <div class="metric-value">{weekly_average:.2f} kWh</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)  # Araya boşluk eklemek için

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader(f"{start_date.date()} ve {end_date.date()} arasındaki Aylara Göre Toplam Enerji Tüketimi")
    
    # Monthly energy consumption
    monthly_energy = filtered_df.groupby("month")["energy"].sum().reset_index()
    monthly_energy["month"] = monthly_energy["month"].astype(str)

    # Bar Chart for Monthly Energy Consumption
    monthly_bar_chart = alt.Chart(monthly_energy).mark_bar(size=20).encode(
        x=alt.X("month:T", title="Ay"),
        y=alt.Y("energy:Q", title="Toplam Enerji Tüketimi"),
        tooltip=["month:T", "energy:Q"],
    ).properties(
        width=700,
        height=400,
    ).interactive()

    st.altair_chart(monthly_bar_chart, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("İki Yıl Arasındaki Fark (%)")
    # Yıllar listesi ve varsayılan değerler
    years = filtered_df["year"].sort_values().unique().tolist()
    if len(years) >= 2:
        year1 = st.selectbox("Birinci Yıl", years, index=0)
        year2 = st.selectbox("İkinci Yıl", years, index=1)

        if year1 != year2:
            energy1 = filtered_df[filtered_df["year"] == year1]["energy"].sum()
            energy2 = filtered_df[filtered_df["year"] == year2]["energy"].sum()
            difference = energy2 - energy1
            percent_change = (difference / energy1) * 100 if energy1 != 0 else float("inf")

            st.metric(label="Yıllar Arası Yüzdesel Fark", value=f"{round(percent_change, 2)}%", delta=f"{round(difference, 2)} Enerji", delta_color="inverse")
            st.write(f"{year2} yılındaki enerji tüketimi {year1} yılına göre {'%' + str(round(percent_change, 2)) if energy1 != 0 else 'sonsuz'} değişti.")
    else:
        st.warning("Yeterli yıllık veri yok.")

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("İki Hafta Arasındaki Fark (%)")
    # Haftalar listesi ve varsayılan değerler
    weeks = weekly_df["date"].dt.strftime("%Y-%W").sort_values().unique().tolist() 
    if len(weeks) >= 2:
        week1 = st.selectbox("Birinci Hafta", weeks, index=0)
        week2 = st.selectbox("İkinci Hafta", weeks, index=1)

        if week1 != week2:
            week1_start = pd.to_datetime(week1 + "-1", format="%Y-%W-%w")
            week1_end = week1_start + timedelta(days=7)
            week2_start = pd.to_datetime(week2 + "-1", format="%Y-%W-%w")
            week2_end = week2_start + timedelta(days=7)

            week1_energy = weekly_df[(weekly_df["date"] >= week1_start) & (weekly_df["date"] < week1_end)]["energy"].sum()
            week2_energy = weekly_df[(weekly_df["date"] >= week2_start) & (weekly_df["date"] < week2_end)]["energy"].sum()
            week_difference = week2_energy - week1_energy
            week_percent_change = (week_difference / week1_energy) * 100 if week1_energy != 0 else float("inf")

            st.metric(label="Haftalar Arası Yüzdesel Fark", value=f"{round(week_percent_change, 2)}%", delta=f"{round(week_difference, 2)} Enerji", delta_color="inverse")
            st.write(f"{week2} haftasındaki enerji tüketimi {week1} haftasına göre {'%' + str(round(week_percent_change, 2)) if week1_energy != 0 else 'sonsuz'} değişti.")
    else:
        st.warning("Yeterli haftalık veri yok.")

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Reaktif Tüketim Oranı")
    reactive_data = pd.DataFrame({
        "Reaktif Türü": ["Kapasitif Enerji", "Endüktif Enerji"],
        "Oran": [4.8, 20.2],
        "Renk": ["#00B050", "#FF0000"]
    })

    reactive_chart = alt.Chart(reactive_data).mark_bar(size=30).encode(
        x=alt.X("Oran:Q", title="Oran (%)", scale=alt.Scale(domain=[0, 100])),
        y=alt.Y("Reaktif Türü:N", title=""),
        color=alt.Color("Renk:N", scale=None),
        tooltip=["Reaktif Türü:N", "Oran:Q"]
    ).properties(
        width=700,
        height=150
    ).configure_view(stroke='transparent')

    st.altair_chart(reactive_chart, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("Enerji Tüketiminin Noktalara Göre Dağılımı")
    
  
    point_grouped_data = filtered_df.groupby("point")["energy"].sum().reset_index()
    
    
    points_bar_chart = alt.Chart(point_grouped_data).mark_bar(size=150).encode(
        x=alt.X('point:N', title='Nokta', sort=alt.SortField('energy', order='descending')),
        y=alt.Y('energy:Q', title='Toplam Enerji Tüketimi'),
        color=alt.Color('point:N', legend=None),
        tooltip=['point:N', 'energy:Q']
    ).properties(
        width=700,
        height=400
    ).interactive()

    st.altair_chart(points_bar_chart, use_container_width=True)

if __name__ == "__main__":
    show_points_dashboard()