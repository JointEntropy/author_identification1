import os
import json
import sys

# lifehack как не копировать код и юзать костыли
path_external_project = '/home/grigory/PycharmProjects/wikisource'

sys.path.append(path_external_project)
from utils import load_obj
from dataset import split_sequence, preprocessing
from char_lstm_preprocess import filter_chars
from extra_layers import AttentionWithContext
from word_lstm_preprocess import Normalizer

def load_json(pth):
    with open(pth, 'rb') as f:
        fcontent = json.load(f)
        return fcontent
