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

# Сайдбар для загрузки JSON
st.sidebar.header("Загрузка и фильтры")
uploaded_json = st.sidebar.file_uploader("Загрузите JSON с отзывами", type=['json'])

# Словарь для тональности
SENTIMENT_LEXICON = {
    'positive': {
        'отличн': 2, 'хорош': 2, 'прекрасн': 2, 'быстр': 1, 'удобн': 1, 'понятн': 1,
        'рекоменд': 2, 'довол': 2, 'спасиб': 2, 'рад': 2, 'легк': 1, 'приятн': 1,
        'качествен': 2, 'профессионал': 2, 'оператив': 1, 'четк': 1, 'прозрачн': 1,
        'выгодн': 2, 'надежн': 2, 'лучш': 2, 'супер': 2, 'замечательн': 2, 'впечатл': 2,
        'удовлетворен': 2, 'понравилось': 2, 'нравится': 2, 'вовремя': 1, 'своевремен': 1,
        'гладко': 1, 'эффективн': 1, 'без проблем': 2, 'не плохо': 1, 'без ошибок': 2,
        'не медлен': 1, 'не зависает': 2
    },
    'negative': {
        'плох': -2, 'ужасн': -3, 'медлен': -2, 'неудобн': -2, 'сложн': -2, 'не нравится': -3,
        'проблем': -2, 'ошибк': -2, 'глюк': -2, 'зависа': -2, 'не работ': -3, 'отказ': -2,
        'обман': -3, 'дорог': -2, 'комисс': -1, 'долг': -2, 'неясн': -1, 'неполадк': -2,
        'недовол': -2, 'разочарован': -3, 'кошмар': -3, 'зависает': -2, 'виснет': -2, 'тупит': -2,
        'лагает': -2, 'маленьк': -1, 'ненадежн': -2
    },
    'neutral': {
        'нормальн': 0, 'обычн': 0, 'стандартн': 0, 'приемлем': 0, 'изменен': 0,
        'ожида': 0, 'средн': 0, 'работ': 0, 'нейтральн': 0
    }
}

INTENSIFIERS = {
    'очень': 1.5, 'крайне': 2, 'совсем': 1.5, 'абсолютно': 2, 'полностью': 1.5, 'сильно': 1.5,
    'чрезвычайно': 2, 'невероятно': 2, 'удивительно': 1.5, 'необычно': 1.5, 'весьма': 1.5,
    'слишком': 2, 'часто': 1
}

NEGATION_WORDS = {
    'не', 'нет', 'ни', 'без', 'нельзя', 'невозможно', 'никак', 'ничуть'
}

# Словарь для классификации продуктов с подкатегориями
PRODUCT_CATEGORIES_MAIN = {
    'Повседневные финансы и платежи': {
        'subcategories': {
            'Ведение валютных счетов': {'keywords': ['валют', 'счет', 'конвертац'], 'phrases': ['валютный счет']},
            'Дебетовые карты': {'keywords': ['дебет', 'снятие', 'кэшбэк'], 'phrases': ['дебетовая карта']},
            'Мобильный банк': {'keywords': ['мобиль', 'приложен', 'онлайн'], 'phrases': ['мобильный банк']},
            'Переводы': {'keywords': ['перевод', 'средств'], 'phrases': ['перевод денег']},
            'Зарплатные карты': {'keywords': ['зарплат'], 'phrases': ['зарплатная карта']},
            'Обслуживание в отделении': {'keywords': ['обслуживан', 'отделени', 'филиал', 'персонал', 'менеджер', 'консультант'], 'phrases': ['обслуживание в отделении', 'отделение банка', 'обслуживание в банке']}
        },
        'keywords': ['перевод', 'зарплат', 'мобиль', 'счет', 'платеж', 'валют', 'снят', 'банкомат', 'оплат', 'комисс', 'онлайн', 'приложен', 'интернет', 'уведомлен', 'деньг', 'налич', 'безнал', 'выпис', 'баланс', 'остаток', 'обслуживан', 'отделени', 'филиал'],
        'phrases': ['мобильный банк', 'перевод денег', 'открыть счет', 'валютный счет', 'снять деньги', 'оплатить услуги', 'обслуживание карты', 'отделение банка', 'интернет банк', 'мобильное приложение', 'выписка по счету', 'остаток на счете']
    },
    'Сбережения и накопления': {
        'subcategories': {
            'Срочные вклады': {'keywords': ['срочн', 'вклад'], 'phrases': ['срочный вклад']},
            'Сберегательные счета': {'keywords': ['сберегательн', 'счет'], 'phrases': ['сберегательный счет']},
            'Обезличенные металлические счета': {'keywords': ['металл', 'обезличен'], 'phrases': ['обезличенный металлический']},
            'Накопительные счета': {'keywords': ['накопит', 'счет'], 'phrases': ['накопительный счет']}
        },
        'keywords': ['вклад', 'сберегательн', 'накопит', 'металл', 'счет', 'процент', 'депозит', 'ставк', 'доходност', 'пополнен', 'снят', 'начислен'],
        'phrases': ['срочный вклад', 'сберегательный счет', 'металлический счет', 'накопительный счет', 'банковский вклад', 'процентная ставка', 'доход по вкладу']
    },
    'Кредитование': {
        'subcategories': {
            'Потребительские кредиты': {'keywords': ['потребительск', 'кредит'], 'phrases': ['потребительский кредит']},
            'Кредитные карты': {'keywords': ['кредитн', 'карта'], 'phrases': ['кредитная карта']},
            'Ипотечные кредиты': {'keywords': ['ипотек'], 'phrases': ['ипотечный кредит']},
            'Автокредиты': {'keywords': ['автокредит'], 'phrases': ['автомобильный кредит']},
            'Рефинансирование': {'keywords': ['рефинансирован'], 'phrases': ['рефинансирование кредита']}
        },
        'keywords': ['кредит', 'ипотек', 'автокредит', 'рефинансирован', 'заем', 'платеж', 'процент', 'ставк', 'одобрен', 'погашен', 'долг', 'просрочк'],
        'phrases': ['потребительский кредит', 'ипотечный кредит', 'кредитная карта', 'рефинансирование кредита', 'автомобильный кредит', 'погашение кредита', 'процентная ставка']
    },
    'Инвестиции': {
        'subcategories': {
            'Брокерский счет': {'keywords': ['брокер', 'счет'], 'phrases': ['брокерский счет']},
            'ИИС (Индивидуальный инвестиционный счет)': {'keywords': ['иис'], 'phrases': ['индивидуальный инвестиционный счет']},
            'ПИФы (Паевые инвестиционные фонды)': {'keywords': ['пиф'], 'phrases': ['паевой фонд']},
            'Структурные продукты': {'keywords': ['структурн'], 'phrases': ['структурный продукт']}
        },
        'keywords': ['инвест', 'брокер', 'иис', 'пиф', 'акци', 'облигац', 'портфель', 'доходност', 'структурн', 'торгов', 'дивиденд'],
        'phrases': ['брокерский счет', 'индивидуальный инвестиционный счет', 'паевой фонд', 'структурный продукт', 'инвестиционный портфель', 'торговля на бирже']
    },
    'Страхование и защита': {
        'subcategories': {
            'Страхование путешествий': {'keywords': ['путешестви'], 'phrases': ['страхование путешествий']},
            'Страхование имущества': {'keywords': ['имуществ'], 'phrases': ['страхование имущества']},
            'Страхование от несчастных случаев и болезней': {'keywords': ['несчастн', 'болезн'], 'phrases': ['страхование от несчастных случаев']},
            'Страхование при оформлении кредитов': {'keywords': ['кредит', 'страхован'], 'phrases': ['страхование при оформлении кредита']}
        },
        'keywords': ['страховк', 'полис', 'выплат', 'ущерб', 'риск', 'оформлен'],
        'phrases': ['страховой полис', 'оформление страховки', 'выплата по страховке', 'возмещение ущерба']
    },
    'Премиальные услуги': {
        'subcategories': {
            'Приват банкинг': {'keywords': ['приват'], 'phrases': ['приват-банкинг']},
            'Депозитарные ячейки': {'keywords': ['ячейк'], 'phrases': ['депозитарные ячейки']},
            'Услуги по консультированию и планированию': {'keywords': ['консультирован', 'планирован'], 'phrases': ['услуги по консультированию']}
        },
        'keywords': ['премиум', 'вип', 'персональн', 'обслужван', 'услуг', 'капитал', 'управлен', 'хранен'],
        'phrases': ['премиум-обслуживание', 'VIP-услуги', 'управление капиталом', 'хранение ценностей']
    }
}

# Функции классификации
def classify_sentiment(text):
    text = text.lower()
    sentiment_score = 0
    words = re.findall(r'\w+', text)
    for i, word in enumerate(words):
        base_score = 0
        for sentiment, keywords in SENTIMENT_LEXICON.items():
            for key, score in keywords.items():
                if key in word:
                    base_score = score
                    break
            if base_score != 0:
                break
        if base_score != 0:
            if i > 0 and words[i-1] in INTENSIFIERS:
                base_score *= INTENSIFIERS[words[i-1]]
            if i > 0 and words[i-1] in NEGATION_WORDS:
                base_score = -base_score
            sentiment_score += base_score
    return 'положительно' if sentiment_score > 1 else 'отрицательно' if sentiment_score < -1 else 'нейтрально'

def classify_rating(sentiment):
    if sentiment == 'положительно':
        return random.randint(4, 5)
    elif sentiment == 'нейтрально':
        return 3
    elif sentiment == 'отрицательно':
        return random.randint(1, 2)

def classify_product_category(text):
    text = text.lower()
    categories = set()
    words = set(re.findall(r'\w+', text))
    for category, data in PRODUCT_CATEGORIES_MAIN.items():
        keywords = set(data['keywords'])
        phrases = set(data['phrases'])
        if any(word in keywords for word in words) or any(phrase in text for phrase in phrases):
            subcategories = []
            for subcat, subdata in data['subcategories'].items():
                sub_keywords = set(subdata['keywords'])
                sub_phrases = set(subdata['phrases'])
                if any(word in sub_keywords for word in words) or any(phrase in text for phrase in sub_phrases):
                    subcategories.append(subcat)
            if subcategories:
                for subcat in subcategories:
                    categories.add(f"{category} - {subcat}")
            else:
                categories.add(category)
    return list(categories)

def random_review_date():
    start = datetime(2024, 1, 1)
    end = datetime(2025, 5, 31)
    delta = end - start
    random_days = random.randrange(delta.days + 1)
    return (start + timedelta(days=random_days)).strftime('%d.%m.%Y')

def process_review(review):
    text = review.get('text', '')
    id = review.get('id', 0)
    parts = re.split(r'\bно\b', text, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]
    
    topics = []
    sentiments = []
    if parts:
        for part in parts:
            sentiment = classify_sentiment(part)
            part_products = classify_product_category(part)
            if part_products:
                for p in part_products:
                    topics.append(p)
                    sentiments.append(sentiment)
            else:
                topics.append('Другое')
                sentiments.append(sentiment)
    if not topics:
        sentiment = classify_sentiment(text)
        product_categories = classify_product_category(text)
        topics = product_categories if product_categories else ['Другое']
        sentiments = [sentiment] * len(topics)
    
    # Удаляем дубликаты тем, сохраняя первое sentiment для каждой
    unique_topics = []
    unique_sentiments = []
    seen = set()
    for t, s in zip(topics, sentiments):
        if t not in seen:
            seen.add(t)
            unique_topics.append(t)
            unique_sentiments.append(s)
    
    rating = sum(classify_rating(s) for s in unique_sentiments) // len(unique_sentiments) if unique_sentiments else 3
    
    return {
        'id': id,
        'text': text,
        'topics': ', '.join(unique_topics),
        'sentiments': ', '.join(unique_sentiments),
        'date': random_review_date(),
        'rating': rating,
        'author': review.get('author', 'Клиент банка'),
        'source': 'gold'
    }

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        data = json.load(uploaded_file)
        if 'data' in data and isinstance(data['data'], list):
            predictions = [process_review(review) for review in data['data']]
            df = pd.DataFrame(predictions)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
                st.info(f"Загружено {len(df)} отзывов")
                return df
        st.error("Неверный формат JSON. Ожидается {'data': [{'id': 1, 'text': '...'}]}")
    return pd.DataFrame()

if uploaded_json:
    df = load_data(uploaded_json)
    # Фильтры после загрузки данных
    st.sidebar.header("Фильтры")
    min_date = df['date'].min().date() if 'date' in df and pd.notna(df['date'].min()) else datetime(2024, 1, 1).date()
    max_date = df['date'].max().date() if 'date' in df and pd.notna(df['date'].max()) else datetime(2025, 5, 31).date()
    start_date = st.sidebar.date_input("Начальная дата", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Конечная дата", max_date, min_value=min_date, max_value=max_date)

    rating_filter = st.sidebar.slider("Рейтинг", min_value=1, max_value=5, value=(1, 5))

    product_categories = ['Все'] + sorted(PRODUCT_CATEGORIES_MAIN.keys())
    product_filter = st.sidebar.multiselect("Категория продукта", options=product_categories, default=['Все'])

    subcategories = {
        'Повседневные финансы и платежи': ['Ведение валютных счетов', 'Дебетовые карты', 'Мобильный банк', 'Переводы', 'Зарплатные карты', 'Обслуживание в отделении'],
        'Сбережения и накопления': ['Срочные вклады', 'Сберегательные счета', 'Обезличенные металлические счета', 'Накопительные счета'],
        'Кредитование': ['Потребительские кредиты', 'Кредитные карты', 'Ипотечные кредиты', 'Автокредиты', 'Рефинансирование'],
        'Инвестиции': ['Брокерский счет', 'ИИС (Индивидуальный инвестиционный счет)', 'ПИФы (Паевые инвестиционные фонды)', 'Структурные продукты'],
        'Страхование и защита': ['Страхование путешествий', 'Страхование имущества', 'Страхование от несчастных случаев и болезней', 'Страхование при оформлении кредитов'],
        'Премиальные услуги': ['Приват банкинг', 'Депозитарные ячейки', 'Услуги по консультированию и планированию']
    }
    subcat_filter = st.sidebar.multiselect("Подкатегория продукта", options=[subcat for cats in subcategories.values() for subcat in cats], default=[])
else:
    df = pd.DataFrame()
    st.sidebar.warning("Загрузите JSON с отзывами для анализа")

if not df.empty:
    # Фильтрация
    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date) & (df['rating'].between(*rating_filter))
    if 'Все' not in product_filter and product_filter:
        mask &= df['topics'].str.contains('|'.join(product_filter), case=False, na=False)
    if subcat_filter:
        mask &= df['topics'].str.contains('|'.join(subcat_filter), case=False, na=False)

    filtered_df = df[mask].copy()

    # Создание exploded_df для анализа (парные topic и sentiment)
    temp = filtered_df.assign(topic=filtered_df['topics'].str.split(', '), sentiment=filtered_df['sentiments'].str.split(', '))
    exploded_df = temp.explode(['topic', 'sentiment'])
    exploded_df['date'] = filtered_df['date'].repeat(filtered_df['topics'].str.count(', ') + 1).values[:len(exploded_df)]

    # Таблица отзывов
    st.subheader("📝 Подробные отзывы")
    st.dataframe(filtered_df)

    # График распределения тональности
    st.subheader("😊 Распределение тональности")
    if 'sentiment' in exploded_df:
        sentiment_counts = exploded_df['sentiment'].value_counts()
        fig_sentiment = px.pie(names=sentiment_counts.index, values=sentiment_counts.values, title="Тональность отзывов",
                               color=sentiment_counts.index,
                               color_discrete_map={'положительно': '#90EE90', 'отрицательно': '#FF6347', 'нейтрально': '#D3D3D3'})
        st.plotly_chart(fig_sentiment, use_container_width=True)
    else:
        st.write("Нет данных для отображения тональности.")

    # Распределение по категориям продуктов
    st.subheader("📋 Распределение по категориям продуктов")
    if 'topic' in exploded_df:
        product_counts = exploded_df['topic'].value_counts()
        fig_product = px.bar(x=product_counts.index, y=product_counts.values, title="Категории продуктов",
                             color=product_counts.index)
        st.plotly_chart(fig_product, use_container_width=True)
    else:
        st.write("Нет данных для отображения категорий.")

    # Детализация по продуктам
    st.subheader("📊 Детализация по продуктам/услугам")
    unique_topics = sorted(exploded_df['topic'].unique())
    for topic in unique_topics:
        if topic == 'Другое':
            continue  # Пропускаем "Другое" если нужно, или оставляем
        st.markdown(f"### {topic}")
        topic_df = exploded_df[exploded_df['topic'] == topic].copy()
        if not topic_df.empty:
            sentiment_counts = topic_df['sentiment'].value_counts()
            percent = sentiment_counts / len(topic_df) * 100

            col1, col2 = st.columns(2)
            with col1:
                st.write("Абсолютное количество отзывов по тональностям:")
                st.table(sentiment_counts)
            with col2:
                st.write("Процентное распределение тональностей:")
                st.table(percent)

            # Динамика количества упоминаний
            topic_df['month'] = topic_df['date'].dt.to_period('M')
            count_by_month = topic_df.groupby('month').size()
            fig_count = px.line(x=count_by_month.index.astype(str), y=count_by_month.values,
                                title=f"Динамика количества упоминаний для {topic}")
            st.plotly_chart(fig_count, use_container_width=True)

            # Динамика долей тональностей
            sentiment_prop = topic_df.groupby('month')['sentiment'].value_counts(normalize=True).unstack(fill_value=0) * 100
            fig_prop = px.line(sentiment_prop, title=f"Динамика долей тональностей для {topic}")
            st.plotly_chart(fig_prop, use_container_width=True)
        else:
            st.write("Нет данных для этого продукта/услуги.")
else:
    st.write("Нет данных для анализа. Загрузите JSON с отзывами.")
