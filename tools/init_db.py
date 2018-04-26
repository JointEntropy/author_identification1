# http://flask-sqlalchemy.pocoo.org/2.3/quickstart/
from models import db, User, Composition, Author
import pickle as pkl
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import sqlalchemy as sa
from flask import Flask
import pandas as pd


def restore_after_flush():
    try:
        db.session.commit()
    except SQLAlchemy.exc as e:
        db.session.rollback()


def db_create():
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    # # Дропает все таблицы и данные.
    # db.reflect()
    # db.drop_all()

    # Инициализация таблиц на основе полей моделей
    db.create_all()

    # Добавления к юзверам.
    # admin = User(username='admin', email='admin@example.com')
    # guest = User(username='guest', email='guest@example.com')
    # db.session.add(admin)
    # db.session.add(guest)

    # Пример добавления экземпляров.
    # a = Author(name='Айзек Азимоввв', img_url="https://data.fantlab.ru/images/autors/6",            bio='Я РОБОТ!!')
    # c = Composition(title='Сумма технологий', text='  1. Нам предстоит разговор о будущем.', features=pkl.dumps([1,2,3]))
    # a.compositions.append(c)
    # db.session.add(a)
    # a =  Author.query.get(1)
    # print(a.compositions)
    # c = Composition.query.get(1)
    # # коммитимся иначе все изменения будут потеряны

    # res = db.session.query(Author.id).filter_by(name='Лев Никлаевич Толстой').all()
    db.session.commit()
    #
    # # получение всех записей.
    # print(Composition.query.all())
    # # print(Author.query.all())
