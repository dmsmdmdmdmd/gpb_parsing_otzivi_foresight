# gpb_parsing_otzivi_foresight
</h1>Сервис для отслеживания динамики клиентских настроений и проблем по конкретным банковским продуктам в режиме реального времени.</h1>

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
 
</h3>Открывается красивый и понятный дашборд с полным анализом.</h3>

</h1>Как запустить? [По ссылке](https://gpbparsingotziviforesight-wgf4rxgq65hm6pbuqb4cad.streamlit.app/) </h1>
