import pymongo
from analysis import classifyResult
from helpers import getMongoCollection
from numpy import array, histogram

if __name__ == '__main__':

    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife

    page_data = mongo_db.page_data

    pages = page_data.find({})

    range_with = (None, None)
    range_without = (None, None)

    with_v = []
    without_v = []

    for page in pages:

        if ('compression' in page):
            if page['has_illustration']['gold_standard']:
                with_v.append(page['compression'])
            else:
                without_v.append(page['compression'])
        else:
            print 'No compression on', page['scan_id'], page['ia_page_num']


    with_v = array(with_v)
    without_v = array(without_v)            

    print 'Range with: (%f, %f)' % (with_v.min(), with_v.max())
    print 'Range without: (%f, %f)' % (without_v.min(), without_v.max())

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111)

    n, bins, patches = ax.hist([with_v, without_v], 100, color=('green', 'grey'), edgecolor=None, histtype='barstacked')

    ax.set_xlabel('Compression')
    ax.set_ylabel('Occurrences')
    #ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
    #ax.set_xlim(0, 120)
    ax.grid(True)

    plt.show()
