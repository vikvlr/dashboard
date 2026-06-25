import streamlit as st

st.set_page_config(page_title="Дашборды Яндекса", page_icon="📊", layout="wide")

st.sidebar.title("🗺️ Навигация")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Выберите дашборд",
    [
        "Главная",
        "4.1 Финансовое здоровье",
        "4.2 ESG-аналитика",
        "4.3 Интегрированный анализ",
        "4.4 Мониторинг рисков",
        "4.5 Прогнозы vs Факт"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Проект: Дашборды для анализа компании Яндекс")
st.sidebar.caption("Команда: Вика, Стефа, Алена")

if page == "Главная":
    st.title("📊 Дашборды для анализа компании Яндекс")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Доступные дашборды

        **4.1 Финансовое здоровье** — Вика
        - Ключевые финансовые метрики
        - LLM-комментарии
        - Drill-down по кварталам

        **4.2 ESG-аналитика** — Стефа
        - ESG-метрики в динамике
        - Матрица существенности
        - Сравнение с бенчмарками

        **4.3 Интегрированный анализ** — Алена
        - Финансы + ESG + новости + акции
        - Корреляционный анализ
        - Таймлайн событий
        """)
    with col2:
        st.markdown("""
        ### Доступные дашборды

        **4.4 Мониторинг рисков** — Вика
        - Матрица рисков
        - Тепловая карта

        **4.5 Прогнозы vs Факт** — Стефа
        - Сравнение прогнозов
        - Earnings surprise
        - LLM-анализ расхождений
        """)
    st.markdown("---")
    st.caption("Выберите дашборд в боковой панели для начала работы")

elif page == "4.1 Финансовое здоровье":
    import dashboards.dashboard_1 as d1

elif page == "4.2 ESG-аналитика":
    import dashboards.dashboard_2 as d2

elif page == "4.3 Интегрированный анализ":
    import dashboards.dashboard_3 as d3

elif page == "4.4 Мониторинг рисков":
    import dashboards.dashboard_4 as d4

elif page == "4.5 Прогнозы vs Факт":
    import dashboards.dashboard_5 as d5