import pymongo
import os
from cStringIO import StringIO
from PIL import Image
from urllib import urlopen
import logging
import urllib2
from xml.etree import cElementTree as ET


base_path = '/tmp/ia'
base_url = 'http://www.archive.org'
log = logging.getLogger('helper')
log.setLevel(logging.DEBUG)
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

    url = '%s/download/%s/page/n%s' % (base_url, book_id, ia_page_index)
    log.debug("fetching image: %s" % (url))
    img_file = StringIO(urlopen(url).read())
    image = Image.open(img_file)
    image.save(tmp_file)
    log.debug("saved image: %s" % (tmp_file))
    os.chmod(tmp_file, 0664)

    return image


def fetch_files(scan):

    if not os.path.exists(base_path):
        os.mkdir(base_path)
    if not os.path.exists('%s/scandata' % (base_path)):
        os.mkdir('%s/scandata' % (base_path))

    dest_dir = '%s/scandata/%s' % (base_path, scan)
    abbyy_file = '%s_abbyy.gz' % (scan)
    abbyy_file_uncompressed = '%s_abbyy' % (scan)
    scandata_file = '%s_scandata.xml' % (scan)

    abbyyLocalPath = '%(dir)s/%(file)s' % {
        'dir': dest_dir,
        'file': abbyy_file
    }

    abbyyLocalPathUncompressed = '%(dir)s/%(file)s' % {
        'dir': dest_dir,
        'file': abbyy_file_uncompressed
    }

    scanLocalPath = '%(dir)s/%(file)s' % {
        'dir': dest_dir,
        'file': scandata_file
    }

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    if not os.path.exists(abbyyLocalPath):
        try:
            url = '%(url)s/download/%(scan)s/%(file)s' % {
                'scan': scan,
                'file': abbyy_file,
                'url': base_url
            }
            f = urllib2.urlopen(url)
            with open(abbyyLocalPath, "wb") as local_file:
                local_file.write(f.read())
                os.chmod(local_file, 0664)
            f.close()
            helper.log.debug("abbyy file saved: %s" % (abbyyLocalPath))
        except urllib2.HTTPError, e:
            log.error("HTTP Error:", e.code, url)
        except urllib2.URLError, e:
            log.error("URL Error:", e.reason, url)

    if not os.path.exists(abbyyLocalPathUncompressed):
        abbyy = gzip.open(abbyyLocalPath)
        with open(abbyyLocalPathUncompressed) as local_file:
            local_file.write(abbyy.read())
            os.chmod(local_file, 0664)
        abbyy.close()
        helper.log.debug("abbyy file uncompressed: %s" % (abbyyLocalPathUncompressed))

    if not os.path.exists(scanLocalPath):
        try:
            url = '%(url)s/download/%(scan)s/%(file)s' % {
                'scan': scan,
                'file': scandata_file,
                'url': base_url
            }

            f = urllib2.urlopen(url)
            with open(scanLocalPath, "wb") as local_file:
                local_file.write(f.read())
                os.chmod(local_file, 0664)
            f.close()
            helper.log.debug("scandata file saved: %s" % (scanLocalPath))

        except urllib2.HTTPError, e:
            log.error("HTTP Error:", e.code, url)
            if (e.code == 404):
                url = '%(url)s/services/find_file.php?file=%(scan)s&loconly=1' % {
                    'scan': scan,
                    'url': base_url
                }
                try:
                    xmlFile = urllib2.urlopen(url).read()
                    location = ET.fromstring(xmlFile)
                    locationHost = location[0].attrib['host']
                    locationDir = location[0].attrib['dir']

                    url = 'http://%(host)s/zipview.php?zip=%(dir)s/scandata.zip&file=scandata.xml' % {
                        'host': locationHost,
                        'dir': locationDir
                    }
                    try:
                        f = urllib2.urlopen(url)
                        with open(scanLocalPath, "wb") as local_file:
                            local_file.write(f.read())
                            os.chmod(local_file, 0664)
                        f.close()
                    except urllib2.HTTPError, e:
                        log.error("HTTP Error:", e.code, url)
                    except urllib2.URLError, e:
                        log.error("URL Error:", e.reason, url)
                except urllib2.HTTPError, e:
                    log.error("HTTP Error:", e.code, url)
                except urllib2.URLError, e:
                    log.error("URL Error:", e.reason, url)
        except urllib2.URLError, e:
            log.error("URL Error:", e.reason, url)
