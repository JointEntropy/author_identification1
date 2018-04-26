from models import Author, Composition
from sqlalchemy.orm import load_only
import pickle as pkl

class MBackEnd:
    def __init__(self, model, db, decoder):
        self.predict_model = model
        self.db = db
        self.decoder = decoder

    def predict(self, X):
        """
        Получаем сырой текст запроса. Декодирует его и предсказывает топ 5 бомжей.
        :param X: сырой текст запроса.
        :return: топ 5 авторов с вероятностями.
        """
        X = self.decoder.process(X)
        predictions = self.predict_model.predict(X)
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
            author = Author.query.get(author_id)
        else:
            self.add_author({'name': author_name})
            author_id = self.db.session.query(Author.id).filter_by(name=author_name).scalar()
            author = Author.query.get(author_id)
        c = Composition(title=title, text=text, author=author, features=pkl.dumps(features))


        ### TODO здесь косяк с тем. что db импортирована криво и возникает несколько сессий.\
        ### Так что при попытке добавления он пытается их пихнуть во все и вылазиет ошибка.
        ### https: // stackoverflow.com / questions / 24291933 / sqlalchemy - object - already - attached - to - session
        self.db.session.add(c)
        self.db.session.commit()

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
