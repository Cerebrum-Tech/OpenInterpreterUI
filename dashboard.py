import streamlit as st
import pandas as pd
import plotly.express as px
from api_utils import authenticate, list_point_full_data, get_data, get_data_breakdown

def extract_tags_for_group(df, group_name):
    tags = []
    for tags_list in df['tags']:
        for tag in tags_list:
            if tag.get('groupName') == group_name:
                tags.append(tag.get('name'))
    return tags

def show_full_point_dashboard(df):
    st.subheader("Konum Gösterimi")
    fig_map_name = px.scatter_mapbox(
        df, 
        lat="lat", 
        lon="lng",
        hover_name="name",
        zoom=5,
        height=600,
        color="name"
    )
    fig_map_name.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map_name)

def show_dashboard():
    # st.title("Combined Dashboard")

    # Kimlik doğrulama ve connectionId alma
    connection_id = authenticate()
    if not connection_id:
        st.error("Kimlik doğrulama başarısız.")
        return

    raw_data = get_data(connection_id)
    raw_data_breakdown = get_data_breakdown(connection_id)
    if not raw_data or not raw_data_breakdown:
        st.error("Veri çekme işlemi başarısız.")
        return

    raw_data_point = list_point_full_data(connection_id)
    if not raw_data_point:
        st.error("Veri çekme işlemi başarısız.")
        return

    df_point = pd.json_normalize(raw_data_point, max_level=1)
    if df_point.empty:
        st.error("Dönen veri seti boş.")
        return

    if df_point['totalArea'].dtype != 'float64':
        df_point['totalArea'] = pd.to_numeric(df_point['totalArea'], errors='coerce')
    
    if df_point['age'].dtype != 'float64':
        df_point['age'] = pd.to_numeric(df_point['age'], errors='coerce')

    df_point = df_point.dropna(subset=['lat', 'lng', 'name'])
    df_point = df_point[df_point['lat'].apply(lambda x: isinstance(x, (int, float)))]
    df_point = df_point[df_point['lng'].apply(lambda x: isinstance(x, (int, float)))]

    if df_point.empty:
        st.error("Geçerli konum verileri içeren satır bulunamadı.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Enerji Tüketiminin Zaman İçinde Dağılımı - Main")
        date_values = []
        energy_values = []
        for point_entry in raw_data['0']:
            date_values.append(point_entry[0])
            energy_values.append(point_entry[1])

        data = {
            'date': date_values,
            'energy': energy_values
        }
        df = pd.DataFrame(data)
        st.line_chart(df.set_index('date'))

    show_full_point_dashboard(df_point)

    with col2:
        st.subheader("Enerji Tüketiminin Zaman İçinde Dağılımı - Breakdown")
        date_values_breakdown, energy_values_breakdown = [], []
        for point_entry in raw_data_breakdown['0']:
            date_values_breakdown.append(point_entry[0])
            energy_values_breakdown.append(point_entry[1])

        data_breakdown = {
            'date': date_values_breakdown,
            'energy_breakdown': energy_values_breakdown
        }
        df_breakdown = pd.DataFrame(data_breakdown)
        st.line_chart(df_breakdown.set_index('date'))

if __name__ == "__main__":
    show_dashboard()