
from helpers import getIAImage
from time import clock
from PIL import Image, ImageDraw

import os

def processImage(scan_id, image_index):
    print 'Processing', scan_id, image_index


def renderBlocks(scan_id, ia_page_index, pblocks):

    img = getIAImage(scan_id, ia_page_index)

    if not os.path.exists('tmp/pictureblocks'):
        os.mkdir('tmp/pictureblocks')
    if not os.path.exists('tmp/pictureblocks/%s' % (scan_id)):
        os.mkdir('tmp/pictureblocks/%s' % (scan_id))

    output_file = 'tmp/pictureblocks/%s/%s.png' % (scan_id, ia_page_index)

    t0 = clock()

    size = img.size
    print 'Image size:', size

    scale = 0.2
    small = img.resize([int(size[0]*scale), int(size[1]*scale)])

    draw = ImageDraw.Draw(small)
    for block in pblocks:
        print block.attrib
        draw.rectangle([
                (float(block.attrib['l'])*scale, float(block.attrib['t'])*scale),
                (float(block.attrib['r'])*scale, float(block.attrib['b'])*scale)
            ],
            outline=(0,255,0)
        )
        del draw

    small.save(output_file)
    del img
    del small



def processPage(scan_id, page_index, scandata, abbyy):
    print 'processing', scan_id, 'page', page_index

    pblocks = abbyy.findall("{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block[@blockType='Picture']")

    if len(pblocks) == 0:
        return False

    renderBlocks(scan_id, page_index, pblocks)

    return True


if __name__ == '__main__':

    import gzip
    from helpers import combinePageData
    from xml.etree import cElementTree as ET

    scan_id = 'hallofshells00hard'

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


    n = 10
    for i in range(0, len(scandata_pages)):
        if scandata_pages[i].find('pageType').text == 'Delete':
            continue
        if (n == None):
            # process all pages
            print 'processing'
        elif (i == n):
            break

    if (n != None):
        processPage(scan_id, n, scandata_pages[i], abbyy_pages[i])
