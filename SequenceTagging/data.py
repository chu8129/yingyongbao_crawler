#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Create By qiuwen(mail:chu8129@gmail.com) @ 2021-08-31 18:38:37



import sys
sys.path.append("./")

import logging
logger = logging.getLogger("root")



import keras
import numpy
import jieba
from collections import Counter
from functools import reduce
import json


class TextGenerator(keras.utils.Sequence):
    def __init__(self, batch_size, vocab_max=100000):
        self.batch_size = batch_size
        self.vocab_size_max = vocab_max

        self.data_list = []

        self.vocab_size = None
        self.vocab_to_index = None
        self.index_to_vocab = None
        self.label_size = None
        self.label_to_index = None
        self.index_to_label = None

        self.data_size = None

    def init(self, file_path, train=True):

        with open(file_path) as fr:
            for line in fr.readlines()[:100]:
                data = line.strip("\n").split("\t", 2)
                self.data_list.append((self.cut_word(data[2]), data[1]))

        self.data_size = len(self.data_list)

        label_set = reduce(lambda data_set, content:set(self.split(content)) | data_set, map(lambda cells:cells[1], iter(self.data_list)), set())
        self.label_to_index = dict(_[::-1] for _ in enumerate(sorted(vocab_set),start=1))
        self.index_to_label = dict(_[::-1] for _ in self.label_to_index.items())
        self.label_size = max(self.index_to_label.keys())

        word_set = dict(
            reduce(
                lambda s1, s2: s1 + s2,
                map(lambda string: Counter(string[0].split()), self.data_list),
            ).most_common(self.vocab_size_max)
        )
        self.vocab_size = len(word_set)
        self.vocab_to_index = dict(zip(word_set, range(self.vocab_size)))
        self.index_to_vocab = dict(zip(range(self.vocab_size), word_set))

        with open("params", "w") as fw:
            fw.write(
                json.dumps(
                    [
                        self.vocab_to_index,
                        self.index_to_vocab,
                        self.label_to_index,
                        self.index_to_label,
                    ]
                )
            )

    def cut_word(self, line):
        return " ".join(jieba.cut(line))

    def __len__(self):
        return self.data_size / self.batch_size

    def __getitem__(self, index):
        sentence_label_list = self.data_list[index * self.batch_size : (index + 1) * self.batch_size]
        sentence_list = [_[0] for _ in sentence_label_list]
        label_list = [_[1] for _ in sentence_label_list]
        return self.transform_data(sentence_list, label_list)

    def transform_data(self, sentence_list, label_list):
        x_vec = numpy.zeros([len(sentence_list), self.vocab_size], dtype=numpy.uint8)
        for index, sentence in enumerate(sentence_list):
            x_words = [word for word in sentence.split()]
            word_indexs = [self.vocab_to_index[word] for word in x_words if word in self.vocab_to_index]
            for word_index in word_indexs:
                x_vec[index][word_index] = 1

        y_vec = numpy.zeros([len(label_list), self.label_size])
        for index, label in enumerate(label_list):
            label_index = self.label_to_index[label]
            y_vec[index][label_index] = 1
        return x_vec, y_vec
