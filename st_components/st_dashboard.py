import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

def dashboard():

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
        .alarm-table h3 {
            color: #E74C3C;
            margin-top: 0;
        }
        .alarm-table-icon {
            color: #E74C3C;
            margin-right: 10px;
        }
        table {
            width: 100%;
            color: black;
            background-color: white;
            border-collapse: collapse;
        }
        td, th {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .alarm-icon {
            color: red;
            margin-right: 5px;
            animation: alarm-blink 1s infinite;
        }
        .red-text {
            color: red;
        }
        .card {
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 25px;
            background-color: #f9f9f9;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 25px;
            text-align: center;
            width: 300px; 
            margin-left: auto; 
            margin-right: auto;
        }
        .meter-text {
            color: blue;
        }
        .valve-text {
            color: green;
        }
        .hydrant-text {
            color: red;
        }
        .count-text {
            font-size: 28px;
            font-weight: bold;
        }
         .icon {
            margin-top: 10px;
            font-size: 40px;
        }
        .meter-icon {
            color: blue;
        }
        .valve-icon {
            color: green;
        }
        .hydrant-icon {
            color: red;
        }

        @keyframes alarm-blink {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.2);
            }
        }
        </style>
        <div class="fixed-link">
            <a href="https://tr.neverlosewater.com/" target="_blank">
                <i class="fas fa-water"></i>
                Visit NELOW for more
            </a>
        </div>
        """, unsafe_allow_html=True)


    st.markdown('<div class="main-title">LEAK INVESTIGATION DASHBOARD</div>', unsafe_allow_html=True)

    df = pd.read_csv('leakage_mock_data_1st_investigation.csv')

    df['AI_result'] = df['AI_result'].replace({'No Leak': 'N', 'Leak': 'L'})

    date_list = sorted(df['recording_time'].str[:10].unique())[::-1]
    selected_date = st.selectbox('Select a date', date_list)
    df_selected_date = df[df['recording_time'].str[:10] == selected_date]

    if df_selected_date.empty:
        st.warning("There is no data on the selected date.")
        return

    def make_choropleth(input_df, color):
        if input_df.empty:
            return px.scatter_mapbox()

        fig = px.scatter_mapbox(
            input_df,
            lat="latitude",
            lon="longitude",
            color_discrete_sequence=[color],
            hover_data={
                "latitude": True, "longitude": True, "ID": True,
                "Sound_strength": True, "AI_result": True, "facil_type": True},
            size_max=15,
            zoom=10,
            height=500
        )
        fig.update_traces(marker=dict(size=22), selector=dict(mode='markers'))
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0, "t":10, "l":0, "b":0})
        return fig

    def make_donut(input_response, input_text, color):
        chart_color = {
            'blue': ['#29b5e8', '#155F7A'],
            'red': ['#E74C3C', '#781F16']
        }[color]

        source = pd.DataFrame({"Category": [input_text, ''], "Value": [input_response, 100 - input_response]})
        donut_chart = alt.Chart(source).mark_arc(innerRadius=60).encode(
            theta=alt.Theta("Value:Q"),
            color=alt.Color("Category:N", scale=alt.Scale(range=chart_color))
        ).properties(width=300, height=250)

        text = donut_chart.mark_text(
            align='center',
            fontSize=28
        ).encode(
            text=alt.value(f'{input_response} '),
            color=alt.value(chart_color[0])
        ).properties(width=250, height=250)

        return donut_chart + text

    st.markdown(f'### Overview for {selected_date}')

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('#### No Leak Locations')
        no_leak_choropleth = make_choropleth(df_selected_date[df_selected_date['AI_result'] == 'N'], 'blue')
        st.plotly_chart(no_leak_choropleth, use_container_width=True)

    with col2:
        st.markdown('#### Leak Locations')
        leak_df = df_selected_date[df_selected_date['AI_result'] == 'L']
        if leak_df.empty:
            st.warning("There is no 'Leak' status on the selected date.")
        else:
            leak_choropleth = make_choropleth(leak_df, 'red')
            st.plotly_chart(leak_choropleth, use_container_width=True)

    with col3:
        st.markdown('#### All Locations')
        all_locations_choropleth = make_choropleth(df, 'black')
        st.plotly_chart(all_locations_choropleth, use_container_width=True)

    st.markdown('### Overview Details')

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        sub_col1, sub_col2 = st.columns([1, 1])
        with sub_col1:
            no_leak_count = len(df_selected_date[df_selected_date['AI_result'] == 'N'])
            st.markdown(f'#### No Leak: {no_leak_count}')
            st.altair_chart(make_donut(no_leak_count, 'No Leak', 'blue'))

        with sub_col2:
            leak_count = len(df_selected_date[df_selected_date['AI_result'] == 'L'])
            st.markdown(f'#### Leak: {leak_count}')
            st.altair_chart(make_donut(leak_count, 'Leak', 'red'))

    st.markdown('### Sound Strength by ID & Leak Probability')

    col1, col2 = st.columns(2)

    def calculate_leak_probability(sound_strength):
        """ A sample function to calculate leak probability based on sound strength. """
        return 1 / (1 + np.exp(-sound_strength))

    df_selected_date['leak_probability'] = calculate_leak_probability(df_selected_date['Sound_strength'])

    with col1:
        color_scale = alt.Scale(domain=['L', 'N'], range=['red', 'blue'])
        sound_strength_chart = alt.Chart(df_selected_date).mark_bar().encode(
            x='ID:O',
            y='Sound_strength:Q',
            color=alt.Color('AI_result:N', scale=color_scale),
            tooltip=['ID', 'Sound_strength', 'AI_result']
        ).properties(width=800, height=400)
        st.altair_chart(sound_strength_chart)

    with col2:
        heatmap = alt.Chart(df_selected_date).mark_rect().encode(
            x=alt.X('longitude:Q', bin=True),
            y=alt.Y('latitude:Q', bin=True),
            color=alt.Color('leak_probability:Q', scale=alt.Scale(domain=[0, 1], range=["red", "blue"])),
            tooltip=['leak_probability:Q', 'latitude:Q', 'longitude:Q']
        ).properties(width=800, height=400)
        st.altair_chart(heatmap)

    st.markdown('### Facility Type Locations & Counts')

    col1, col2 = st.columns([7,2])

    with col1:
        facility_colors = {
            'Water Meter': 'blue',
            'Valve': 'green',
            'Hydrant': 'red'
        }

        df_selected_date['color'] = df_selected_date['facil_type'].map(facility_colors)

        fig_facility_type = px.scatter_mapbox(
            df_selected_date,
            lat="latitude",
            lon="longitude",
            color="facil_type",
            color_discrete_map=facility_colors,
            hover_data={
                "latitude": True, "longitude": True, "ID": True,
                "Sound_strength": True, "facil_type": True, "AI_result": True},
            size_max=15,
            zoom=10,
            height=500
        )
        fig_facility_type.update_traces(marker=dict(size=20), selector=dict(mode='markers'))
        fig_facility_type.update_layout(mapbox_style="open-street-map")
        fig_facility_type.update_layout(margin={"r":0, "t":1, "l":0, "b":0})
        st.plotly_chart(fig_facility_type, use_container_width=True)

    with col2:
        facility_types = ['Water Meter', 'Valve', 'Hydrant']
        facility_count_icons = {
            'Water Meter': '<i class="fas fa-tachometer-alt meter-icon"></i>',
            'Valve': '<i class="fas fa-wrench valve-icon"></i>',
            'Hydrant': '<i class="fas fa-fire-extinguisher hydrant-icon"></i>'
        }
        facility_counts = {facility: df_selected_date['facil_type'].value_counts().get(facility, 0) for facility in facility_types}

        for facility, count in facility_counts.items():
            class_name = facility.lower() + "-text"
            icon_html = facility_count_icons[facility]
            background_color = {
            'Water Meter': '#e0f7fa',  
            'Valve': '#e8f5e9',  
            'Hydrant': '#ffebee'  
             }[facility]
            st.markdown(f"""
            <div class="card" style="background-color: {background_color};">
                <h3 class="{class_name}">{facility} {icon_html}</h3>
                <p class="{class_name} count-text">{count}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f'<div class="alarm-table"><h3><i class="fas fa-exclamation-triangle alarm-table-icon"></i>Alarm Table for Leak Locations</h3>', unsafe_allow_html=True)
    st.markdown('The following table highlights the detected leak locations and their details.', unsafe_allow_html=True)

    if not leak_df.empty:
        leak_df['Alarm'] = '<i class="fas fa-exclamation-circle alarm-icon"></i> <span class="red-text">Above Expected</span>'
        leak_df['leak_probability'] = calculate_leak_probability(leak_df['Sound_strength'])
        leak_df_subset = leak_df[['Alarm', 'ID', 'latitude', 'longitude', 'AI_result', 'Sound_strength', 'leak_probability', 'recording_time']]
        leak_df_subset.columns = ['Alarm', 'ID', 'Latitude', 'Longitude', 'Result', 'Sound Strength', 'Leak Probability', 'Recording Time']

        st.markdown(leak_df_subset.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning("There are no leak locations to display in the alarm table.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="alarm-table"><h3 style="color:green;"></i>Full Data Overview</h3>', unsafe_allow_html=True)
    st.markdown('This table shows all data irrespective of the selected date. "No Leak" is shown with a blue tick and "Leak" with a red cross.', unsafe_allow_html=True)

    df['leak_probability'] = calculate_leak_probability(df['Sound_strength'])
    df_all_data = df.copy()
    df_all_data['Status'] = df_all_data['AI_result'].apply(
        lambda x: '<i class="fas fa-check-circle" style="color: blue;"></i> No Leak' if x == 'N' else '<i class="fas fa-times-circle" style="color: red;"></i> Leak'
    )
    df_all_data_subset = df_all_data[['Status', 'ID', 'latitude', 'longitude', 'AI_result', 'Sound_strength', 'leak_probability', 'recording_time']]
    df_all_data_subset.columns = ['Status', 'ID', 'Latitude', 'Longitude', 'Result', 'Sound Strength', 'Leak Probability', 'Recording Time']

    initial_rows = 5
    if 'show_all' not in st.session_state:
        st.session_state.show_all = False

    def toggle_show_all():
        st.session_state.show_all = not st.session_state.show_all

    if not st.session_state.show_all:
        df_display = df_all_data_subset.head(initial_rows)
        st.markdown(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
        if len(df_all_data_subset) > initial_rows:
            st.button('Show More', on_click=toggle_show_all)
    else:
        st.markdown(df_all_data_subset.to_html(escape=False, index=False), unsafe_allow_html=True)
        st.button('Show Less', on_click=toggle_show_all)

if __name__ == "__main__":
    dashboard()