import os
import random
from math import ceil
from elasticsearch_dsl import Index
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

__author__ = 'adr'

#random.seed(123)

def generate_list_of_files(path):
    files = [(x[0], x[2]) for x in os.walk(path) if x[2]]
    files = map(lambda path_files: [path_files[0] + '/' + f for f in path_files[1]], files)
    return sum(list(files), [])

if __name__ == '__main__':
    client = Elasticsearch()
    
    files = generate_list_of_files('../data/novels')
    num_files = len(files)
    operations = []
    idx = []
    count = 0
    for len_subset in range(1, num_files + 1):
        num_subsets = ceil(num_files / (len_subset * 1.3))
        for i in range(0, num_subsets):
            subset = random.sample(files, len_subset)
            index = 'novels{}'.format(count)
            print(index)
            print()
            idx.append(index)
            for f in subset:
                text = ''
                with open(f, encoding='iso-8859-1') as read_file:
                    text += read_file.read().replace('\n', '')
                operations.append({'_op_type': 'index', '_index': index, '_type': 'document', 'path': f, 'text': text})
            ind = Index(index, using=client)
            if ind.exists():
                ind.delete()
            ind.settings(number_of_shards=1)
            ind.create()
            bulk(client, operations, request_timeout=60)
            operations = []
            count += 1
    
    print("Final count", count)
    