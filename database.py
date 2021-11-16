from flask import Flask
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:070812akbota@localhost/python' # не забудь менять имя датабэйс и пароль
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Tablecoin(db.Model):
    __tablename__ = 'tablecoin'
    id = db.Column(db.Integer, primary_key=True)
    name_of_coin = db.Column( db.String(255))
    news = db.Column( db.String(1000))


    def __init__(self,id,name_of_coin, news):
        self.id = id
        self.name_of_coin = name_of_coin
        self.news = news