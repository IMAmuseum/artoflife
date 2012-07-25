
from helpers import getIAImage
from time import clock
from numpy import average
from PIL import Image, ImageDraw

import os

benchmarks = {
    'image_processing': []
}


def renderBlocks(scan_id, ia_page_index, pblocks, output_width=500):

    img = getIAImage(scan_id, ia_page_index)

    if not os.path.exists('tmp/pictureblocks'):
        os.mkdir('tmp/pictureblocks')
    if not os.path.exists('tmp/pictureblocks/%s' % (scan_id)):
        os.mkdir('tmp/pictureblocks/%s' % (scan_id))

    output_file = 'tmp/pictureblocks/%s/%s_blocks_%s.png' % (scan_id, scan_id, ia_page_index)

    t0 = clock()

    size = img.size
    scale = float(output_width) / img.size[0]
    print 'Image size:', size, 'scale factor:', scale

    small = img.resize([output_width, int(img.size[1] * scale)])

    draw = ImageDraw.Draw(small)
    for block in pblocks:
        print block.attrib
        draw.rectangle([
                (float(block.attrib['l']) * scale, float(block.attrib['t']) * scale),
                (float(block.attrib['r']) * scale, float(block.attrib['b']) * scale)
            ],
            outline=(0, 255, 0)
        )
    del draw

    small.save(output_file)
    del img
    del small

    benchmarks['image_processing'].append(clock() - t0)

    return output_file



def processPage(scan_id, ia_page_index, scandata, abbyy):
    print 'processing', scan_id, 'IA page', ia_page_index

    pblocks = abbyy.findall("{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block[@blockType='Picture']")

    if len(pblocks) == 0:
        return False

    renderBlocks(scan_id, ia_page_index, pblocks)

    return True


if __name__ == '__main__':

    import argparse
    import gzip
#    from helpers import combinePageData
    from xml.etree import cElementTree as ET

    ap = argparse.ArgumentParser(description='picture block processing')
    ap.add_argument('scan', type=str, help='scan id')
    ap.add_argument('--page', type=int, help='page #', default=None)

    args = ap.parse_args()

    #scan_id = 'hallofshells00hard'
    scan_id = args.scan

    abbyy_file = 'scandata/%s/%s_abbyy.gz' % (scan_id, scan_id)
    scandata_file = 'scandata/%s/%s_scandata.xml' % (scan_id, scan_id)

    print 'parsing scandata'
    t = clock()
    scandata = ET.parse(scandata_file)
    scandata_pages = scandata.find('pageData').findall('page')
    print 'found', len(scandata_pages), 'pages from scan data in', clock() - t, 's'

    print 'parsing abbyy'
    t = clock()
    abbyy = ET.parse(gzip.open(abbyy_file))
    abbyy_pages = abbyy.findall('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page')
    print 'found', len(abbyy_pages), 'pages from abbyy data in', clock() - t, 's'

    if (args.page != None):
        processPage(scan_id, args.page, scandata_pages[args.page], abbyy_pages[args.page])
    else:
        ia_page_index = 0
        for i in range(0, len(scandata_pages)):
            if scandata_pages[i].find('pageType').text == 'Delete':
                continue
            if (args.page == None):
                # process all pages
                processPage(scan_id, ia_page_index, scandata_pages[i], abbyy_pages[i])
            elif (i == args.page):
                break
            ia_page_index += 1

    print 'Avg image processing time:', average(benchmarks['image_processing']), 's'
