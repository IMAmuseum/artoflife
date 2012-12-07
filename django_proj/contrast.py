import os
from PIL import Image, ImageEnhance, ImageOps
from time import clock
from helpers import getIAImage

benchmarks = {
    'image_processing': [],
    'single_dim': []
}


def convert(working_file, command):
    os.system('convert ' + working_file + ' ' + command + ' ' + working_file)


def processPage(scan_id, ia_page_index):
    print 'processing', scan_id, ia_page_index

    img = getIAImage(scan_id, ia_page_index)

    result = processImage(img, scan_id, ia_page_index)

    del img

    return result


def processImage(img, scan_id, ia_page_index, pct_thresh=10):

    if not os.path.exists('tmp/contrast'):
        os.mkdir('tmp/contrast')
    if not os.path.exists('tmp/contrast/%s' % (scan_id)):
        os.mkdir('tmp/contrast/%s' % (scan_id))

    t0 = clock()

    working_file = 'tmp/contrast/%s/%s_contrast_%s.png' % (scan_id, scan_id, ia_page_index)

    img.save(working_file)

    # desaturate
    convert(working_file, '-colorspace Gray')
    #img = img.convert('L')

    # apply heavy contrast
    convert(working_file, '-contrast -contrast -contrast -contrast -contrast -contrast -contrast -contrast')
    #img = ImageOps.autocontrast(img, 5)

    t1 = clock()

    processing_size = 500

    # resize to 1px width
    convert(working_file, '-resize 1x%d!' % (processing_size))
    #w_compressed = ImageOps.equalize(img.resize((1, size[1]), Image.BILINEAR))

    # sharpen
    convert(working_file, '-sharpen 0x5')
    #enhancer = ImageEnhance.Sharpness(w_compressed)
    #w_compressed = enhancer.enhance(2.0)

    # convert to grayscale
    convert(working_file, '-negate -threshold 0 -negate')

    # identify long lines
    w_compressed = Image.open(working_file)

    info = {
        'max_contiguous': 0,
        'image_detected': False,
        'total_time': 0,
        '1d_time': 0
    }

    pixel_data = list(w_compressed.getdata())
    #print pixel_data
    n_contig = 0
    for p in pixel_data:
        if p == 0:
            n_contig += 1
        else:
            info['max_contiguous'] = max(info['max_contiguous'], n_contig)
            n_contig = 0

    del w_compressed

    info['max_contiguous'] = float(info['max_contiguous']) / processing_size

    if (info['max_contiguous'] > pct_thresh / 100.0):
        info['image_detected'] = True

    tf = clock()

    info['total_time'] = tf - t0
    info['1d_time'] = tf - t1

    return info


def runMongo(scan_id, page=None):

    from helpers import getMongoCollection

    coll = getMongoCollection('page_data')

    if scan_id is None:
        pages = coll.find({})
    elif page is None:
        pages = coll.find({'scan_id': scan_id})
    else:
        pages = coll.find({'scan_id': scan_id, 'scandata_index': page})

    for page in pages:
        result = processPage(page['scan_id'], page['ia_page_num'])

        page['has_illustration']['contrast'] = result['image_detected']
        page['contrast'] = result
        """
        if not 'benchmarks' in page:
            page['benchmarks'] = {
                'contrast': {}
            }
        page['benchmarks']['contrast']['total'] = benchmarks['image_processing'][-1:][0]
        """

        coll.save(page)

        #print page


if __name__ == '__main__':

    import argparse
#    from helpers import combinePageData
    from numpy import average
    from xml.etree import cElementTree as ET

    ap = argparse.ArgumentParser(description='picture block processing')
    ap.add_argument('--scan', type=str, help='scan id', default=None)
    ap.add_argument('--page', type=int, help='page #', default=None)

    args = ap.parse_args()

    runMongo(args.scan, args.page)

    print 'Avg image processing time:', average(benchmarks['image_processing']), 's'
    print 'Avg time for single dimension:', average(benchmarks['single_dim']), 's'

