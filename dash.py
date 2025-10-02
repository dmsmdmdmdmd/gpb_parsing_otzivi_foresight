import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re
from datetime import datetime
import logging

# Настройки страницы
st.set_page_config(layout="wide", page_title="Аналитика отзывов о Газпромбанке")

# Заголовок
st.title("Аналитика отзывов о Газпромбанке")

# Сайдбар для виджетов
st.sidebar.header("Настройки и загрузка данных")

# Виджеты для загрузки файлов
uploaded_csv = st.sidebar.file_uploader("Загрузите CSV с отзывами", type=['csv'])
uploaded_json = st.sidebar.file_uploader("Загрузите JSON с отзывами для анализа", type=['json'])

# Настройка логирования
logging.basicConfig(filename='app_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Словарь для тональности с весами
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

# Усиливающие слова и отрицания
INTENSIFIERS = {
    'очень': 1.5, 'крайне': 2, 'совсем': 1.5, 'абсолютно': 2, 'полностью': 1.5, 'сильно': 1.5,
    'чрезвычайно': 2, 'невероятно': 2, 'удивительно': 1.5, 'необычно': 1.5, 'весьма': 1.5,
    'слишком': 2, 'часто': 1
}

NEGATION_WORDS = {
    'не', 'нет', 'ни', 'без', 'нельзя', 'невозможно', 'никак', 'ничуть'
}

# Словарь для тем
PRODUCT_CATEGORIES_TOPICS = {
    'Обслуживание': {
        'keywords': ['обслуживан', 'отделени', 'клиент', 'очеред', 'персонал', 'менеджер', 'консультант', 'прием', 'касса', 'оператор', 'обслуживание'],
        'phrases': ['обслуживание в банке', 'отделение банка', 'персональный менеджер', 'консультация в банке', 'очередь в отделении']
    },
    'Мобильное приложение': {
        'keywords': ['мобиль', 'приложен', 'онлайн', 'интернет', 'смс', 'глюк', 'зависа', 'не работ', 'тормоз', 'виснет', 'тупит', 'лагает'],
        'phrases': ['мобильный банк', 'мобильное приложение', 'интернет банк', 'смс информирование', 'приложение зависло']
    },
    'Кредитная карта': {
        'keywords': ['кредитн', 'лимит', 'одобрен', 'погашен', 'процент', 'платеж', 'заявк'],
        'phrases': ['кредитная карта', 'одобрение кредита', 'погашение кредита', 'кредитный лимит', 'оформить карту']
    }
}

# Словарь для классификации продуктов
PRODUCT_CATEGORIES_MAIN = {
    'Повседневные финансы и платежи': {
        'subcategories': {
            'Ведение валютных счетов': {'keywords': ['валют', 'рубл', 'доллар', 'евро', 'валютн', 'счет', 'конвертац', 'обмен'], 'phrases': ['валютный счет', 'обмен валюты', 'конвертация валюты']},
            'Дебетовые карты': {'keywords': ['дебет', 'снятие', 'обслуживание', 'кэшбэк'], 'phrases': ['дебетовая карта', 'обслуживание карты', 'снятие наличных']},
            'Мобильный банк': {'keywords': ['мобиль', 'приложен', 'онлайн', 'интернет', 'смс'], 'phrases': ['мобильный банк', 'мобильное приложение', 'интернет банк']},
            'Переводы': {'keywords': ['перевод', 'средств', 'деньг', 'перечисление'], 'phrases': ['перевод денег', 'перечисление средств']},
            'Зарплатные карты': {'keywords': ['зарплат', 'зарплатн', 'выплата'], 'phrases': ['зарплатная карта', 'выплата зарплаты']}
        },
        'keywords': ['перевод', 'зарплат', 'мобиль', 'банк', 'платеж', 'валют', 'рубл', 'доллар', 'евро', 'снят', 'получен', 'банкомат', 'оплат', 'квитанц', 'комисс', 'обслужван', 'отделени', 'клиент', 'очеред', 'онлайн', 'приложен', 'интернет', 'смс', 'уведомлен', 'средств', 'деньг', 'налич', 'безнал', 'сберкнижк', 'выпис', 'баланс', 'остаток'],
        'phrases': ['зарплатная карта', 'мобильный банк', 'перевод денег', 'открыть счет', 'валютный счет', 'банковский счет', 'расчетный счет', 'снять деньги', 'получить деньги', 'оплатить услуги', 'комиссия за перевод', 'обслуживание карты', 'отделение банка', 'очередь в банке', 'интернет банк', 'мобильное приложение', 'смс информирование', 'безналичный расчет', 'выписка по счету', 'остаток на счете']
    },
    'Сбережения и накопления': {
        'keywords': ['вклад', 'сберегательн', 'накопит', 'сбережен', 'металл', 'счет', 'срочн', 'процент', 'накоп', 'сберег', 'депозит', 'ставк', 'доходност', 'капитализац', 'пополнен', 'снят', 'пролонгац', 'проценты', 'начислен', 'забрат', 'получен', 'золот', 'серебр', 'платин', 'паллад', 'слитк', 'сберегательн', 'сертификат', 'накоплен', 'открыт', 'закрыт'],
        'phrases': ['срочный вклад', 'сберегательный счет', 'металлический счет', 'открыть вклад', 'накопительный счет', 'обезличенный металлический', 'банковский вклад', 'депозитный счет', 'процентная ставка', 'доход по вкладу', 'капитализация процентов', 'пополнить вклад', 'снять со вклада', 'пролонгация вклада', 'начисление процентов', 'забрать вклад', 'открыть депозит', 'золотой слиток', 'сберегательный сертификат', 'накопить деньги']
    },
    'Кредитование': {
        'keywords': ['кредит', 'займ', 'ипотек', 'автокредит', 'ссуд', 'потребительск', 'рефинансировани', 'долг', 'процент', 'платеж', 'погашени', 'ставк', 'срок', 'документ', 'оформлен', 'отказ', 'одобрен', 'переплата', 'задолжен', 'просрочк'],
        'phrases': ['потребительский кредит', 'ипотечный кредит', 'автокредит', 'оформить кредит', 'рефинансирование кредита', 'процент по кредиту', 'погашение кредита', 'ставка по кредиту', 'документы для кредита', 'отказ в кредите', 'переплата по кредиту']
    },
    'Инвестиции': {
        'keywords': ['инвестиц', 'брокер', 'акци', 'облигац', 'фонды', 'портфель', 'доход', 'риск', 'дивиденд', 'торгов', 'бирж', 'управлен', 'прибыль', 'убыток', 'индекс'],
        'phrases': ['инвестиционный портфель', 'покупка акций', 'облигации банка', 'инвестиционные фонды', 'управление активами', 'дивиденды по акциям', 'торговля на бирже', 'индексный фонд']
    },
    'Страхование и защита': {
        'keywords': ['страховк', 'полис', 'выплат', 'ущерб', 'страхован', 'риск', 'оформлен', 'претензи', 'возмещен', 'документ', 'срок', 'услуг', 'ущерб'],
        'phrases': ['страховой полис', 'оформление страховки', 'выплата по страховке', 'возмещение ущерба', 'страхование жизни', 'претензия по страховке']
    },
    'Премиальные услуги': {
        'keywords': ['премиум', 'привилеги', 'элит', 'VIP', 'обслуживан', 'услуг', 'доступ', 'скидк', 'бонус', 'статус', 'карта', 'предложен'],
        'phrases': ['премиальное обслуживание', 'привилегированный клиент', 'VIP-карта', 'элитный статус', 'бонусная программа']
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
    
    if sentiment_score > 1:
        return 'positive'
    elif sentiment_score < -1:
        return 'negative'
    return 'neutral'

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
        matched = False
        if any(word in keywords for word in words) or any(phrase in text for phrase in phrases):
            matched = True
        if matched and 'subcategories' in data:
            for subcategory, subdata in data['subcategories'].items():
                sub_keywords = set(subdata['keywords'])
                sub_phrases = set(subdata['phrases'])
                sub_matched = False
                if any(word in sub_keywords for word in words) or any(phrase in text for phrase in sub_phrases):
                    sub_matched = True
                if sub_matched:
                    categories.add(f"{category} - {subcategory}")
        else:
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
    
    current_date = datetime.now().strftime('%d.%m.%Y')
    rating_map = {'negative': 1, 'neutral': 3, 'positive': 5}
    source = 'gold'
    author = review.get('author', 'Клиент банка')
    title = ' '.join(re.findall(r'\w+', text)[:5]) if text else 'Без заголовка'
    product_categories = classify_product_category(text, topics)
    
    try:
        df = pd.read_csv('gazprombank_reviews_classified.csv', sep=';', encoding='utf-8-sig')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['text', 'topics', 'sentiments', 'date', 'rating', 'source', 'id', 'author', 'title', 'product_category'])
    except Exception as e:
        logging.error(f"Error reading CSV file: {str(e)}")
        return {'id': id, 'topics': topics, 'sentiments': sentiments, 'error': f"Ошибка при чтении файла: {str(e)}"}
    
    topics_str = ', '.join(topics)
    sentiments_str = ', '.join(sentiments)
    product_category_str = ', '.join(product_categories)
    
    avg_rating = sum(rating_map.get(s, 3) for s in sentiments) / len(sentiments) if sentiments else 3
    
    try:
        new_review = pd.DataFrame({
            'text': [text],
            'topics': [topics_str],
            'sentiments': [sentiments_str],
            'date': [current_date],
            'rating': [round(avg_rating)],
            'source': [source],
            'id': [id],
            'author': [author],
            'title': [title],
            'product_category': [product_category_str]
        })
        df = pd.concat([df, new_review], ignore_index=True)
        df.to_csv('gazprombank_reviews_classified.csv', index=False, sep=';', encoding='utf-8-sig')
    except Exception as e:
        logging.error(f"Error writing to CSV file: {str(e)}")
        return {'id': id, 'topics': topics, 'sentiments': sentiments, 'error': f"Ошибка при записи в файл: {str(e)}"}
    
    return {'id': id, 'topics': topics, 'sentiments': sentiments, 'product_category': product_categories}

@st.cache_data
def load_data(uploaded_file, file_type):
    if uploaded_file is not None:
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
        else:  # json
            data = json.load(uploaded_file)
            if 'data' in data and isinstance(data['data'], list):
                predictions = []
                for review in data['data']:
                    result = process_review(review)
                    if 'error' not in result:
                        predictions.append(result)
                # Создаём DataFrame без разбиения на строки
                rows = []
                for pred, orig in zip(predictions, data['data']):
                    row = {
                        'id': pred['id'],
                        'text': orig.get('text', ''),
                        'topics': ', '.join(pred['topics']),
                        'sentiments': ', '.join(pred['sentiments']),
                        'product_category': ', '.join(pred['product_category']),
                        'date': orig.get('date', datetime.now().strftime('%d.%m.%Y')),
                        'rating': orig.get('rating', 3),
                        'author': orig.get('author', 'Клиент банка'),
                        'source': orig.get('source', 'gold'),
                        'title': ' '.join(re.findall(r'\w+', orig.get('text', ''))[:5]) if orig.get('text', '') else 'Без заголовка'
                    }
                    rows.append(row)
                df = pd.DataFrame(rows)
            else:
                st.error("Неверный формат JSON. Ожидается {'data': [{'id': 1, 'text': '...'}]}")
                return pd.DataFrame()

        if not df.empty:
            required_cols = ['text']
            if not all(col in df.columns for col in required_cols):
                missing_cols = [col for col in required_cols if col not in df.columns]
                st.error(f"Отсутствуют колонки: {missing_cols}. Проверьте данные.")
                return pd.DataFrame()

            if 'product_category' not in df.columns:
                df['product_category'] = df['text'].apply(lambda x: ', '.join(classify_product_category(x, classify_topics(x))))
            if 'sentiments' not in df.columns:
                df['sentiments'] = df['text'].apply(classify_sentiment)
            if 'topics' not in df.columns:
                df['topics'] = df['text'].apply(lambda x: ', '.join(classify_topics(x)))

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y', errors='coerce')
            if 'id' not in df.columns:
                df['id'] = df.index + 1

            st.info(f"Загружено {len(df)} строк. Уникальные продукты: {sorted(df['product_category'].unique())}")
            if 'date' in df.columns:
                st.info(f"Диапазон дат: {df['date'].min().strftime('%d.%m.%Y')} - {df['date'].max().strftime('%d.%m.%Y')}")

            return df
    return pd.DataFrame()

if uploaded_csv or uploaded_json:
    df = load_data(uploaded_csv if uploaded_csv else uploaded_json, 'csv' if uploaded_csv else 'json')
else:
    df = pd.DataFrame()
    st.sidebar.warning("Загрузите CSV или JSON с отзывами для анализа")

if not df.empty:
    st.sidebar.header("Фильтры")
    min_date = df['date'].min().date() if 'date' in df and pd.notna(df['date'].min()) else datetime(2024, 1, 1).date()
    max_date = df['date'].max().date() if 'date' in df and pd.notna(df['date'].max()) else datetime(2025, 5, 31).date()
    start_date = st.sidebar.date_input("Начальная дата", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Конечная дата", max_date, min_value=min_date, max_value=max_date)

    source_options = ['Все'] + sorted(df['source'].dropna().unique().tolist()) if 'source' in df.columns else ['Все']
    source_filter = st.sidebar.multiselect("Источник", options=source_options, default=['Все'])

    sentiment_options = ['Все'] + ['positive', 'negative', 'neutral']
    sentiment_filter = st.sidebar.multiselect("Тональность", options=sentiment_options, default=['Все'])

    main_product_options = ['Все'] + sorted([cat for cat in df['product_category'].str.split(', ').explode().unique() if ' - ' not in str(cat)])
    product_filter = st.sidebar.multiselect("Категория продукта", options=main_product_options, default=['Все'])

    subcategories_filter = []
    if 'Повседневные финансы и платежи' in product_filter and len(product_filter) == 1:
        subcategories = sorted([cat for cat in df['product_category'].str.split(', ').explode().unique() if cat.startswith('Повседневные финансы и платежи - ')])
        subcategories_filter = st.sidebar.multiselect("Подкатегория продукта", options=subcategories, default=subcategories)

    if 'Все' in product_filter and len(product_filter) > 1:
        product_filter = ['Все']
        subcategories_filter = []
        st.rerun()

    rating_filter = st.sidebar.slider("Рейтинг", min_value=1, max_value=5, value=(1, 5)) if 'rating' in df.columns else (1, 5)
    keyword_filter = st.sidebar.text_input("Ключевое слово в тексте", "")

    # Фильтрация данных с проверкой наличия колонок
    mask = pd.Series(True, index=df.index)
    if 'date' in df.columns:
        mask &= (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
    if 'rating' in df.columns:
        mask &= df['rating'].between(*rating_filter)
    if 'source' in df.columns and source_filter and 'Все' not in source_filter:
        mask &= df['source'].isin(source_filter)
    if 'sentiments' in df.columns and sentiment_filter and 'Все' not in sentiment_filter:
        mask &= df['sentiments'].str.contains('|'.join(sentiment_filter), case=False, na=False)
    if product_filter and 'Все' not in product_filter:
        mask &= df['product_category'].str.contains('|'.join(product_filter + subcategories_filter), case=False, na=False)
    if 'text' in df.columns and keyword_filter:
        mask &= df['text'].str.contains(keyword_filter, case=False, na=False, regex=True)

    filtered_df = df[mask].copy()

    st.info(f"После фильтрации: {len(filtered_df)} строк. Уникальные продукты в фильтре: {sorted(filtered_df['product_category'].str.split(', ').explode().unique())}")

    # Статистика
    st.header("📊 Общая статистика")
    group_cols = ['id', 'text'] if 'id' in filtered_df.columns else ['text']
    total_reviews = len(filtered_df.groupby(group_cols).size()) if not filtered_df.empty else 0
    st.write(f"Всего уникальных отзывов: {total_reviews}")

    # График распределения тональности
    st.subheader("😊 Распределение тональности")
    if 'sentiments' in filtered_df and not filtered_df['sentiments'].isna().all():
        sentiment_counts = filtered_df.groupby(group_cols + ['sentiments']).size().groupby('sentiments').count()
        fig_sentiment = px.pie(names=sentiment_counts.index, values=sentiment_counts.values, title="Тональность отзывов",
                              color=sentiment_counts.index,
                              color_discrete_map={'positive': '#90EE90', 'negative': '#FF6347', 'neutral': '#D3D3D3'},
                              height=600)
        st.plotly_chart(fig_sentiment, use_container_width=True)
    else:
        st.write("Нет данных для отображения тональности.")

    # Динамика по продуктам по месяцам
    st.subheader("📈 Динамика по продуктам по месяцам")
    if 'date' in filtered_df and 'product_category' in filtered_df and not filtered_df.empty:
        filtered_df['month'] = filtered_df['date'].dt.to_period('M').astype(str)
        product_monthly = filtered_df.groupby(['month', 'product_category']).size().reset_index(name='count')
        if not product_monthly.empty:
            if 'Повседневные финансы и платежи' in product_filter and len(product_filter) == 1:
                product_monthly = product_monthly[product_monthly['product_category'].str.contains('Повседневные финансы и платежи')]
            else:
                product_monthly = product_monthly[product_monthly['product_category'].str.split(', ').apply(lambda x: all(' - ' not in str(cat) for cat in x))]
            if not product_monthly.empty:
                fig_product_trend = px.line(product_monthly, x='month', y='count', color='product_category', title="Отзывы по продуктам по месяцам",
                                           height=600)
                st.plotly_chart(fig_product_trend, use_container_width=True)
            else:
                st.write("Нет данных для отображения динамики.")
        else:
            st.write("Нет данных для отображения динамики.")
    else:
        st.write("Нет данных для отображения динамики.")

    # Распределение по категориям продуктов
    st.subheader("📋 Распределение по категориям продуктов")
    if 'product_category' in filtered_df and not filtered_df['product_category'].isna().all():
        product_counts = filtered_df['product_category'].str.split(', ').explode().value_counts()
        if not product_counts.empty:
            if not product_filter or ('Все' in product_filter and len(product_filter) == 1):
                product_counts_filtered = product_counts[~product_counts.index.str.contains(' - ', na=False)]
            elif 'Повседневные финансы и платежи' in product_filter and len(product_filter) == 1:
                product_counts_filtered = product_counts[product_counts.index.isin(['Повседневные финансы и платежи'] + subcategories_filter)]
            else:
                product_counts_filtered = product_counts[~product_counts.index.str.contains(' - ', na=False)]

            if not product_counts_filtered.empty:
                fig_product = px.bar(x=product_counts_filtered.index, y=product_counts_filtered.values, title="Категории продуктов",
                                    color=product_counts_filtered.index,
                                    color_discrete_map={
                                        'Повседневные финансы и платежи': '#1f77b4',
                                        'Повседневные финансы и платежи - Ведение валютных счетов': '#1f77b4',
                                        'Повседневные финансы и платежи - Дебетовые карты': '#1f77b4',
                                        'Повседневные финансы и платежи - Мобильный банк': '#1f77b4',
                                        'Повседневные финансы и платежи - Переводы': '#1f77b4',
                                        'Повседневные финансы и платежи - Зарплатные карты': '#1f77b4',
                                        'Сбережения и накопления': '#ff7f0e',
                                        'Кредитование': '#2ca02c',
                                        'Инвестиции': '#d62728',
                                        'Страхование и защита': '#9467bd',
                                        'Премиальные услуги': '#8c564b',
                                        'Другое': '#bcbd22'
                                    },
                                    height=600)
                st.plotly_chart(fig_product, use_container_width=True)
            else:
                st.write("Нет данных для отображения категорий.")
        else:
            st.write("Нет данных для отображения категорий.")

    # Таблица отзывов
    st.subheader("📝 Подробные отзывы")
    if not filtered_df.empty:
        group_cols_table = ['id', 'date', 'author', 'title', 'text', 'rating', 'sentiments', 'source', 'topics', 'product_category'] if all(col in filtered_df.columns for col in ['id', 'date', 'author', 'title', 'text', 'rating', 'sentiments', 'source', 'topics', 'product_category']) else ['date', 'author', 'title', 'text', 'rating', 'sentiments', 'source', 'topics', 'product_category']
        display_df = filtered_df.groupby(group_cols_table).size().reset_index(name='count')
        st.dataframe(display_df, width=1500, height=800)
    else:
        st.write("Нет данных для отображения таблицы.")
else:
    st.write("Нет данных для анализа. Загрузите CSV или JSON с отзывами.")
