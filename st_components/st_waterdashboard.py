import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import pytz


def water_dashboard():
    st.markdown(
        """
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
        <style>
        .fixed-link {
            position: -webkit-sticky;
            position: sticky;
            top: 0;
            background-color: rgba(255, 255, 255, 0.9);
            text-align: center;
            z-index: 9999;
            padding: 10px;
            font-size: 20px;
            font-weight: bold;
            width: 100%;
            border-bottom: 2px solid #f1f1f1;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .fixed-link a {
            color: blue;
            text-decoration: none;
            display: flex;
            align-items: center;
        }
        .fixed-link i {
            margin-right: 10px;
        }
        </style>
        <div class="fixed-link">
            <a href="https://tr.neverlosewater.com/" target="_blank">
                <i class="fas fa-water"></i>
                Visit NELOW for more
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="main-title">PRESSURE MONITORING DASHBOARD</div>', unsafe_allow_html=True)

   
    df = pd.read_csv('/home/esra/OpenInterpreterUI/pressure_mock_data (4).csv')

    df['MEASURE_DATETIME'] = pd.to_datetime(df['MEASURE_DATETIME'], errors='coerce')
    df['REG_TIME'] = pd.to_datetime(df['REG_TIME'], errors='coerce')

    df = df.dropna(subset=['MEASURE_DATETIME'])

    df['MEASURE_TIME'] = df['MEASURE_DATETIME'].dt.strftime('%H:%M:%S')

  
    region_colors = {
        'ANKARA DMA 1-1': 'blue',
        'ANKARA DMA 1-2': 'green',
        'ANKARA DMA 1-3': 'yellow',
        'ANKARA DMA 1-4': 'pink',
        'ANKARA DMA 1-5': 'red'
    }

    date_list = sorted(df['MEASURE_DATETIME'].dt.date.unique())[::-1]
    selected_date = st.selectbox('Select a date', date_list)

    df['MEASURE_DATETIME'] = df['MEASURE_DATETIME'].dt.floor('10T')
    df_selected_date = df[df['MEASURE_DATETIME'].dt.date == selected_date]

    if df_selected_date.empty:
        st.warning("There is no data for the selected date.")
        return

    df_selected_date['MEASURE_TIME'] = df_selected_date['MEASURE_DATETIME'].dt.strftime('%H:%M')
    time_list = sorted(df_selected_date['MEASURE_TIME'].unique())
    selected_time = st.selectbox('Select a time', time_list)
    df_selected_time = df_selected_date[df_selected_date['MEASURE_TIME'] == selected_time]

    point_names = df_selected_date['POINT_NAME'].unique()

    def make_map(input_df):
        if input_df.empty:
            return px.scatter_mapbox()

        fig = px.scatter_mapbox(
            input_df,
            lat="LATITUDE",
            lon="LONGITUDE",
            color='POINT_NAME',
            hover_data={
                'LATITUDE': True,
                'LONGITUDE': True,
                'POINT_NAME': True,
                'WATER_PRESSURE': True,
                'DEVICE_TEMPERATURE': True,
                'MEASURE_DATETIME': True,
                'MEASURE_TIME': True 
            },
            size_max=15,
            zoom=10,
            height=500
        )
        fig.update_traces(marker=dict(size=20), selector=dict(mode='markers'))
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
        return fig

    def make_bar_chart(input_df, x_column, y_column, color_column, chart_title):
        chart = alt.Chart(input_df).mark_bar().encode(
            x=alt.X(x_column, title=x_column.replace('_', ' ').title()),
            y=alt.Y(y_column, title=y_column.replace('_', ' ').title()),
            color=alt.Color(color_column, legend=None), 
            tooltip=[x_column, y_column, color_column]
        ).properties(
            width=800,
            height=400,
            title=chart_title  
        )
        return chart

    def make_line_chart(input_df, x_column, y_column, color_column, chart_title, region_colors, perma_color=None):
        chart = alt.Chart(input_df).mark_line(point=True).encode(
            x=alt.X(x_column, title=x_column.replace('_', ' ').title()),
            y=alt.Y(y_column, title=y_column.replace('_', ' ').title()),
            color=alt.value(perma_color) if perma_color else alt.Color(
                color_column, 
                scale=alt.Scale(domain=list(region_colors.keys()), range=list(region_colors.values()))
            ),
            tooltip=[x_column, y_column, color_column, 'MEASURE_TIME']  
        ).properties(
            width=800,
            height=400,
            title=chart_title
        )
        return chart

    st.markdown(f'### Overview for {selected_date}')
    st.dataframe(df_selected_date)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### Water Pressure Locations by Point Name')
        water_pressure_map = make_map(df_selected_time)
        st.plotly_chart(water_pressure_map, use_container_width=True, key="water_pressure_map")

    with col2:
        st.markdown('#### Device Temperature Locations by Point Name')
        device_temperature_map = make_map(df_selected_time)
        st.plotly_chart(device_temperature_map, use_container_width=True, key="device_temperature_map")

    st.markdown(f'### Details for {selected_time}')

    st.dataframe(df_selected_time[['POINT_NAME', 'MEASURE_DATETIME', 'WATER_PRESSURE', 'DEVICE_TEMPERATURE']])

    col1, col2 = st.columns(2)
    with col1:
        chart_title = f'Water Pressure by Point Name for {selected_date} {selected_time}'
        water_pressure_chart = make_bar_chart(df_selected_time, 'POINT_NAME', 'WATER_PRESSURE', 'POINT_NAME', chart_title)
        st.altair_chart(water_pressure_chart, use_container_width=True, key="water_pressure_chart")

    with col2:
        chart_title = f'Device Temperature by Point Name for {selected_date} {selected_time}'
        device_temperature_chart = make_bar_chart(df_selected_time, 'POINT_NAME', 'DEVICE_TEMPERATURE', 'POINT_NAME', chart_title)
        st.altair_chart(device_temperature_chart, use_container_width=True, key="device_temperature_chart")


    st.markdown(f'### Detailed Time-Series for a Selected Point')
    selected_point = st.selectbox('Select a point', point_names)
    df_selected_point = df_selected_date[df_selected_date['POINT_NAME'] == selected_point]

    chart_title = f'Water Pressure Over Time for {selected_point} on {selected_date}'
    water_pressure_time_chart = make_line_chart(df_selected_point, 'MEASURE_DATETIME', 'WATER_PRESSURE', 'POINT_NAME', chart_title, region_colors, '#e066ff')
    st.altair_chart(water_pressure_time_chart, use_container_width=True, key="water_pressure_time_chart")

    chart_title = f'Device Temperature Over Time for {selected_point} on {selected_date}'
    device_temperature_time_chart = make_line_chart(df_selected_point, 'MEASURE_DATETIME', 'DEVICE_TEMPERATURE', 'POINT_NAME', chart_title, region_colors, '#e066ff')
    st.altair_chart(device_temperature_time_chart, use_container_width=True, key="device_temperature_time_chart")


if __name__ == "__main__":
    water_dashboard()