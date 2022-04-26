from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# pip install email_validator
# В классе LoginForm() пропишем переменные которые будут представлять поля  email, password, checkbox, submit, ...
# -- переменная email ссылается на экземпляр класса StringField() - т.е. поле ввода обычное, с названием поля "Email" и параметром validators, который ссылается на список валидаторов для проверки корректности введенных данных
# чтоб мы могли использовать класс StringField() и валидатор Email мы должны их импортировать
# Базовый класс FlaskForm будем расширять с помощью дочернего класса LoginForm()
# Импортируем классы StringField, ... из модуля wtforms
# Импортируем валидаторы Email, ... из модуля wtforms.validators
# -- переменная psw ссылается на экземпляр класса PasswordField() - т.е. поле ввода обычное, с названием поля "Password" и параметром validators, DataRequired() - требует чтоб в поле был хотя бы 1 символ
class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Incorrect email")])
    psw = PasswordField("Password: ", validators=[DataRequired(), Length(min=4, max=100, message="password must be between 4 and 100 characters long")])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Login")

# Заменим еще одну форму для описания регистрации пользователей, будем расширять базовый класс FlaskForm
# Валидатор EqualTo - проверяет, соответствует ли содержимое поля psw2 полю psw
# если содержимое совпадает поля Пароль: с полем Повтор пароля: то значит валидатор проходит и возвращает True
# далее шаблон register.html запишем в виде
class RegisterForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100,
                                                       message="Пароль должен быть от 4 до 100 символов")])

    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")