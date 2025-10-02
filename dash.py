import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re
from datetime import datetime

# Настройки страницы
st.set_page_config(layout="wide", page_title="Аналитика отзывов о Газпромбанке")

st.title("Аналитика отзывов о Газпромбанке")

# === СООТВЕТСТВИЕ: Подкатегория → Название в ответе (как в эталоне) ===
SUBCATEGORY_TO_TOPIC_NAME = {
    'Мобильный банк': 'Мобильное приложение',
    'Ведение валютных счетов': 'Валютные счета',
    'Дебетовые карты': 'Дебетовая карта',
    'Переводы': 'Переводы',
    'Зарплатные карты': 'Зарплатная карта',
    'Срочные вклады': 'Вклады',
    'Сберегательные счета': 'Сберегательные счета',
    'Обезличенные металлические счета': 'Металлические счета',
    'Накопительные счета': 'Накопительные счета',
    'Потребительские кредиты': 'Потребительский кредит',
    'Кредитные карты': 'Кредитная карта',
    'Ипотечные кредиты': 'Ипотека',
    'Автокредиты': 'Автокредит',
    'Рефинансирование': 'Рефинансирование',
    'Брокерский счет': 'Брокерский счет',
    'ИИС (Индивидуальный инвестиционный счет)': 'ИИС',
    'ПИФы (Паевые инвестиционные фонды)': 'ПИФы',
    'Структурные продукты': 'Структурные продукты',
    'Страхование путешествий': 'Страхование путешествий',
    'Страхование имущества': 'Страхование имущества',
    'Страхование от несчастных случаев и болезней': 'Страхование от несчастных случаев',
    'Страхование при оформлении кредитов': 'Страхование при кредитовании',
    'Приват банкинг': 'Приват банкинг',
    'Депозитарные ячейки': 'Депозитарные ячейки',
    'Услуги по консультированию и планированию': 'Финансовое консультирование'
}

# Обратное соответствие для поиска
TOPIC_NAME_TO_SUBCATEGORY = {v: k for k, v in SUBCATEGORY_TO_TOPIC_NAME.items()}

# Все возможные темы (в формате эталона)
ALL_TOPIC_NAMES = list(SUBCATEGORY_TO_TOPIC_NAME.values())

# Ключевые слова для каждой подкатегории
KEYWORDS = {
    'Мобильный банк': {'keywords': ['мобильн', 'приложен', 'онлайн', 'зависа', 'мобилка'], 'phrases': ['мобильное приложение', 'мобильный банк']},
    'Ведение валютных счетов': {'keywords': ['валют', 'счет', 'конвертац'], 'phrases': ['валютный счет']},
    'Дебетовые карты': {'keywords': ['дебет', 'снятие', 'кэшбэк'], 'phrases': ['дебетовая карта']},
    'Переводы': {'keywords': ['перевод', 'средств', 'перевести'], 'phrases': ['перевод денег']},
    'Зарплатные карты': {'keywords': ['зарплат', 'зп'], 'phrases': ['зарплатная карта']},
    'Срочные вклады': {'keywords': ['срочн', 'вклад'], 'phrases': ['срочный вклад']},
    'Сберегательные счета': {'keywords': ['сберегательн', 'счет'], 'phrases': ['сберегательный счет']},
    'Обезличенные металлические счета': {'keywords': ['металл', 'обезличен', 'омс'], 'phrases': ['обезличенный металлический счет']},
    'Накопительные счета': {'keywords': ['накопит', 'счет'], 'phrases': ['накопительный счет']},
    'Потребительские кредиты': {'keywords': ['потребительск', 'кредит'], 'phrases': ['потребительский кредит']},
    'Кредитные карты': {'keywords': ['кредитн', 'карта', 'лимит'], 'phrases': ['кредитная карта']},
    'Ипотечные кредиты': {'keywords': ['ипотек', 'ипотечн'], 'phrases': ['ипотечный кредит']},
    'Автокредиты': {'keywords': ['автокредит', 'авто кредит'], 'phrases': ['автомобильный кредит']},
    'Рефинансирование': {'keywords': ['рефинансирован'], 'phrases': ['рефинансирование кредита']},
    'Брокерский счет': {'keywords': ['брокер', 'счет'], 'phrases': ['брокерский счет']},
    'ИИС (Индивидуальный инвестиционный счет)': {'keywords': ['иис', 'инвест', 'счет'], 'phrases': ['индивидуальный инвестиционный счет']},
    'ПИФы (Паевые инвестиционные фонды)': {'keywords': ['пиф', 'паев', 'фонд'], 'phrases': ['паевой фонд']},
    'Структурные продукты': {'keywords': ['структурн'], 'phrases': ['структурный продукт']},
    'Страхование путешествий': {'keywords': ['путешестви', 'туризм', 'поездк'], 'phrases': ['страхование путешествий']},
    'Страхование имущества': {'keywords': ['имуществ', 'дом', 'квартир'], 'phrases': ['страхование имущества']},
    'Страхование от несчастных случаев и болезней': {'keywords': ['несчастн', 'болезн', 'травм', 'инвалид'], 'phrases': ['страхование от несчастных случаев']},
    'Страхование при оформлении кредитов': {'keywords': ['кредит', 'страхован'], 'phrases': ['страхование при оформлении кредита']},
    'Приват банкинг': {'keywords': ['приват', 'премиум', 'vip'], 'phrases': ['приват-банкинг']},
    'Депозитарные ячейки': {'keywords': ['ячейк', 'сейф'], 'phrases': ['депозитарные ячейки']},
    'Услуги по консультированию и планированию': {'keywords': ['консультирован', 'планирован', 'финансов', 'совет'], 'phrases': ['услуги по консультированию']}
}

# Лексикон тональности
SENTIMENT_LEXICON = {
    'positive': {
        'отличн': 2, 'хорош': 2, 'прекрасн': 2, 'быстр': 1, 'удобн': 1, 'понятн': 1,
        'рекоменд': 2, 'довол': 2, 'спасиб': 2, 'рад': 2, 'легк': 1, 'приятн': 1,
        'качествен': 2, 'профессионал': 2, 'оператив': 1, 'четк': 1, 'прозрачн': 1,
        'выгодн': 2, 'надежн': 2, 'лучш': 2, 'супер': 2, 'замечательн': 2, 'впечатл': 2,
        'удовлетворен': 2, 'понравилось': 2, 'нравится': 2, 'вовремя': 1, 'своевремен': 1,
        'гладко': 1, 'эффективн': 1, 'без проблем': 2, 'не плохо': 1, 'без ошибок': 2,
    },
    'negative': {
        'плох': -2, 'ужасн': -3, 'медлен': -2, 'неудобн': -2, 'сложн': -2, 'не нравится': -3,
        'проблем': -2, 'ошибк': -2, 'глюк': -2, 'зависа': -2, 'не работ': -3, 'отказ': -2,
        'обман': -3, 'дорог': -2, 'комисс': -1, 'долг': -2, 'неясн': -1, 'неполадк': -2,
        'недовол': -2, 'разочарован': -3, 'кошмар': -3, 'зависает': -2, 'виснет': -2, 'тупит': -2,
        'лагает': -2, 'маленьк': -1
    }
}

NEGATION_WORDS = {'не', 'нет', 'ни', 'без', 'нельзя', 'невозможно', 'никак', 'ничуть'}

def classify_sentiment(text):
    text = text.lower()
    score = 0
    words = re.findall(r'\w+', text)
    for i, word in enumerate(words):
        for sentiment, lex in SENTIMENT_LEXICON.items():
            for key, val in lex.items():
                if key in word:
                    adjusted_val = val
                    if i > 0 and words[i-1] in NEGATION_WORDS:
                        adjusted_val = -adjusted_val
                    score += adjusted_val
                    break
    if score > 0.5:
        return 'положительно'
    elif score < -0.5:
        return 'отрицательно'
    else:
        return 'нейтрально'

def find_topics_in_fragment(fragment):
    """Возвращает список тем (в формате эталона), найденных в фрагменте"""
    fragment = fragment.lower()
    words = set(re.findall(r'\w+', fragment))
    found_topics = []
    
    for subcat, data in KEYWORDS.items():
        # Проверяем фразы
        if any(phrase in fragment for phrase in data['phrases']):
            topic_name = SUBCATEGORY_TO_TOPIC_NAME[subcat]
            if topic_name not in found_topics:
                found_topics.append(topic_name)
            continue
        # Проверяем ключевые слова
        if any(kw in words for kw in data['keywords']):
            topic_name = SUBCATEGORY_TO_TOPIC_NAME[subcat]
            if topic_name not in found_topics:
                found_topics.append(topic_name)
    
    return found_topics

def process_review(review):
    text = review.get('text', '')
    id = review.get('id', 0)
    
    # Разбиваем на фрагменты по союзам
    parts = re.split(r'\b(но|зато|однако|а также|при этом|и|но при этом|зато при этом)\b', text, flags=re.IGNORECASE)
    fragments = []
    for i in range(0, len(parts), 2):
        frag = parts[i].strip()
        if i + 1 < len(parts) and parts[i+1].strip():
            frag += ' ' + parts[i+1].strip()
        if frag:
            fragments.append(frag.strip())
    
    if not fragments:
        fragments = [text]
    
    all_topics = []
    all_sentiments = []
    
    for frag in fragments:
        topics_in_frag = find_topics_in_fragment(frag)
        sentiment = classify_sentiment(frag)
        # Для каждой темы в этом фрагменте — добавляем её и тональность
        for topic in topics_in_frag:
            all_topics.append(topic)
            all_sentiments.append(sentiment)
    
    # Если ни одна тема не найдена — ставим "Другое"
    if not all_topics:
        all_topics = ["Другое"]
        all_sentiments = [classify_sentiment(text)]
    
    # Rating для дашборда (не возвращается в API!)
    if all(s == 'положительно' for s in all_sentiments):
        rating = 5
    elif all(s == 'нейтрально' for s in all_sentiments):
        rating = 3
    else:
        rating = 1  # есть хотя бы один негатив
    
    return {
        'id': id,
        'text': text,
        'topics': ', '.join(all_topics),
        'sentiments': ', '.join(all_sentiments),
        'product_category': ', '.join(all_topics),
        'date': datetime.now().strftime('%d.%m.%Y'),
        'rating': rating,
        'author': review.get('author', 'Клиент банка'),
        'source': 'gold'
    }

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            if 'data' in data and isinstance(data['data'], list):
                predictions = [process_review(review) for review in data['data']]
                df = pd.DataFrame(predictions)
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
                    st.info(f"Загружено {len(df)} отзывов")
                    return df
        except Exception as e:
            st.error(f"Ошибка при загрузке JSON: {e}")
    st.error("Неверный формат JSON. Ожидается {'data': [{'id': 1, 'text': '...'}]}")
    return pd.DataFrame()

# === Streamlit UI ===
st.sidebar.header("Загрузка и фильтры")
uploaded_json = st.sidebar.file_uploader("Загрузите JSON с отзывами", type=['json'])

if uploaded_json:
    df = load_data(uploaded_json)
    if not df.empty:
        st.sidebar.header("Фильтры")
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        start_date = st.sidebar.date_input("Начальная дата", min_date, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("Конечная дата", max_date, min_value=min_date, max_value=max_date)
        rating_filter = st.sidebar.slider("Рейтинг", min_value=1, max_value=5, value=(1, 5))
        
        selected_topics = st.sidebar.multiselect("Темы", options=sorted(ALL_TOPIC_NAMES), default=[])

        # Фильтрация
        mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date) & (df['rating'].between(*rating_filter))
        if selected_topics:
            mask &= df['product_category'].str.contains('|'.join(selected_topics), case=False, na=False)
        filtered_df = df[mask].copy()

        # Вывод
        st.subheader("📝 Подробные отзывы")
        st.dataframe(filtered_df[['id', 'text', 'topics', 'sentiments', 'rating', 'date']])

        # Тональность
        st.subheader("😊 Распределение тональности")
        exploded = filtered_df.copy()
        exploded['sent_list'] = exploded['sentiments'].str.split(', ')
        exploded = exploded.explode('sent_list')
        sent_counts = exploded['sent_list'].value_counts()
        fig = px.pie(
            names=sent_counts.index,
            values=sent_counts.values,
            title="Тональность по всем темам",
            color=sent_counts.index,
            color_discrete_map={'положительно': '#90EE90', 'отрицательно': '#FF6347', 'нейтрально': '#D3D3D3'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Распределение по темам
        st.subheader("📋 Распределение по темам")
        exploded_cat = filtered_df.copy()
        exploded_cat['topic_list'] = exploded_cat['product_category'].str.split(', ')
        exploded_cat = exploded_cat.explode('topic_list')
        topic_counts = exploded_cat['topic_list'].value_counts()
        fig2 = px.bar(x=topic_counts.index, y=topic_counts.values, title="Упоминания тем")
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.write("Нет данных для анализа.")
else:
    st.sidebar.warning("Загрузите JSON с отзывами для анализа")
    st.write("Загрузите JSON с отзывами в сайдбаре.")
