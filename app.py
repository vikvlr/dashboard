import streamlit as st

st.set_page_config(page_title="Дашборды Яндекса", page_icon="📊", layout="wide")

st.sidebar.title("Дашборды для анализа компании Яндекс")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Выберите дашборд",
    [
        "Главная",
        "Финансовое здоровье",
        "ESG-аналитика",
        "Интегрированный анализ",
        "Мониторинг рисков",
        "Прогнозы vs Факт"
    ]
)

if page == "Главная":
    st.title("Дашборды для анализа компании Яндекс")
    st.markdown("---")

    st.markdown("""
    <div style="margin-bottom: 24px;">
        <p style="font-size: 16px; color: #4B5563; margin: 0;">
            Дашборды построены на основе финансовых, ESG-данных и новостного фона компании Яндекс.
            Используются реальные данные из отчётности за 2021–2024 гг.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style="
                background-color: #f8f9fa;
                padding: 16px 18px;
                border-radius: 12px;
                margin-bottom: 12px;
                border-left: 4px solid #2E86C1;
            ">
                <h4 style="margin: 0 0 8px 0; color: #1E3A5F;">Финансовое здоровье</h4>
                <p style="margin: 0; font-size: 14px; color: #4B5563;">
                    — Ключевые финансовые метрики<br>
                    — Динамика показателей и LLM-комментарии<br>
                    — Детализация по кварталам
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="
                background-color: #f8f9fa;
                padding: 16px 18px;
                border-radius: 12px;
                margin-bottom: 12px;
                border-left: 4px solid #E67E22;
            ">
                <h4 style="margin: 0 0 8px 0; color: #1E3A5F;">Интегрированный анализ</h4>
                <p style="margin: 0; font-size: 14px; color: #4B5563;">
                    — Финансы, ESG, новости и акции на одном экране<br>
                    — Корреляционный анализ<br>
                    — Таймлайн событий
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div style="
                background-color: #f8f9fa;
                padding: 16px 18px;
                border-radius: 12px;
                margin-bottom: 12px;
                border-left: 4px solid #28A745;
            ">
                <h4 style="margin: 0 0 8px 0; color: #1E3A5F;">ESG-аналитика</h4>
                <p style="margin: 0; font-size: 14px; color: #4B5563;">
                    — Динамика ESG-метрик<br>
                    — Матрица существенности<br>
                    — Сравнение с бенчмарками и целями SDGs
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="
                background-color: #f8f9fa;
                padding: 16px 18px;
                border-radius: 12px;
                margin-bottom: 12px;
                border-left: 4px solid #E74C3C;
            ">
                <h4 style="margin: 0 0 8px 0; color: #1E3A5F;">Мониторинг рисков</h4>
                <p style="margin: 0; font-size: 14px; color: #4B5563;">
                    — Тепловая карта рисков<br>
                    — Алерты при изменении профилей<br>
                    — Автоматическая генерация PDF-отчёта
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div style="
                background-color: #f8f9fa;
                padding: 16px 18px;
                border-radius: 12px;
                margin-bottom: 12px;
                border-left: 4px solid #8E44AD;
            ">
                <h4 style="margin: 0 0 8px 0; color: #1E3A5F;">Прогнозы vs Факт</h4>
                <p style="margin: 0; font-size: 14px; color: #4B5563;">
                    — Сравнение прогнозов и факта<br>
                    — Earnings surprise<br>
                    — LLM-анализ расхождений
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.caption("Выберите дашборд в боковой панели для начала работы")

elif page == "Финансовое здоровье":
    import dashboards.dashboard_1 as d1

elif page == "ESG-аналитика":
    import dashboards.dashboard_2 as d2

elif page == "Интегрированный анализ":
    import dashboards.dashboard_3 as d3

elif page == "Мониторинг рисков":
    import dashboards.dashboard_4 as d4

elif page == "Прогнозы vs Факт":
    import dashboards.dashboard_5 as d5
