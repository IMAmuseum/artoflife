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

def processPage(scan_id, ia_page_index, scandata_page):
    print 'processing', scan_id, ia_page_index

    img = getIAImage(scan_id, ia_page_index)

    if not os.path.exists('tmp/contrast'):
        os.mkdir('tmp/contrast')
    if not os.path.exists('tmp/contrast/%s' % (scan_id)):
        os.mkdir('tmp/contrast/%s' % (scan_id))

    working_file = 'tmp/contrast/%s/%s_contrast_%s.png' % (scan_id, scan_id, ia_page_index)

    t0 = clock()

    orig_size = img.size
    scale = 0.25
    print 'Original image size:', orig_size

    # scale down to improve performance
    size = (int(orig_size[0] * scale), int(orig_size[1] * scale))
    print 'working size:', size
    img.thumbnail(size, Image.ANTIALIAS)
    img.save(working_file)

    # desaturate
    convert(working_file, '-colorspace Gray')
    #img = img.convert('L')

    # apply heavy contrast
    convert(working_file, '-contrast -contrast -contrast -contrast -contrast -contrast -contrast -contrast')
    #img = ImageOps.autocontrast(img, 5)

    t1 = clock()

    # resize to 1px width
    convert(working_file, '-resize 1x500!')
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
        'image_detected': False
    }

    pixel_data = list(w_compressed.getdata())
    #print pixel_data
    n_contig = 0
    for p in pixel_data:
        if p == 0:
            n_contig += 1
            if (n_contig > 50):
                info['image_detected'] = True
                print 'image detected'
                break
        else:
            n_contig = 0

    del img

    tf = clock()

    benchmarks['image_processing'].append(tf - t0)
    benchmarks['single_dim'].append(tf - t1)

    return info


if __name__ == '__main__':

    import argparse
#    from helpers import combinePageData
    from numpy import average
    from xml.etree import cElementTree as ET

    ap = argparse.ArgumentParser(description='picture block processing')
    ap.add_argument('scan', type=str, help='scan id')
    ap.add_argument('--page', type=int, help='page #', default=None)

    args = ap.parse_args()

    #scan_id = 'hallofshells00hard'
    scan_id = args.scan

    scandata_file = 'scandata/%s/%s_scandata.xml' % (scan_id, scan_id)

    print 'parsing scandata'
    t = clock()
    scandata = ET.parse(scandata_file)
    scandata_pages = scandata.find('pageData').findall('page')
    print 'found', len(scandata_pages), 'pages from scan data in', clock() - t, 's'

    if (args.page != None):
        result = processPage(scan_id, args.page, scandata_pages[args.page])
        print result
    else:
        results = []
        ia_page_index = 0
        for i in range(0, len(scandata_pages)):
            if scandata_pages[i].find('pageType').text == 'Delete':
                continue
            if (args.page == None):
                # process all pages
                results.append(processPage(scan_id, ia_page_index, scandata_pages[i]))
            elif (i == args.page):
                break
            ia_page_index += 1
            if (ia_page_index > 10):
                break

    import csv
    output_filename = 'output/contrast/%s.csv' % scan_id
    if not os.path.exists(os.path.dirname(output_filename)):
        os.mkdir(os.path.dirname(output_filename))

    output_file = open(output_filename, 'w')
    writer = csv.writer(output_file)
    writer.writerow(['IA page', 'Image detected', 'Processing time', '1D'])

    for p in range(0, len(results)):
        writer.writerow([p, results[p]['image_detected'], benchmarks['image_processing'][p], benchmarks['single_dim'][p]])
        if (results[p]['image_detected']):
            print 'Image detected on page', p

    output_file.close()
    print 'Avg image processing time:', average(benchmarks['image_processing']), 's'
    print 'Avg time for single dimension:', average(benchmarks['single_dim']), 's'

