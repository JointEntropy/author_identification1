###############################  MODELS.py
# http://flask-sqlalchemy.pocoo.org/2.3/quickstart/
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from gvars import app, db

from sqlalchemy.orm import load_only
import pickle as pkl
import numpy as np


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Composition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    text = db.Column(db.Text, nullable=False)
    features = db.Column(db.PickleType)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    # pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author = db.relationship('Author', backref=db.backref('compositions', lazy=True))

    def __repr__(self):
        return '<Composition %r>' % self.title


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    img_url = db.Column(db.String(1000), nullable=True)
    # class_label = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Author %r>' % self.name
##################################


class MBackEnd:
    def __init__(self, model, db, decoder, generate_features=False):
        self.predict_model = model
        self.db = db
        self.decoder = decoder
        self.class_labels_mapping = None

        self.first_call = True
        if generate_features:
            pass
            # пробегаем по всем записям и генерим для них фичи
            # этот блок под вопросом, ибо в любом случае пока непонятно когда иницилизируется сессия для бд.
            # self.predict_model.prepare_features(...)

    def fit_predict_model(self):
        tuples = self.db.session.query(Composition).options(load_only('features', 'author_id')).all()
        features, targets = [item.features for item in tuples], [item.author_id for item in tuples]

        features = [np.random.random(size=(5,5)).ravel() for f in features]

        # собираем уникальные id'шники с авторов и готовим отображения из предсказанного класса в id автора из базы.
        unique_author_ids = self.db.session.query(Author.id).all()
        self.class_labels_mapping = dict((class_[0], idx) for idx, class_ in enumerate(unique_author_ids))

        # конвертим метки в произвеениях в целевые классы.
        targets = [ self.class_labels_mapping[target] for target in targets]

        # обучаем knn на прризнаках текстов и id'шниках произведений.
        self.predict_model.fit(features, targets)

    def predict(self, text):
        """
        Получаем сырой текст запроса. Декодирует его и предсказывает топ 5 бомжей.

        :param X: сырой текст запроса.
        :return: упорядоченный по убываний список author_id и prob.
        """
        if self.first_call:
            compositions_raw = Composition.query.options(load_only('text','features')).all()
            texts = [c.text for c in compositions_raw]
            self.predict_model.fit_extractor(texts)
            texts_features = self.predict_model.prepare_features(texts)
            for c, f in zip(compositions_raw, texts_features):
                c.features = f.todense()
            self.db.session.commit()
            self.fit_predict_model()
            self.first_call = False

        # декодируем
        text = self.decoder.process(text),
        # предсказываем фичи
        features = self.predict_model.predict_features(text)
        # предсказываем метки классов
        predictions = self.predict_model.predict(features)

        inverse_mapping = dict((val, key) for key, val in self.class_labels_mapping.items())
        predictions = [(inverse_mapping[label], prob) for label, prob in predictions]
        predictions.sort(key=lambda x: x[1], reverse=True)
        predictions = [{'id': idx, 'prob': prob} for idx, prob in predictions[:5]]
        return predictions

    def update_model(self):
        texts = self.db['texts']
        text_features = texts['features']
        authors_ids = texts['authors']
        self.predict_model.fit(text_features, authors_ids)

    def add_author(self, author_data,):
        # добавляем автора в базу если его там нет.
        # переобучаем knn классификатор под новый класс.
        author = Author(**author_data)
        self.db.session.add(author)
        self.db.session.commit()
        self.db.session.close()

    def del_author(self, id):
        Author.query.filter_by(id=id).delete()
        self.db.session.commit()

    def del_comp(self, id):
        Composition.query.filter_by(id=id).delete()
        self.db.session.commit()

    def get_authors(self):
        # запрос к ДБ на получение списка имён всех авторов
        return self.db.session.query(Author.name).all()  # оверкилл

    def get_compositions(self, author_id, page_idx):
        # запрос к ДБ на получения списка всех  известных произведений.
        a = Author.query.get(author_id)
        comps = a.compositions
        comps = [{'id': c.id, 'title': c.title} for c in comps]
        return comps

    def get_composition(self, id):
        c = Composition.query.get(id)
        if c is not None:
            response = {
                'id': id,
                'title': c.title,
                'author_name': c.author.name,
                'author': c.author.id,
                'text': c.text,
            }
            return response

    def add_composition(self, composition_data):
        title = composition_data['title']
        text = self.decoder.process(composition_data['text'])
        author_name = composition_data['author_name']
        features = self.predict_model.predict_features(text)

        author_exists = self.db.session.query(Author.id).filter_by(name=author_name).scalar()
        if author_exists is not None:
            author_id = author_exists
        else:
            self.add_author({'name': author_name})
            author_id = self.db.session.query(Author.id).filter_by(name=author_name).scalar()
        c = Composition(title=title, text=text, author_id=author_id, features=pkl.dumps(features))


        ### TODO здесь косяк с тем. что db импортирована криво и возникает несколько сессий.\
        ### Так что при попытке добавления он пытается их пихнуть во все и вылазиет ошибка.
        ### https: // stackoverflow.com / questions / 24291933 / sqlalchemy - object - already - attached - to - session
        self.db.session.add(c)
        self.db.session.commit()
        self.db.session.close()

        # обучаем knn на новый класс и новый сэмпл
        self.fit_predict_model()

    def get_author_info(self, id):
        a = Author.query.get(id)
        if a is not None:
            response = {
                'id': id,
                'name': a.name,
                'bio': a.bio,
                'img_url': a.img_url
            }
            return response




