import os
from cStringIO import StringIO
from time import clock
from urllib import urlopen
from PIL import Image


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


def combinePageData(scandata_pages, abbyy_pages, include_deleted=False):

    pages = []
    for i in range(0, len(scandata_pages)):
        if (not include_deleted) and (scandata_pages[i].find('pageType').text == 'Delete'):
            continue
        pages.append({
            'scandata': scandata_pages[i],
            'abbyy': abbyy_pages[i]
        })

    return pages
