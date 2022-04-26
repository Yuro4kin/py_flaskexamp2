import sqlite3
from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g

# https://flask.palletsprojects.com/en/1.1.x/blueprints/ - документация
# Например в качестве примера сделаем вывод списка статей и пользователей зарегистрированных на сайте из БД.
# Обычно, админ-панель использует БД приложения и выполняет определенные действия
# Но для начала нам нужно в Blueprint выполнить соединение с БД. Как это сделать, чтобы максимально сохранить модульность приложения?
# Хорошей практикой является использование декораторов:
# - before_request – перед выполнением запроса, для установления связи с БД
# - teardown_request – после выполнения запроса, для закрытия соединения с БД



# создадим admin-экземпляр класса-Blueprint <class 'flask.blueprints.Blueprint'>
# Параметры Blueprint()
# 'admin' – имя Blueprint, которое будет суффиксом ко всем именам методов, данного модуля;
# __name__ – имя исполняемого модуля, относительно которого будет искаться папка admin и соответствующие подкаталоги;
# template_folder – подкаталог для шаблонов данного Blueprint (необязательный параметр, при его отсутствии берется подкаталог шаблонов приложения);
# static_folder – подкаталог для статических файлов (необязательный параметр, при его отсутствии берется подкаталог static приложения).
# далее регистрируем Blueprint() в основном приложении файле flsite.py
admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')
#                  bp


# пропишем функцию из обработчика login
# session - в сессии создаем и сохраняем следующую запись со значением 1, если эта запись существует, то пользователь зашел в admin панель
def login_admin():
    session['admin_logged'] = 1

# isLogged() - функция проверяет, зашел администратор в admin панель, True - возвращает, если запись admin_logged существует
# False - если запись не существует
def isLogged():
    return True if session.get('admin_logged') else False

# logout_admin() - функция, которая будет удалять из сессии запись admin_logged, с помощью данной ф-ции будем выходить из admin панели
def logout_admin():
    session.pop('admin_logged', None)

# .listpubs - добавим пункт menu по которому сможем видеть список статей
# .listusers - добавим в список menu список пользователей, url формируется по функции представления .listusers
menu = [{'url': '.index', 'title': 'Панель'},
        {'url': '.listusers', 'title': 'Список пользователей'},
        {'url': '.listpubs', 'title': 'Список статей'},
        {'url': '.logout', 'title': 'Выйти'}]

# декораторы before_request и teardown_request
# db - глобальная переменная, которая будет ссылаться на БД, соединение с БД
db = None

# из глобальной переменной g-контекста приложения мы обращаемся к свойству link_db, в этом свойстве link_db храним соединение с БД
# Причем, декораторы уровня приложения как бы «обертывают» выполнение декораторов в Blueprint.
# То есть, их последовательность вызовов будет такой:
# @app.before_request   - вызывается на уровне приложения
# @admin.before_request - вызывается на уровне Blueprint, обращаемся к глобальной переменной g, там уже храниться соединение с БД
# @admin.teardown_request
# @app.teardown_appcontext - разрыв соединения происходит в последнюю очередь
# g - глобальная переменная, которую нужно импортировать
@admin.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global db
    db = g.get('link_db')

@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request



# Перейдем в модуль admin.py и пропишем декоратор route:
# admin - переменная, ссылка на Blueprint() и зарегистрирована в нашем приложении
# route - создает функцию представления для обработки запроса, главная страница с учетом префикса будет соответствовать адресу
# http://127.0.0.1:5000/admin/
# улучшим обработчик index(), проверим if-если пользователь не залогинился, то мы не будем отображать admin панель, a
# будем перенаправлять пользователя на форму авторизации, далее отобразим панель с шаблоном index.html у шаблона будет отображаться menu b
@admin.route('/')
def index():
#    return "admin"
    if not isLogged():
        return redirect(url_for('.login'))

    return render_template('admin/index.html', menu=menu, title='Админ-панель')

# например добавим возможность авторизации в нашей тестовой панели администрации
# для этого пропишем функцию представления login для авторизации
# if - проверяем, что пришли данные по POST запросу, затем
# if - проверяем верность login-admin и пароля-12345, где при истинности
# будем выполнять авторизацию с помощью функции login_admin() которую проишем позже, далее
# делаем перенаправление на страницу admin панели
# flash - если были какие-то ошибки
# если шаблон не сработает сработает форма авторизации админ панели admin/login.html
# .index - точка означает, что функцию представления index следует брать из текущего Blueprint, а не глобальную из основного WSGI приложения программы
# admin.index эквивалентно записи .index, admin - это имя Blueprint

# сделаем проверку, если-if зарегистрирован, залогинился, то мы перенаправим нашего пользователя на главную страницу .index
# .index - точки означает, что берем ф-цию index из Blueprint и к url будет добавлен префикс /admin - главня страница нашей admin панели
@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))
#                                 index - без точки переход на главную страницу
    if request.method == "POST":
        if request.form['user'] == "admin" and request.form['psw'] == "12345":
            login_admin()
            return redirect(url_for('.index'))
#                               admin.index - эквивалентная запись
#                                  bp.index - эквивалентная запись
        else:
            flash("Неверная пара логин/пароль", "error")

    return render_template('admin/login.html', title='Админ-панель')

# пропишем выход администратора из админ панели
# обработчик - /logout
# logout() - функция представления
# if - проверяем если администратор не вошел в админ панель, то переводим его на страницу login
# иначе, если он авторизован, выполняем удаление из сессии, т.е. выходим из админ-панели logout_admin() и
# перенаправляем-redirect его на страницу авторизации login
# далее создадим шаблон login.html для авторизации
@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()

    return redirect(url_for('.login'))

# в панели администратора вывести список статей - создадим функцию представление listpubs() со следующим содержимым
# /list-pubs - список статей
# if-если администратор не залогинился, то мы его перенаправляем на страницу авторизации
# list = [] из БД читаем список статей и сохраняем в переменной list
# if-если соединение с БД-db произошло успешно, то пытаемся прочитать из таблицы posts все статьи, учитывая поля title, text, url
# в нашем списке-list будут списки словарей, содержащие записи title, text, url, когда
# fatchall() вызываем, то получаем список словарей
# except - иначе если возникли ошибки то в консоль сообщение об ошибке
# render_template() - отображаем шаблон listpubs.html c title, menu, list
# пропишем шаблон listpubs.html
@admin.route('/list-pubs')
def listpubs():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT title, text, url FROM posts")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД " + str(e))

    return render_template('admin/listpubs.html', title='Список статей', menu=menu, list=list)

# добавим обработчик listusers() - отображение списка пользователей
# проверяем если-id администратор не авторизовался, то перенаправляем его на страницу авторизации .login
# по умолчанию список-list пользователей пустой-[] и мы пытаемся прочитать его с БД-db
# выполняем запрос SELECT - берем из таблицы users поля name, email
# с помощью функции fetchall() пытаемся все это прочитать
# при отображении шаблона render_template параметру list передадим то, что прочитали из БД
# пропишем шаблон listusers.html
@admin.route('/list-users')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT name, email FROM users ORDER BY time DESC")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД " + str(e))

    return render_template('admin/listusers.html', title='Список пользователей', menu=menu, list=list)

# добавим на главную страницу сайта ссылку для перехода в admin панель перейдем в index.html
# <p><a href="{{ url_for('admin.index')}}">Админ-панель</a></p>
#                         admin.      - из внешнего модуля обращаемся к функции представления
#                              .index - из текущего модуля