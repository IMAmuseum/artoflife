import pymongo
import os
from cStringIO import StringIO
from PIL import Image
from urllib import urlopen
from urllib import urlretrieve
import logging
import urllib2
import shutil
import requests
import zipfile
from xml.etree import cElementTree as ET


base_path = '/home/kjaebker/tmp'
base_url = 'http://www.archive.org'
log = logging.getLogger('helper')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
onCluster = False


def mongoConnect():
    log.debug("connecting to mongo")
    mongo_conn = pymongo.Connection('localhost', 12456)
    mongo_db = mongo_conn.artoflife
    log.debug("mongo connection established")
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
    #img_file = StringIO(urlopen(url).read())
    #image = Image.open(img_file)
    #image.save(tmp_file)
    urlretrieve(url, tmp_file);

    log.debug("saved image: %s" % (tmp_file))
    os.chmod(tmp_file, 0664)

    return Image.open(tmp_file)


def removeIAImages(book_id):

    tmp_path = '%s/%s' % (base_path, book_id);
    shutil.rmtree(tmp_path);

    tmp_path = '%s/scandata/%s' % (base_path, book_id);
    shutil.rmtree(tmp_path);

    tmp_path = '%s/contrast/%s' % (base_path, book_id);
    shutil.rmtree(tmp_path);


def fetch_files(scan):

    if not os.path.exists(base_path):
        os.mkdir(base_path)
    if not os.path.exists('%s/scandata' % (base_path)):
        os.mkdir('%s/scandata' % (base_path))

    dest_dir = '%s/scandata/%s' % (base_path, scan)
    abbyy_file = '%s_abbyy.gz' % (scan)
    scandata_file = '%s_scandata.xml' % (scan)

    abbyyLocalPath = '%(dir)s/%(file)s' % {
        'dir': dest_dir,
        'file': abbyy_file
    }

    scanLocalPath = '%(dir)s/%(file)s' % {
        'dir': dest_dir,
        'file': scandata_file
    }

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    if not os.path.exists(abbyyLocalPath):
        try:
            if (onCluster == False):
                url = '%(url)s/download/%(scan)s/%(file)s' % {
                    'scan': scan,
                    'file': abbyy_file,
                    'url': base_url
                }
            else:
                url = '%(url)s/download/%(scan_first)s/%(scan)s/%(file)s' % {
                    'scan': scan,
                    'scan_first': scan[0],
                    'file': abbyy_file,
                    'url': base_url
                }
            f = urllib2.urlopen(url)
            with open(abbyyLocalPath, "wb") as local_file:
                local_file.write(f.read())
            os.chmod(abbyyLocalPath, 0664)
            f.close()
            log.debug("abbyy file saved: %s" % (abbyyLocalPath))
        except urllib2.HTTPError, e:
            log.error("HTTP Error: %s:%s", e.code, url)
        except urllib2.URLError, e:
            log.error("URL Error %s:%s:", e.reason, url)

    if not os.path.exists(scanLocalPath):
        try:
            if (onCluster == False):
                url = '%(url)s/download/%(scan)s/%(file)s' % {
                    'scan': scan,
                    'file': scandata_file,
                    'url': base_url
                }
            else:
                url = '%(url)s/download/%(scan_first)s/%(scan)s/%(file)s' % {
                    'scan': scan,
                    'scan_first': scan[0],
                    'file': scandata_file,
                    'url': base_url
                }

            f = urllib2.urlopen(url)
            with open(scanLocalPath, "wb") as local_file:
                local_file.write(f.read())
            os.chmod(scanLocalPath, 0664)
            f.close()
            log.debug("scandata file saved: %s", scanLocalPath)

        except urllib2.HTTPError, e:
            log.error("HTTP Error: %d %s", e.code, url)
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
                        os.chmod(scanLocalPath, 0664)
                        f.close()
                    except urllib2.HTTPError, e:
                        log.error("HTTP Error: %d %s", e.code, url)
                    except urllib2.URLError, e:
                        log.error("URL Error: %s %s", e.reason, url)
                except urllib2.HTTPError, e:
                    log.error("HTTP Error: %d %s", e.code, url)
                except urllib2.URLError, e:
                    log.error("URL Error: %s %s", e.reason, url)
        except urllib2.URLError, e:
            log.error("URL Error: %s %s", e.reason, url)
        except IOError, e:
            log.error("IO Error: File not found? %s", url)


def fetchAllImages(book_id):
    metaUrl = '%(url)s/metadata/%(bookid)s/files' % {
        'url': base_url,
        'bookid': book_id
    }

    r = requests.get(url = metaUrl)
    imagePackageFilename = None

    if (r.status_code == 200):
        data = r.json()
        for fileMeta in data['result']:
            if fileMeta['format'] == "Single Page Processed JP2 ZIP":
                imagePackageFilename = fileMeta['name']
    else:
        log.error("Error getting book metadata file %d %s", r.status_code, metaUrl)

    if imagePackageFilename is None:
        log.error("No Image Package File Name Found: %s", book_id)
        return None

    imageUrl = '%(url)s/download/%(bookid)s/%(filename)s' % {
        'url': base_url,
        'bookid': book_id,
        'filename': imagePackageFilename
    }

    tmp_file = '%s/%s/%s' % (base_path, book_id, imagePackageFilename)

    if not os.path.exists(base_path):
        os.mkdir(base_path)
    if not os.path.exists('%s/%s' % (base_path, book_id)):
        os.mkdir('%s/%s' % (base_path, book_id))
    if os.path.isfile(tmp_file):
        log.debug("loading package: %s" % (tmp_file))

    log.debug("fetching image package: %s" % (imageUrl))
    urlretrieve(imageUrl, tmp_file);

    log.debug("saved image package: %s" % (tmp_file))
    os.chmod(tmp_file, 0664)

    tempLocation = '%s/%s/' % (base_path, book_id)

    try:
        zfile = zipfile.ZipFile(tmp_file)
        log.debug("extracting images")
        zfile.extractall(tempLocation)
        zfile.close()
    except:
        log.error("error extracting images: %s", tmp_file)
        return False

    return True
