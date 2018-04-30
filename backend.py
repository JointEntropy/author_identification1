from sqlalchemy.orm import load_only
import pickle as pkl
import numpy as np
from models import Author, Composition, db


class MBackEnd:
    def __init__(self, model,  decoder):
        self.predict_model = model
        self.decoder = decoder
        self.class_labels_mapping = None

    def on_start(self,
                 generate_features=False,
                 fit_extractor=False,
                 fit_predict_model=True):

        # генерим фичи
        compositions_raw = Composition.query.options(load_only('text','features')).all()
        texts = [c.text for c in compositions_raw]
        if generate_features or fit_extractor:
            self.predict_model.fit_extractor(texts)
        if generate_features:
            texts_features = self.predict_model.prepare_features(texts)
            for c, f in zip(compositions_raw, texts_features):
                c.features = f
            db.session.commit()
        if fit_predict_model:
            self.fit_predict_model()

    def fit_predict_model(self):
        tuples = db.session.query(Composition).options(load_only('features', 'author_id')).all()
        features, targets = [item.features for item in tuples], [item.author_id for item in tuples]

        # собираем уникальные id'шники с авторов и готовим отображения из предсказанного класса в id автора из базы.
        unique_author_ids = db.session.query(Author.id).all()
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

        # декодируем
        text = self.decoder.process(text)
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
        texts = db['texts']
        text_features = texts['features']
        authors_ids = texts['authors']
        self.predict_model.fit(text_features, authors_ids)

    def add_author(self, author_data,):
        # добавляем автора в базу если его там нет.
        # переобучаем knn классификатор под новый класс.
        author = Author(**author_data)
        db.session.add(author)
        db.session.commit()
        db.session.close()

    def del_author(self, id):
        Author.query.filter_by(id=id).delete()
        db.session.commit()

    def del_comp(self, id):
        Composition.query.filter_by(id=id).delete()
        db.session.commit()

    def get_authors(self):
        # запрос к ДБ на получение списка имён всех авторов
        return db.session.query(Author.name).all()  # оверкилл

    def edit_author(self, idx, new_fields):
        a = Author.query.get(idx)
        for key, val in new_fields.items():
            setattr(a, key, val)
        db.session.commit()

    def edit_composition(self, idx, new_fields):
        c = Composition.query.get(idx)
        for key, val in new_fields.items():
            setattr(c, key, val)
        db.session.commit()

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

        author_exists = db.session.query(Author.id).filter_by(name=author_name).scalar()
        if author_exists is not None:
            author_id = author_exists
        else:
            self.add_author({'name': author_name})
            author_id = db.session.query(Author.id).filter_by(name=author_name).scalar()
        c = Composition(title=title, text=text, author_id=author_id, features=features)


        ### TODO здесь косяк с тем. что db импортирована криво и возникает несколько сессий.\
        ### Так что при попытке добавления он пытается их пихнуть во все и вылазиет ошибка.
        ### https: // stackoverflow.com / questions / 24291933 / sqlalchemy - object - already - attached - to - session
        db.session.add(c)
        db.session.commit()
        db.session.close()

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



from tools.decoders import Decoder
from predict_models.LinearModels import LinearModel
from predict_models.NetsModels import NetsModel, WordLSTM, BWordCharLSTM

from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from gvars import modal_package_path

decoder = Decoder(None)
inner_model = LogisticRegression()
pmodel = LinearModel(inner_model)
# inner_model = WordLSTM()
# classifier = LogisticRegression()  # KNeighborsClassifier(n_neighbors=2, n_jobs=-1)
# pmodel = NetsModel(inner_model, classifier, modal_package_path)
be = MBackEnd(pmodel, decoder)

