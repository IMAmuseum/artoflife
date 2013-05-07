import argparse
import os
import urllib2
from xml.etree import cElementTree as ET


def fetch_files(scan):

    dest_dir = 'scandata/%s' % (scan)
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
            url = 'http://archive.org/download/%(scan)s/%(file)s' % {
                'scan': scan,
                'file': abbyy_file
            }
            f = urllib2.urlopen(url)
            with open(abbyyLocalPath, "wb") as local_file:
                local_file.write(f.read())
        except urllib2.HTTPError, e:
            print "HTTP Error:", e.code, url
        except urllib2.URLError, e:
            print "URL Error:", e.reason, url

    if not os.path.exists(scanLocalPath):
        try:
            url = 'http://archive.org/download/%(scan)s/%(file)s' % {
                'scan': scan,
                'file': scandata_file
            }

            f = urllib2.urlopen(url)
            with open(scanLocalPath, "wb") as local_file:
                local_file.write(f.read())

        except urllib2.HTTPError, e:
            print "HTTP Error:", e.code, url
            if (e.code == 404):
                url = 'http://www.archive.org/services/find_file.php?file=%(scan)s&loconly=1' % {
                    'scan': scan
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
                    except urllib2.HTTPError, e:
                        print "HTTP Error:", e.code, url
                    except urllib2.URLError, e:
                        print "URL Error:", e.reason, url
                except urllib2.HTTPError, e:
                    print "HTTP Error:", e.code, url
                except urllib2.URLError, e:
                    print "URL Error:", e.reason, url
        except urllib2.URLError, e:
            print "URL Error:", e.reason, url

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description='fetch')
    ap.add_argument('scan', type=str, help='scan id')

    args = ap.parse_args()

    fetch_files(args.scan)
