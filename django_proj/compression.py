import os
from helpers import getIAImage


def processPage(scan_id, ia_page_index):

    img = getIAImage(scan_id, ia_page_index)
    filesize = os.path.getsize('tmp/ia/%s/%s.jpeg' % (scan_id, ia_page_index))

    mode_to_bpp = {'1': 1, 'L': 8, 'P': 8, 'RGB': 24, 'RGBA': 32, 'CMYK': 32, 'YCbCr': 24, 'I': 32, 'F': 32}

    area = img.size[0] * img.size[1]

    return {
        'file_size': filesize,
        'bytes_per_pixel': float(filesize) / area,
        'pixel_depth': mode_to_bpp[img.mode],
        'compression': float(filesize) * 8 / (area * mode_to_bpp[img.mode])
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
