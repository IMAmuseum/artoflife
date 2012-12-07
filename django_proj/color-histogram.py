import tarfile, zipfile
from time import clock
from wand.image import Image as wImage
from PIL import Image as pImage 
from cStringIO import StringIO

import colorsys
from numpy import histogram, mean, std

def getJP2asPIL(book_id, ia_page_index, scale=0.5):

    tar_filename = 'scandata/%s/%s_jp2.tar' % (book_id, book_id)
    tar_file = tarfile.open(tar_filename)

    jp2_file = '%s_jp2/%s_%04d.jp2' % (book_id, book_id, int(ia_page_index) + 1)
    jp2_data = tar_file.extractfile(jp2_file)

    # Use Wand to read jp2, then pass to PIL as png
    w_image = wImage(blob=jp2_data)
    w_image.resize(int(w_image.width * scale), int(w_image.height * scale))

    image = pImage.open(StringIO(w_image.make_blob('png')))
    del w_image

    return image


def plotHist(data, x_label):

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111)

    n, bins, patches = ax.hist(data, 100, facecolor='green', alpha=0.75)

    ax.set_xlabel(x_label)
    ax.set_ylabel('Occurrences')
    ax.grid(True)

    return plt


def processPage(book_id, page_id):

    t0 = clock()
    image = getJP2asPIL(book_id, page_id)
    if image.mode == 'L':
        print 'b&w'
        return None

    t1 = clock()
    data = image.getdata()
    hues = []
    sats = []
    for d in data:
        hsv = colorsys.rgb_to_hsv(d[0] / 255.0, d[1] / 255.0, d[2] / 255.0)
        hues.append(hsv[0])
        sats.append(hsv[1])

    del image

    result = {
        'h': {
            'mean': mean(hues),
            'std': std(hues),
            'hist': []
        },
        's': {
            'mean': mean(sats),
            'std': std(sats),
            'hist': []
        }
    }

    result['h']['hist'], bin_edges = histogram(hues, 100, (0, 1), density=True)
    result['s']['hist'], bin_edges = histogram(sats, 100, (0, 1), density=True)
    result['load_t'] = t1 - t0
    result['eval_t'] = clock() - t1

    return result


def processBook(page_coll, color_coll, book_id):

    color_coll.remove({'scan_id': book_id})

    pages = page_coll.find({'scan_id': args.scan}, timeout=False).sort('ia_page_num')

    print 'Processing all pages'
    for page in pages:

        print page['ia_page_num'], 'of', pages.count()
        info = processPage(args.scan, page['ia_page_num'])

        if info is not None:

            info['scan_id'] = args.scan
            info['ia_page_num'] = page['ia_page_num']
            info['h']['hist'] = list(info['h']['hist'])
            info['s']['hist'] = list(info['s']['hist'])

            color_coll.save(info)


if __name__ == '__main__':

    import argparse

    ap = argparse.ArgumentParser(description='picture block processing')
    ap.add_argument('--scan', type=str, help='scan id', default=None)
    ap.add_argument('--page', type=int, help='page #', default=None)

    args = ap.parse_args()

    if (args.scan != None) and (args.page != None):
        result = processPage(args.scan, args.page)
        #plotHist(result['h'], 'Hue').show()
        plotHist(result['s'], 'Saturation').show()
    else:

        import pymongo
        mongo_conn = pymongo.Connection('localhost', 27017)
        mongo_db = mongo_conn.artoflife
        page_coll = mongo_db.page_data
        color_coll = mongo_db.color_data

        if (args.scan == None):
            print 'Processing all books'
        else:
            processBook(page_coll, color_coll, args.scan)

