import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="ESG-аналитика • Яндекс",
    page_icon="🌱",
    layout="wide"
)

# Загрузка данных
@st.cache_data
def load_esg_data():
    return pd.read_csv('data/yandex_esg.csv')

@st.cache_data
def load_materiality_data():
    return pd.read_csv('data/materiality_matrix.csv')

esg_df = load_esg_data()
materiality_df = load_materiality_data()

# Боковая панель
st.sidebar.title("ESG-аналитика")
st.sidebar.markdown("---")

years = sorted(esg_df['year'].unique())
selected_year = st.sidebar.selectbox("Выберите год", years, index=len(years)-1)
esg_filtered = esg_df[esg_df['year'] == selected_year]

metric_categories = {
    'Все': [],
    'Социальные': ['staff_total', 'women_percent', 'women_management_percent',
                   'women_stem_percent', 'turnover_total', 'turnover_unwanted',
                   'interns', 'rounding_users'],
    'Экологические': ['co2_scope1_2_total_tons', 'co2_intensity_per_mwh',
                      'water_withdrawal_megaliters', 'waste_total_tons',
                      'pue_average', 'taxi_emissions_moscow_g_per_passenger_km'],
    'Партнёрские': ['ngo_partners', 'free_taxi_rides_for_ngo_thousands']
}
selected_category = st.sidebar.selectbox("Выберите категорию", list(metric_categories.keys()))
if selected_category != 'Все' and metric_categories[selected_category]:
    esg_filtered = esg_filtered[esg_filtered['metric'].isin(metric_categories[selected_category])]

st.sidebar.markdown("---")
st.sidebar.caption(f"Показано метрик: {len(esg_filtered)}")

# Основная часть
st.title("🌱 ESG-аналитика компании Яндекс")
st.markdown("---")

# KPI
col1, col2, col3, col4 = st.columns(4)

def get_metric_value(metric_name):
    val = esg_filtered[esg_filtered['metric'] == metric_name]['value'].values
    return val[0] if len(val) > 0 else None

co2 = get_metric_value('co2_scope1_2_total_tons')
women = get_metric_value('women_management_percent')
turnover = get_metric_value('turnover_total')
staff = get_metric_value('staff_total')

with col1:
    st.metric("👥 Сотрудников", f"{staff:,.0f}" if staff else "Нет данных")
with col2:
    st.metric("🌍 CO₂ (Scope 1+2)", f"{co2:,.0f} т" if co2 else "Нет данных")
with col3:
    st.metric("👩 Женщины в управлении", f"{women:.1f}%" if women else "Нет данных")
with col4:
    st.metric("🔄 Текучесть кадров", f"{turnover:.1f}%" if turnover else "Нет данных")

st.markdown("---")

# Динамика ESG-метрик
col_graph, col_info = st.columns([3, 1])

with col_graph:
    st.subheader("Динамика ESG-метрик")
    metric_options = {
        'co2_scope1_2_total_tons': 'CO₂ (тонн)',
        'co2_intensity_per_mwh': 'Углеродная интенсивность (т/MWh)',
        'women_management_percent': 'Женщины в управлении (%)',
        'women_percent': 'Женщины в компании (%)',
        'turnover_total': 'Текучесть кадров (%)',
        'turnover_unwanted': 'Нежелательная текучесть (%)',
        'staff_total': 'Сотрудники (чел)',
        'water_withdrawal_megaliters': 'Водопотребление (мегалитры)',
        'waste_total_tons': 'Отходы (тонн)',
        'pue_average': 'PUE (энергоэффективность)',
        'interns': 'Стажёры (чел)',
        'rounding_users': 'Пользователи помогающих сервисов',
        'ngo_partners': 'Партнёры-НКО'
    }
    selected_metric = st.selectbox(
        "Выберите метрику",
        options=list(metric_options.keys()),
        format_func=lambda x: metric_options[x]
    )
    metric_data = esg_df[esg_df['metric'] == selected_metric].sort_values('year')
    fig = px.line(
        metric_data,
        x='year',
        y='value',
        title=f'Динамика: {metric_options[selected_metric]}',
        markers=True,
        labels={'year': 'Год', 'value': metric_options[selected_metric]}
    )
    fig.update_layout(
        height=400,
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=10, r=10, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_info:
    st.subheader("Справка")
    st.markdown("""
    **О метриках:**
    - **CO₂ (Scope 1+2)** — прямые и косвенные выбросы
    - **Женщины в управлении** — доля женщин в руководстве
    - **Текучесть кадров** — увольнения за год (%)
    - **PUE** — энергоэффективность дата-центров (чем ниже, тем лучше)
    """)
    st.markdown("---")

# Матрица существенности с градиентными зонами
st.subheader("Матрица существенности")

col_matrix, col_legend = st.columns([3, 1])

with col_matrix:
    # Создаём фигуру с зонами
    fig_matrix = go.Figure()

    # Добавляем фоновые зоны (градиент важности)
    fig_matrix.add_shape(type="rect", x0=7.5, x1=10, y0=7.5, y1=10,
                         fillcolor="rgba(255, 100, 100, 0.15)", line=dict(width=0))
    fig_matrix.add_shape(type="rect", x0=4, x1=7.5, y0=7.5, y1=10,
                         fillcolor="rgba(255, 200, 100, 0.10)", line=dict(width=0))
    fig_matrix.add_shape(type="rect", x0=7.5, x1=10, y0=4, y1=7.5,
                         fillcolor="rgba(100, 200, 255, 0.10)", line=dict(width=0))
    fig_matrix.add_shape(type="rect", x0=4, x1=7.5, y0=4, y1=7.5,
                         fillcolor="rgba(200, 200, 200, 0.05)", line=dict(width=0))

    # Добавляем разделительные линии
    fig_matrix.add_hline(y=7.5, line_dash="dash", line_color="gray", opacity=0.5)
    fig_matrix.add_vline(x=7.5, line_dash="dash", line_color="gray", opacity=0.5)

    # Добавляем аннотации зон
    fig_matrix.add_annotation(x=9.2, y=9.5, text="Критически важно", showarrow=False,
                              font=dict(size=12, color="darkred"), opacity=0.7)
    fig_matrix.add_annotation(x=6, y=9.2, text="Высокое влияние\nна стейкхолдеров", showarrow=False,
                              font=dict(size=10, color="darkorange"), opacity=0.7)
    fig_matrix.add_annotation(x=9.2, y=6, text="Высокое влияние\nна бизнес", showarrow=False,
                              font=dict(size=10, color="darkblue"), opacity=0.7)

    # Точки
    fig_matrix.add_trace(go.Scatter(
        x=materiality_df['impact_on_business'],
        y=materiality_df['impact_on_stakeholders'],
        text=materiality_df['factor'],
        mode='markers+text',
        textposition='top center',
        textfont=dict(size=8),  # <- уменьшаем шрифт подписей
        marker=dict(
            size=materiality_df['impact_on_business'] * 6,
            color=materiality_df['impact_on_stakeholders'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Влияние\nна стейкхолдеров")
        ),
        hovertemplate='<b>%{text}</b><br>Влияние на бизнес: %{x:.1f}<br>Влияние на стейкхолдеров: %{y:.1f}<extra></extra>'
    ))

    fig_matrix.update_layout(
        title='Матрица существенности (зоны: критическая, высокая, средняя)',
        xaxis=dict(title='Влияние на бизнес', range=[4, 10], dtick=1),
        yaxis=dict(title='Влияние на стейкхолдеров', range=[4, 10], dtick=1),
        height=550,
        template='plotly_white',
        margin=dict(l=10, r=10, t=50, b=20),
        legend=dict(font=dict(size=8))
    )
    st.plotly_chart(fig_matrix, use_container_width=True)

with col_legend:
    st.subheader("Легенда")
    st.markdown("""
    **Цветовые зоны:**
    - 🔴 Критическая (право-верх)
    - 🟠 Высокое влияние на стейкхолдеров
    - 🔵 Высокое влияние на бизнес
    - ⚪ Средняя важность
    """)
    st.markdown("**Размер точки** отражает влияние на бизнес.")
    st.markdown("**Цвет точки** отражает влияние на стейкхолдеров.")
    st.markdown("---")
    st.caption("Источник: экспертная оценка на основе ESG-отчётов Яндекса")

st.markdown("---")

# Сравнение с бенчмарками и SDGs
st.subheader("Сравнение с бенчмарками и целями SDGs")

col_bench1, col_bench2 = st.columns(2)

with col_bench1:
    st.subheader("Выбросы CO₂")
    co2_data = pd.DataFrame({
        'Категория': ['Яндекс', 'Отраслевой средний', 'Цель SDG (13)'],
        'Значение': [co2 if co2 else 0, 300000, 250000]
    })
    fig_co2 = px.bar(
        co2_data,
        x='Категория',
        y='Значение',
        title='CO₂ (Scope 1+2)',
        labels={'Значение': 'Тонн CO₂'},
        color='Категория',
        color_discrete_map={'Яндекс': '#FF6B6B', 'Отраслевой средний': '#4ECDC4', 'Цель SDG (13)': '#45B7D1'}
    )
    fig_co2.update_layout(template='plotly_white', height=300)
    st.plotly_chart(fig_co2, use_container_width=True)

with col_bench2:
    st.subheader("Доля женщин в управлении")
    women_data = pd.DataFrame({
        'Категория': ['Яндекс', 'Отраслевой средний', 'Цель SDG (5)'],
        'Значение': [women if women else 0, 30, 40]
    })
    fig_women = px.bar(
        women_data,
        x='Категория',
        y='Значение',
        title='Женщины в управлении (%)',
        labels={'Значение': '%'},
        color='Категория',
        color_discrete_map={'Яндекс': '#FF6B6B', 'Отраслевой средний': '#4ECDC4', 'Цель SDG (5)': '#45B7D1'}
    )
    fig_women.update_layout(template='plotly_white', height=300)
    st.plotly_chart(fig_women, use_container_width=True)

st.markdown("---")

# Полная таблица метрик
st.subheader("Полный список ESG-метрик")
table_data = esg_filtered.pivot(index='year', columns='metric', values='value').reset_index()
column_names = {
    'year': 'Год',
    'co2_scope1_2_total_tons': 'CO₂ (т)',
    'co2_intensity_per_mwh': 'CO₂ интенсивность',
    'women_management_percent': 'Женщины в упр. (%)',
    'women_percent': 'Женщины (%)',
    'turnover_total': 'Текучесть (%)',
    'turnover_unwanted': 'Нежел. текучесть (%)',
    'staff_total': 'Сотрудники',
    'water_withdrawal_megaliters': 'Вода (мегалитры)',
    'waste_total_tons': 'Отходы (т)',
    'pue_average': 'PUE',
    'interns': 'Стажёры',
    'rounding_users': 'Пользователи',
    'ngo_partners': 'НКО-партнёры',
    'free_taxi_rides_for_ngo_thousands': 'Поездки НКО (тыс)',
    'taxi_emissions_moscow_g_per_passenger_km': 'CO₂ такси (г/км)'
}
table_data = table_data.rename(columns=column_names)
st.dataframe(table_data, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Данные: ESG-отчёты Яндекса | Матрица существенности на основе отраслевых данных | Цели SDG: Цель 5 (гендерное равенство), Цель 13 (климат)")