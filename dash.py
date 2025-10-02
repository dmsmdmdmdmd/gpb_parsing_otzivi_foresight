import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re
from datetime import datetime

# Настройки страницы
st.set_page_config(layout="wide", page_title="Аналитика отзывов о Газпромбанке")

# Заголовок
st.title("Аналитика отзывов о Газпромбанке")

# Сайдбар для загрузки JSON
st.sidebar.header("Загрузка данных")
uploaded_json = st.sidebar.file_uploader("Загрузите JSON с отзывами", type=['json'])

# Словарь для тональности
SENTIMENT_LEXICON = {
    'positive': {'отличн': 2, 'хорош': 2, 'прекрасн': 2, 'быстр': 1, 'удобн': 1, 'понятн': 1, 'рекоменд': 2, 'довол': 2, 'спасиб': 2, 'рад': 2},
    'negative': {'плох': -2, 'ужасн': -3, 'медлен': -2, 'неудобн': -2, 'сложн': -2, 'проблем': -2},
    'neutral': {'нормальн': 0, 'обычн': 0, 'стандартн': 0}
}

INTENSIFIERS = {'очень': 1.5, 'крайне': 2}
NEGATION_WORDS = {'не', 'нет'}

# Словарь для тем
PRODUCT_CATEGORIES_TOPICS = {
    'Обслуживание': {'keywords': ['обслуживан', 'отделени', 'клиент', 'персонал'], 'phrases': ['обслуживание в банке']},
    'Мобильное приложение': {'keywords': ['мобиль', 'приложен', 'онлайн', 'зависа'], 'phrases': ['мобильное приложение']},
    'Кредитная карта': {'keywords': ['кредитн', 'лимит', 'одобрен'], 'phrases': ['кредитная карта']}
}

# Словарь для продуктов
PRODUCT_CATEGORIES_MAIN = {
    'Повседневные финансы и платежи': {'keywords': ['мобиль', 'перевод', 'счет'], 'phrases': ['мобильный банк']},
    'Кредитование': {'keywords': ['кредит', 'лимит'], 'phrases': ['кредитная карта']},
    'Инвестиции': {'keywords': ['инвестиц', 'акци'], 'phrases': ['инвестиционный портфель']},
    'Сбережения и накопления': {'keywords': ['вклад', 'сберегательн'], 'phrases': ['сберегательный счет']},
    'Страхование и защита': {'keywords': ['страховк'], 'phrases': ['страховой полис']},
    'Премиальные услуги': {'keywords': ['премиум', 'VIP'], 'phrases': ['премиальное обслуживание']}
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
    return 'positive' if sentiment_score > 1 else 'negative' if sentiment_score < -1 else 'neutral'

def classify_topics(text):
    text = text.lower()
    categories = set()
    words = set(re.findall(r'\w+', text))
    for category, data in PRODUCT_CATEGORIES_TOPICS.items():
        keywords = set(data['keywords'])
        phrases = set(data['phrases'])
        if any(word in keywords for word in words) or any(phrase in text for phrase in phrases):
            categories.add(category)
    return list(categories) if categories else ['Другое']

def classify_product_category(text, topics):
    text = text.lower()
    categories = set()
    words = set(re.findall(r'\w+', text))
    for category, data in PRODUCT_CATEGORIES_MAIN.items():
        keywords = set(data['keywords'])
        phrases = set(data['phrases'])
        if any(word in keywords for word in words) or any(phrase in text for phrase in phrases):
            categories.add(category)
    if len(categories) > 1 and 'Другое' in categories:
        categories.remove('Другое')
    return list(categories) if categories else ['Другое']

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
    
    if len(topics) > 1 and 'Другое' in topics:
        idx = topics.index('Другое')
        topics.pop(idx)
        sentiments.pop(idx)
    
    return {
        'id': id,
        'text': text,
        'topics': ', '.join(topics),
        'sentiments': ', '.join(sentiments),
        'product_category': ', '.join(classify_product_category(text, topics)),
        'date': datetime.now().strftime('%d.%m.%Y'),
        'rating': 3,  # Средний рейтинг по умолчанию
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

if not df.empty:
    # Таблица отзывов
    st.subheader("📝 Подробные отзывы")
    st.dataframe(df)

    # График распределения тональности
    st.subheader("😊 Распределение тональности")
    if 'sentiments' in df:
        sentiment_counts = df['sentiments'].str.split(', ').explode().value_counts()
        fig_sentiment = px.pie(names=sentiment_counts.index, values=sentiment_counts.values, title="Тональность отзывов",
                              color=sentiment_counts.index,
                              color_discrete_map={'positive': '#90EE90', 'negative': '#FF6347', 'neutral': '#D3D3D3'})
        st.plotly_chart(fig_sentiment, use_container_width=True)
    else:
        st.write("Нет данных для отображения тональности.")

    # Распределение по категориям продуктов
    st.subheader("📋 Распределение по категориям продуктов")
    if 'product_category' in df:
        product_counts = df['product_category'].str.split(', ').explode().value_counts()
        fig_product = px.bar(x=product_counts.index, y=product_counts.values, title="Категории продуктов",
                             color=product_counts.index,
                             color_discrete_map={
                                 'Повседневные финансы и платежи': '#1f77b4',
                                 'Кредитование': '#2ca02c',
                                 'Инвестиции': '#d62728',
                                 'Сбережения и накопления': '#ff7f0e',
                                 'Страхование и защита': '#9467bd',
                                 'Премиальные услуги': '#8c564b',
                                 'Другое': '#bcbd22'
                             })
        st.plotly_chart(fig_product, use_container_width=True)
    else:
        st.write("Нет данных для отображения категорий.")
else:
    st.write("Нет данных для анализа. Загрузите JSON с отзывами.")
