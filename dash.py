import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re
from datetime import datetime, timedelta
import random

# Настройки страницы
st.set_page_config(layout="wide", page_title="Аналитика отзывов о Газпромбанке")

# Заголовок
st.title("Аналитика отзывов о Газпромбанке")

# Словарь продуктов и подкатегорий (ТОЧНО как в ТЗ, с корректировками для примера)
PRODUCT_CATEGORIES = {
    'Повседневные финансы и платежи': [
        'Ведение валютных счетов',
        'Дебетовые карты',
        'Мобильное приложение',
        'Переводы',
        'Зарплатные карты',
        'Обслуживание'
    ],
    'Сбережения и накопления': [
        'Срочные вклады',
        'Сберегательные счета',
        'Обезличенные металлические счета',
        'Накопительные счета'
    ],
    'Кредитование': [
        'Потребительские кредиты',
        'Кредитная карта',
        'Ипотечные кредиты',
        'Автокредиты',
        'Рефинансирование'
    ],
    'Инвестиции': [
        'Брокерский счет',
        'ИИС (Индивидуальный инвестиционный счет)',
        'ПИФы (Паевые инвестиционные фонды)',
        'Структурные продукты'
    ],
    'Страхование и защита': [
        'Страхование путешествий',
        'Страхование имущества',
        'Страхование от несчастных случаев и болезней',
        'Страхование при оформлении кредитов'
    ],
    'Премиальные услуги': [
        'Приват банкинг',
        'Депозитарные ячейки',
        'Услуги по консультированию и планированию'
    ]
}

# Собираем все подкатегории и категории
ALL_CATEGORIES = list(PRODUCT_CATEGORIES.keys())
ALL_SUBCATEGORIES = [sub for subs in PRODUCT_CATEGORIES.values() for sub in subs]

# Словарь ключевых слов (расширенный и точный)
KEYWORDS = {}

# Заполняем KEYWORDS
for category, subcats in PRODUCT_CATEGORIES.items():
    for subcat in subcats:
        if subcat == 'Ведение валютных счетов':
            words = ['валют', 'счет', 'конвертац']
            phrases = ['валютный счет']
        elif subcat == 'Дебетовые карты':
            words = ['дебет', 'снятие', 'кэшбэк', 'дебетовая карта']
            phrases = ['дебетовая карта']
        elif subcat == 'Мобильное приложение':
            words = ['мобильн', 'приложен', 'онлайн', 'интернет', 'зависа', 'мобилка']
            phrases = ['мобильное приложение', 'мобильный банк']
        elif subcat == 'Переводы':
            words = ['перевод', 'средств', 'перевести']
            phrases = ['перевод денег']
        elif subcat == 'Зарплатные карты':
            words = ['зарплат', 'зп']
            phrases = ['зарплатная карта']
        elif subcat == 'Обслуживание':
            words = ['обслуживан', 'отделени', 'клиент', 'персонал', 'менеджер', 'консультант']
            phrases = ['обслуживание в отделении', 'обслуживание в банке']
        elif subcat == 'Срочные вклады':
            words = ['срочн', 'вклад']
            phrases = ['срочный вклад']
        elif subcat == 'Сберегательные счета':
            words = ['сберегательн', 'счет']
            phrases = ['сберегательный счет']
        elif subcat == 'Обезличенные металлические счета':
            words = ['металл', 'обезличен', 'омс']
            phrases = ['обезличенный металлический счет']
        elif subcat == 'Накопительные счета':
            words = ['накопит', 'счет']
            phrases = ['накопительный счет']
        elif subcat == 'Потребительские кредиты':
            words = ['потребительск', 'кредит']
            phrases = ['потребительский кредит']
        elif subcat == 'Кредитная карта':
            words = ['кредитн', 'карта', 'лимит']
            phrases = ['кредитная карта']
        elif subcat == 'Ипотечные кредиты':
            words = ['ипотек', 'ипотечн']
            phrases = ['ипотечный кредит']
        elif subcat == 'Автокредиты':
            words = ['автокредит', 'авто кредит']
            phrases = ['автомобильный кредит']
        elif subcat == 'Рефинансирование':
            words = ['рефинансирован']
            phrases = ['рефинансирование кредита']
        elif subcat == 'Брокерский счет':
            words = ['брокер', 'счет']
            phrases = ['брокерский счет']
        elif subcat == 'ИИС (Индивидуальный инвестиционный счет)':
            words = ['иис', 'инвест', 'счет']
            phrases = ['индивидуальный инвестиционный счет']
        elif subcat == 'ПИФы (Паевые инвестиционные фонды)':
            words = ['пиф', 'паев', 'фонд']
            phrases = ['паевой фонд']
        elif subcat == 'Структурные продукты':
            words = ['структурн']
            phrases = ['структурный продукт']
        elif subcat == 'Страхование путешествий':
            words = ['путешестви', 'туризм', 'поездк']
            phrases = ['страхование путешествий']
        elif subcat == 'Страхование имущества':
            words = ['имуществ', 'дом', 'квартир']
            phrases = ['страхование имущества']
        elif subcat == 'Страхование от несчастных случаев и болезней':
            words = ['несчастн', 'болезн', 'травм', 'инвалид']
            phrases = ['страхование от несчастных случаев']
        elif subcat == 'Страхование при оформлении кредитов':
            words = ['кредит', 'страхован']
            phrases = ['страхование при оформлении кредита']
        elif subcat == 'Приват банкинг':
            words = ['приват', 'премиум', 'vip']
            phrases = ['приват-банкинг']
        elif subcat == 'Депозитарные ячейки':
            words = ['ячейк', 'сейф']
            phrases = ['депозитарные ячейки']
        elif subcat == 'Услуги по консультированию и планированию':
            words = ['консультирован', 'планирован', 'финансов', 'совет']
            phrases = ['услуги по консультированию']
        else:
            words = []
            phrases = []

        KEYWORDS[subcat] = {'keywords': words, 'phrases': phrases}

    # Добавляем категорию как fallback (без подкатегорий)
    cat_keywords = []
    for sub in subcats:
        cat_keywords.extend(KEYWORDS[sub]['keywords'])
    KEYWORDS[category] = {'keywords': list(set(cat_keywords)), 'phrases': []}

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

def extract_topic_from_fragment(fragment):
    """Возвращает ТОЛЬКО одну тему: сначала подкатегорию, потом категорию"""
    fragment = fragment.lower()
    words = set(re.findall(r'\w+', fragment))
    
    # Сначала проверяем подкатегории
    for category, subcats in PRODUCT_CATEGORIES.items():
        for subcat in subcats:
            data = KEYWORDS[subcat]
            if any(kw in fragment for kw in data['phrases']) or any(w in words for w in data['keywords']):
                return subcat  # Возвращаем только subcat
    
    # Потом категории
    for category in PRODUCT_CATEGORIES.keys():
        data = KEYWORDS[category]
        if any(w in words for w in data['keywords']):
            return category
    
    return None

def random_review_date():
    start = datetime(2024, 1, 1)
    end = datetime(2025, 5, 31)
    delta = end - start
    random_days = random.randrange(delta.days + 1)
    return (start + timedelta(days=random_days)).strftime('%d.%m.%Y')

def process_review(review):
    text = review.get('text', '')
    id = review.get('id', 0)
    
    # Разбиваем на части по союзам-разделителям
    parts = re.split(r'\b(но|зато|однако|а также|при этом|и|но при этом)\b', text, flags=re.IGNORECASE)
    fragments = []
    for i in range(0, len(parts), 2):
        frag = parts[i].strip()
        if i + 1 < len(parts):
            frag += ' ' + parts[i+1].strip()
        if frag:
            fragments.append(frag.strip())
    
    if not fragments:
        fragments = [text]
    
    topics = []
    sentiments = []
    
    for frag in fragments:
        topic = extract_topic_from_fragment(frag)
        if topic is None:
            continue  # пропускаем, если не относится к темам
        sentiment = classify_sentiment(frag)
        topics.append(topic)
        sentiments.append(sentiment)
    
    # Если ни одна тема не найдена — ставим "Другое"
    if not topics:
        topics = ["Другое"]
        # Для "Другое" определяем тональность по всему тексту
        sentiments = [classify_sentiment(text)]
    
    # Определяем rating (только для дашборда!)
    if len(set(sentiments)) > 1:
        rating = 3  # нейтральный, если разные тональности
    else:
        first_sent = sentiments[0] if sentiments else 'нейтрально'
        if first_sent == 'положительно':
            rating = 5
        elif first_sent == 'отрицательно':
            rating = 1
        else:
            rating = 3
    
    return {
        'id': id,
        'text': text,
        'topics': ', '.join(topics),
        'sentiments': ', '.join(sentiments),
        'product_category': ', '.join(topics),
        'date': random_review_date(),
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

# Сайдбар
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

        selected_categories = st.sidebar.multiselect("Категории", options=ALL_CATEGORIES, default=[])
        selected_subcategories = st.sidebar.multiselect("Подкатегории", options=ALL_SUBCATEGORIES, default=[])

        # Фильтрация
        mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date) & (df['rating'].between(*rating_filter))
        
        if selected_categories:
            mask &= df['product_category'].str.contains('|'.join(selected_categories), case=False, na=False)
        if selected_subcategories:
            mask &= df['product_category'].str.contains('|'.join(selected_subcategories), case=False, na=False)

        filtered_df = df[mask].copy()

        # Вывод
        st.subheader("📝 Подробные отзывы")
        st.dataframe(filtered_df[['id', 'text', 'topics', 'sentiments', 'rating', 'date']])

        # Тональность
        st.subheader("😊 Распределение тональности")
        if not filtered_df.empty:
            exploded = filtered_df.copy()
            exploded['sentiments_list'] = exploded['sentiments'].str.split(', ')
            exploded = exploded.explode('sentiments_list')
            sentiment_counts = exploded['sentiments_list'].value_counts()
            fig_sentiment = px.pie(
                names=sentiment_counts.index,
                values=sentiment_counts.values,
                title="Тональность отзывов",
                color=sentiment_counts.index,
                color_discrete_map={'положительно': '#90EE90', 'отрицательно': '#FF6347', 'нейтрально': '#D3D3D3'}
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)

        # Распределение по категориям
        st.subheader("📋 Распределение по категориям продуктов")
        if not filtered_df.empty:
            exploded_cat = filtered_df.copy()
            exploded_cat['cat_list'] = exploded_cat['product_category'].str.split(', ')
            exploded_cat = exploded_cat.explode('cat_list')
            cat_counts = exploded_cat['cat_list'].value_counts()
            fig_cat = px.bar(
                x=cat_counts.index,
                y=cat_counts.values,
                title="Категории и подкатегории",
                labels={'x': 'Тема', 'y': 'Количество отзывов'}
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        # Распределение отзывов по датам
        st.subheader("📅 Распределение отзывов по датам")
        if not filtered_df.empty:
            count_by_date = filtered_df['date'].dt.date.value_counts().sort_index()
            fig_date = px.bar(
                x=count_by_date.index,
                y=count_by_date.values,
                title="Количество отзывов по датам",
                labels={'x': 'Дата', 'y': 'Количество отзывов'}
            )
            st.plotly_chart(fig_date, use_container_width=True)
    else:
        st.write("Нет данных для анализа.")
else:
    st.sidebar.warning("Загрузите JSON с отзывами для анализа")
    st.write("Загрузите JSON с отзывами в сайдбаре.")
