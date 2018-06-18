import numpy as np
from keras.preprocessing.sequence import pad_sequences
import pandas as pd
from .utils import (filter_chars,  preprocessing, load_obj, load_json,
                    split2sentences, group2articles, pad_sentences_df,
                    AttentionWithContext, GlobalOneHalfPooling, split_sequence,  split_long_texts,
                    Normalizer)
from predict_models.core import PredictModel
from keras.models import Model, load_model
from itertools import chain


class NetsModel(PredictModel):
    def __init__(self, fp_model, classifier,  model_package, normalizer=None):
        self.fp_model = fp_model
        self.classifier = classifier

        tools = load_obj(model_package + '/preprocess_tools')
        params = load_json(model_package + '/params.json')
        nm = normalizer if normalizer is not None else Normalizer(backend='mystem', tokenizer=None)

        name = params.get('model', 'model.h5')
        model = load_model(model_package + '/' + name,
                           custom_objects={'AttentionWithContext': AttentionWithContext,
                                           'GlobalOneHalfPooling': GlobalOneHalfPooling})
        model = Model(inputs=model.input, outputs=model.layers[-1].input)
        self.fp_model = fp_model(model=model,
                                 tools=tools, params=params,
                                 normalizer=nm)

    def fit(self, X, y):
        self.classifier.fit(X, y)

    def fit_extractor(self, texts):
        pass

    def predict(self, x):
        predictions = self.classifier.predict_proba([x])
        return list(enumerate(predictions[0]))

    def predict_features(self, text):
        texts = self.fp_model.process(text)
        features = self.fp_model.predict(texts)
        return features.mean(axis=0)
        # return np.random.random(size=(5, ))

    def prepare_features(self, texts):
        texts, groups = self.fp_model.process_batch(texts)
        features = self.fp_model.predict(texts)

        features_df = pd.DataFrame({'features':  [list(f) for f in features],
                                    'groups': groups})
        average_features = features_df.groupby('groups')['features'].apply(list).apply(lambda x: np.mean(x, axis=0))
        for f in average_features:
            yield f


class FeaturePredictModel:
    def __init__(self, model, tools, params, normalizer):
        self.nm = normalizer
        self.model = model
        self.nm = normalizer
        self.tools = tools
        self.params = params

    def process(self, text, normalizer):
        raise NotImplementedError

    def predict(self, X):
        raise NotImplementedError


class BWordCharLSTM(FeaturePredictModel):
    def process(self, text, normalizer):
        # нарезаем на куски, ибо кормить в сеть слишком большой не можем.
        split_threshold = self.params['split_threshold']
        if len(text) > split_threshold:
            text_split = split_sequence(text, split_threshold)  # теперь index - номер произведения, и он дублируется
        else:
            text_split = [text]
        text_split = pd.Series(text_split)
        # предобработка на уровне слов.

        # препроцессим вход.
        filtered_data = filter_chars(text_split)
        text_word = self.nm.normalize(filtered_data)

        # основная часть функции preprocessing из wikisource/dataset, но без работы с метками.
        contexts = self.tools['words_tokenizer'].texts_to_sequences(text_word)
        text_word = pad_sequences(contexts, maxlen=self.params['MAX_TEXT_WORDS'])

        contexts = self.tools['chars_tokenizer'].texts_to_sequences(text_split)
        text_char = pad_sequences(contexts, maxlen=self.params['MAX_TEXT_CHARS'])
        return text_word, text_char

    def predict(self, X):
        return self.model.predict(X, verbose=1)


class WordLSTM(FeaturePredictModel):
    def process(self, text, normalizer):
        # нарезаем на куски, ибо кормить в сеть слишком большой не можем.
        split_threshold = self.params['split_threshold']
        if len(text) > split_threshold:
            text_split = [''.join(text) for text in split_sequence(text, split_threshold) ] # теперь index - номер произведения, и он дублируется
        else:
            text_split = [text]
        text_split = pd.Series(text_split)

        # препроцессим вход.
        filtered_data = filter_chars(text_split)
        text_word = self.nm.normalize(filtered_data)

        # основная часть функции preprocessing из wikisource/dataset, но без работы с метками.
        contexts = self.tools['words_tokenizer'].texts_to_sequences(text_word)
        text_word = pad_sequences(contexts, maxlen=self.params['MAX_TEXT_WORDS'])
        return text_word

    def process_batch(self, texts):

        texts_df = split_long_texts(texts, np.arange(len(texts)), np.arange(len(texts)),self.params['split_threshold'])
        filtered_data = filter_chars(texts_df['text'])

#         nm = Normalizer(backend='mystem')
        texts_word = self.nm.normalize(filtered_data)
        contexts = self.tools['words_tokenizer'].texts_to_sequences(texts_word)
        texts_word = pad_sequences(contexts, maxlen=self.params['MAX_TEXT_WORDS'])
        return texts_word, texts_df.index.values

    def predict(self, X):
        return self.model.predict(X, verbose=1)


class SentenceWordLSTM(FeaturePredictModel):
    def process(self, text, normalizer):
        # нарезаем на куски, ибо кормить в сеть слишком большой не можем.
        split_threshold = self.params['split_threshold']
        if len(text) > split_threshold:
            text_split = [''.join(text) for text in split_sequence(text, split_threshold) ]
        else:
            text_split = [text]
        text_split = pd.Series(text_split)




        # препроцессим вход.
        filtered_data = filter_chars(text_split)

        # нарезаем на предложения
        splitted = split2sentences(filtered_data)
        sentence_counts = splitted.apply(len)

        sentences = pd.Series(list(chain.from_iterable(splitted)))


        nm = Normalizer()
        normalized_sentences = nm.normalize(sentences)
        normalized_texts = pd.Series(list(group2articles(normalized_sentences, sentence_counts)))






        text_word = self.nm.normalize(filtered_data)

        # основная часть функции preprocessing из wikisource/dataset, но без работы с метками.
        contexts = self.tools['words_tokenizer'].texts_to_sequences(text_word)
        text_word = pad_sequences(contexts, maxlen=self.params['MAX_TEXT_WORDS'])
        return text_word

    def process_batch(self, texts):

        texts_df = split_long_texts(texts, np.arange(len(texts)), self.params['split_threshold'])
        filtered_data = filter_chars(texts_df['text'])

        # сплитим на предложения
        splitted = split2sentences(filtered_data)
        sentence_counts = splitted.apply(len)

        sentences = pd.Series(list(chain.from_iterable(splitted)))
        nm = Normalizer()
        normalized_sentences = nm.normalize(sentences)
        normalized_texts = pd.Series(list(group2articles(normalized_sentences, sentence_counts)))




        texts_word = self.nm.normalize(filtered_data)
        contexts = self.tools['words_tokenizer'].texts_to_sequences(texts_word)
        texts_word = pad_sequences(contexts, maxlen=self.params['MAX_TEXT_WORDS'])
        return texts_word, texts_df.index.values

    def predict(self, X):
        return self.model.predict(X, verbose=1)

