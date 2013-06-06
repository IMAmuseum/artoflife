import argparse
import csv
import pymongo
from time import clock
from helpers import skipScanDataPage
from xml.etree import ElementTree as ET
import fetch_scandata
import json


if __name__ == "__main__":

    ap = argparse.ArgumentParser(description='csv-import')
    ap.add_argument('--file', type=str, help='csv file to import', default=None)
    ap.add_argument('-v', help='verbose', action='store_true')

    args = ap.parse_args()

    input_filename = args.file

    control_file = open(input_filename, 'rU')
    control_reader = csv.reader(control_file)
    control_reader.next()  # skip header

    # mongo_conn = pymongo.Connection('localhost', 27017)
    # mongo_db = mongo_conn.artoflife_final
    # collection = mongo_db.page_data

    t0 = clock()
    rowCount = 0
    fileNumber = 0

    n_control = 0
    control_data = {}
    for row in control_reader:

        if args.v:
                print 'row: ', rowCount

        if (rowCount % 1000 == 0):
            fileNumber += 1
            outputFileName = "scandata/json_load/data_%s.json" % (fileNumber)

        with open(outputFileName, 'a') as outfile:

            # New scan encountered
            if not row[0] in control_data:

                print row[0]

                #fetch data from Internet Archive to local
                fetch_scandata.fetch_files(row[0])

                control_data[row[0]] = {'rows': [], 'n_image_pages': 0}

                scan_id = row[0]
                scandata_file = 'scandata/%s/%s_scandata.xml' % (scan_id, scan_id)

                if args.v:
                    print 'scandata_file: ', scandata_file

                t = clock()

                try:
                    scan_file = open(scandata_file)
                    scan_file_string = scan_file.read()
                    scan_file_string = scan_file_string.replace('xmlns="http://archive.org/scribe/xml"', '')
                    scandata = ET.fromstring(scan_file_string)
                except:
                    if args.v:
                        print 'error reading scandata file: ', scandata_file
                    continue

                scandata_pages = scandata.find('pageData').findall('page')

                if args.v:
                    print 'Loaded', len(scandata_pages), ' scandata pages in', clock() - t, 's'

                ia_page_index = 0
                scandata_index = 0

                for page in scandata_pages:

                    if (skipScanDataPage(page)):
                        scandata_index += 1
                        continue

                    # db_item = collection.find_one({'scan_id': row[0], 'ia_page_num': ia_page_index})

                    # if (db_item is None):

                    info = {
                        'scan_id': row[0],
                        'scandata_index': scandata_index,
                        'ia_page_num': ia_page_index,
                        'page_num': ia_page_index + 1,
                        'leaf_num': page.get('leafNum'),
                        'has_illustration': {
                            'gold_standard': False
                        },
                        'processing_lock': False,
                        'processing_lock_start': 0,
                        'processing_lock_end': 0,
                        'processing_error': False,
                        'abbyy_complete': False,
                        'compression_complete': False,
                        'contrast_complete': False
                    }

                    json.dump(info, outfile)
                    outfile.write("\n")


                    #collection.insert(info)

                    if args.v:
                        print 'Inserted page in', clock() - t, 's'

                    # else:
                    #     if args.v:
                    #         print ia_page_index, 'exists'

                    ia_page_index += 1
                    scandata_index += 1

        rowCount += 1

    control_file.close()

    print 'Finished in', (clock() - t0)
