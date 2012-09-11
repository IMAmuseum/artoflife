
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


def processPage(scan_id, ia_page_index, scandata, abbyy, render=False):
    #print 'processing', scan_id, 'IA page', ia_page_index

    t0 = clock()

    pblocks = abbyy.findall("{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block[@blockType='Picture']")

    info = {
        'image_detected': (not len(pblocks) == 0),
        'n_picture_blocks': len(pblocks),
        'abbyy_processing': clock() - t0,
        'coverage': 0,
        'blocks_intersect': False
    }

    if len(pblocks) == 0:
        return info

    # calculate page area
    Ap = float(abbyy.attrib['width']) * float(abbyy.attrib['height'])

    # calculate total picture block area
    Ab = 0
    for block in pblocks:
        Ab += (int(block.attrib['r']) - int(block.attrib['l'])) * (int(block.attrib['b']) - int(block.attrib['t']))

    info['coverage'] = 100 * Ab / Ap

    # determine intersections
    for b1 in pblocks:
        for b2 in pblocks:
            if b2 == b1:
                break
            info['blocks_intersect'] = blocksIntersect(b1, b2)
            if info['blocks_intersect']:
                break
        if info['blocks_intersect']:
            break

    if render:
        renderBlocks(scan_id, ia_page_index, pblocks)

    return info


def blocksIntersect(b1, b2):
    return rectsIntersect(b1.attrib, b2.attrib)


def rectsIntersect(r1, r2):
    return not (
        (r2['l'] > r1['r']) or
        (r2['r'] > r1['l']) or
        (r2['t'] > r1['b']) or
        (r2['b'] > r1['t'])
    )


def runCSV():

    import argparse
    import gzip
    from helpers import skipScanDataPage
    from xml.etree import cElementTree as ET
    import sys

    ap = argparse.ArgumentParser(description='picture block processing')
    ap.add_argument('scan', type=str, help='scan id')
    ap.add_argument('--page', type=int, help='page #', default=None)
    ap.add_argument('--render', type=bool, help='render blocks', default=False)

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

    results = []
    ia_page_index = 0
    for i in range(0, len(scandata_pages)):
        if skipScanDataPage(scandata_pages[i]):
            continue
        if (args.page == None):
            # process all pages
            results.append(processPage(
                scan_id,
                ia_page_index,
                scandata_pages[i],
                abbyy_pages[i],
                args.render
            ))
        elif (i == args.page):
            break
        ia_page_index += 1

    if (args.page != None):
        print processPage(scan_id, ia_page_index, scandata_pages[i], abbyy_pages[i], args.render)
        sys.exit()

    import csv
    output_filename = 'output/pictureblocks/%s-pictureblocks.csv' % scan_id
    if not os.path.exists(os.path.dirname(output_filename)):
        os.mkdir(os.path.dirname(output_filename))

    output_file = open(output_filename, 'w')
    writer = csv.writer(output_file)
    writer.writerow([
        'IA page',
        'Image detected',
        'Processing time',
        '# of picture blocks',
        '% coverage',
        'intersection'
    ])

    for p in range(0, len(results)):
        #print p
        writer.writerow([
            p,
            results[p]['image_detected'],
            results[p]['abbyy_processing'],
            results[p]['n_picture_blocks'],
            results[p]['coverage'],
            results[p]['blocks_intersect']
        ])
        if (results[p]['image_detected']):
            print 'Image detected on page', p

    output_file.close()

    if (args.render):
        print 'Avg image processing time:', average(benchmarks['image_processing']), 's'


def processScanMongo(collection, scan_id=None):

    for result in collection.find({'scan_id': scan_id}):

        if 'abbyy' not in result:
            print 'Abbyy data not found for', scan_id, result['scandata_index']
            continue

        if len(result['abbyy']['picture_blocks']) == 0:
            continue

        # calculate page area
        Ap = float(result['abbyy']['width']) * float(result['abbyy']['height'])

        result['abbyy']['coverage'] = 0
        result['abbyy']['blocks_intersect'] = False

        for block in result['abbyy']['picture_blocks']:

            block['coverage'] = 100 * (int(block['r']) - int(block['l'])) * (int(block['b']) - int(block['t'])) / Ap
            result['abbyy']['coverage'] += block['coverage']

            # determine intersections
            if not result['abbyy']['blocks_intersect']:
                for other_block in result['abbyy']['picture_blocks']:
                    if other_block == block:
                        break
                    result['abbyy']['blocks_intersect'] = rectsIntersect(block, other_block)
                    if result['abbyy']['blocks_intersect']:
                        break

        print result
        collection.save(result)


def runMongo():

    import argparse
    import pymongo

    ap = argparse.ArgumentParser(description='picture block processing')
    ap.add_argument('scan', type=str, help='scan id')

    args = ap.parse_args()

    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife
    collection = mongo_db.page_data

    processScanMongo(collection, args.scan)


if __name__ == '__main__':

#    runCSV()
    runMongo()
