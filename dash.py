import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re
from datetime import datetime

st.set_page_config(layout="wide", page_title="Аналитика отзывов о Газпромбанке")
st.title("Аналитика отзывов о Газпромбанке")

# === ТОЧНЫЙ СПИСОК ПОДКАТЕГОРИЙ ИЗ ТЗ ===
PRODUCT_CATEGORIES = {
    'Повседневные финансы и платежи': [
        'Ведение валютных счетов',
        'Дебетовые карты',
        'Мобильный банк',
        'Переводы',
        'Зарплатные карты'
    ],
    'Сбережения и накопления': [
        'Срочные вклады',
        'Сберегательные счета',
        'Обезличенные металлические счета',
        'Накопительные счета'
    ],
    'Кредитование': [
        'Потребительские кредиты',
        'Кредитные карты',
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

# Собираем все темы в формате "Категория — Подкатегория"
ALL_TOPICS = []
for cat, subcats in PRODUCT_CATEGORIES.items():
    for sub in subcats:
        ALL_TOPICS.append(f"{cat} — {sub}")

# Ключевые слова для каждой подкатегории
KEYWORDS = {}

for cat, subcats in PRODUCT_CATEGORIES.items():
    for sub in subcats:
        full_name = f"{cat} — {sub}"
        if sub == 'Ведение валютных счетов':
            words = ['валют', 'счет', 'конвертац']
            phrases = ['валютный счет']
        elif sub == 'Дебетовые карты':
            words = ['дебет', 'снятие', 'кэшбэк']
            phrases = ['дебетовая карта']
        elif sub == 'Мобильный банк':
            words = ['мобильн', 'приложен', 'онлайн', 'зависа', 'мобилка']
            phrases = ['мобильное приложение', 'мобильный банк']
        elif sub == 'Переводы':
            words = ['перевод', 'средств', 'перевести']
            phrases = ['перевод денег']
        elif sub == 'Зарплатные карты':
            words = ['зарплат', 'зп']
            phrases = ['зарплатная карта']
        elif sub == 'Срочные вклады':
            words = ['срочн', 'вклад']
            phrases = ['срочный вклад']
        elif sub == 'Сберегательные счета':
            words = ['сберегательн', 'счет']
            phrases = ['сберегательный счет']
        elif sub == 'Обезличенные металлические счета':
            words = ['металл', 'обезличен', 'омс']
            phrases = ['обезличенный металлический счет']
        elif sub == 'Накопительные счета':
            words = ['накопит', 'счет']
            phrases = ['накопительный счет']
        elif sub == 'Потребительские кредиты':
            words = ['потребительск', 'кредит']
            phrases = ['потребительский кредит']
        elif sub == 'Кредитные карты':
            words = ['кредитн', 'карта', 'лимит']
            phrases = ['кредитная карта']
        elif sub == 'Ипотечные кредиты':
            words = ['ипотек', 'ипотечн']
            phrases = ['ипотечный кредит']
        elif sub == 'Автокредиты':
            words = ['автокредит', 'авто кредит']
            phrases = ['автомобильный кредит']
        elif sub == 'Рефинансирование':
            words = ['рефинансирован']
            phrases = ['рефинансирование кредита']
        elif sub == 'Брокерский счет':
            words = ['брокер', 'счет']
            phrases = ['брокерский счет']
        elif sub == 'ИИС (Индивидуальный инвестиционный счет)':
            words = ['иис', 'инвест', 'счет']
            phrases = ['индивидуальный инвестиционный счет']
        elif sub == 'ПИФы (Паевые инвестиционные фонды)':
            words = ['пиф', 'паев', 'фонд']
            phrases = ['паевой фонд']
        elif sub == 'Структурные продукты':
            words = ['структурн']
            phrases = ['структурный продукт']
        elif sub == 'Страхование путешествий':
            words = ['путешестви', 'туризм', 'поездк']
            phrases = ['страхование путешествий']
        elif sub == 'Страхование имущества':
            words = ['имуществ', 'дом', 'квартир']
            phrases = ['страхование имущества']
        elif sub == 'Страхование от несчастных случаев и болезней':
            words = ['несчастн', 'болезн', 'травм', 'инвалид']
            phrases = ['страхование от несчастных случаев']
        elif sub == 'Страхование при оформлении кредитов':
            words = ['кредит', 'страхован']
            phrases = ['страхование при оформлении кредита']
        elif sub == 'Приват банкинг':
            words = ['приват', 'премиум', 'vip']
            phrases = ['приват-банкинг']
        elif sub == 'Депозитарные ячейки':
            words = ['ячейк', 'сейф']
            phrases = ['депозитарные ячейки']
        elif sub == 'Услуги по консультированию и планированию':
            words = ['консультирован', 'планирован', 'финансов', 'совет']
            phrases = ['услуги по консультированию']
        else:
            words = []
            phrases = []
        KEYWORDS[full_name] = {'keywords': words, 'phrases': phrases}

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

def split_into_fragments(text):
    # Разделяем по союзам, сохраняя контекст
    parts = re.split(r'\b(но|зато|однако|при этом|а также|и|но при этом|зато при этом)\b', text, flags=re.IGNORECASE)
    fragments = []
    current = ""
    for i, part in enumerate(parts):
        if i % 2 == 0:
            current = part.strip()
        else:
            if current:
                fragments.append(current)
            current = part.strip() + " " + (parts[i+1].strip() if i+1 < len(parts) else "")
    if current:
        fragments.append(current)
    return fragments if fragments else [text]

def process_review(review):
    text = review.get('text', '')
    id = review.get('id', 0)
    
    # Находим все темы в отзыве
    found_topics = []
    for topic, data in KEYWORDS.items():
        if any(phrase in text.lower() for phrase in data['phrases']) or \
           any(kw in text.lower() for kw in data['keywords']):
            found_topics.append(topic)
    
    if not found_topics:
        found_topics = ["Другое"]
    
    # Разбиваем на фрагменты
    fragments = split_into_fragments(text)
    
    # Для каждой темы находим ближайший фрагмент и определяем тональность
    sentiments = []
    for topic in found_topics:
        if topic == "Другое":
            sent = classify_sentiment(text)
        else:
            # Ищем фрагмент, содержащий ключевые слова темы
            sent = 'нейтрально'
            data = KEYWORDS[topic]
            for frag in fragments:
                if any(phrase in frag.lower() for phrase in data['phrases']) or \
                   any(kw in frag.lower() for kw in data['keywords']):
                    sent = classify_sentiment(frag)
                    break
        sentiments.append(sent)
    
    # Rating для дашборда (не возвращается в API)
    if all(s == 'положительно' for s in sentiments):
        rating = 5
    elif all(s == 'нейтрально' for s in sentiments):
        rating = 3
    else:
        rating = 1
    
    return {
        'id': id,
        'text': text,
        'topics': ', '.join(found_topics),
        'sentiments': ', '.join(sentiments),
        'product_category': ', '.join(found_topics),
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
        
        # Фильтры по категориям и подкатегориям
        selected_categories = st.sidebar.multiselect(
            "Категории",
            options=list(PRODUCT_CATEGORIES.keys()),
            default=[]
        )
        all_subcats = [sub for subs in PRODUCT_CATEGORIES.values() for sub in subs]
        selected_subcategories = st.sidebar.multiselect(
            "Подкатегории",
            options=all_subcats,
            default=[]
        )

        # Фильтрация
        mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date) & (df['rating'].between(*rating_filter))
        
        if selected_categories:
            cat_pattern = '|'.join([re.escape(cat) for cat in selected_categories])
            mask &= df['product_category'].str.contains(cat_pattern, case=False, na=False)
        if selected_subcategories:
            subcat_pattern = '|'.join([re.escape(sub) for sub in selected_subcategories])
            mask &= df['product_category'].str.contains(subcat_pattern, case=False, na=False)

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
