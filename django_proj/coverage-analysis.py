import pymongo
from analysis import classifyResult
from helpers import getMongoCollection

if __name__ == '__main__':

    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife

    page_data = mongo_db.page_data

    pages = page_data.find({})

    t_data = range(0, 101)
    p_data = []
    r_data = []
    a_data = []

    for thresh in t_data:

        info = {
            'true-pos': 0,
            'true-neg': 0,
            'false-pos': 0,
            'false-neg': 0,
            'p': None,
            'r': None,
            'a': None
        }

        value = 'coverage_sum'
        #value = 'coverage_max'

        for page in pages:

            passes = False
            if (value in page['abbyy']) and (page['abbyy'][value] is not None):
                passes = page['abbyy'][value] >= thresh

            result = classifyResult(page['has_illustration']['gold_standard'], passes)

            info[result] += 1

        if (info['true-pos'] == 0):
            info['p'] = 0
            info['r'] = 0
        else:
            info['p'] = float(info['true-pos']) / (info['true-pos'] + info['false-pos'])
            info['r'] = float(info['true-pos']) / (info['true-pos'] + info['false-neg'])

        if pages.count() > 0:
            info['a'] = float(info['true-pos'] + info['true-neg']) / pages.count()

        p_data.append(info['p'])
        r_data.append(info['r'])
        a_data.append(info['a'])

        pages.rewind()

        print thresh, info

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel('threshold on sum of picture block coverage')
    ax.plot(t_data, p_data, 'o', label='Precision', color='b')
    ax.plot(t_data, r_data, 's', label='Recall', color='r')
    ax.plot(t_data, a_data, 'o', label='Accuracy', color='g')
    ax.legend(loc=3, numpoints=1)

    plt.show()

