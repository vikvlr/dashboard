import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"


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

    # Запрос к Ollama
    try:
        prompt = f"""
        Ты профессиональный финансовый аналитик. Твой ответ должен быть строго на русском языке.

        Прокомментируй динамику показателя "{name}" за анализируемый период.

        Данные:
        - Значения за период: {values}
        - Первое значение: {values[0]:.2f}
        - Последнее значение: {values[-1]:.2f}
        - Тренд: {trend}
        - Изменение: {change:+.1f}%

        Напиши краткий, профессиональный комментарий на русском языке (3 предложения).
        В ответе обязательно:
        1. Укажи конкретные числовые значения (первое и последнее значение, изменение в процентах).
        2. Сделай вывод о динамике показателя.
        3. Укажи, о чём свидетельствует данный показатель для компании.
        4. Используй только русский язык, без англицизмов и смешения языков.

        Пример правильного ответа для показателя "EBITDA":
        "За анализируемый период показатель EBITDA вырос с 10 426 млн руб до 48 700 млн руб, что составляет рост на 367%. Это свидетельствует о значительном улучшении операционной эффективности компании. Рост EBITDA говорит о том, что компания увеличивает прибыльность своей основной деятельности и генерирует больше денежных средств для инвестиций и обслуживания долга."

        Напиши комментарий для показателя "{name}" в том же формате.
        """
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 150
                }
            },
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            llm_comment = data.get('response', '').strip()
            if llm_comment:
                return llm_comment
            else:
                return comment + "\n\n*(Модель вернула пустой ответ)*"
        else:
            return comment + f"\n\n*(Ошибка Ollama: {response.status_code})*"

    except requests.exceptions.ConnectionError:
        return comment + "\n\n**Ollama не запущена!** Запусти приложение Ollama."
    except Exception as e:
        return comment + f"\n\n*(Ошибка: {e})*"
