import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.llm_helper import generate_commentary

st.set_page_config(
    page_title="Финансовое здоровье - Яндекс",
    page_icon="📊",
    layout="wide"
)


# Загрузка финансовых данных
@st.cache_data
def load_data():
    df = pd.read_csv('data/yandex_financial.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df


df = load_data()

# Настройка фильтров
st.sidebar.title("Финансовое здоровье")
st.sidebar.markdown("---")

# Выбор метрики для графика
metric = st.sidebar.selectbox(
    "Выберите метрику",
    options=['revenue', 'net_income', 'ebitda', 'current_ratio', 'quick_ratio',
             'cash_ratio', 'equity_ratio', 'roe', 'roa', 'ros', 'debt_to_equity'],
    format_func=lambda x: {
        'revenue': 'Выручка (млн руб)',
        'net_income': 'Чистая прибыль (млн руб)',
        'ebitda': 'EBITDA (млн руб)',
        'current_ratio': 'Текущая ликвидность',
        'quick_ratio': 'Быстрая ликвидность',
        'cash_ratio': 'Абсолютная ликвидность',
        'equity_ratio': 'Финансовая независимость',
        'roe': 'Рентабельность капитала (ROE)',
        'roa': 'Рентабельность активов (ROA)',
        'ros': 'Рентабельность продаж (ROS)',
        'debt_to_equity': 'Долговая нагрузка (D/E)'
    }[x]
)

# Выбор периода
min_date = df['date'].min().to_pydatetime()
max_date = df['date'].max().to_pydatetime()
default_start = min_date
default_end = max_date

date_range = st.sidebar.slider(
    "Выберите период",
    min_value=min_date,
    max_value=max_date,
    value=(default_start, default_end),
    format="YYYY-MM-DD"
)

df_filtered = df[(df['date'] >= date_range[0]) & (df['date'] <= date_range[1])]

st.sidebar.markdown("---")
st.sidebar.caption(f"Данных: {len(df_filtered)} кварталов")
st.sidebar.caption(f"Период: {date_range[0].strftime('%Y-%m')} — {date_range[1].strftime('%Y-%m')}")



st.title("Финансовое здоровье компании Яндекс")
st.markdown("---")

# 1 - KPI
col1, col2, col3, col4, col5 = st.columns(5)

last = df_filtered.iloc[-1]
prev = df_filtered.iloc[-2] if len(df_filtered) > 1 else last


def get_delta(current, previous):
    if previous == 0 or pd.isna(previous):
        return 0
    return (current - previous) / abs(previous)


with col1:
    delta = get_delta(last['revenue'], prev['revenue'])
    st.metric(
        "Выручка",
        f"{last['revenue']:,.0f} млн ₽",
        f"{delta:+.1%} к предыдущему"
    )

with col2:
    delta = get_delta(last['net_income'], prev['net_income'])
    st.metric(
        "Чистая прибыль",
        f"{last['net_income']:,.0f} млн ₽",
        f"{delta:+.1%} к предыдущему"
    )

with col3:
    st.metric(
        "EBITDA",
        f"{last['ebitda']:,.0f} млн ₽",
        f"{get_delta(last['ebitda'], prev['ebitda']):+.1%} к предыдущему"
    )

with col4:
    st.metric(
        "ROE",
        f"{last['roe']:.1%}",
        f"{get_delta(last['roe'], prev['roe']):+.1%} к предыдущему"
    )

with col5:
    st.metric(
        "Долговая нагрузка",
        f"{last['debt_to_equity']:.2f}",
        f"{get_delta(last['debt_to_equity'], prev['debt_to_equity']):+.1%} к предыдущему"
    )

st.markdown("---")

# 2 - Построение графика + LLM
col_graph, col_comment = st.columns([3, 1])

with col_graph:
    metric_labels = {
        'revenue': 'Выручка',
        'net_income': 'Чистая прибыль',
        'ebitda': 'EBITDA',
        'current_ratio': 'Текущая ликвидность',
        'quick_ratio': 'Быстрая ликвидность',
        'cash_ratio': 'Абсолютная ликвидность',
        'equity_ratio': 'Финансовая независимость',
        'roe': 'ROE',
        'roa': 'ROA',
        'ros': 'ROS',
        'debt_to_equity': 'Долговая нагрузка'
    }
    metric_label = metric_labels.get(metric, metric)
    st.subheader(f"📈 Динамика показателя: {metric_label}")

    fig = px.line(
        df_filtered,
        x='date',
        y=metric,
        title=f"{metric} — динамика по кварталам",
        markers=True,
        labels={'date': 'Дата', metric: metric}
    )

    fig.update_layout(
        height=400,
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=10, r=10, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

with col_comment:
    st.subheader("💡 Комментарий LLM")

    values = df_filtered[metric].tolist()

    # Генерируем LLM комментарий
    comment = generate_commentary(metric, values)
    st.info(comment)

st.markdown("---")


# 3 - Drill-down
st.subheader("🔎 Детализация по кварталам (Drill-down)")

selected_date = st.selectbox(
    "Выберите квартал для детализации",
    options=df_filtered['date'].dt.strftime('%Y-%m-%d').tolist(),
    index=len(df_filtered) - 1
)

selected_row = df_filtered[df_filtered['date'] == pd.to_datetime(selected_date)].iloc[0]

col_detail1, col_detail2 = st.columns(2)

with col_detail1:
    st.write("**Основные показатели**")
    detail_data = {
        "Показатель": ["Выручка", "Чистая прибыль", "EBITDA", "ROE", "ROA", "ROS"],
        "Значение": [
            f"{selected_row['revenue']:,.0f} млн руб",
            f"{selected_row['net_income']:,.0f} млн руб",
            f"{selected_row['ebitda']:,.0f} млн руб",
            f"{selected_row['roe']:.2%}",
            f"{selected_row['roa']:.2%}",
            f"{selected_row['ros']:.2%}"
        ]
    }
    st.dataframe(pd.DataFrame(detail_data), hide_index=True, use_container_width=True)

with col_detail2:
    st.write("**Финансовые коэффициенты**")
    detail_data2 = {
        "Показатель": ["Текущая ликвидность", "Быстрая ликвидность", "Абсолютная ликвидность", "Финансовая независимость", "Долг/Капитал"],
        "Значение": [
            f"{selected_row['current_ratio']:.2f}",
            f"{selected_row['quick_ratio']:.2f}",
            f"{selected_row['cash_ratio']:.2f}",
            f"{selected_row['equity_ratio']:.2%}",
            f"{selected_row['debt_to_equity']:.2f}"
        ]
    }
    st.dataframe(pd.DataFrame(detail_data2), hide_index=True, use_container_width=True)

# 4 - Дополнительные графики
st.markdown("---")
st.subheader("📊 Сводный анализ")

col_extra1, col_extra2 = st.columns(2)

# График корреляции ROE и ROA
with col_extra1:
    fig_trend = px.line(
        df_filtered,
        x='date',
        y=['roe', 'roa'],
        title='Динамика рентабельности: ROE и ROA',
        labels={'value': 'Рентабельность', 'date': 'Дата', 'variable': 'Показатель'},
        color_discrete_map={'roe': '#2E86C1', 'roa': '#E67E22'}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# График соотношения выручки, прибыли, EBITDA
with col_extra2:
    fig_bar = px.bar(
        df_filtered,
        x='date',
        y=['revenue', 'net_income', 'ebitda'],
        title='Выручка, EBITDA и чистая прибыль',
        labels={'value': 'Млн руб', 'date': 'Дата', 'variable': 'Показатель'},
        barmode='group'
    )
    st.plotly_chart(fig_bar, use_container_width=True)


st.markdown("---")
st.caption("📊 Данные: квартальные отчёты Яндекса 2021–2024 | 💡 Комментарии генерируются LLM")