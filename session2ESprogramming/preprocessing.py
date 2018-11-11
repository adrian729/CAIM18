import os
import re
import numpy as np
import matplotlib.pyplot as plt
from math import log
from scipy.optimize import curve_fit


def generate_files_dict(path):
    dfiles = {}
    for df in os.walk(path):
        if df[2]:
            for f in df[2]:                
                dfiles[df[0] + '/' + f] = {}
    return dfiles


def prepare_data(file):
    ydata = []
    words = []
    with open(file, encoding='iso-8859-1') as cw_novels:
        lines = cw_novels.readlines()
        for line in lines:
            line = line.replace('\x00','').replace('ÿþ', '').replace('\n', '')
            if re.search(r',', line):
                [count, word] = line.split(', ', maxsplit=1)
                word = word[2:-1] # CountWords.py doesn't work, needed a cast and saved data as binaries in a string 
                                  # (recast was a lot more work than doing this)
                if not re.search(r'\d|\.|_', word) \
                    and re.match(r'^[A-Za-z]+$', word):
                    ydata.insert(0, int(count))
                    words. insert(0, word)
    xdata = [x for x in range(1, len(ydata) + 1)]
    
    return xdata, ydata, words


def func_zipf(x, a, b, c):
    return c / (x + b) ** a


def fitting(xdata, ydata, func):
    popt, pcov = curve_fit(
        func, 
        xdata,
        ydata, 
        maxfev=2000
    )
    return popt, pcov


def fmse(xdata, ydata, popt, func):
    x = np.array(list(map(lambda x: func(x, *popt), xdata)))
    y = np.array(ydata)
    return ((x - y)**2).mean(axis=None)


def reduce_head_mse(x_data, y_data, func, max_rem=1000):
    rem = 1
    last_mse = -1
    mse = 0
    step = 200
    while rem < max_rem and abs(last_mse - mse) > 0.1:
        last_mse = mse
        x = x_data[rem:]
        y = y_data[rem:]
        popt, _ = fitting(x, y, func)
        mse = fmse(x, y, popt, func)
        rem += step
    return (rem - step), popt, mse


def explore_data(file):
    x, y, words = prepare_data(file)
    popt, _ = fitting(x, y, func_zipf)
    mse = fmse(x, y, popt, func_zipf)
    rem, popt_rem, mse_rem = reduce_head_mse(x, y, func_zipf, 4500)
    result = {}
    result['file'] = file
    result['all'] = {}
    result['all']['y'] = y
    result['all']['words'] = words
    # result['all']['popt'] = list(popt)
    result['all']['mse'] = mse
    result['remove'] = {}
    result['remove']['rem'] = rem
    # result['remove']['popt'] = list(popt_rem)
    result['remove']['mse'] = mse_rem
    return result


def print_info(res):
    print('-'*24)
    print('-'*24)
    print('FILE: ', res['file'])
    print('-'*24)
    print('ALL DATA:')
    print('first words:', res['all']['words'][0:10])
    print('freq first words:', res['all']['y'][0:10])
    print('mse', res['all']['mse'])
    print('-'*12)
    print('REMOVED DATA')
    rem = res['remove']['rem']
    print('removed', rem)
    print('first words:', res['all']['words'][(0 + rem):(10 + rem)])
    print('freq first words:', res['all']['y'][(0 + rem):(10 + rem)])
    print('mse', res['remove']['mse'])
    print('-'*24)
    print('-'*24)
    print()


if __name__ == '__main__':
    data = generate_files_dict("./cwords_done")
    results = []
    for k in data:
        res = explore_data(k)
        results.append(res)
        print_info(res)

    min_mse_all = min(results, key = lambda data: data['all']['mse'])
    min_mse_rem = min(results, key = lambda data: data['remove']['mse'])
    min_rem = min(results, key = lambda data: data['remove']['rem'])

    print()    
    print()
    print()
    print('-'*24)
    print('-'*24)
    print('BEST RESULTS')
    print('-'*24)
    print('-'*24)
    print()
    print_info(min_mse_all)
    print_info(min_mse_rem)
    print_info(min_rem)