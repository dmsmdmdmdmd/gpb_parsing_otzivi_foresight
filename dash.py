import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import re
from datetime import datetime

# Настройки страницы
st.set_page_config(layout="wide", page_title="Аналитика отзывов о Газпромбанке")

# Заголовок
st.title("Аналитика отзывов о Газпромбанке")

# Сайдбар для виджетов
st.sidebar.header("Настройки и загрузка данных")

# Виджеты для загрузки файлов (вне функции)
uploaded_csv = st.sidebar.file_uploader("Загрузите CSV с отзывами", type=['csv'])
uploaded_json = st.sidebar.file_uploader("Загрузите JSON с отзывами для анализа", type=['json'])

# Функция классификации продуктов
PRODUCT_CATEGORIES = {
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

def classify_product(text):
    text = text.lower()
    categories = set()
    words = set(re.findall(r'\w+', text))
    
    for category, data in PRODUCT_CATEGORIES.items():
        keywords = set(data['keywords'])
        phrases = set(data['phrases'])
        if any(word in keywords for word in words) or any(phrase in text for phrase in phrases):
            if category == 'Повседневные финансы и платежи' and 'subcategories' in data:
                for subcategory, subdata in data['subcategories'].items():
                    sub_keywords = set(subdata['keywords'])
                    sub_phrases = set(subdata['phrases'])
                    if any(word in sub_keywords for word in words) or any(phrase in text for phrase in sub_phrases):
                        categories.add(f"{category} - {subcategory}")
            else:
                categories.add(category)
    
    return list(categories) if categories else ['Другое']

# Загрузка и обработка данных
@st.cache_data
def load_data(uploaded_file, file_type):
    if uploaded_file is not None:
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
        else:  # json
            data = json.load(uploaded_file)
            if 'data' in data and isinstance(data['data'], list):
                response = requests.post('https://dmsmdmdmdmd.pythonanywhere.com/predict', json=data)
                if response.status_code == 200:
                    result = response.json()
                    df = pd.DataFrame(result.get('predictions', []))
                else:
                    st.error(f"Ошибка API: {response.text} (код: {response.status_code}). Проверьте логи на PythonAnywhere.")
                    return pd.DataFrame()
            else:
                st.error("Неверный формат JSON. Ожидается {'data': [{'id': 1, 'text': '...'}]}")
                return pd.DataFrame()

        if not df.empty:
            # Проверка наличия необходимых колонок
            required_cols = ['text', 'rating']
            if not all(col in df.columns for col in required_cols):
                missing_cols = [col for col in required_cols if col not in df.columns]
                st.error(f"Отсутствуют колонки: {missing_cols}. Проверьте данные.")
                return pd.DataFrame()

            # Классификация продуктов
            df['product'] = df.apply(lambda row: classify_product(row.get('text', '')), axis=1)
            # Классификация тональности
            df['sentiment'] = df['rating'].apply(lambda x: 'negative' if x < 3 else 'neutral' if x == 3 else 'positive' if pd.notna(x) else 'neutral')
            df.to_csv('temp_reviews.csv', index=False, sep=';', encoding='utf-8-sig')

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y', errors='coerce')
            if 'id' not in df.columns:
                df['id'] = df.index + 1
            expanded_rows = []
            for _, row in df.iterrows():
                categories = row['product'] if isinstance(row['product'], list) else [row['product']]
                for category in categories:
                    new_row = row.copy()
                    new_row['product'] = category.strip()
                    expanded_rows.append(new_row)
            expanded_df = pd.DataFrame(expanded_rows)

            st.info(f"Загружено {len(expanded_df)} строк. Уникальные продукты: {sorted(expanded_df['product'].unique())}")
            if 'date' in expanded_df.columns:
                st.info(f"Диапазон дат: {expanded_df['date'].min().strftime('%d.%m.%Y')} - {expanded_df['date'].max().strftime('%d.%m.%Y')}")

            return expanded_df
    return pd.DataFrame()

# Логика выбора файла и загрузки данных
if uploaded_csv or uploaded_json:
    df = load_data(uploaded_csv if uploaded_csv else uploaded_json, 'csv' if uploaded_csv else 'json')
else:
    df = pd.DataFrame()
    st.sidebar.warning("Загрузите CSV или JSON с отзывами для анализа")

# Фильтры в сайдбаре
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

    main_product_options = ['Все'] + sorted([cat for cat in df['product'].unique() if ' - ' not in str(cat)])
    product_filter = st.sidebar.multiselect("Категория продукта", options=main_product_options, default=['Все'])

    subcategories_filter = []
    if 'Повседневные финансы и платежи' in product_filter and len(product_filter) == 1:
        subcategories = sorted([cat for cat in df['product'].unique() if cat.startswith('Повседневные финансы и платежи - ')])
        subcategories_filter = st.sidebar.multiselect("Подкатегория продукта", options=subcategories, default=subcategories)

    if 'Все' in product_filter and len(product_filter) > 1:
        product_filter = ['Все']
        subcategories_filter = []
        st.rerun()

    rating_filter = st.sidebar.slider("Рейтинг", min_value=1, max_value=5, value=(1, 5))
    keyword_filter = st.sidebar.text_input("Ключевое слово в тексте", "")

    # Фильтрация данных
    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date) if 'date' in df.columns else True
    if 'rating' in df.columns:
        mask &= df['rating'].between(*rating_filter)
    if source_filter and 'Все' not in source_filter and 'source' in df.columns:
        mask &= df['source'].isin(source_filter)
    if sentiment_filter and 'Все' not in sentiment_filter and 'sentiment' in df.columns:
        mask &= df['sentiment'].isin(sentiment_filter)
    if product_filter and 'Все' not in product_filter:
        mask &= df['product'].isin(product_filter + subcategories_filter)
    if keyword_filter and 'text' in df.columns:
        mask &= df['text'].str.contains(keyword_filter, case=False, na=False, regex=True)

    filtered_df = df[mask].copy()

    st.info(f"После фильтрации: {len(filtered_df)} строк. Уникальные продукты в фильтре: {sorted(filtered_df['product'].unique())}")

    # Статистика
    st.header("📊 Общая статистика")
    group_cols = ['id', 'text'] if 'id' in filtered_df.columns else ['text']
    total_reviews = len(filtered_df.groupby(group_cols).size()) if not filtered_df.empty else 0
    st.write(f"Всего уникальных отзывов: {total_reviews}")

    # График распределения тональности
    st.subheader("😊 Распределение тональности")
    if 'sentiment' in filtered_df and not filtered_df['sentiment'].isna().all():
        sentiment_counts = filtered_df.groupby(group_cols + ['sentiment']).size().groupby('sentiment').count()
        fig_sentiment = px.pie(names=sentiment_counts.index, values=sentiment_counts.values, title="Тональность отзывов",
                              color=sentiment_counts.index,
                              color_discrete_map={'positive': '#90EE90', 'negative': '#FF6347', 'neutral': '#D3D3D3'},
                              height=600)
        st.plotly_chart(fig_sentiment, use_container_width=True)
    else:
        st.write("Нет данных для отображения тональности.")

    # Динамика по продуктам по месяцам
    st.subheader("📈 Динамика по продуктам по месяцам")
    if 'date' in filtered_df and 'product' in filtered_df and not filtered_df.empty:
        filtered_df['month'] = filtered_df['date'].dt.to_period('M').astype(str)
        product_monthly = filtered_df.groupby(['month', 'product']).size().reset_index(name='count')
        if not product_monthly.empty:
            if 'Повседневные финансы и платежи' in product_filter and len(product_filter) == 1:
                product_monthly = product_monthly[product_monthly['product'].isin(['Повседневные финансы и платежи'] + subcategories_filter)]
            else:
                product_monthly = product_monthly[~product_monthly['product'].str.contains(' - ', na=False)]
            if not product_monthly.empty:
                fig_product_trend = px.line(product_monthly, x='month', y='count', color='product', title="Отзывы по продуктам по месяцам",
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
    if 'product' in filtered_df and not filtered_df['product'].isna().all():
        product_counts = filtered_df['product'].value_counts()
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
        group_cols_table = ['id', 'date', 'author', 'title', 'text', 'rating', 'sentiment', 'source'] if 'id' in filtered_df.columns else ['date', 'author', 'title', 'text', 'rating', 'sentiment', 'source']
        display_df = filtered_df.groupby(group_cols_table)['product'].apply(lambda x: ', '.join(x.dropna())).reset_index()
        st.dataframe(display_df, width=1500, height=800)
    else:
        st.write("Нет данных для отображения таблицы.")
else:
    st.write("Нет данных для анализа. Загрузите CSV или JSON с отзывами.")
