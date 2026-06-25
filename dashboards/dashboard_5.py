import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

# Импортируем обе функции из llm_helper
from utils.llm_helper import generate_commentary, generate_surprise_analysis

st.set_page_config(
    page_title="Прогнозы vs Факт • Яндекс",
    page_icon="🎯",
    layout="wide"
)

# Загрузка данных
@st.cache_data
def load_consensus_data():
    return pd.read_csv('data/analyst_consensus.csv')

@st.cache_data
def load_news_data():
    return pd.read_csv('data/news_with_sentiment.csv', parse_dates=['date'])

consensus_df = load_consensus_data()
news_df = load_news_data()

# Боковая панель
st.sidebar.title("Прогнозы vs Факт")
st.sidebar.markdown("---")

metric_options = {
    'revenue': 'Выручка',
    'ebitda': 'EBITDA',
    'net_income': 'Чистая прибыль'
}
selected_metric = st.sidebar.selectbox(
    "Выберите метрику",
    options=list(metric_options.keys()),
    format_func=lambda x: metric_options[x]
)

quarters = consensus_df['quarter'].tolist()
selected_quarters = st.sidebar.multiselect(
    "Выберите кварталы",
    options=quarters,
    default=quarters[-4:]
)

if selected_quarters:
    df_filtered = consensus_df[consensus_df['quarter'].isin(selected_quarters)]
else:
    df_filtered = consensus_df

st.sidebar.markdown("---")
st.sidebar.caption(f"Кварталов показано: {len(df_filtered)}")

# Основная часть
st.title("Сравнение прогнозов аналитиков с фактическими результатами")
st.markdown("---")

# KPI
col1, col2, col3 = st.columns(3)

forecast_col = f"{selected_metric}_forecast"
actual_col = f"{selected_metric}_actual"

if len(df_filtered) > 0:
    last_row = df_filtered.iloc[-1]
    last_forecast = last_row[forecast_col]
    last_actual = last_row[actual_col]
    surprise = ((last_actual - last_forecast) / abs(last_forecast)) * 100 if last_forecast != 0 else 0

    avg_forecast = df_filtered[forecast_col].mean()
    avg_actual = df_filtered[actual_col].mean()
    avg_surprise = ((avg_actual - avg_forecast) / abs(avg_forecast)) * 100 if avg_forecast != 0 else 0

    with col1:
        st.metric(
            f"{metric_options[selected_metric]} (последний квартал)",
            f"{last_actual:,.0f} млн ₽",
            f"{surprise:+.1f}% vs прогноз"
        )
    with col2:
        st.metric(
            "Средний прогноз",
            f"{avg_forecast:,.0f} млн ₽",
            f"{avg_surprise:+.1f}% среднее отклонение"
        )
    with col3:
        st.metric(
            "Количество кварталов",
            f"{len(df_filtered)}"
        )
else:
    with col1:
        st.metric("Нет данных", "—")
    with col2:
        st.metric("Нет данных", "—")
    with col3:
        st.metric("Кварталов", "0")

st.markdown("---")

# График сравнения
st.subheader(f"Сравнение прогнозов и факта: {metric_options[selected_metric]}")

col_graph, col_comment = st.columns([3, 1])

with col_graph:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_filtered['quarter'],
        y=df_filtered[actual_col],
        name='Факт',
        mode='lines+markers',
        line=dict(color='#2E86C1', width=3),
        marker=dict(size=10)
    ))
    fig.add_trace(go.Scatter(
        x=df_filtered['quarter'],
        y=df_filtered[forecast_col],
        name='Прогноз',
        mode='lines+markers',
        line=dict(color='#E67E22', width=3, dash='dash'),
        marker=dict(size=10, symbol='diamond')
    ))
    fig.update_layout(
        title=f'{metric_options[selected_metric]} — прогноз vs факт',
        xaxis_title='Квартал',
        yaxis_title=f'{metric_options[selected_metric]} (млн ₽)',
        height=400,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=10, r=10, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_comment:
    st.subheader("Комментарий LLM")
    values = df_filtered[actual_col].tolist()
    comment = generate_commentary(selected_metric, values)
    st.info(comment)

st.markdown("---")

# Earnings Surprise
st.subheader("Earnings Surprise (отклонения)")

df_filtered['surprise'] = ((df_filtered[actual_col] - df_filtered[forecast_col]) / abs(df_filtered[forecast_col])) * 100
df_filtered['surprise_color'] = df_filtered['surprise'].apply(
    lambda x: 'positive' if x > 0 else 'negative' if x < 0 else 'neutral'
)

fig_surprise = px.bar(
    df_filtered,
    x='quarter',
    y='surprise',
    color='surprise_color',
    title='Earnings Surprise по кварталам',
    labels={'quarter': 'Квартал', 'surprise': 'Отклонение (%)'},
    color_discrete_map={'positive': '#2ECC71', 'negative': '#E74C3C', 'neutral': '#F1C40F'}
)
fig_surprise.update_layout(
    height=350,
    template='plotly_white',
    margin=dict(l=10, r=10, t=40, b=20),
    showlegend=False
)
st.plotly_chart(fig_surprise, use_container_width=True)

st.markdown("---")

# LLM-анализ причин расхождений (используем функцию из llm_helper)
st.subheader("Анализ причин расхождений")

if len(df_filtered) > 0:
    max_surprise_idx = df_filtered['surprise'].abs().idxmax()
    max_surprise_row = df_filtered.loc[max_surprise_idx]
    max_surprise = max_surprise_row['surprise']

    quarter_str = max_surprise_row['quarter']
    try:
        year = int(quarter_str.split('-')[0])
        news_for_period = news_df[news_df['date'].dt.year == year]
        news_texts = news_for_period['title'].tolist() if len(news_for_period) > 0 else []
    except:
        news_texts = []

    st.write(f"**Квартал с максимальным отклонением:** {quarter_str}")
    st.write(f"Отклонение: **{max_surprise:+.1f}%**")

    # Вызываем функцию из llm_helper
    analysis = generate_surprise_analysis(
        max_surprise_row[actual_col],
        max_surprise_row[forecast_col],
        news_texts
    )
    st.info(analysis)
else:
    st.write("Нет данных для анализа.")

st.markdown("---")

# Таблица
st.subheader("Детальные данные по кварталам")

display_df = df_filtered.copy()
display_df['surprise'] = display_df['surprise'].apply(lambda x: f"{x:+.1f}%")
display_df[forecast_col] = display_df[forecast_col].apply(lambda x: f"{x:,.0f}")
display_df[actual_col] = display_df[actual_col].apply(lambda x: f"{x:,.0f}")

display_df = display_df.rename(columns={
    'quarter': 'Квартал',
    forecast_col: 'Прогноз',
    actual_col: 'Факт',
    'surprise': 'Отклонение'
})
st.dataframe(display_df[['Квартал', 'Прогноз', 'Факт', 'Отклонение']],
             use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Данные: консенсус-прогнозы аналитиков | Источник новостей: официальные пресс-релизы Яндекса")