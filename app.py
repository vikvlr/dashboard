import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Аналитика Яндекса", layout="wide")
st.title("📊 Интегрированный дашборд: Яндекс")

stock_df = pd.read_csv("data/yandex_stock.csv", parse_dates=["date"])
news_df = pd.read_csv("data/news_with_sentiment.csv", parse_dates=["date"])

st.subheader("📈 Динамика цены акций")
fig1 = px.line(stock_df, x="date", y="close", markers=True, title="Цена закрытия акций Яндекса")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📰 Тональность новостей")
fig2 = px.bar(news_df, x="date", y="sentiment_score",
              color="sentiment_score",
              color_continuous_scale=["red", "yellow", "green"],
              title="Тональность новостей (от -1 до +1)",
              text="title")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("📊 Ключевые показатели")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Максимальная цена акции", f"{stock_df['close'].max():.2f} ₽")
with col2:
    st.metric("Средняя тональность новостей", f"{news_df['sentiment_score'].mean():.2f}")
with col3:
    st.metric("Количество новостей", len(news_df))