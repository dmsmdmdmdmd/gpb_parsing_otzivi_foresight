import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re
from datetime import datetime
import random

# Настройки страницы
st.set_page_config(layout="wide", page_title="Аналитика отзывов о Газпромбанке")

# Заголовок
st.title("Аналитика отзывов о Газпромбанке")

# Сайдбар для загрузки JSON и фильтров
st.sidebar.header("Загрузка и фильтры")
uploaded_json = st.sidebar.file_uploader("Загрузите JSON с отзывам", type=['json'])

# Фильтры
if 'df' in locals():
    min_date = df['date'].min().date() if 'date' in df and pd.notna(df['date'].min()) else datetime(2024, 1, 1).date()
    max_date = df['date'].max().date() if 'date' in df and pd.notna(df['date'].max()) else datetime(2025, 10, 2).date()
    start_date = st.sidebar.date_input("Начальная дата", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Конечная дата", max_date, min_value=min_date, max_value=max_date)

    rating_filter = st.sidebar.slider("Рейтинг", min_value=1, max_value=5, value=(1, 5))

    product_categories = ['Все'] + sorted(['Повседневные финансы и платежи', 'Сбережения и накопления', 'Кредитование', 'Инвестиции', 'Страхование и защита', 'Премиальные услуги'])
    product_filter = st.sidebar.multiselect("Категория продукта", options=product_categories, default=['Все'])

    subcategories = {
        'Повседневные финансы и платежи': ['Ведение валютных счетов', 'Дебетовые карты', 'Мобильный банк', 'Переводы', 'Зарплатные карты'],
        'Сбережения и накопления': ['Срочные вклады', 'Сберегательные счета', 'Обезличенные металлические счета', 'Накопительные счета'],
        'Кредитование': ['Потребительские кредиты', 'Кредитные карты', 'Ипотечные кредиты', 'Автокредиты', 'Рефинансирование'],
        'Инвестиции': ['Брокерский счет', 'ИИС (Индивидуальный инвестиционный счет)', 'ПИФы (Паевые инвестиционные фонды)', 'Структурные продукты'],
        'Страхование и защита': ['Страхование путешествий', 'Страхование имущества', 'Страхование от несчастных случаев и болезней', 'Страхование при оформлении кредитов'],
        'Премиальные услуги': ['Приват банкинг', 'Депозитарные ячейки', 'Услуги по консультированию и планированию']
    }
    subcat_filter = st.sidebar.multiselect("Подкатегория продукта", options=[subcat for cats in subcategories.values() for subcat in cats], default=[])

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
        'лагает': -2, 'маленьк': -1
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

# Словарь для тем (topics)
PRODUCT_CATEGORIES_TOPICS = {
    'Обслуживание': {'keywords': ['обслуживан', 'отделени', 'клиент', 'персонал', 'менеджер', 'консультант'], 'phrases': ['обслуживание в банке', 'отделение банка']},
    'Мобильное приложение': {'keywords': ['мобиль', 'приложен', 'онлайн', 'интернет', 'зависа'], 'phrases': ['мобильное приложение', 'мобильный банк']},
    'Кредитная карта': {'keywords': ['кредитн', 'лимит', 'одобрен'], 'phrases': ['кредитная карта']}
}

# Словарь для классификации продуктов с подкатегориями
PRODUCT_CATEGORIES_MAIN = {
    'Повседневные финансы и платежи': {
        'subcategories': {
            'Ведение валютных счетов': {'keywords': ['валют', 'счет', 'конвертац'], 'phrases': ['валютный счет']},
            'Дебетовые карты': {'keywords': ['дебет', 'снятие', 'кэшбэк'], 'phrases': ['дебетовая карта']},
            'Мобильный банк': {'keywords': ['мобиль', 'приложен', 'онлайн'], 'phrases': ['мобильный банк']},
            'Переводы': {'keywords': ['перевод', 'средств'], 'phrases': ['перевод денег']},
            'Зарплатные карты': {'keywords': ['зарплат'], 'phrases': ['зарплатная карта']}
        },
        'keywords': ['перевод', 'зарплат', 'мобиль', 'счет', 'платеж', 'валют', 'снят', 'банкомат', 'оплат', 'комисс', 'онлайн', 'приложен', 'интернет', 'уведомлен', 'деньг', 'налич', 'безнал', 'выпис', 'баланс', 'остаток'],
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

def classify_topics(text):
    text = text.lower()
    categories = set()
    words = set(re.findall(r'\w+', text))
    for category, data in PRODUCT_CATEGORIES_TOPICS.items():
        keywords = set(data['keywords'])
        phrases = set(data['phrases'])
        if any(word in keywords for word in words) or any(phrase in text for phrase in phrases):
            categories.add(category)
    return list(categories)

def classify_product_category(text, topics):
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
    return list(categories) if categories else []

def process_review(review):
    text = review.get('text', '')
    id = review.get('id', 0)
    parts = re.split(r'\bно\b', text, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]
    
    topics = []
    sentiments = []
    if parts:
        for part in parts:
            part_topics = classify_topics(part)
            sentiment = classify_sentiment(part)
            for topic in part_topics:
                if topic not in topics:
                    topics.append(topic)
                    sentiments.append(sentiment)
    else:
        topics = classify_topics(text)
        sentiment = classify_sentiment(text)
        sentiments = [sentiment] * len(topics)
    
    product_categories = classify_product_category(text, topics)
    
    return {
        'id': id,
        'text': text,
        'topics': ', '.join(topics),
        'sentiments': ', '.join(sentiments),
        'product_category': ', '.join(product_categories) if product_categories else 'Другое',
        'date': datetime.now().strftime('%d.%m.%Y'),
        'rating': sum(classify_rating(s) for s in sentiments) // len(sentiments) if sentiments else 3,
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
else:
    df = pd.DataFrame()
    st.sidebar.warning("Загрузите JSON с отзывами для анализа")

if not df.empty and 'df' in locals():
    # Фильтрация
    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date) & (df['rating'].between(*rating_filter))
    if 'Все' not in product_filter and product_filter:
        mask &= df['product_category'].str.contains('|'.join(product_filter), case=False, na=False)
    if subcat_filter:
        mask &= df['product_category'].str.contains('|'.join(subcat_filter), case=False, na=False)

    filtered_df = df[mask].copy()

    # Таблица отзывов
    st.subheader("📝 Подробные отзывы")
    st.dataframe(filtered_df)

    # График распределения тональности
    st.subheader("😊 Распределение тональности")
    if 'sentiments' in filtered_df:
        sentiment_counts = filtered_df['sentiments'].str.split(', ').explode().value_counts()
        fig_sentiment = px.pie(names=sentiment_counts.index, values=sentiment_counts.values, title="Тональность отзывов",
                              color=sentiment_counts.index,
                              color_discrete_map={'положительно': '#90EE90', 'отрицательно': '#FF6347', 'нейтрально': '#D3D3D3'})
        st.plotly_chart(fig_sentiment, use_container_width=True)
    else:
        st.write("Нет данных для отображения тональности.")

    # Распределение по категориям продуктов
    st.subheader("📋 Распределение по категориям продуктов")
    if 'product_category' in filtered_df:
        product_counts = filtered_df['product_category'].str.split(', ').explode().value_counts()
        fig_product = px.bar(x=product_counts.index, y=product_counts.values, title="Категории продуктов",
                             color=product_counts.index,
                             color_discrete_map={
                                 'Повседневные финансы и платежи - Ведение валютных счетов': '#1f77b4',
                                 'Повседневные финансы и платежи - Дебетовые карты': '#1f77b4',
                                 'Повседневные финансы и платежи - Мобильный банк': '#1f77b4',
                                 'Повседневные финансы и платежи - Переводы': '#1f77b4',
                                 'Повседневные финансы и платежи - Зарплатные карты': '#1f77b4',
                                 'Сбережения и накопления - Срочные вклады': '#ff7f0e',
                                 'Сбережения и накопления - Сберегательные счета': '#ff7f0e',
                                 'Сбережения и накопления - Обезличенные металлические счета': '#ff7f0e',
                                 'Сбережения и накопления - Накопительные счета': '#ff7f0e',
                                 'Кредитование - Потребительские кредиты': '#2ca02c',
                                 'Кредитование - Кредитные карты': '#2ca02c',
                                 'Кредитование - Ипотечные кредиты': '#2ca02c',
                                 'Кредитование - Автокредиты': '#2ca02c',
                                 'Кредитование - Рефинансирование': '#2ca02c',
                                 'Инвестиции - Брокерский счет': '#d62728',
                                 'Инвестиции - ИИС (Индивидуальный инвестиционный счет)': '#d62728',
                                 'Инвестиции - ПИФы (Паевые инвестиционные фонды)': '#d62728',
                                 'Инвестиции - Структурные продукты': '#d62728',
                                 'Страхование и защита - Страхование путешествий': '#9467bd',
                                 'Страхование и защита - Страхование имущества': '#9467bd',
                                 'Страхование и защита - Страхование от несчастных случаев и болезней': '#9467bd',
                                 'Страхование и защита - Страхование при оформлении кредитов': '#9467bd',
                                 'Премиальные услуги - Приват банкинг': '#8c564b',
                                 'Премиальные услуги - Депозитарные ячейки': '#8c564b',
                                 'Премиальные услуги - Услуги по консультированию и планированию': '#8c564b',
                                 'Другое': '#bcbd22'
                             })
        st.plotly_chart(fig_product, use_container_width=True)
    else:
        st.write("Нет данных для отображения категорий.")
else:
    st.write("Нет данных для анализа. Загрузите JSON с отзывами.")
