import pymongo
from analysis import classifyResult
from helpers import getMongoCollection

if __name__ == '__main__':

    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife

    page_data = mongo_db.page_data

    pages = page_data.find({})

    p_data = []
    r_data = []

    info = {
        'true-pos': 0,
        'true-neg': 0,
        'false-pos': 0,
        'false-neg': 0,
        'p': None,
        'r': None,
    }

    for page in pages:
        result = classifyResult(page['has_illustration']['gold_standard'], page['has_illustration']['contrast'])
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

    print info


