import argparse, os, urllib2, zlib

from cStringIO import StringIO
from PIL import Image
from xml.etree import cElementTree as ET

ap = argparse.ArgumentParser(description='picture block processing')
ap.add_argument('scan', type=str, help='scan id', default=None)
ap.add_argument('-v', help='verbose', action='store_true')

args = ap.parse_args()

abbyy_filename = '%s_abbyy.gz' % (args.scan)
scandata_filename = '%s_scandata.xml' % (args.scan)

# Fetch scandata file
if (args.v):
    print 'Fetching scandata...'
scandata_file = urllib2.urlopen("http://archive.org/download/%(scan)s/%(file)s" % {'scan': args.scan, 'file': scandata_filename})

if (args.v):
    print 'Parsing scandata...'
scandata = ET.parse(scandata_file)
scandata_pages = scandata.find('pageData').findall('page')

#print scandata_pages

page_data = []

ia_page_num = 0
scandata_index = 0
for page in scandata_pages:

    if page.find('addToAccessFormats').text != 'true':
        scandata_index += 1
        continue

    has_illustration = None

    pageType = page.find('pageType')
    altPageTypes = page.find('altPageTypes')

    # Check if this page has been paginated as a cover page
    if (pageType.text == 'Cover') or (
        (altPageTypes != None) and (altPageTypes.find('altPageType').text == 'Cover')):
        has_illustration = False

    # Check if this page has been paginated as an index page
    if (pageType.text == 'Index') or (
        (altPageTypes != None) and (altPageTypes.find('altPageType').text == 'Index')):
        has_illustration = False

    # Add the basic page information
    page_data.append({
        'scan_id': args.scan,
        'leafNum': page.attrib['leafNum'],
        'ia_page_num': ia_page_num,
        'scandata_index': scandata_index,
        'has_illustration': {
            'alg_result': has_illustration
        }
    })

    ia_page_num += 1
    scandata_index += 1

if (args.v):
    print len(page_data), 'pages'


import compression
import contrast
import abbyy

# Fetch ABBYY file
if (args.v):
    print 'Fetching ABBYY...'
abbyy_file = urllib2.urlopen("http://archive.org/download/%(scan)s/%(file)s" % {'scan': args.scan, 'file': abbyy_filename})
abbyy_data = ET.fromstring(zlib.decompress(abbyy_file.read(), 15 + 32))
abbyy_pages = abbyy_data.findall('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page')

# Process each page
for page in page_data:

    url = 'http://www.archive.org/download/%s/page/n%s' % (page['scan_id'], page['ia_page_num'])
    img_file = StringIO(urllib2.urlopen(url).read())
    image = Image.open(img_file)

    print compression.processImage(img_file, image)
    print contrast.processImage(image, page['scan_id'], page['ia_page_num'])
    print abbyy.processABBYY(abbyy_pages[page['scandata_index']])

    break


# Process metadata

