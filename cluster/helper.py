import pymongo
import os
from cStringIO import StringIO
from PIL import Image
from urllib import urlopen
import logging


base_path = '/tmp/ia'
base_url = 'http://www.archive.org/download'
log = logging.getLogger('helper')
log.setLevel(logging.ERROR)
log.addHandler(logging.StreamHandler())


def mongoConnect():
    log.debug("connecting to mongo")
    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife
    return mongo_db.page_data


def getIAImage(book_id, ia_page_index):

    tmp_file = '%s/%s/%s.jpeg' % (base_path, book_id, ia_page_index)

    if not os.path.exists(base_path):
        os.mkdir(base_path)
    if not os.path.exists('%s/%s' % (base_path, book_id)):
        os.mkdir('%s/%s' % (base_path, book_id))
    if os.path.isfile(tmp_file):
        log.debug("loading image: %s" % (tmp_file))
        return Image.open(tmp_file)

    url = '%s/%s/page/n%s' % (base_url, book_id, ia_page_index)
    log.debug("fetching image: %s" % (url))
    img_file = StringIO(urlopen(url).read())
    image = Image.open(img_file)
    image.save(tmp_file)

    return image


def fetch_files(scan):

    if not os.path.exists(base_path):
        os.mkdir(base_path)
    if not os.path.exists('%s/scandata' % (base_path)):
        os.mkdir('%s/scandata' % (base_path))

    dest_dir = '%s/scandata/%s' % (base_path, scan)
    abbyy_file = '%s_abbyy.gz' % (scan)
    scandata_file = '%s_scandata.xml' % (scan)

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    if not os.path.exists(dest_dir + '/' + abbyy_file):
        log.debug("fetching abbyy file")
        os.system('wget %(url)s/%(scan)s/%(file)s -O %(dir)s/%(file)s' % {
            'scan': scan,
            'dir': dest_dir,
            'file': abbyy_file,
            'url': base_url
        })
    if not os.path.exists(dest_dir + '/' + scandata_file):
        log.debug("fetching scandata file")
        os.system('wget %(url)s/%(scan)s/%(file)s -O %(dir)s/%(file)s' % {
            'scan': scan,
            'dir': dest_dir,
            'file': scandata_file,
            'url': base_url
        })
