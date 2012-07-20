import cStringIO, glob, gzip, os, subprocess, urllib, zipfile
from PIL import Image, ImageDraw
from xml.etree import cElementTree as ET

from helpers import getIAImage


def process(book_id, page_index):
    image = getIAImage(book_id, page_index)





def process_all(scan_id):

    scandata_file = 'scandata/%s/%s_scandata.xml' % (scan_id, scan_id)
    if not os.path.isfile(scandata_file):
        raise Exception('Unable to find scandata file: %s' % scandata_file)

    print 'parsing scandata'
    scandata = ET.parse(scandata_file)
    scandata_pages = scandata.find('pageData').findall('page')
    print 'found', len(scandata_pages), 'pages in scan data'

    orig_index = 0
    ia_index = 0
    for page in scandata_pages:

        # Skip 'delete' pages
        if page.find('pageType').text == 'Delete':
            orig_index += 1
            continue

        process(scan_id, ia_index)

        ia_index += 1
        orig_index += 1


#process_all('hallofshells00hard')
process('hallofshells00hard', 10)
