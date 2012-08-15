import argparse, csv, gzip, os
from time import clock
from helpers import skipScanDataPage
from xml.etree import cElementTree as ET
from pictureblocks import processPage

if __name__ == "__main__":

    ap = argparse.ArgumentParser(description='analysis')
    ap.add_argument('--scan', type=str, help='scan id', default=None)

    args = ap.parse_args()

    input_file = 'BHL-gold-standard.csv'

    control_file = open(input_file, 'rU')
    control_reader = csv.reader(control_file)
    control_reader.next()  # skip header

    n_control = 0
    control_data = {}
    for row in control_reader:

        # temporary
        if row[0] != 'mobot31753002719497':
            continue

        # New scan encountered
        if not row[0] in control_data:

            print 'Processing', row[0]

            control_data[row[0]] = {'rows': [], 'n_image_pages': 0}

            scan_id = row[0]

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

            ia_page_index = 0
            scandata_index = 0


        while(skipScanDataPage(scandata_pages[scandata_index])):
            scandata_index += 1

        print 'page', ia_page_index, scandata_index

        result = processPage(
            scan_id,
            ia_page_index,
            scandata_pages[scandata_index],
            abbyy_pages[scandata_index],
            False
        )


        ia_page_index += 1
        scandata_index += 1




