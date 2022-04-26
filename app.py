# Flask #5:  Flask-SQLAlchemy - установка, создание таблиц, добавление записей

import sqlite3
import os
from flask import Flask, render_template, request, flash, redirect, url_for, abort, g, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin
#                       переменная

# Flask позволяет разделять большой, сложный проект на набор независимых модулей: авторизация, админ-панель, счетчик
# каждый модуль может содержать свои шаблоны, свои стили оформления, наборы изображений, и все это может находиться в отдельном подкаталоге
# при необходимости этот подкаталог можно скопировать в другой проект и подключить к другому сайту
# Blueprint (эскиз) чертеж
# Например создадим админ-панель с Blueprint с реализацией в отдельном подкаталоге admin
# admin.py - реализация админ панели с помощью Blueprint
# django - подход в уаждом модуле помещается такой же шаблон с именем что и основной подкаталог admin
#          при компиляции проекта все шаблоны собираются в одну кучу и может возникнуть конфликт имен, когда в разных модулях будут одинаковые файлы с именами шаблонов
#          в момент выполнения шаблоны будут отделяться подкаталогами



DATABASE = '/tmp/flsite.db'


DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
MAX_CONTENT_LENGTH = 1024 * 1024


app = Flask(__name__)
app.config.from_object(__name__)

#app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
# heroku - deploy
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'postgres://blkoxyculkooop:f4e64f7893687fc1b766bcb547b8ec89a8da26f35199763c0f1cdb16bde62a67@ec2-52-203-118-49.compute-1.amazonaws.com:5432/ddcj014p2o12hs')))

# через переменную app выполняем регистрацию blueprint
# admin - первый параметр говорит, что регистрируем Blueprint с названием admin
# /admin - все наши url внутри blueprint будут иметь вид домен/<url_prefix>/<URL-blueprint>
# главная страница админ панели будет находиться по адресу  http://127.0.0.1:5000/admin
# admin – ссылка на созданный Blueprint
# url_prefix – префикс для всех URL модуля admin
# далее добавим обработчик страницы в blueprint - admin.py
app.register_blueprint(admin, url_prefix='/admin')





# создадим экземпляр класса LoginManager() и связываем его с нашим приложением app
# и далее будем работать с переменной login_manager и управлять его авторизацией
login_manager = LoginManager(app)

# перенаправление на страницу авторизации вместо Unauthorized The server could not verify...
# свойству login_view присвоим функцию обработчик, которая будет вызываться если пользователь посещает закрытую страницу
# и в случае ели он не авторизован то перенаправлен будет по адресу login, т.е. на страницу авторизации
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

# декоратор, который будет загружать, формировать экземпляр класса UserLogin() при каждом запросе от сайта
@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

# декоратор перехвата запросов
# before_request() - функция работает перед выполнением запроса
# FDataBase() - создание экземпляра класса
# чтоб переменная dbase была доступна во всех запросах мы сделали ее глобальной
# global dbase - говорит, что внутри функции будем обращаться к переменной dbase, так мы вынесли за скобку общий код
# теперь можно в функциях представления использовать переменную dbase вместо строк
dbase = None
@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено"""
    if hasattr(g, 'link_db'):
        g.link_db.close()



@app.route("/")
def index():
    # db = get_db()              - теперь используем глобальную переменную dbase
    # dbase = FDataBase(db)
    return render_template('index.html', menu = dbase.getMenu(), posts=dbase.getPostsAnonce())



@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    # db = get_db()
    # dbase = FDataBase(db)
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('ERROR  of add post', category='error')
            else:
                flash('Post added successfully', category='success')
        else:
            flash('ERROR  of add post', category='error')

    return render_template('addpost.html', menu=dbase.getMenu(), title="Add post")

# @login_required - ограничим доступ к нашим статьям только для авторизованных пользователей
@app.route("/post/<alias>")
@login_required
def showPost(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)

# пропишем обработчик для авторизации пользователя по адрессу представления функции login()
# данный метод можем проверять по POST и GET запросам
# ели пришел POST запрос, то соответственно обращаемся к БД dbase. берем информацию по пользователю getUserByEmail
# мы идентифицируем пользователя по email. По email - получаем данные о пользователе и делаем проверку
# if user - если данные были получены и пароль был введен вверно, то мы создаем экземпляр класса UserLogin()
# create(user) - передаем ему всю информацию которую прочитали из БД
# login_user - авторизуем пользователя с помощью метода login_user(userlogin)
# return redirect(url_for('index')) - делаем перенаправление на главную страницу сайта
# flash() - если пошло что-то не так, немедленно формируем мгновенное сообщение и отображаем снова страницу авторизации return render_template()

# next=%2Fpost%2Fframework-flask-intro3 next - хранит адрес путь запроса с которого мы перешли
# мы можем воспользоваться этим параметром, чтоб после авторизации пользователя перенаправить на страницу которую он хотел посмотреть
# преобразуем redirect, если параметр next в нашем запросе существует, то переходим к url, который там указан, или иначе переходим в profile
@app.route("/login", methods=["POST", "GET"])
def login():
    # проверка, чтоб авторизованные пользователи не попадали на страницу авторизауции
    # current_user - через эту переменную мы можем проверить авторизован пользователь или нет
    # если авторизован, то перенаправим на страницу profile
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    # создаем экземпляр класса LoginForm(), в шаблон login.html передаем ссылку на этот экземпляр класса form=form
    # через именованный параметр form мы сможем в шаблоне login.html обратиться к нашему классу и выполнить определенные действия
    # validate_on_submit() - метод проверяет были ли отправлены данные POST запросом, эквивалентная строка - if request.method == "POST":
    # form.email - доступ к переменным мы можем делать через форму
    # data - свойство к которому обращаемся чтоб получить данные из этого поля
    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
    #       return redirect(url_for('profile'))                             # страница для перехода после авторизации
            return redirect(request.args.get("next") or url_for("profile"))  # преобразованный redirect

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация", form=form)

#     if request.method == "POST":
#         user = dbase.getUserByEmail(request.form['email'])
#         if user and check_password_hash(user['psw'], request.form['psw']):
#             userlogin = UserLogin().create(user)
#             # функционал кнопки checkbox запомнить меня True или False c именем авторизации remainme
#             rm = True if request.form.get('remainme') else False
#             login_user(userlogin, remember=rm)
# #            return redirect(url_for('profile'))                             # страница для перехода после авторизации
#             return redirect(request.args.get("next") or url_for("profile"))  # преобразованный redirect
#
#         flash("Неверная пара логин/пароль", "error")
#
#     return render_template('login.html', menu=dbase.getMenu(), title="Авторизация")


# обработчик для формы регистрации c шифрованием паролей в БД
# когда регистрируется новый пользователь должна создаваться аватарка по умолчанию, для этого изменим addUser() в FDataBase()
# в RegisterForm() проверяем, что данные были отправлены по POST запросу и они корректно введены
# если-if данные корректно введены то выполняется True
# generate_password_hash - генерируем hash пароли
# addUser() - добавляем пользователя
# form=form - параметр form - для указания ссылки на созданный класс RegisterForm()
@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
            hash = generate_password_hash(form.psw.data)
            res = dbase.addUser(form.name.data, form.email.data, hash)

# Проверки валидатора можно убрать, т.к. все проверки будут проходить через валидатор validate_on_submit()
#    if request.method == "POST":
#        session.pop('_flashes', None)
#        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
#            and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
#            hash = generate_password_hash(request.form['psw'])
#            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
#        else:
#            flash("Неверно заполнены поля", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация", form=form)


# Функция представления logout() вызывает функцию logout_user()
# если функция logout_user() срабатывает, то вся сессионная информация очищается и пользователь будет не авторизован
# после выхода из профиля мы переходим на страницу авторизации страницы login
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


# добавим страницу про файл пользователя c функцией обаботчиком profile() - эта страница будет доступна только для авторизованных пользователей
# user info: отображаем информацию о пользователе, будем отображать ID текущего пользователя
# c помощью глобальной переменной current_user через которую можно обращаться к методам класса UserLogin()
# мы обращаемся к методу get_id, чтоб получить уникальный идентификатор текущего пользователя
# logout - это функционал, чтоб выйти из профиля
@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Account")
        # f"""<p><a href="{url_for('logout')}">Выйти из профиля</a>
        #         <p>user info: {current_user.get_id()}"""
              # <p>user info: """
              # Сделаем нормальную форму profile() - для html

# обработчик userava()
# getAvatar(app) - берем загружаем аватарку нашего текущего пользователя
# if - если при получении аватарка не была загружена, то обработчик возвращает пустую строку
# иначе make_responce() создается объект запроса и Content-Type устанавливается в значение image/png
# return h - возвращаем ответ сервера браузеру
# /userava - по этому адресу будет возвращаться изображение в формате png
# чтоб обработчик userava() работал нужно прописать метод getAvatar() в классе UserLogin
@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


# обработчик upload() - доступный только для зарегистрированных пользователей @login_required
# if - проверка, что пришли данные по методу POST, если это так то
# берем поле файл из объекта request current_user, который ассоциирован с загруженным на сервер файлом, т.е. тем файлом
# который был выбран в профайле пользователя
# далее проверка, что файл current_user был успешно загружен, и что его расширение метод verifyExt() соответствет png
# если файл нормально прочитан метод updateUserAvatar(), где происходит изменение аватара пользователя в БД
# проверки if not res: прошли успешно и возвращаем return redirect(url_for('profile'))
@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))


# webserver start
if __name__ == "__main__":
    app.run(debug=True)




# Test
# http://127.0.0.1:5000/admin/
# # http://127.0.0.1:5000/admin/login