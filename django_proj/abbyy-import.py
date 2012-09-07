import argparse, csv, gzip, os, pymongo
from time import clock
from xml.etree import cElementTree as ET


def importScan(scan_id):

    abbyy_file = 'scandata/%s/%s_abbyy.gz' % (scan_id, scan_id)
    print 'parsing abbyy'
    t = clock()
    abbyy = ET.parse(gzip.open(abbyy_file))
    abbyy_pages = abbyy.findall('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page')
    print 'found', len(abbyy_pages), 'pages from abbyy data in', clock() - t, 's'

    for result in collection.find({'scan_id': scan_id}):

        abbyy_page = abbyy_pages[result['scandata_index']]

        if ('abbyy' not in result):
            result['abbyy'] = {
                'width': int(abbyy_page.attrib['width']),
                'height': int(abbyy_page.attrib['height']),
                'picture_blocks': []
            }

            pblocks = abbyy_page.findall("{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block[@blockType='Picture']")
            for block in pblocks:
                result['abbyy']['picture_blocks'].append({
                    'blockType': block.attrib['blockType'],
                    'r': int(block.attrib['r']),
                    'l': int(block.attrib['l']),
                    't': int(block.attrib['t']),
                    'b': int(block.attrib['b'])
                })

        #print repr(result)
        #print result['scandata_index']
        collection.save(result)

    print 'parsed', len(abbyy_pages), 'pages from abbyy data in', clock() - t, 's'


if __name__ == "__main__":

    ap = argparse.ArgumentParser(description='csv-import')
    ap.add_argument('--scan', type=str, help='scan id')
    ap.add_argument('-v', help='verbose', action='store_true')

    args = ap.parse_args()

    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife
    collection = mongo_db.page_data

    t = clock()

    if (args.scan):
        importScan(args.scan)
    else:
        for scan_id in collection.distinct('scan_id'):
            if 'abbyy' in collection.find_one({'scan_id': scan_id}):
                print 'abbyy data exists for', scan_id
            else:
                print 'importing abbyy data for', scan_id
                importScan(scan_id)

    print 'Completed in', clock() - t, 's'







