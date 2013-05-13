import os, pymongo, zipfile
from cStringIO import StringIO
from time import clock
from urllib import urlopen
from PIL import Image


def combinePageData(scandata_pages, abbyy_pages, include_deleted=False):

    pages = []
    for i in range(0, len(scandata_pages)):
        if (not include_deleted) and (scandata_pages[i].find('addToAccessFormats').text == 'false'):
            continue
        pages.append({
            'scandata': scandata_pages[i],
            'abbyy': abbyy_pages[i]
        })

    return pages


def skipScanDataPage(scandata_page):
    """
    Determine whether a scandata page should be skipped
    """

    if scandata_page.find('addToAccessFormats').text == 'false':
        return True

    try:
        if (int(scandata_page.find('origHeight').text) == 0) and (int(scandata_page.find('origWidth').text) == 0):
            return True
    except:
        return False

    return False


def getIAImage(book_id, ia_page_index):

    tmp_file = 'tmp/ia/%s/%s.jpeg' % (book_id, ia_page_index)

    if not os.path.exists('tmp/ia'):
        os.mkdir('tmp/ia')
    if not os.path.exists('tmp/ia/%s' % (book_id)):
        os.mkdir('tmp/ia/%s' % (book_id))
    if os.path.isfile(tmp_file):
        print 'Loaded from', tmp_file
        return Image.open(tmp_file)

    t0 = clock()

    url = 'http://www.archive.org/download/%s/page/n%s' % (book_id, ia_page_index)
    print 'Fetching', url
    img_file = StringIO(urlopen(url).read())
    image = Image.open(img_file)
    image.save(tmp_file)

    print 'Fetched in', clock() - t0, 's'

    return image


def getJP2Image(book_id, ia_page_index):

    if not os.path.exists('tmp/jp2'):
        os.mkdir('tmp/jp2')

    zip_filename = 'scandata/%s/%s_jp2.zip' % (book_id, book_id)
    print 'Opening', zip_filename
    image_zip = zipfile.ZipFile(zip_filename)
    jp2_file = '%s_jp2/%s_%04d.jp2' % (book_id, book_id, ia_page_index)
    #image_zip.extract(jp2_file, 'tmp/jp2')

    return image_zip.open(jp2_file)


def scanIndexForIAIndex(ia_index, scandata_pages):
    index = 0
    for scan_index in range(0, len(scandata_pages)):
        if scandata_pages[scan_index].find('pageType').text == 'Delete':
            continue
        if int(index) == int(ia_index):
            return scan_index
        index += 1


def getMongoCollection(name):
    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife
    return mongo_db[name]
