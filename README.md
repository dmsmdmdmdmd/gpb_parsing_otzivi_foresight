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
<br>1.Moving on *[By the link](https://gpbparsingotziviforesight-wgf4rxgq65hm6pbuqb4cad.streamlit.app /)*. <br>
2.Download the format file.json with reviews, <br>
3.Enjoy <br>
<br>
