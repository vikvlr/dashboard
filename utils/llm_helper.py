import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_AVAILABLE = False
try:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False
    print("OpenAI API ключ не найден. Используется режим заглушки.")


def generate_commentary(metric_name, values):
    """
    Генерирует текстовый комментарий к графику на основе значений метрики.
    """

    metric_names = {
        'revenue': 'Выручка',
        'net_income': 'Чистая прибыль',
        'ebitda': 'EBITDA',
        'current_ratio': 'Текущая ликвидность',
        'quick_ratio': 'Быстрая ликвидность',
        'cash_ratio': 'Абсолютная ликвидность',
        'equity_ratio': 'Финансовая независимость',
        'roe': 'Рентабельность капитала (ROE)',
        'roa': 'Рентабельность активов (ROA)',
        'ros': 'Рентабельность продаж (ROS)',
        'debt_to_equity': 'Долговая нагрузка (D/E)'
    }

    name = metric_names.get(metric_name, metric_name)

    # Если нет данных
    if not values or len(values) == 0:
        return "⚠️ Недостаточно данных для анализа."

    # Если только одно значение
    if len(values) == 1:
        return f"📊 **{name}**: {values[0]:.2f}. Данных за один период недостаточно для выявления тренда."

    # Расчёт тренда
    first_val = values[0]
    last_val = values[-1]
    change = ((last_val - first_val) / abs(first_val)) * 100 if first_val != 0 else 0

    if change > 5:
        trend = "📈 растёт"
    elif change < -5:
        trend = "📉 снижается"
    else:
        trend = "➡️ стабилен"

    avg_val = sum(values) / len(values)

    comment = f"**{name}** {trend} за анализируемый период. "
    comment += f"Среднее значение: **{avg_val:.2f}**. "
    comment += f"Изменение: **{change:+.1f}%**."

    if metric_name == 'current_ratio' and last_val < 1.0:
        comment += " ⚠️ Риск ликвидности."
    elif metric_name == 'current_ratio' and last_val > 2.0:
        comment += " ✅ Хорошая ликвидность."
    elif metric_name == 'debt_to_equity' and last_val > 0.7:
        comment += " ⚠️ Долговая нагрузка выше нормы."
    elif metric_name == 'debt_to_equity' and last_val < 0.3:
        comment += " ✅ Низкая долговая нагрузка."
    elif metric_name in ['roe', 'roa', 'ros'] and last_val < 0:
        comment += " ⚠️ Отрицательная рентабельность."
    elif metric_name in ['roe', 'roa', 'ros'] and last_val > 0.15:
        comment += " ✅ Высокая рентабельность."

    # Если OpenAI доступен, то улучшаем комментарий
    if OPENAI_AVAILABLE:
        try:
            prompt = f"""
            Ты финансовый аналитик. Прокомментируй динамику показателя {name}.
            Значения за период: {values}
            Тренд: {trend}
            Изменение: {change:.1f}%
            Напиши краткий, профессиональный комментарий на русском языке (1-2 предложения).
            """
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            llm_comment = response.choices[0].message.content.strip()
            return llm_comment
        except Exception as e:
            return comment + f"\n\n*(Режим заглушки — API недоступен: {e})*"

    return comment