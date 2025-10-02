import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import re

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
        'keywords': ['кредит', 'ипотек', 'автокредит', 'рефинансирован', 'заем', 'платеж', 'процент', 'ставк', 'одобрен', 'погашен', 'взят', 'оформлен', 'долг', 'задолженност', 'просрочк', 'штраф', 'пени', 'реструктуризац', 'решен', 'отказ', 'услов', 'требован', 'справк', 'заявк', 'анкет', 'кредитн', 'истори', 'скоринг', 'лимит', 'льготн', 'период', 'график', 'платеж'],
        'phrases': ['потребительский кредит', 'ипотечный кредит', 'взять кредит', 'оформить кредит', 'кредитная карта', 'рефинансирование кредита', 'автомобильный кредит', 'одобрение кредита', 'погашение кредита', 'кредитная история', 'процентная ставка', 'ежемесячный платеж', 'льготный период', 'график платежей', 'просрочка платежа', 'штрафные санкции', 'реструктуризация долга', 'отказ в кредите', 'кредитная заявка', 'справка о доходах', 'кредитный лимит']
    },
    'Инвестиции': {
        'keywords': ['инвест', 'брокер', 'иис', 'пиф', 'акци', 'облигац', 'бирж', 'портфель', 'доходност', 'структурн', 'пай', 'фонд', 'ценн', 'бумаг', 'торгов', 'сделк', 'купля', 'продаж', 'котировк', 'дивиденд', 'купон', 'выплат', 'риск', 'прибыл', 'убыток', 'анализ', 'совет', 'управлен', 'инвестор', 'трейдер', 'лиценз', 'комисс', 'тариф'],
        'phrases': ['брокерский счет', 'инвестиционный счет', 'паевой фонд', 'структурный продукт', 'купить акции', 'инвестировать деньги', 'индивидуальный инвестиционный счет', 'ценные бумаги', 'торговля на бирже', 'инвестиционный портфель', 'доходность инвестиций', 'покупка акций', 'продажа облигаций', 'дивидендные выплаты', 'купонный доход', 'управление портфелем', 'инвестиционный риск', 'биржевые торги', 'лицензия брокера', 'тарифы на обслуживание', 'инвестиционная стратегия', 'финансовый советник']
    },
    'Страхование и защита': {
        'keywords': ['страхов', 'защит', 'путешеств', 'имуществ', 'несчастн', 'случа', 'болезн', 'риск', 'полис', 'страховк', 'выплат', 'компенсац', 'дтп', 'авария', 'здоров', 'жизн', 'недвиж', 'квартир', 'дом', 'машин', 'авто', 'лечен', 'больничн', 'госпитализац', 'оплат', 'лекарств', 'ущерб', 'поврежден', 'краж', 'пожар', 'затоплен', 'ответственност', 'гражданск'],
        'phrases': ['страхование путешественников', 'страхование имущества', 'страховой полис', 'страхование от несчастных случаев', 'страхование здоровья', 'страхование жизни', 'страхование квартиры', 'страхование автомобиля', 'страховой случай', 'страховая выплата', 'компенсация ущерба', 'добровольное страхование', 'обязательное страхование', 'страхование ответственности', 'страхование ипотеки', 'медицинская страховка', 'страхование выезжающих за рубеж', 'страховое возмещение', 'оформить страховку', 'отказали в выплате', 'страховая компания']
    },
    'Премиальные услуги': {
        'keywords': ['приват', 'премиум', 'депозитар', 'ячейк', 'консультирован', 'планирован', 'персонал', 'менеджер', 'эксклюзив', 'вип', 'персональн', 'обслужван', 'услуг', 'богат', 'состоян', 'капитал', 'наслед', 'сохран', 'приумножен', 'управлен', 'актив', 'ценност', 'драгоценност', 'хранен', 'привилеги', 'элитн', 'специальн', 'индивидуальн', 'конфиденц', 'преференц', 'сервис', 'комнат', 'зал', 'зона', 'приемн', 'оформлен', 'доступ', 'уникальн'],
        'phrases': ['приват-банкинг', 'премиум-обслуживание', 'депозитарные услуги', 'сейфовая ячейка', 'персональный менеджер', 'эксклюзивное обслуживание', 'VIP-услуги', 'индивидуальный подход', 'управление капиталом', 'наследование капитала', 'сохранение активов', 'приумножение средств', 'хранение ценностей', 'премиальный сервис', 'конфиденциальное обслуживание', 'элитный зал', 'привилегированный доступ', 'уникальные предложения', 'персональный консультант', 'оформление премиум-услуг']
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

# Загрузка данных
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('gazprombank_reviews_classified.csv', sep=';', encoding='utf-8-sig')
        df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
        
        # Если 'id' нет, добавляем искусственно
        if 'id' not in df.columns:
            df['id'] = df.index + 1  # Нумерация начиная с 1
        
        # Разделяем множественные категории продуктов
        expanded_rows = []
        for _, row in df.iterrows():
            categories = row['product_category'].split(', ') if pd.notna(row['product_category']) else ['Другое']
            for category in categories:
                new_row = row.copy()
                new_row['product'] = category.strip()
                expanded_rows.append(new_row)
        
        expanded_df = pd.DataFrame(expanded_rows)
        
        # Классификация тональности по рейтингу
        expanded_df['sentiment'] = expanded_df['rating'].apply(lambda x: 'negative' if x < 3 else 'neutral' if x == 3 else 'positive')
        
        # Отладка: выводим информацию о данных
        st.info(f"Загружено {len(expanded_df)} строк. Уникальные продукты: {sorted(expanded_df['product'].unique())}")
        st.info(f"Диапазон дат: {expanded_df['date'].min().strftime('%d.%m.%Y')} - {expanded_df['date'].max().strftime('%d.%m.%Y')}")
        
        return expanded_df
    except FileNotFoundError:
        st.error("Файл gazprombank_reviews_classified.csv не найден. Запустите api_reviews.py для сбора данных.")
        return pd.DataFrame()

# Основной дашборд
st.set_page_config(layout="wide")  # Установка широкого макета
st.title("Аналитика отзывов о Газпромбанке")

# Загрузка данных
df = load_data()

if not df.empty:
    # Фильтры
    st.sidebar.header("Фильтры")
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    start_date = st.sidebar.date_input("Начальная дата", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("Конечная дата", max_date, min_value=min_date, max_value=max_date)
    
    # Фильтр по источникам
    source_options = ['Все'] + sorted(df['source'].unique().tolist())
    source_filter = st.sidebar.multiselect("Источник", options=source_options, default=['Все'])
    
    # Тональность с выпадающим списком и "Все" по умолчанию
    sentiment_options = ['Все'] + ['positive', 'negative', 'neutral']
    sentiment_filter = st.sidebar.multiselect("Тональность", options=sentiment_options, default=['Все'])
    
    # Категории продуктов с выпадающим списком и "Все" по умолчанию
    main_product_options = ['Все'] + sorted([cat for cat in df['product'].unique() if ' - ' not in cat])
    product_filter = st.sidebar.multiselect("Категория продукта", options=main_product_options, default=['Все'])
    
    # Динамическое отображение подпунктов только при выборе "Повседневные финансы и платежи"
    subcategories_filter = []
    if 'Повседневные финансы и платежи' in product_filter and len(product_filter) == 1:
        subcategories = sorted([cat for cat in df['product'].unique() if cat.startswith('Повседневные финансы и платежи - ')])
        subcategories_filter = st.sidebar.multiselect("Подкатегория продукта", options=subcategories, default=subcategories)
    
    # Сброс "Все" при выборе другой категории
    if 'Все' in product_filter and len(product_filter) > 1:
        product_filter = ['Все']
        subcategories_filter = []
        st.rerun()
    
    rating_filter = st.sidebar.slider("Рейтинг", min_value=1, max_value=5, value=(1, 5))
    keyword_filter = st.sidebar.text_input("Ключевое слово в тексте", "")
    
    # Фильтрация данных
    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date) & \
           (df['rating'].between(*rating_filter))
    if source_filter and 'Все' not in source_filter:
        mask &= df['source'].isin(source_filter)
    if sentiment_filter and 'Все' not in sentiment_filter:
        mask &= df['sentiment'].isin(sentiment_filter)
    if product_filter and 'Все' not in product_filter:
        mask &= df['product'].isin(product_filter + subcategories_filter)
    if keyword_filter:
        mask &= df['text'].str.contains(keyword_filter, case=False, na=False)
    
    filtered_df = df[mask].copy()
    
    # Отладка: выводим информацию о фильтрованных данных
    st.info(f"После фильтрации: {len(filtered_df)} строк. Уникальные продукты в фильтре: {sorted(filtered_df['product'].unique())}")
    
    # Статистика
    st.header("📊 Общая статистика")
    group_cols = ['id', 'text'] if 'id' in filtered_df.columns else ['text']
    total_reviews = len(filtered_df.groupby(group_cols))
    st.write(f"Всего уникальных отзывов: {total_reviews}")
    
    # График распределения тональности с цветами
    sentiment_counts = filtered_df.groupby(group_cols + ['sentiment']).size().groupby('sentiment').count()
    st.subheader("😊 Распределение тональности")
    if not sentiment_counts.empty:
        fig_sentiment = px.pie(names=sentiment_counts.index, values=sentiment_counts.values, title="Тональность отзывов",
                               color=sentiment_counts.index,
                               color_discrete_map={'positive': '#90EE90', 'negative': '#FF6347', 'neutral': '#D3D3D3'},
                               height=600)
        st.plotly_chart(fig_sentiment, use_container_width=True)
    else:
        st.write("Нет данных для отображения тональности.")
    
    # Динамика по продуктам по месяцам
    filtered_df['month'] = filtered_df['date'].dt.to_period('M').astype(str)
    product_monthly = filtered_df.groupby(['month', 'product']).size().reset_index(name='count')
    st.subheader("📈 Динамика по продуктам по месяцам")
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
    
    # График по категориям продуктов с цветами
    product_counts = filtered_df['product'].value_counts()
    st.subheader("📋 Распределение по категориям продуктов")
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
    
    # Таблица отзывов (шире и с фильтрами)
    st.subheader("📝 Подробные отзывы")
    group_cols_table = ['id', 'date', 'author', 'title', 'text', 'rating', 'sentiment', 'source'] if 'id' in filtered_df.columns else ['date', 'author', 'title', 'text', 'rating', 'sentiment', 'source']
    display_df = filtered_df.groupby(group_cols_table)['product'].apply(lambda x: ', '.join(x)).reset_index()
    st.dataframe(display_df, width=1500, height=800)
else:
    st.write("Нет данных для отображения. Убедитесь, что файл данных создан.")
