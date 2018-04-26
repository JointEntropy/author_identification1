import time
import os
import json
import numpy as np
from sklearn.cluster import AffinityPropagation, \
    AgglomerativeClustering, DBSCAN, Birch, \
    FeatureAgglomeration, KMeans, MiniBatchKMeans, MeanShift,\
    SpectralClustering

METHODS_MAPPING = {
    'AffinityPropagation': AffinityPropagation,
    'AgglomerativeClustering': AgglomerativeClustering,
    'DBSCAN': DBSCAN,
    'Birch': Birch,
    'FeatureAgglomeration': FeatureAgglomeration,
    'KMeans': KMeans,
    'MiniBatchKMeans': MiniBatchKMeans,
    'MeanShift': MeanShift,
    'SpectralClustering': SpectralClustering
}


def calculate(method, data, parameters=None):
    """
    Главный интерфейс для методов кластеризации. Принимает на вход параметры
    вычислений, включающие в себя имя метода и значение аргументы, а также
    путь к файлу с данными. Выполняет вычисления, записывает
    результат в файл и возвращает ссылку на него.
    :param method: имя метода
    :param data: матрица входных наблюдений(список списков)
    :param parameters: параметры для выбранного метода.
    :return список кортежей: метка кластера, соответствующий входной объект.
    """
    parameters = parameters or {}
    if method not in METHODS_MAPPING:
        raise ValueError('Unknown method.')
    method = METHODS_MAPPING[method]
    # Исправление параметров
    params = fix_params(parameters)
    print('Fixed params:\n', params)
    X = np.array(data)
    # Вычисления
    method_instance = method(**params)
    result = method_instance.fit_predict(X) if hasattr(method_instance,'fit_predict') \
                                            else method_instance.fit(X).labels_
    # Склеиваем метки кластеров и входные данные
    samples = list(zip(result.tolist(), data))
    return samples


def fix_params(raw_params):
    """
    Приводит значения словаря с параметрами метода в подходящие типы.
    :param raw_params: словарь с параметрами методов со значениями параметров неправильного типа.
    :return: словарь со значениями параметров пригодными для методов кластеризации.
    """
    def cast_to_type(val):
        if val in ['True', 'False']:
            return True if val == 'True' else False
        try:
            return int(val)
        except ValueError:
            pass
        try:
            return float(val)
        except ValueError:
            pass
        return str(val)
    cleared_params = {}
    for name, value in ((k, v) for k, v in raw_params.items() if v is not None):
        try:
            value = value.strip(' \t"\'’’‘‘`')
        except AttributeError:
            pass
        cleared_params[name] = cast_to_type(value)
    return cleared_params


if __name__ == '__main__':
    ...
