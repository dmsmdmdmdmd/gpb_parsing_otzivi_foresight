# gpb_parsing_otzivi_foresight
<h1>Сервис для отслеживания динамики клиентских настроений и проблем по конкретным банковским продуктам в режиме реального времени.</h1>

Как запустить? (На локальной машине)

1.В нужной директории (cd + путь до директории) в powershell пишем: py app.py <br>

2.В powershell (так же в нашей директории) вставляем следующую команду:

```
curl.exe -s -X POST -H "Content-Type: application/json" -d "@C:\...\test_250_reviews.json" http://localhost:5000/predict
```

Комментарий: вместо "@C:\...\test_250_reviews.json" используем свой путь до файла который вы используете в качестве теста, в этом проекте файл "test_250_reviews.json"<br>
<em>Вы можете использовать любой файл, желательно предварительно поместить его в нашу директорию.</em><br>

 3.У нас появляется файл "gazprombank_reviews_classified.csv"<br>
 4.Открываем и запускаем файл "api_reviews.py"<br>
 5.Открываем powershell и в нужной директории прописываем: streamlit run dash.py<br>
 
Открывается красивый и понятный дашборд с полным анализом. <br>

<h1>Запускаем удаленно</h1> 

**<h3>Тут все просто</h3>** <br>
<br>1.Переходим *[По ссылке](https://gpbparsingotziviforesight-wgf4rxgq65hm6pbuqb4cad.streamlit.app/)*. <br>
2.Загружаем файл формата .json с отзывами, <br>
3.Наслаждаемся <br>
<br>
<h1>dash.py</h1>
<br>
📊Аналитика отзывов о Газпромбанке

Веб-приложение для анализа клиентских отзывов о продуктах и услугах Газпромбанка.<br>
Разработано с использованием Streamlit, Pandas и Plotly.<br>

<h3>🚀 Возможности</h3>

Загрузка отзывов из JSON-файла формата:<br>

```{
  "data": [
    {"id": 1, "text": "Отличное мобильное приложение, но переводы иногда задерживаются", "author": "Иван"},
    {"id": 2, "text": "Очень доволен ипотекой, но приложение часто зависает", "author": "Анна"}
  ]
}
```
📂 Пример работы

После загрузки JSON в сайдбаре:
<ul>
<li>появится таблица с отзывами (id, текст, тема, тональность, рейтинг, дата),</li>

<li>визуализации по тональности и категориям, </li>

<li>возможность фильтровать по параметрам: </li>
<ul>
<li>дата (начальная и конечная указываются на странице с помощью календаря),</li>

<li>рейтинг (слайдер от 1 до 5),</li>

<li>категории и подкатегории (множественный выбор).</li>
</ul>
</ul>

📋 Интерфейс загрузки и фильтрации

Автоматическая обработка отзывов:
<ul>

<li>определение тематики (категории и подкатегории продукта),</li>

<li>анализ тональности (положительная, нейтральная, отрицательная),</li>

<li>расчет условного рейтинга (1–5).</li>

</ul>

Интерактивные фильтры:
<ul>
 
<li>по дате,</li>

<li>по рейтингу,</li>

<li>по категориям и подкатегориям.</li>

</ul>
Визуализации:

📈 Диаграмма распределения тональности отзывов,

📊 Распределение отзывов по категориям и подкатегориям,

📝 Таблица с детальными данными по отзывам.

🗂 Структура анализа

Категории и подкатегории продуктов

Словарь продуктов строго соответствует ТЗ и включает:
<ul>
 
<li>Повседневные финансы и платежи</li>

<li>Сбережения и накопления</li>

<li>Кредитование</li>

<li>Инвестиции</li>

<li>Страхование и защита</li>

<li>Премиальные услуги</li>

<li>Классификация отзывов</li>

<li>Разбивка текста на фрагменты (по союзам: «и», «но», «однако» и др.)</li>

<li>Определение темы по ключевым словам и фразам</li>

<li>Анализ тональности с использованием кастомного лексикона и обработки отрицаний </li>

<li>Подсчет итогового рейтинга: </li>
<ul>
<li>👍 Все положительные → рейтинг 5</li>

<li>😐 Все нейтральные → рейтинг 3</li>

<li>👎 Есть негатив → рейтинг 1</li>
</ul>
</ul>

Выводы

Если отзыв не относится к продуктам банка, он попадает в категорию *«Другое»*.

Для *«Другое»* тональность определяется по всему тексту.<br>

<h2>Пример работы</h2>

После загрузки JSON в сайдбаре:

появится таблица с отзывами (id, текст, тема, тональность, рейтинг, дата),

визуализации по тональности и категориям,

возможность фильтровать по параметрам.

📋 Интерфейс загрузки и фильтрации

📝 Таблица с отзывами

😊 Диаграмма тональности

📊 Распределение по категориям

🛠 Используемые технологии

*Streamlit*
 — интерфейс и интерактивные фильтры

*Pandas*
 — обработка данных

*Plotly*
 — визуализация

*re*
 — обработка текста

*datetime*
 — работа с датами

<h1>in English</h1>
<h1>A service for tracking the dynamics of customer sentiment and problems related to specific banking products in real time.</h1>

How do I launch it? (On the local machine)

1.In the desired directory (cd + directory path) in powershell, write: py app.py <br>

2.In powershell (also in our directory), insert the following command:

```
curl.exe -s -X POST -H "Content-Type: application/json" -d "@C:\...\test_250_reviews.json" http://localhost:5000/predict
```

Comment: instead of "@C:\...\test_250_reviews.json" we use our path to the file that you are using as a test, in this project the file "test_250_reviews.json"<br>
<em>You can use any file, preferably put it in our directory first.</em><br>

 3.We have the file "gazprombank_reviews_classified.csv"<br>
 4.Open and run the file "api_reviews.py "<br>
 5.Open powershell and write in the required directory: streamlit run dash.py <br>
 
It opens a beautiful and clear dashboard with full analysis. <br>

<h1>Launching remotely</h1> 

**<h3>Everything is simple</h3>** <br>
<br> 1.Moving on *[By the link](https://gpbparsingotziviforesight-wgf4rxgq65hm6pbuqb4cad.streamlit.app/)*. <br>
2.Download the format file.json with reviews, <br>
3.Enjoy <br>
<br>

<h1>dash.py</h1>
<br>
📊 Gazprombank reviews analysis

A web application for analyzing customer reviews of Gazprombank's products and services.<br>
Developed using Streamlit, Pandas and Plotly.<br>

<h3>🚀 Features</h3>

Uploading reviews from a JSON file format:<br>

```{
  "data": [
{"id": 1, "text": "Excellent mobile app, but translations are sometimes delayed", "author": "Ivan"},
    {"id": 2, "text": "I am very happy with the mortgage, but the application often freezes", "author": "Anna"}
]
}
```
📂 Work example

After uploading the JSON in the sidebar:
<ul>
<li>a table with reviews will appear (id, text, subject, tone, rating, date),</li>

<li>visualizations by tonality and categories, </li>

<li>the ability to filter by parameters: </li>
<ul>
<li>date (start and end date are indicated on the page using the calendar),</li>

<li>rating (slider from 1 to 5),</li>

<li>categories and subcategories (multiple choice).</li>
</ul>
</ul>

📋 Loading and filtering interface

Automatic review processing:
<ul>

<li>defining the subject (product categories and subcategories),</li>

<li>tonality analysis (positive, neutral, negative),</li>

<li>calculation of conditional rating (1-5).</li>

</ul>

Interactive filters:
<ul>
 
<li>by date,</li>

<li>by rating,</li>

<li>by category and subcategory.</li>

</ul>
Visualizations:

📈 A diagram of the distribution of the tonality of reviews,

📊 Distribution of reviews by category and subcategory,

📝A table with detailed data on reviews.

🗂 The structure of the analysis

Product categories and subcategories

The product dictionary strictly complies with the TOR and includes:
<ul>
 
<li>Everyday finance and payments</li>

<li>Savings and savings</li>

<li>Lending</li>

<li>Investments</li>

<li>Insurance and protection</li>

<li>Premium services</li>

<li>Classification of reviews</li>

<li>Splitting the text into fragments (by conjunctions: "and", "but", "however", etc.)

<li>Defining a topic by keywords and phrases</li>

<li>Tonality analysis using custom vocabulary and negation processing </li>

<li>Calculation of the final rating: </li>
<ul>
<li>👍 All positive → rating 5</li>

<li>😐 All neutral → rating 3</li>

<li>👎 There is a negative → rating 1</li>
</ul>
</ul>

Conclusions

If the review does not relate to the bank's products, it falls into the *"Other"* category.

For *"Other"* Tonality is determined throughout the text.<br>

<h2>Example of operation</h2>

After uploading the JSON in the sidebar:

a table with reviews will appear (id, text, subject, tone, rating, date),

visualizations by tonality and category,

the ability to filter by parameters.

📋 Loading and filtering interface

📝 Table with reviews

😊 Tonality diagram

📊 Categorization

🛠 Technologies used

*Streamlit*
— interface and interactive filters

*Pandas*
 — data processing

*Plotly*
 — visualization

*re*
— text processing

*datetime*
 — working with dates
