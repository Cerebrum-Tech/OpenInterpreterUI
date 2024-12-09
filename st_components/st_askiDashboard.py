import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import plotly.graph_objects as go

def show_aski_panel():
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
            color: #0056b3;
            text-decoration: none;
            display: flex;
            align-items: center;
        }
        .fixed-link i {
            margin-right: 10px;
        }
        .alarm-table h3 {
            color: #3cbdde;
            margin-top: 0;
        }
        .alarm-table-icon {
            color: #3cbdde;
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
            background-color: #004080;
            color: white;
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
            padding: 10px;
            border-radius: 25px;
            background-color: #f9f9f9;
            box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
            text-align: center;
            width: 300px; 
            height: 130px;
            margin-left: auto; 
            margin-right: auto;
        }
        .sayaç-text {
            color: #4c1ea8;
        }
        .vana-text {
            color: #129652;
        }
        .hidrant-text {
            color: #15cbcf;
        }
        .boru-text {
            color: #0f35a8;
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
            color: #4c1ea8;
        }
        .valve-icon {
            color: #129652;
        }
        .hydrant-icon {
            color: #15cbcf;
        }
        .pipe-icon {
            color: #0f35a8;
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
        
        """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">ASKİ GÖRÜNTÜLEME PANELİ</div>', unsafe_allow_html=True)

    df = pd.read_csv('R2Tap-Aski.csv')
    df['Sonuç'] = df['Sonuç'].replace({'No Leak': 'N', 'Leak': 'L'})

    date_list = sorted(df['kayit_zamani'].str[:10].unique())[::-1]
    selected_date = st.selectbox('Tarih Seçiniz', date_list)
    df_selected_date = df[df['kayit_zamani'].str[:10] == selected_date]

    if df_selected_date.empty:
        st.warning("Seçilen tarihte herhangi bir veri bulunamadı.")
        return

    def calculate_leak_probability(Ses_Gücü):
        """ A sample function to calculate leak probability based on sound strength. """
        return 1 / (1 + np.exp(-Ses_Gücü))

    df_selected_date['Sızıntı_Olasılığı'] = calculate_leak_probability(df_selected_date['Ses_Gücü'])
    df['Sızıntı_Olasılığı'] = calculate_leak_probability(df['Ses_Gücü'])

    def make_choropleth(input_df, color, title):
        if input_df.empty:
            return px.scatter_mapbox(title=title)

        fig = px.scatter_mapbox(
            input_df,
            lat="enlem",
            lon="boylam",
            color_discrete_sequence=[color],
            size="Sızıntı_Olasılığı",  
            hover_data={
                "enlem": True, "boylam": True, "ID": True,
                "Ses_Gücü": True, "Sonuç": True, "Tesis_Türü": True},
            size_max=35,
            zoom=10,
            title=title,
            height=500
        )
        fig.update_traces(marker=dict(opacity=0.7, symbol='circle'), selector=dict(mode='markers'))
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0, "t":40, "l":0, "b":0})
        return fig

    def make_donut(input_response, input_text, color):
        chart_color = {
            'blue': ['#0056b3', '#004080'],
            'red': ['#E74C3C', '#781F16']
        }[color]

        source = pd.DataFrame({"Kategori": [input_text, ''], "Değer": [input_response, 100 - input_response]})
        donut_chart = alt.Chart(source).mark_arc(innerRadius=60).encode(
            theta=alt.Theta("Değer:Q"),
            color=alt.Color("Kategori:N", scale=alt.Scale(range=chart_color))
        ).properties(width=300, height=250)

        text = donut_chart.mark_text(
            align='center',
            fontSize=28
        ).encode(
            text=alt.value(f'{input_response} '),
            color=alt.value(chart_color[0])
        ).properties(width=250, height=250)

        return donut_chart + text

    st.markdown(f'### Seçilen Tarih Ayrıntıları: {selected_date}')

    col1, col2, col3 = st.columns(3)

    with col1:
        #st.markdown('#### Sızıntı Olmayan Konumlar')
        no_leak_choropleth = make_choropleth(df_selected_date[df_selected_date['Sonuç'] == 'N'], '#0056b3', 'Sızıntı Olmayan Konumlar')
        st.plotly_chart(no_leak_choropleth, use_container_width=True)

    with col2:
        #st.markdown('#### Sızıntı Olan Konumlar')
        leak_df = df_selected_date[df_selected_date['Sonuç'] == 'L']
        if leak_df.empty:
            st.warning("Seçilen tarihte sızıntı bilgisi bulunamamıştır.")
        else:
            leak_choropleth = make_choropleth(leak_df, 'red', 'Sızıntı Olan Konumlar')
            st.plotly_chart(leak_choropleth, use_container_width=True)

    with col3:
        #st.markdown('#### Tüm Konumlar')
        all_locations_choropleth = make_choropleth(df, 'green', 'Tüm Konumlar')
        st.plotly_chart(all_locations_choropleth, use_container_width=True)

    st.markdown('### Genel Detaylar')

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        sub_col1, sub_col2 = st.columns([1, 1])
        with sub_col1:
            no_leak_count = len(df_selected_date[df_selected_date['Sonuç'] == 'N'])
            st.markdown(f'#### Sızıntı Yok: {no_leak_count}')
            st.altair_chart(make_donut(no_leak_count, 'Sızıntı Yok', 'blue'))

        with sub_col2:
            leak_count = len(df_selected_date[df_selected_date['Sonuç'] == 'L'])
            st.markdown(f'#### Sızıntı Var: {leak_count}')
            st.altair_chart(make_donut(leak_count, 'Sızıntı Var', 'red'))

    st.markdown('### Ses Gücü ve Sızıntı Olasılığı')

    show_only_leak_strength = st.checkbox('Sadece Sızıntı Olanları Göster (Ses Gücü)')
    
    sound_strength_filter = df_selected_date
    if show_only_leak_strength:
        sound_strength_filter = sound_strength_filter[sound_strength_filter['Sonuç'] == 'L']
    
    color_scale = alt.Scale(domain=['L', 'N'], range=['#E74C3C', '#0056b3'])
    sound_strength_chart = alt.Chart(sound_strength_filter).mark_bar().encode(
        x='ID:O',
        y='Ses_Gücü:Q',
        color=alt.Color('Sonuç:N', scale=color_scale),
        tooltip=['ID', 'Ses_Gücü', 'Sonuç']
    ).properties(width=1400, height=400)
    
    st.altair_chart(sound_strength_chart)

    
    show_only_leak_probability = st.checkbox('Sadece Sızıntı Olanları Göster (Sızıntı Olasılığı)')
    
    leak_probability_filter = df_selected_date
    if show_only_leak_probability:
        leak_probability_filter = leak_probability_filter[leak_probability_filter['Sonuç'] == 'L']
        
    line_chart = alt.Chart(leak_probability_filter).mark_line(point=True).encode(
        x=alt.X('ID:O', title='ID', axis=alt.Axis(labels=False)),
        y=alt.Y('Sızıntı_Olasılığı:Q', title='Sızıntı Olasılığı'),
        color=alt.Color('Sonuç:N', scale=alt.Scale(domain=['L', 'N'], range=['#E74C3C', '#0056b3'])),
        tooltip=['ID', 'Sızıntı_Olasılığı:Q', 'enlem:Q', 'boylam:Q']
    ).properties(
        width=1400,
        height=400,
        title='ID bazında Sızıntı Olasılığı'
    )
    st.altair_chart(line_chart)

    st.markdown('### Teçhizat Türleri Konumları ve Sayıları')
    
    

    col1, col2 = st.columns([7, 2])

    with col1:
        facility_colors = {
            'Sayaç': '#4c1ea8',
            'Vana': '#129652',
            'Hidrant': '#15cbcf',
            'Boru': '#0f35a8'
        }

        df_selected_date['color'] = df_selected_date['Tesis_Türü'].map(facility_colors)

        fig_facility_type = px.scatter_mapbox(
            df_selected_date,
            lat="enlem",
            lon="boylam",
            color="Tesis_Türü",
            size="Sızıntı_Olasılığı",  
            color_discrete_map=facility_colors,
            hover_data={
                "enlem": True, "boylam": True, "ID": True,
                "Ses_Gücü": True, "Tesis_Türü": True, "Sonuç": True},
            size_max=35,
            zoom=10,
            height=550
        )
        fig_facility_type.update_traces(marker=dict(opacity=0.7, symbol='circle'), selector=dict(mode='markers'))
        fig_facility_type.update_layout(mapbox_style="open-street-map")
        fig_facility_type.update_layout(margin={"r":0, "t":1, "l":0, "b":0})
        st.plotly_chart(fig_facility_type, use_container_width=True)

    with col2:
        Tesis_Türü = ['Sayaç', 'Vana', 'Hidrant', 'Boru']
        facility_count_icons = {
            'Sayaç': '<i class="fas fa-tachometer-alt meter-icon"></i>',
            'Vana': '<i class="fas fa-wrench valve-icon"></i>',
            'Hidrant': '<i class="fas fa-fire-extinguisher hydrant-icon"></i>',
            'Boru': '<i class="fas fa-tint pipe-icon"></i>'  
        }
        facility_counts = {facility: df_selected_date['Tesis_Türü'].value_counts().get(facility, 0) for facility in Tesis_Türü}

        for facility, count in facility_counts.items():
            class_name = facility.lower() + "-text"
            icon_html = facility_count_icons[facility]
            background_color = {
                'Sayaç': '#e0f7fa',  
                'Vana': '#e6f2ff',  
                'Hidrant': '#ccd9ff',
                'Boru': '#e6f5ff' 
            }[facility]
            st.markdown(f"""
            <div class="card" style="background-color: {background_color};">
                <h3 class="{class_name}">{facility} {icon_html}</h3>
                <p class="{class_name} count-text">{count}</p>
            </div>
            """, unsafe_allow_html=True)
            
    #st.markdown('### 3D Ses Gücü Bar Grafiği')

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=df_selected_date['enlem'],
        y=df_selected_date['boylam'],
        z=[0]*len(df_selected_date['Ses_Gücü']),
        mode='lines+markers',
        marker=dict(size=3),
        name='Base',
        text='Base'
    ))

    fig.add_trace(go.Scatter3d(
        x=df_selected_date['enlem'],
        y=df_selected_date['boylam'],
        z=df_selected_date['Ses_Gücü'],
        mode='markers',
        marker=dict(
            size=5,
            color=df_selected_date['Ses_Gücü'],
            colorscale='Viridis',
            colorbar=dict(
                title='Ses Gücü',
                x=0.5,  
                y=-0.2, 
                orientation='h' 
            ),
            opacity=0.8
        ),
        name='Ses Gücü',
        text='Ses Gücü'
    ))

    fig.update_layout(
        title='3D Ses Gücü Bar Grafiği',
        autosize=True,
        width=800,
        height=600,
        margin=dict(l=65, r=50, b=65, t=90),
        scene=dict(
            xaxis_title='Enlem',
            yaxis_title='Boylam',
            zaxis_title='Ses Gücü'
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f'<div class="alarm-table"><h3><i class="fas fa-exclamation-triangle alarm-table-icon"></i>Sızıntı Olan Konumlar İçin Alarm Tablosu</h3>', unsafe_allow_html=True)
    st.markdown('Aşağıdaki tabloda tespit edilen sızıntı yerleri ve detayları gösterilmektedir.', unsafe_allow_html=True)

    if not leak_df.empty:
        leak_df['Alarm'] = '<i class="fas fa-exclamation-circle alarm-icon"></i> <span class="red-text">Beklenenin Üzerinde</span>'
        leak_df['Sızıntı_Olasılığı'] = calculate_leak_probability(leak_df['Ses_Gücü'])
        leak_df_subset = leak_df[['Alarm', 'ID', 'enlem', 'boylam', 'Sonuç', 'Ses_Gücü', 'Sızıntı_Olasılığı', 'kayit_zamani']]
        leak_df_subset.columns = ['Alarm', 'ID', 'Enlem', 'Boylam', 'Sonuç', 'Ses Gücü', 'Sızıntı Olasılığı', 'Kayıt Zamanı']

        st.markdown(leak_df_subset.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning("Alarm tablosunda görüntülenecek sızıntı verisi bulunmuyor.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="alarm-table"><h3 style="color: blue;"></i>Tüm Veriler</h3>', unsafe_allow_html=True)
    st.markdown('Bu tablo seçilen tarihten bağımsız olarak tüm verileri gösterir. "Sızıntı Yok" mavi bir tikle ve "Sızıntı Var" kırmızı bir çarpı ile gösterilir.', unsafe_allow_html=True)

    df['Sızıntı_Olasılığı'] = calculate_leak_probability(df['Ses_Gücü'])
    df_all_data = df.copy()
    df_all_data['Status'] = df_all_data['Sonuç'].apply(
        lambda x: '<i class="fas fa-check-circle" style="color: #0056b3;"></i> Sızıntı Yok' if x == 'N' else '<i class="fas fa-times-circle" style="color: red;"></i> Sızıntı Var'
    )
    df_all_data_subset = df_all_data[['Status', 'ID', 'enlem', 'boylam', 'Sonuç', 'Ses_Gücü', 'Sızıntı_Olasılığı', 'kayit_zamani']]
    df_all_data_subset.columns = ['Durum', 'ID', 'Enlem', 'Boylam', 'Sonuç', 'Ses Gücü', 'Sızıntı Olasılığı', 'Kayıt Zamanı']

    initial_rows = 5
    if 'show_all' not in st.session_state:
        st.session_state.show_all = False

    def toggle_show_all():
        st.session_state.show_all = not st.session_state.show_all

    if not st.session_state.show_all:
        df_display = df_all_data_subset.head(initial_rows)
        st.markdown(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
        if len(df_all_data_subset) > initial_rows:
            st.button('Daha Fazla Göster', on_click=toggle_show_all)
    else:
        st.markdown(df_all_data_subset.to_html(escape=False, index=False), unsafe_allow_html=True)
        st.button('Daha Az Göster', on_click=toggle_show_all)

if __name__ == "__main__":
    show_aski_panel()