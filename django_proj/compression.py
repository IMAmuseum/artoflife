import os
from helpers import getIAImage


def processPage(scan_id, ia_page_index):

    img = getIAImage(scan_id, ia_page_index)
    filesize = os.path.getsize('tmp/ia/%s/%s.jpeg' % (scan_id, ia_page_index))
    print 'size:', filesize

    return {
        'compression': float(filesize) / (img.size[0] * img.size[1])
    }
