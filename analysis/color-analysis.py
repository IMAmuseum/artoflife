import pymongo
from numpy import array

def analyzePages(page_coll, color_coll, scan_id=None):

    if scan_id is None:
        pages = color_coll.find({}).sort('ia_page_num')
    else:
        pages = color_coll.find({'scan_id': scan_id}).sort('ia_page_num')

    with_v = []
    without_v = []

    for page in pages:
        page_data = page_coll.find_one({'scan_id': page['scan_id'], 'ia_page_num': page['ia_page_num']})

        #value = page['s']['std']
        #value = page['s']['mean']
        value = float(array(page['s']['hist'][60:]).sum())

        if page_data['has_illustration']['gold_standard']:
            with_v.append(value)
        else:
            without_v.append(value)

    with_v = array(with_v)
    without_v = array(without_v)

    print 'Range with: (%f, %f)' % (with_v.min(), with_v.max())
    print 'Range without: (%f, %f)' % (without_v.min(), without_v.max())

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111)

    n, bins, patches = ax.hist([with_v, without_v], 100, color=('green', 'grey'), edgecolor=None, histtype='barstacked')

    ax.set_xlabel('Value')
    ax.set_ylabel('Occurrences')
    #ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
    #ax.set_xlim(0, 120)
    ax.grid(True)

    plt.show()


if __name__ == '__main__':

    import argparse

    ap = argparse.ArgumentParser(description='color analysis')
    ap.add_argument('--scan', type=str, help='scan id', default=None)
    ap.add_argument('--page', type=int, help='page #', default=None)

    args = ap.parse_args()

    import pymongo
    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife
    page_coll = mongo_db.page_data
    color_coll = mongo_db.color_data

    analyzePages(page_coll, color_coll, args.scan)