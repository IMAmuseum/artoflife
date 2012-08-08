import argparse
import os

ap = argparse.ArgumentParser(description='fetch')
ap.add_argument('scan', type=str, help='scan id')

args = ap.parse_args()


def fetch_files(scan):

    dest_dir = 'scandata/%s' % (scan)
    abbyy_file = '%s_abbyy.gz' % (scan)
    scandata_file = '%s_scandata.xml' % (scan)

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    if not os.path.exists(dest_dir + '/' + abbyy_file):
        os.system('wget http://archive.org/download/%(scan)s/%(file)s -O %(dir)s/%(file)s' % {
            'scan': scan,
            'dir': dest_dir,
            'file': abbyy_file
        })
    if not os.path.exists(dest_dir + '/' + scandata_file):
        os.system('wget http://archive.org/download/%(scan)s/%(file)s -O %(dir)s/%(file)s' % {
            'scan': scan,
            'dir': dest_dir,
            'file': scandata_file
        })

fetch_files(args.scan)
