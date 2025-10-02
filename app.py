from flask import Flask, request, jsonify
import re
import json
import pandas as pd
from datetime import datetime
import logging

app = Flask(__name__)

# Настройка логирования ошибок
logging.basicConfig(filename='app_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Словарь для тональности с уточнёнными весами
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
PRODUCT_CATEGORIES = {
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
        'keywords': ['кредит', 'ипотек', 'автокредит', 'рефинансирован', 'заем', 'платеж', 'процент', 'ставк', 'одобрен', 'погашен', 'взят', 'оформлен', 'долг', 'задолженност', 'просрочк', 'штраф', 'пени', 'реструктуризац', 'решен', 'отказ', 'услов', 'требован', 'справк', 'заявк', 'анкет', 'кредитн', 'истори', 'скоринг', 'лимит', 'льготн', 'период', 'график', 'платеж'],
        'phrases': ['потребительский кредит', 'ипотечный кредит', 'взять кредит', 'оформить кредит', 'кредитная карта', 'рефинансирование кредита', 'автомобильный кредит', 'одобрение кредита', 'погашение кредита', 'кредитная история', 'процентная ставка', 'ежемесячный платеж', 'льготный период', 'график платежей', 'просрочка платежа', 'штрафные санкции', 'реструктуризация долга', 'отказ в кредите', 'кредитная заявка', 'справка о доходах', 'кредитный лимит']
    },
    'Премиальные услуги': {
        'keywords': ['приват', 'премиум', 'депозитар', 'ячейк', 'консультирован', 'планирован', 'персонал', 'менеджер', 'эксклюзив', 'вип', 'персональн', 'обслужван', 'услуг', 'богат', 'состоян', 'капитал', 'наслед', 'сохран', 'приумножен', 'управлен', 'актив', 'ценност', 'драгоценност', 'хранен', 'привилеги', 'элитн', 'специальн', 'индивидуальн', 'конфиденц', 'преференц', 'сервис', 'комнат', 'зал', 'зона', 'приемн', 'оформлен', 'доступ', 'уникальн'],
        'phrases': ['приват-банкинг', 'премиум-обслуживание', 'депозитарные услуги', 'сейфовая ячейка', 'персональный менеджер', 'эксклюзивное обслуживание', 'VIP-услуги', 'индивидуальный подход', 'управление капиталом', 'наследование капитала', 'сохранение активов', 'приумножение средств', 'хранение ценностей', 'премиальный сервис', 'конфиденциальное обслуживание', 'элитный зал', 'привилегированный доступ', 'уникальные предложения', 'персональный консультант', 'оформление премиум-услуг']
    },
    'Инвестиции': {
        'keywords': ['инвест', 'брокер', 'иис', 'пиф', 'акци', 'облигац', 'бирж', 'портфель', 'доходност', 'структурн', 'пай', 'фонд', 'ценн', 'бумаг', 'торгов', 'сделк', 'купля', 'продаж', 'котировк', 'дивиденд', 'купон', 'выплат', 'риск', 'прибыл', 'убыток', 'анализ', 'совет', 'управлен', 'инвестор', 'трейдер', 'лиценз', 'комисс', 'тариф'],
        'phrases': ['брокерский счет', 'инвестиционный счет', 'паевой фонд', 'структурный продукт', 'купить акции', 'инвестировать деньги', 'индивидуальный инвестиционный счет', 'ценные бумаги', 'торговля на бирже', 'инвестиционный портфель', 'доходность инвестиций', 'покупка акций', 'продажа облигаций', 'дивидендные выплаты', 'купонный доход', 'управление портфелем', 'инвестиционный риск', 'биржевые торги', 'лицензия брокера', 'тарифы на обслуживание', 'инвестиционная стратегия', 'финансовый советник']
    }
}

def classify_sentiment(text):
    text = text.lower()
    sentiment_score = 0
    words = re.findall(r'\w+', text)
    
    # Проверка на отрицания
    has_negation = any(word in NEGATION_WORDS for word in words)
    
    # Оценка тональности с учетом фраз и стемов
    for sentiment_type, lex_dict in SENTIMENT_LEXICON.items():
        for key, value in lex_dict.items():
            if ' ' in key:  # Для фраз проверяем наличие в тексте
                if key in text:
                    sentiment_score += value
            else:  # Для стемов проверяем startswith на словах
                for word in words:
                    if word.startswith(key):
                        sentiment_score += value
    
    # Простая обработка интенсификаторов
    multiplier = 1.0
    for word in words:
        for intens, mult in INTENSIFIERS.items():
            if word.startswith(intens):
                multiplier = max(multiplier, mult)
    sentiment_score *= multiplier
    
    # Корректировка тональности при наличии отрицания
    if has_negation and sentiment_score > 0:
        sentiment_score = -sentiment_score  # Инвертируем положительную тональность
    elif has_negation and sentiment_score < 0:
        sentiment_score = abs(sentiment_score) * 0.5  # Снижаем эффект отрицания для негативной тональности
    
    if sentiment_score > 1:
        return 'положительно'
    elif sentiment_score < -1:
        return 'отрицательно'
    else:
        return 'нейтрально'

def classify_topics(text):
    text = text.lower()
    topics = []
    words = re.findall(r'\w+', text)
    
    for category, data in PRODUCT_CATEGORIES.items():
        matched = False
        # Проверка ключевых слов с startswith
        for word in words:
            if any(word.startswith(kw) for kw in data['keywords']):
                matched = True
                break
        # Проверка фраз
        if not matched and any(phrase in text for phrase in data['phrases']):
            matched = True
        if matched:
            topics.append(category)
    
    return topics if topics else ['Другое']

def classify_product_category(text, topics):
    text = text.lower()
    words = re.findall(r'\w+', text)
    categories = set()

    # Соответствие тем и категорий продуктов
    topic_to_category = {
        'Обслуживание': 'Повседневные финансы и платежи',
        'Мобильное приложение': 'Повседневные финансы и платежи - Мобильный банк',
        'Кредитная карта': 'Кредитование'
    }

    for topic in topics:
        if topic in topic_to_category:
            categories.add(topic_to_category[topic])

    # Если темы не определены или нет соответствия, проверяем по общим категориям
    if not categories:
        for category, data in PRODUCT_CATEGORIES_MAIN.items():
            matched = False
            for w in words:  # Используем локальную переменную w
                if any(w.startswith(kw) for kw in data['keywords']):
                    matched = True
                    break
            if not matched and any(phrase in text for phrase in data['phrases']):
                matched = True
            if matched:
                if category == 'Повседневные финансы и платежи' and 'subcategories' in data:
                    for subcategory, subdata in data['subcategories'].items():
                        sub_matched = False
                        for w in words:  # Используем локальную переменную w
                            if any(w.startswith(kw) for kw in subdata['keywords']):
                                sub_matched = True
                                break
                        if not sub_matched and any(phrase in text for phrase in subdata['phrases']):
                            sub_matched = True
                        if sub_matched:
                            categories.add(f"{category} - {subcategory}")
                else:
                    categories.add(category)

    return list(categories) if categories else ['Другое']

def process_review(review):
    text = review.get('text', '')
    id = review.get('id', 0)
    
    # Разделяем текст на части по "но" и обрабатываем
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
        # Если нет разделения по "но", классифицируем весь текст
        topics = classify_topics(text)
        sentiment = classify_sentiment(text)
        sentiments = [sentiment] * len(topics)
    
    # Удаляем "Другое", если есть конкретные темы
    if len(topics) > 1 and 'Другое' in topics:
        idx = topics.index('Другое')
        topics.pop(idx)
        sentiments.pop(idx)
    
    # Сохранение в файл с дополнительными атрибутами
    current_date = datetime.now().strftime('%d.%m.%Y')
    rating = {
        'отрицательно': 1,
        'нейтрально': 3,
        'положительно': 5
    }
    source = 'gold'  # Источник для отзывов через консоль
    author = review.get('author', 'Клиент банка')  # Гарантированно "Клиент банка", если не указан
    title = ' '.join(re.findall(r'\w+', text)[:5]) if text else 'Без заголовка'  # Первые 5 слов
    product_categories = classify_product_category(text, topics)  # Классификация категорий
    
    # Читаем существующий файл или создаем новый
    try:
        df = pd.read_csv('gazprombank_reviews_classified.csv', sep=';', encoding='utf-8-sig')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['text', 'topics', 'sentiments', 'date', 'rating', 'source', 'id', 'author', 'title', 'product_category'])
    except Exception as e:
        logging.error(f"Error reading CSV file: {str(e)}")
        return {'id': id, 'topics': topics, 'sentiments': sentiments, 'error': f"Ошибка при чтении файла: {str(e)}"}
    
    # Преобразуем topics, sentiments и product_categories в строки для CSV
    topics_str = ', '.join(topics)
    sentiments_str = ', '.join(sentiments)
    product_category_str = ', '.join(product_categories)
    
    # Определяем рейтинг на основе средней тональности
    avg_rating = sum(rating.get(s, 3) for s in sentiments) / len(sentiments) if sentiments else 3
    
    # Добавляем новую запись
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
    
    return {'id': id, 'topics': topics, 'sentiments': sentiments}

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({'error': 'No data provided'}), 400
        
        reviews = data['data']
        if not isinstance(reviews, list):
            return jsonify({'error': 'Data must be a list'}), 400
        
        predictions = []
        errors = []
        
        for review in reviews:
            result = process_review(review)
            if 'error' in result:
                errors.append({'id': result['id'], 'error': result['error']})
            else:
                predictions.append(result)
        
        response = {'predictions': predictions}
        if errors:
            response['errors'] = errors
        
        return app.response_class(
            response=json.dumps(response, ensure_ascii=False, indent=4),
            status=200 if not errors else 400,
            mimetype='application/json'
        )
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        return jsonify({'error': f'Серверная ошибка: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
