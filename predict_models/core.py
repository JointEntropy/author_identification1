class PredictModel:
    def fit(self, X, y):
        """
        Обучает классификатор на фичах.
        :param X:
        :param y:
        :return:
        """
        raise NotImplementedError('Fit not implemented!')

    def fit_extractor(self, texts):
        """
        Обучает извлекатель фич на текстах. Опциональный метод
        :param texts:
        :return:
        """
        raise  NotImplementedError;

    def predict(self, x):
        """
        Принимает на вход вектор фичей и предсказывает вероятности по классам.
        Работает только после вызова fit.
        :param X:
        :return:
        """
        raise NotImplementedError('Predict not implemented!')

    def predict_features(self, texts):
        """
        Готовит фичи для обучения классификатора.
        Должен работать и без преварительного fit.
        :param text:
        :return:
        """
        raise NotImplementedError('Predict features not implemented!')

    def prepare_features(self, texts):
        """
        Готовит фичи для многих текстов сразу.. Работает и без предварительного fit.
        :param texts:
        :return:
        """
        raise NotImplementedError('Prepare features not implemented!')
