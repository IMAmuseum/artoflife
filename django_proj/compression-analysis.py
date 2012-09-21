import pymongo
from analysis import classifyResult
from helpers import getMongoCollection
from numpy import arange

if __name__ == '__main__':

    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife

    page_data = mongo_db.page_data

    pages = page_data.find({})

    t_data = arange(0, 1, 0.01)

    p_data = []
    r_data = []

    for thresh in t_data:

        info = {
            'true-pos': 0,
            'true-neg': 0,
            'false-pos': 0,
            'false-neg': 0,
            'p': None,
            'r': None,
        }

        for page in pages:

            passes = False
            if ('compression' in page) and (page['compression'] is not None):
                passes = page['compression'] >= thresh

            result = classifyResult(page['has_illustration']['gold_standard'], passes)

            info[result] += 1

        if (info['true-pos'] == 0):
            info['p'] = 0
            info['r'] = 0
        else:
            info['p'] = float(info['true-pos']) / (info['true-pos'] + info['false-pos'])
            info['r'] = float(info['true-pos']) / (info['true-pos'] + info['false-neg'])

        p_data.append(info['p'])
        r_data.append(info['r'])

        pages.rewind()

        print thresh, info

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel('threshold on compression ratio')
    ax.plot(t_data, p_data, 'o', label='Precision', color='b')
    ax.plot(t_data, r_data, 's', label='Recall', color='r')
    ax.legend(loc=1, numpoints=1)

    plt.show()

