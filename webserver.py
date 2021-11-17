from datetime import datetime, timedelta
from flask import Flask, render_template, redirect
from flask.helpers import make_response
from flask import request
from flask.json import jsonify
from database import Tablecoin, db,app, UserTable
from selenium import webdriver
from bs4 import BeautifulSoup
from transformers import pipeline
summarizer = pipeline("summarization")

#Удаляем таблицу, если существует
db.engine.execute('drop table IF EXISTS tablecoin')
#Создаем таблицу заново, без уникального ключа в айди
db.engine.execute('CREATE TABLE tablecoin (ID int, name_of_coin VARCHAR (255), news VARCHAR)')

db.session.commit()

app.config['SECRET_KEY'] = 'thisismyflasksecretkey'

@app.route('/signup')
def signup():
    return render_template('login.html')

@app.route('/auth', methods = ['POST', 'GET'])
def auth():
    if request.method == 'GET':
        return "GETTING DATA"
    if request.method == 'POST':
        login1 = request.form['login']
        password2 = request.form['password']
        auth = request.authorization
        user = UserTable.query.filter_by(login=login1, password=password2).first_or_404(description='Could not found a user with login and password:  {}'.format(login1))
        return redirect('/webpage')
    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login required'})

@app.route('/webpage')
def webpage():
    return render_template('form.html')


@app.route('/coin',  methods = ['POST', 'GET'])
def coin():
    if request.method == 'GET':
        return "GETTING DATA"

    if request.method == 'POST':
        names = request.form['name']
        url = 'https://coinmarketcap.com/currencies/'+ str(names) + "/news/"

        driver = webdriver.Firefox(executable_path=r'C:\Users\abazy\Downloads\geckodriver.exe')
        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page,'html.parser')

        filteredNews = []
        allNews = []
        allNews = soup.findAll('div', class_='sc-16r8icm-0 jKrmxw container')



        for i in range(len(allNews)):
            if allNews[i].find('p', class_='sc-1eb5slv-0 svowul-3 ddtKCV') is not None:
                filteredNews.append(allNews[i].text)

        for i, news_item in enumerate(filteredNews):
            print(i, f"{news_item}\n")
        

        for filteredParagraphs in filteredNews:
            max_chunk = 15
            filteredParagraphs = filteredParagraphs.replace('...', ' ')
            filteredParagraphs = filteredParagraphs.replace('.', '.<eos>')
            filteredParagraphs = filteredParagraphs.replace('?', '?<eos>')
            filteredParagraphs = filteredParagraphs.replace('!', '!<eos>')
            sentences = filteredParagraphs.split('<eos>')
            current_chunk = 0 
            chunks = []
            for sentence in sentences:
                if len(chunks) == current_chunk + 1: 
                    if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                        chunks[current_chunk].extend(sentence.split(' '))
                    else:
                        current_chunk += 1
                        chunks.append(sentence.split(' '))
                else:
                    print(current_chunk)
                    chunks.append(sentence.split(' '))

            for chunk_id in range(len(chunks)):
                chunks[chunk_id] = ' '.join(chunks[chunk_id])
            res = summarizer(chunks, max_length=15, min_length=5, do_sample=False)
            text = ' '.join([summ['summary_text'] for summ in res])
            new_ex = Tablecoin(1, names, str(text))
            db.session.add(new_ex)
            db.session.commit()

#Тут выводим все записи в таблице и фильтруем по имени монеты
           
            coins = db.engine.execute("select * from tablecoin where name_of_coin = '"+names+"'")
            return render_template("news.html", coins=coins)





if __name__ == '__main__':
    app.run(debug=True)
