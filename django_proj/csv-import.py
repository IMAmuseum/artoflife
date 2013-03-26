import argparse
import csv
import pymongo
from time import clock
from helpers import skipScanDataPage
from xml.etree import cElementTree as ET
import fetch_scandata

if __name__ == "__main__":

    ap = argparse.ArgumentParser(description='csv-import')
    ap.add_argument('--file', type=str, help='csv file to import', default=None)
    ap.add_argument('--scan', type=str, help='scan id', default=None)
    ap.add_argument('-v', help='verbose', action='store_true')

    args = ap.parse_args()

    input_filename = args.file

    control_file = open(input_filename, 'rU')
    control_reader = csv.reader(control_file)
    control_reader.next()  # skip header

    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife
    collection = mongo_db.page_data

    t0 = clock()

    n_control = 0
    control_data = {}
    for row in control_reader:

        if (args.scan is not None) and (row[0] != args.scan):
            continue

        # New scan encountered
        if not row[0] in control_data:

            print row[0]

            #fetch data from Internet Archive to local
            fetch_scandata.fetch_files(row[0])

            control_data[row[0]] = {'rows': [], 'n_image_pages': 0}

            scan_id = row[0]
            scandata_file = 'scandata/%s/%s_scandata.xml' % (scan_id, scan_id)

            t = clock()
            scandata = ET.parse(scandata_file)
            scandata_pages = scandata.find('pageData').findall('page')

            if args.v:
                print 'Loaded', len(scandata_pages), ' scandata pages in', clock() - t, 's'

            ia_page_index = 0
            scandata_index = 0

        while(skipScanDataPage(scandata_pages[scandata_index])):
            scandata_index += 1

        db_item = collection.find_one({'scan_id': row[0], 'ia_page_num': ia_page_index})

        if (db_item is None):

            info = {
                'scan_id': row[0],
                'scandata_index': scandata_index,
                'ia_page_num': ia_page_index,
                'page_num': ia_page_index + 1,
                'leaf_num': scandata_pages[scandata_index].get('leafNum'),
                'has_illustration': {
                    'gold_standard': (row[6] == 'Yes')
                }
            }

            collection.insert(info)

            if args.v:
                print ia_page_index, 'inserted'

        else:
            if args.v:
                print ia_page_index, 'exists'

        ia_page_index += 1
        scandata_index += 1

    control_file.close()

    print 'Finished in', (clock() - t0)
