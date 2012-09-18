import os
from helpers import getIAImage


def processPage(scan_id, ia_page_index):

    img = getIAImage(scan_id, ia_page_index)
    filesize = os.path.getsize('tmp/ia/%s/%s.jpeg' % (scan_id, ia_page_index))

    return {
        'file_size': filesize,
        'compression': float(filesize) / (img.size[0] * img.size[1])
    }


def processScan(scan_id, collection):

    print 'Processing', scan_id

    for page in collection.find({'scan_id': scan_id}):

        result = processPage(scan_id, page['ia_page_num'])

        print result

        page.update(result)
        collection.save(page)


if __name__ == '__main__':

    import argparse
    import pymongo

    ap = argparse.ArgumentParser(description='picture block processing')
    ap.add_argument('--scan', type=str, help='scan id', default=None)

    args = ap.parse_args()

    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife
    collection = mongo_db.page_data

    if args.scan == None:

        for scan_id in collection.distinct('scan_id'):
            processScan(scan_id, collection)

    else:

        processScan(args.scan, collection)
