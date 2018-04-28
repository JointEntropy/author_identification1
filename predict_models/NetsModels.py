from sklearn.neighbors import KNeighborsClassifier
import numpy as np
from keras.preprocessing.sequence import pad_sequences
import pandas as pd
from .utils import (filter_chars,  preprocessing, load_obj, load_json,
                    AttentionWithContext, split_sequence,
                    Normalizer)
from predict_models.core import PredictModel
from keras.models import Model, load_model


class NetsModel(PredictModel):
    def __init__(self, fp_model, model_package):
        self.fp_model = fp_model
        self.fp_model.tools = load_obj(model_package + '/preprocess_tools')
        self.fp_model.params = load_json(model_package + '/params.json')

        model = load_model(model_package + '/model.h5',
                           custom_objects={'AttentionWithContext': AttentionWithContext})
        self.fp_model.model = Model(inputs=model.input, outputs=model.layers[-2].output)
        self.knn = KNeighborsClassifier(n_neighbors=5)

    def fit(self, X, y):
        self.knn.fit(X, y)

    def fit_extractor(self, texts):
        pass

    def predict(self, x):
        predictions = self.knn.predict_proba([x])
        return list(enumerate(predictions[0]))

    def predict_features(self, text):
        # texts = self.fp_model.process(text)
        # features = self.fp_model.predict(texts)
        # return features.mean(axis=0)
        return np.random.random(size=(5, 5)).ravel()

    def prepare_features(self, texts):
        pass


class BWordCharLSTM:
    def process(self, X):
        # нарезаем на куски, ибо кормить в сеть слишком большой не можем.
        split_threshold = self.params['split_threshold']
        if len(X) > split_threshold:
            text_split = split_sequence(X, split_threshold)  # теперь index - номер произведения, и он дублируется
        else:
            text_split = [X]
        text_split = pd.Series(text_split)
        # предобработка на уровне слов.
        nm = Normalizer(backend='mystem', tokenizer=None) # default tokenizer of mystem is used.

        # препроцессим вход.
        filtered_data = filter_chars(text_split)
        text_word = nm.normalize(filtered_data)

        # основная часть функции preprocessing из wikisource/dataset, но без работы с метками.
        contexts = self.tools['words_tokenizer'].texts_to_sequences(text_word)
        text_word = pad_sequences(contexts, maxlen=self.params['MAX_TEXT_WORDS'])

        contexts = self.tools['chars_tokenizer'].texts_to_sequences(text_split)
        text_char = pad_sequences(contexts, maxlen=self.params['MAX_TEXT_CHARS'])
        return text_word, text_char

    def predict(self, X):
        return self.model.predict(X, verbose=0)


class WordLSTM:
    def process(self, X):
        # нарезаем на куски, ибо кормить в сеть слишком большой не можем.
        split_threshold = self.params['split_threshold']
        if len(X) > split_threshold:
            text_split = split_sequence(X, split_threshold)  # теперь index - номер произведения, и он дублируется
        else:
            text_split = [X]
        text_split = pd.Series(text_split)
        # предобработка на уровне слов.
        nm = Normalizer(backend='mystem', tokenizer=None) # default tokenizer of mystem is used.

        # препроцессим вход.
        filtered_data = filter_chars(text_split)
        text_word = nm.normalize(filtered_data)

        # основная часть функции preprocessing из wikisource/dataset, но без работы с метками.
        contexts = self.tools['words_tokenizer'].texts_to_sequences(text_word)
        text_word = pad_sequences(contexts, maxlen=self.params['MAX_TEXT_WORDS'])
        return text_word

    def predict(self, X):
        return self.model.predict(X, verbose=0)