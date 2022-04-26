# Flask-SQLAlchemy - установка, создание таблиц, добавление записей
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

# https://flask-sqlalchemy-russian.readthedocs.io/ru/latest/index.html
# после создания экземпляра приложения app создадим конфигурацию
# SQLALCHEMY_DATABASE_URI - константа определяет вид использования систем управления БД и местоположения БД
# в данном случае это корневой каталог программы, имя константы связывает управление с той или иной БД
# в будущем если понадобится другая СУБД, можем переопределить константу
# - postgresql://user:password@localhost/mydatabase
# - mysql://user:password@localhost/mydatabase
# - oracle://user:password@127.0.0.1:1521/mydatabase
# К программе будет подключено указанное СУБД, с котрым будет работать наше приложение
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
# errors при создании БД - FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS, пропишем в конфигурации и ошибки не будет
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# создадим экземпляр класса SQLAlchemy через который и осуществляется работа с БД
# экземпляру-db db передается ссылка на текущее приложение app - теперь мы подключили SQLAlchemy к нашему приложению
# далее определяем набор таблиц с которыми мы будем работать
# Например: будем использовать регистрацию пользователей и сохранять информацию о них в двух таблицах users и profiles
#           определим структуры-поля этих таблиц
# Концепция: SQLAlchemy заключается в отображении таблиц с помощью Python класса, т.е. нам достаточно прописать
#           два класса Users и Profiles, которые будут расширять базовый класс .Model и описывать соответствующие таблицы
db = SQLAlchemy(app)

# опишем класс Users(), который наследуется от класса Model, который превращает класс Users в модель таблицы для SQLAlchemy
# поля таблицы описываются как обычные переменные: id этот Class воспринимает SQLAlchemy как поле таблицы,
# поле таблицы будет иметь тип Integer и быть главным ключом primary_key
# поле id будет главным ключом и будет уникальным для каждой записи
# email - строковое поле и максимум содержит 50 символов, unique=True - параметр указывает, что поле уникально в рамках данной таблицы
# psw - максимум содержит 500 символов, параметр nullable=False означает, что это поле не должно быть пустым
# data - поле будет хранить текущую дату DateTime, когда пользователь зарегистрировался, если явно не передаем значения, то берется текущее время
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # при выборе записи из таблицы pr будет содержать все записи из таблицы Profiles
    pr = db.relationship('Profiles', backref='users', uselist=False)

    # вспомогательный метод __repr__(), который будет определять отображение классов в консоли
    # с его помощью класс выводится в формате users.{текущий идентификатор пользователя}
    # данный метод записан для удобства и к функционалу таблиц отношения не имеет
    def __repr__(self):
        return f"<users {self.id}>"


# опишем класс Profiles(), который расширяет класс Model, и задаем поля id, name, old, city
# наиболее распространенными типами данными в SQLAlchemy, являются следующие:
# Integer – целочисленный;
# String(size) – строка максимальной длиной size;
# Text – текст (в формате Unicode);
# DateTime – дата и время представленные в формате объекта datetime;
# Float – число с плавающей точкой (вещественное);
# Boolean – логическое значение;
# LargeBinary – для больших произвольных бинарных данных (например, изображений)

# user_id - будет являться внешним ключом определять связь записи таблицы profiles  с записями таблицы Users
# через внешний ключ user_id устанавливается соответствия между таблицами users и записями из таблицы profiles
# далее создадим поля в БД - переходим в Python Console или в файл create_db
class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    old = db.Column(db.Integer)
    city = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"<profiles {self.id}>"


# добавим функцию представления index()
@app.route("/")
def index():
    # механизмом (связи между двумя таблицами) через переменную pr
    # info = [] - будем содержать имя пользователей
    # Users.query.all() - мы выбираем всех пользователей из таблицы Users()
    # дальше мы передаем этот список index.html - переходим в index.html и добавляем список
    # list=info
    info = []
    try:
        info = Users.query.all()
    except:
        print("Ошибка чтения из БД")

    return render_template("index.html", title="Главная", list=info)


# создадим первую функцию представления для регистрации пользователей, где мы могли бы добавлять новые записи в эти таблицы
# вначале пропишем обработчик
# по адресу /register будем получать данные по методу POST GET запросу и отображать шаблон register.html
# запишем добавление данных в БД - первое - проверим, что данные пришли по POST запросу
# если-if данные пришли по POST запросу
# по итогам выполнения этап-1 и этап-2 добавится в таблицы users и profile добавится по одной записи для нового зарегистрированного пользователя
# причем внешний ключ user_id будет ссылаться на id запись из таблицы users. По внешнему ключу записи можно объединять между собой
@app.route("/register", methods=("POST", "GET"))
def register():
    if request.method == "POST":
    # здесь должна быть проверка корректности введенных данных
        # пропишем добавление записей в БД с помощью оператора try, если будут ошибки их можно отлавливать
        # возьмем пароль из формы, которую заполнил пользователь при регистрации и построить его hash
        # импортируем функцию generate_password_hash() из пакета werkzeug.security
        # далее создаем экземпляр класса Users и через именованные параметры email, psw передаем данные кземпляру класса
        # причем именованные параметры должны совпадать с этими параметрами, которые мы здесь указали при объявлении класса Users()
        # чтоб добавить именованные записи таблицы происходит обращение к специальному объекту session сеессии БД и
        # вызывается метод add() которому передается ссылка на созданный экземпляр-u класса Users(), но
        # но выполняя этото метод память все еще храниться в сессии памяти устройства, фактически в таблицу она еще не занесена
        # flush() - метод, который из сессии перемещает запись уже в таблицу, но пока все изменения происходят в памяти устройства и фактически файл из БД остается прежним
        # если ошибки возникнут, мы выполним специальный метод rollback() и откатим состояние БД к исходному положению
        try:
            hash = generate_password_hash(request.form['psw'])
            # этап-1
            u = Users(email=request.form['email'], psw=hash)
            db.session.add(u)
            db.session.flush()

            # этап-2 добавление записи в таблицу profiles
            # создаем экземпляр-p класса Profiles(), который ссылается на создаваемые записи name, old, city, user_id - они же именованные параметры которым передаем значения
            # поле user_id, которое является внешним ключом мы передаем id записи, которая была сформирована на этапе-1
            # user_id=u.id - атрибут id экземпляра класса u будет принимать значение id добавочной записи
            # помещаем сформированные записи в таблицу profiles - db.session.add(p)
            # вызываем метод commit(), который физически меняет файлы БД и сохраняет изменения в таблица
            p = Profiles(name=request.form['name'], old=request.form['old'],city=request.form['city'], user_id=u.id)
            db.session.add(p)
            db.session.commit()

            # если при добавлении в БД произошли ошибки, то мы откатываем ее состояние rollback(), делаем так, как будто туда ничего не добавлялось
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

    return render_template("register.html", title="Регистрация")


# Так настраивается конфигурация для SQLAlchemy
# webserver start
if __name__ == "__main__":
    app.run(debug=True)