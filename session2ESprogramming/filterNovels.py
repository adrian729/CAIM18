# -*- coding: utf-8 -*-
import os
from itertools import chain, combinations

def subsets(ss):
    return chain(*map(lambda x: combinations(ss, x), range(0, len(ss)+1)))

def gen_index(name, token=None, set_filters=()):
    index = name
    if token is not None:
        index += '_{}'.format(token[0:2])
    for f in set_filters:
        index += '_{}'.format(f[0:2])
    return index

def gen_filter(set_filters=()):
    arg_filter = ''
    if len(set_filters) > 0:
        arg_filter = ' --filter'
        for f in set_filters:
            arg_filter += ' {}'.format(f)
    return arg_filter

def gen_tokenizer(tokenizer):
    arg_tokenizer = ''
    if tokenizer is not None:
        arg_tokenizer += ' --token {}'.format(tokenizer)
    return arg_tokenizer

tokenizers = ['whitespace', 'classic', 'standard', 'letter']
filters = ['lowercase', 'asciifolding', 'stop', 'snowball', 'porter_stem', 'kstem']

name = 'novels'
for t in tokenizers:
    for subset in subsets(filters):
        index = gen_index(name, t, subset)
        arg_tokenizer = gen_tokenizer(t)
        arg_filter = gen_filter(subset)
        IndexFilesPreprocess = 'python IndexFilesPreprocess.py --index {} --path ../data/novels{}{}'.format(index, arg_tokenizer, arg_filter)
        cwords = 'python CountWords.py --index {} > ./cwords/{}.txt'.format(index, index)
        print('ifp:', IndexFilesPreprocess)
        print ('cwords:', cwords)
        print()
        os.system(IndexFilesPreprocess)
        os.system(cwords)