# create DB
# метод создает и БД и таблицы
from app import db
db.create_all()

# errors при создании БД - FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS
# пропишем в конфигурации файла app.py и ошибки не будет


