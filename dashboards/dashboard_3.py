import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Интегрированный анализ", layout="wide")

def clean_number(x):
    if isinstance(x, str):
        x = x.replace(",", "")
        if "M" in x:
            return float(x.replace("M", "")) * 1_000_000
        if "K" in x:
            return float(x.replace("K", "")) * 1000
        return float(x)
    return float(x)

@st.cache_data
def load_financial_data():
    df = pd.read_csv('data/yandex_financial.csv', parse_dates=['date'])
    return df

@st.cache_data
def load_esg_data():
    return pd.read_csv('data/yandex_esg.csv')

@st.cache_data
def load_stock_data():
    df = pd.read_csv('data/yandex_stock.csv', parse_dates=['date'])
    df['close'] = df['close'].apply(clean_number)
    df['volume'] = df['volume'].apply(clean_number)
    return df

@st.cache_data
def load_news_data():
    df = pd.read_csv('data/news_with_sentiment.csv', parse_dates=['date'])
    return df

fin_df = load_financial_data()
esg_df = load_esg_data()
stock_df = load_stock_data()
news_df = load_news_data()

st.sidebar.title("Интегрированный анализ")
st.sidebar.markdown("---")

min_date = fin_df['date'].min().to_pydatetime()
max_date = fin_df['date'].max().to_pydatetime()

date_range = st.sidebar.slider(
    "Выберите период",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

fin_filtered = fin_df[(fin_df['date'] >= date_range[0]) & (fin_df['date'] <= date_range[1])]
stock_filtered = stock_df[(stock_df['date'] >= date_range[0]) & (stock_df['date'] <= date_range[1])]
news_filtered = news_df[(news_df['date'] >= date_range[0]) & (news_df['date'] <= date_range[1])]

st.sidebar.markdown("---")
st.sidebar.caption(f"Данных за период: {len(fin_filtered)} кварталов")
st.sidebar.caption(f"Новостей: {len(news_filtered)}")

st.title("Интегрированный анализ компании Яндекс")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

last_fin = fin_filtered.iloc[-1] if len(fin_filtered) > 0 else None
last_stock = stock_filtered.iloc[-1] if len(stock_filtered) > 0 else None
avg_sentiment = news_filtered['sentiment_score'].mean() if len(news_filtered) > 0 else 0

with col1:
    if last_stock is not None:
        stock_change = 0
        if len(stock_filtered) > 1:
            prev_stock = stock_filtered.iloc[-2]['close']
            stock_change = ((last_stock['close'] - prev_stock) / prev_stock) * 100
        st.metric("Цена акций", f"{last_stock['close']:.2f} ₽", f"{stock_change:+.2f}%")
    else:
        st.metric("Цена акций", "Нет данных")

with col2:
    st.metric("Тональность новостей", f"{avg_sentiment:.2f}", f"{len(news_filtered)} событий")

with col3:
    if last_fin is not None:
        st.metric("ROE (последний)", f"{last_fin['roe']:.2%}")
    else:
        st.metric("ROE", "Нет данных")

with col4:
    if last_fin is not None:
        st.metric("Долг/Капитал", f"{last_fin['debt_to_equity']:.2f}")
    else:
        st.metric("Долг/Капитал", "Нет данных")

st.markdown("---")

st.subheader("Основные показатели")
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    fig_stock = px.line(
        stock_filtered,
        x='date',
        y='close',
        title='Динамика цены акций',
        labels={'date': 'Дата', 'close': 'Цена (₽)'}
    )
    fig_stock.update_layout(height=350, hovermode='x unified', template='plotly_white')
    st.plotly_chart(fig_stock, use_container_width=True)

with col_graph2:
    fig_revenue = px.bar(
        fin_filtered,
        x='date',
        y='revenue',
        title='Выручка по кварталам',
        labels={'date': 'Дата', 'revenue': 'Выручка (млн ₽)'},
        color_discrete_sequence=['#2E86C1']
    )
    fig_revenue.update_layout(height=350, hovermode='x unified', template='plotly_white')
    st.plotly_chart(fig_revenue, use_container_width=True)

st.markdown("---")

st.subheader("Новостной фон и тональность")
col_news1, col_news2 = st.columns([2, 1])

with col_news1:
    fig_news = px.bar(
        news_filtered,
        x='date',
        y='sentiment_score',
        color='sentiment_score',
        color_continuous_scale=['red', 'yellow', 'green'],
        title='Тональность новостей (-1 до +1)',
        labels={'date': 'Дата', 'sentiment_score': 'Тональность'},
        text='title'
    )
    fig_news.update_traces(textposition='outside', textfont_size=8)
    fig_news.update_layout(height=350, template='plotly_white')
    st.plotly_chart(fig_news, use_container_width=True)

with col_news2:
    st.subheader("Статистика")
    st.metric("Всего новостей", len(news_filtered))
    st.metric("Средняя тональность", f"{avg_sentiment:.2f}")
    positive = len(news_filtered[news_filtered['sentiment_score'] > 0.3])
    negative = len(news_filtered[news_filtered['sentiment_score'] < -0.3])
    neutral = len(news_filtered[(news_filtered['sentiment_score'] >= -0.3) & (news_filtered['sentiment_score'] <= 0.3)])
    st.write(f"🟢 Позитивных: {positive}")
    st.write(f"🔴 Негативных: {negative}")
    st.write(f"⚪ Нейтральных: {neutral}")

st.markdown("---")

st.subheader("Корреляция: нефинансовые события и рыночная динамика")

news_sentiment_daily = news_filtered.groupby('date')['sentiment_score'].mean().reset_index()
news_sentiment_daily.columns = ['date', 'sentiment_avg']
corr_data = stock_filtered.merge(news_sentiment_daily, on='date', how='inner')

if len(corr_data) > 1:
    corr_value = corr_data['close'].corr(corr_data['sentiment_avg'])
    col_corr1, col_corr2 = st.columns(2)
    with col_corr1:
        fig_corr = px.scatter(
            corr_data,
            x='sentiment_avg',
            y='close',
            title=f'Корреляция цены и тональности (r = {corr_value:.2f})',
            labels={'sentiment_avg': 'Тональность', 'close': 'Цена (₽)'},
            trendline='ols',
            color='date'
        )
        fig_corr.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig_corr, use_container_width=True)
    with col_corr2:
        st.subheader("Интерпретация")
        if corr_value > 0.7:
            st.success(f"Сильная положительная корреляция ({corr_value:.2f})")
            st.write("Рост позитивных новостей связан с ростом цены акций.")
        elif corr_value > 0.3:
            st.info(f"Умеренная положительная корреляция ({corr_value:.2f})")
            st.write("Новостной фон влияет на цену акций.")
        elif corr_value > -0.3:
            st.warning(f"Слабая корреляция ({corr_value:.2f})")
            st.write("Влияние новостей на цену акций ограничено.")
        else:
            st.error(f"Отрицательная корреляция ({corr_value:.2f})")
            st.write("Позитивные новости могут сопровождаться падением цены.")
else:
    st.warning("Недостаточно данных для корреляционного анализа")

st.markdown("---")

st.subheader("Таймлайн событий с автоматической разметкой")
col_timeline1, col_timeline2 = st.columns([3, 1])

with col_timeline1:
    fig_timeline = px.scatter(
        news_filtered,
        x='date',
        y='sentiment_score',
        color='sentiment_score',
        text='title',
        title='Таймлайн событий',
        labels={'date': 'Дата', 'sentiment_score': 'Тональность'},
        color_continuous_scale=['red', 'yellow', 'green'],
        hover_data={'title': True}
    )
    fig_timeline.update_traces(textposition='top center', textfont_size=8)
    fig_timeline.update_layout(height=500, template='plotly_white')
    st.plotly_chart(fig_timeline, use_container_width=True)

with col_timeline2:
    st.subheader("Легенда")
    st.markdown("**Цвета:**")
    st.markdown("🟢 **Зелёный** – позитивные (> 0.3)")
    st.markdown("🟡 **Жёлтый** – нейтральные (-0.3 до 0.3)")
    st.markdown("🔴 **Красный** – негативные (< -0.3)")
    st.markdown("---")
    st.markdown("**Размер точки:**")
    st.markdown("Чем больше точка – тем сильнее событие повлияло на тональность.")

st.markdown("---")

st.subheader("Последние события")
for _, row in news_filtered.tail(3).iterrows():
    emoji = "🟢" if row['sentiment_score'] > 0.3 else "🔴" if row['sentiment_score'] < -0.3 else "🟡"
    st.caption(f"{emoji} {row['date'].strftime('%Y-%m-%d')}")
    st.caption(f"{row['title'][:50]}...")
    st.markdown("---")

st.subheader("Детализация по периоду")

if len(fin_filtered) > 0:
    selected_date = st.selectbox(
        "Выберите квартал для детализации",
        options=fin_filtered['date'].dt.strftime('%Y-%m-%d').tolist(),
        index=len(fin_filtered) - 1
    )
    selected_row = fin_filtered[fin_filtered['date'] == pd.to_datetime(selected_date)].iloc[0]

    col_detail1, col_detail2 = st.columns(2)
    with col_detail1:
        st.write("**Финансовые показатели**")
        detail_data = {
            "Показатель": ["Выручка", "Чистая прибыль", "EBITDA", "ROE", "ROA", "ROS"],
            "Значение": [
                f"{selected_row['revenue']:,.0f} млн ₽",
                f"{selected_row['net_income']:,.0f} млн ₽",
                f"{selected_row['ebitda']:,.0f} млн ₽",
                f"{selected_row['roe']:.2%}",
                f"{selected_row['roa']:.2%}",
                f"{selected_row['ros']:.2%}"
            ]
        }
        st.dataframe(pd.DataFrame(detail_data), hide_index=True, use_container_width=True)

    with col_detail2:
        st.write("**Новости периода**")
        quarter_start = pd.to_datetime(selected_date) - pd.DateOffset(months=3)
        quarter_news = news_filtered[
            (news_filtered['date'] >= quarter_start) &
            (news_filtered['date'] <= pd.to_datetime(selected_date))
        ]
        if len(quarter_news) > 0:
            for _, row in quarter_news.tail(3).iterrows():
                emoji = "🟢" if row['sentiment_score'] > 0.3 else "🔴" if row['sentiment_score'] < -0.3 else "🟡"
                st.caption(f"{emoji} {row['title'][:50]}...")
        else:
            st.caption("Новостей за период нет.")

st.markdown("---")
st.caption("Данные: финансовые отчёты, ESG-отчёты, новости и рыночные данные Яндекс")