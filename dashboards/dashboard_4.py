import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path
import base64
import plotly.graph_objects as go

sys.path.append(str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Мониторинг рисков - Яндекс",
    page_icon="⚠️",
    layout="wide"
)


# Загрузка данных
@st.cache_data
def load_risk_data():
    df = pd.read_csv('data/risk_factors.csv')
    return df


df = load_risk_data()

# Настройка фильтров
st.sidebar.title("Мониторинг рисков")
st.sidebar.markdown("---")

# Фильтр по категории риска
all_categories = df['risk_category'].unique().tolist()
selected_categories = st.sidebar.multiselect("Выберите категории рисков", options=all_categories, default=all_categories)

# Фильтр по уровню риска
st.sidebar.markdown("---")
st.sidebar.subheader("Фильтр по уровню риска")
min_prob = st.sidebar.slider("Минимальная вероятность", 0.0, 1.0, 0.0, 0.05)
min_impact = st.sidebar.slider("Минимальное влияние", 0.0, 1.0, 0.0, 0.05)

df_filtered = df.copy()
if selected_categories:
    df_filtered = df_filtered[df_filtered['risk_category'].isin(selected_categories)]
df_filtered = df_filtered[(df_filtered['probability'] >= min_prob) & (df_filtered['impact'] >= min_impact)]

st.sidebar.markdown("---")
st.sidebar.caption(f"Рисков показано: {len(df_filtered)}")


st.title("Мониторинг рисков портфеля")
st.markdown("---")

# 1 - KPI
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_risks = len(df)
    filtered_risks = len(df_filtered)
    st.metric("Количество рисков", filtered_risks)
    
    if filtered_risks == total_risks:
        sub_text = "Показаны все риски"
    else:
        sub_text = f"Показано {filtered_risks} из {total_risks}"
    
    st.markdown(
        f'<div style="background-color:#E5E7EB; padding:4px 12px; border-radius:12px; font-size:12px; color:#4B5563; display:inline-block;">{sub_text}</div>',
        unsafe_allow_html=True
    )

with col2:
    critical_risks = df_filtered[(df_filtered['probability'] >= 0.6) & (df_filtered['impact'] >= 0.7)]
    st.metric("Критические", len(critical_risks))
    
    if len(critical_risks) > 0:
        st.markdown(
            '<div style="background-color:#FEE2E2; padding:4px 12px; border-radius:12px; font-size:12px; color:#991B1B; display:inline-block;">Требуют срочных мер</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="background-color:#D1FAE5; padding:4px 12px; border-radius:12px; font-size:12px; color:#065F46; display:inline-block;">Не обнаружено</div>',
            unsafe_allow_html=True
        )

with col3:
    high_risk = df_filtered[(df_filtered['probability'] >= 0.5) & (df_filtered['impact'] >= 0.6)]
    st.metric("Высокорисковые", len(high_risk))
    st.markdown(
        '<div style="background-color:#D4E6FF; padding:4px 12px; border-radius:12px; font-size:12px; color:#1E3A8A; display:inline-block;">Требуют внимания</div>',
        unsafe_allow_html=True
    )

with col4:
    if len(df_filtered) > 0:
        max_prob = df_filtered['probability'].max()
        max_prob_name = df_filtered[df_filtered['probability'] == max_prob]['risk_name'].values[0]
        st.metric("Максимальная вероятность", f"{max_prob:.0%}")
        st.markdown(
            f'<div style="background-color:#FEE2E2; padding:4px 12px; border-radius:12px; font-size:12px; color:#991B1B; display:inline-block;">{max_prob_name}</div>',
            unsafe_allow_html=True
        )
    else:
        st.metric("Максимальная вероятность", "—")

with col5:
    if len(df_filtered) > 0:
        max_impact = df_filtered['impact'].max()
        max_impact_name = df_filtered[df_filtered['impact'] == max_impact]['risk_name'].values[0]
        st.metric("Максимальное влияние", f"{max_impact:.0%}")
        st.markdown(
            f'<div style="background-color:#FEE2E2; padding:4px 12px; border-radius:12px; font-size:12px; color:#991B1B; display:inline-block;">{max_impact_name}</div>',
            unsafe_allow_html=True
        )
    else:
        st.metric("Максимальное влияние", "—")

st.markdown("---")

# 2 - Тепловая карта рисков
if 'selected_risk' not in st.session_state:
    st.session_state.selected_risk = None

col_heatmap, col_details = st.columns([3, 1])

with col_heatmap:
    st.subheader("📍 Тепловая карта рисков")

    x_edges = [i / 10 for i in range(11)]
    y_edges = [i / 10 for i in range(11)]
    z_data = [[(i + j) / 20 for j in range(10)] for i in range(10)]

    colorscale = [
        [0.0, '#93C677'], 
        [0.1, '#A4CF79'], 
        [0.2, '#B5DA78'],
        [0.3, '#C7E47B'], 
        [0.4, '#DAED7C'], 
        [0.5, '#EDF87D'],
        [0.6, '#F5E585'], 
        [0.7, "#F4D282"], 
        [0.8, "#EAB383"],
        [0.9, '#F68F6D'], 
        [1.0, '#FF7A71']
    ]

    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        x=x_edges, y=y_edges, z=z_data,
        colorscale=colorscale, showscale=False,
        hoverinfo='skip', opacity=1.0
    ))

    # Точки рисков (по категориям)
    color_map = {
        'financial': '#8D77FF',
        'esg': '#2447FF',
        'reputational': '#52E3E9'
    }

    for category in df_filtered['risk_category'].unique():
        subset = df_filtered[df_filtered['risk_category'] == category]
        color = color_map.get(category, '#888')
        fig.add_trace(go.Scatter(
            x=subset['impact'],
            y=subset['probability'],
            mode='markers',
            name=category,
            marker=dict(
                size=subset['impact'] * 30 + 5,
                color=color_map.get(category, '#888'),
                opacity=1.0,
                line=dict(width=1, color=color)
            ),
            text=subset['risk_name'],
            customdata=subset[['risk_name', 'risk_category', 'probability', 'impact']].values.tolist(),
            hovertemplate=('<b style="font-size:15px; color:#31333E;">%{text}</b><extra></extra>'),
            hoverlabel=dict(bordercolor=color)
        ))

    for i in range(11):
        fig.add_hline(y=i/10, line=dict(color='gray', width=0.5, dash='solid'), opacity=0.3)
        fig.add_vline(x=i/10, line=dict(color='gray', width=0.5, dash='solid'), opacity=0.3)

    fig.update_layout(
        height=500,
        hovermode='closest',
        template='plotly_white',
        xaxis=dict(range=[0, 1], dtick=0.1, title='Влияние', showgrid=False, zeroline=False),
        yaxis=dict(range=[0, 1], dtick=0.1, title='Вероятность', showgrid=False, zeroline=False),
        margin=dict(l=10, r=10, t=40, b=20),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='top',
            y=-0.2,
            xanchor='center',
            x=0.5
        )
    )

    # Обработка клика для получения деталей риска
    selected = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")

    if selected and hasattr(selected, 'selection') and selected.selection and selected.selection.points:
        point = selected.selection.points[0]
        custom = point.get('customdata')
        if custom:
            st.session_state.selected_risk = {
                'name': custom[0],
                'category': custom[1],
                'probability': custom[2],
                'impact': custom[3]
            }

with col_details:
    st.subheader("🔎 Детали риска")
    if st.session_state.selected_risk:
        risk = st.session_state.selected_risk
        st.markdown(f"**Название:** {risk['name']}")
        st.markdown(f"**Категория:** {risk['category']}")
        st.markdown(f"**Вероятность:** {risk['probability']:.0%}")
        st.markdown(f"**Влияние:** {risk['impact']:.0%}")
        color = color_map.get(risk['category'], '#888')
        st.markdown(f"<div style='width:100%;height:10px;background-color:{color};border-radius:5px;'></div>", unsafe_allow_html=True)
        if st.button("Сбросить выбор"):
            st.session_state.selected_risk = None
            st.rerun()
    else:
        st.info("👆🏻 Кликните на точку на тепловой карте, чтобы увидеть детали.")

st.markdown("---")

# 3 - Алерты
st.subheader("📌 Алерты по рискам")

# Критические риски
critical_risks = df_filtered[(df_filtered['probability'] >= 0.6) & (df_filtered['impact'] >= 0.7)]

if len(critical_risks) > 0:
    st.error(f"⚠️ **Обнаружено {len(critical_risks)} критических рисков!**")
    for _, row in critical_risks.iterrows():
        st.markdown(f"🔴 **{row['risk_name']}** ({row['risk_category']}) — Вероятность: {row['probability']:.0%}, Влияние: {row['impact']:.0%}")
else:
    st.success("✅ Критических рисков не обнаружено. Все риски под контролем.")

# Риски, требующие внимания
warning_risks = df_filtered[
    ((df_filtered['probability'] >= 0.5) & (df_filtered['impact'] >= 0.6)) &
    ~((df_filtered['probability'] >= 0.6) & (df_filtered['impact'] >= 0.7))
]

if len(warning_risks) > 0:
    st.info(f"⚠️ {len(warning_risks)} рисков требуют внимания!")
    for _, row in warning_risks.iterrows():
        st.caption(f"🟡 **{row['risk_name']}** — Вероятность: {row['probability']:.0%}, Влияние: {row['impact']:.0%}")

st.markdown("---")

# 4 - Таблица рисков
st.subheader("📋 Полный список рисков")

df_sorted = df_filtered.sort_values(['probability', 'impact'], ascending=[False, False])

display_df = df_sorted.copy()
display_df['probability'] = display_df['probability'].apply(lambda x: f"{x:.0%}")
display_df['impact'] = display_df['impact'].apply(lambda x: f"{x:.0%}")

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")

# 5 - Генерация risk-отчёта в PDF
st.subheader("📄 Генерация Risk-отчёта")

if st.button("Скачать отчёт в PDF"):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import io
    import os

    font_path = None
    possible_paths = [
        '/Library/Fonts/Arial.ttf',
        '/System/Library/Fonts/Supplemental/Arial.ttf',
        '/usr/share/fonts/truetype/msttcorefonts/Arial.ttf',
        'C:/Windows/Fonts/arial.ttf'
    ]
    for path in possible_paths:
        if os.path.exists(path):
            font_path = path
            break

    if font_path is None:
        st.error("⚠️ Шрифт Arial не найден. Установите шрифт для корректного отображения кириллицы.")
        st.stop()

    pdfmetrics.registerFont(TTFont('Arial', font_path))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=30)

    styles = getSampleStyleSheet()
    style_title = ParagraphStyle('Title', parent=styles['Title'], fontName='Arial', fontSize=16, alignment=TA_CENTER)
    style_date = ParagraphStyle('Date', parent=styles['Normal'], fontName='Arial', fontSize=10, alignment=TA_CENTER)
    style_filter = ParagraphStyle('Filter', parent=styles['Normal'], fontName='Arial', fontSize=9, alignment=TA_LEFT)
    style_header = ParagraphStyle('Header', parent=styles['Normal'], fontName='Arial', fontSize=12, alignment=TA_LEFT, spaceAfter=6)
    style_risk = ParagraphStyle('Risk', parent=styles['Normal'], fontName='Arial', fontSize=9, alignment=TA_LEFT)
    style_critical_header = ParagraphStyle('CriticalHeader', parent=styles['Normal'], fontName='Arial', fontSize=10, alignment=TA_LEFT, spaceAfter=6)

    story = []

    # Заголовок, дата, фильтры
    story.append(Paragraph("Отчёт по рискам портфеля", style_title))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Дата генерации: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", style_date))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Категории: {', '.join(selected_categories) if selected_categories else 'Все'}", style_filter))
    story.append(Paragraph(f"Фильтр по вероятности: ≥ {min_prob:.0%}", style_filter))
    story.append(Paragraph(f"Фильтр по влиянию: ≥ {min_impact:.0%}", style_filter))
    story.append(Spacer(1, 12))

    # Таблица рисков
    table_data = [["Риск", "Категория риска", "Вероятность", "Влияние"]]
    for _, row in df_filtered.iterrows():
        table_data.append([
            row['risk_name'],
            row['risk_category'],
            f"{row['probability']:.0%}",
            f"{row['impact']:.0%}"
        ])

    col_widths = [180, 100, 70, 70]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    story.append(Paragraph(f"Список рисков ({len(df_filtered)})", style_header))
    story.append(Spacer(1, 6))
    story.append(table)
    story.append(Spacer(1, 12))

    # Список критических рисков
    critical = df_filtered[(df_filtered['probability'] >= 0.6) & (df_filtered['impact'] >= 0.7)]
    story.append(Paragraph("Критические риски:", style_critical_header))
    if len(critical) > 0:
        for _, row in critical.iterrows():
            text = f"{row['risk_name']} ({row['risk_category']}) — Вероятность: {row['probability']:.0%}, Влияние: {row['impact']:.0%}"
            story.append(Paragraph(text, style_risk))
    else:
        story.append(Paragraph("Критических рисков не обнаружено.", style_risk))

    story.append(Spacer(1, 12))

    # Риски, требующие внимания
    warning_risks = df_filtered[(df_filtered['probability'] >= 0.5) & (df_filtered['impact'] >= 0.6) & ~((df_filtered['probability'] >= 0.6) & (df_filtered['impact'] >= 0.7))]
    story.append(Paragraph("Риски, требующие внимания:", style_critical_header))
    if len(warning_risks) > 0:
        for _, row in warning_risks.iterrows():
            text = f"{row['risk_name']} ({row['risk_category']}) — Вероятность: {row['probability']:.0%}, Влияние: {row['impact']:.0%}"
            story.append(Paragraph(text, style_risk))
    else:
        story.append(Paragraph("Рисков, требующих внимания, не обнаружено.", style_risk))

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    b64 = base64.b64encode(pdf_bytes).decode()

    href = f'<a href="data:application/octet-stream;base64,{b64}" download="risk_report_{pd.Timestamp.now().strftime("%Y%m%d")}.pdf"> Скачать PDF</a>'
    st.markdown(href, unsafe_allow_html=True)


st.markdown("---")
st.caption("📊 Данные: финансовые и ESG-метрики Яндекса")