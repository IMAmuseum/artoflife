import argparse
import os

ap = argparse.ArgumentParser(description='fetch')
ap.add_argument('scan', type=str, help='scan id')

args = ap.parse_args()

dest_dir = 'scandata/%s' % (args.scan)
jp2_file = '%s_jp2.tar' % (args.scan)

if not os.path.exists(dest_dir):
    os.mkdir(dest_dir)
if not os.path.exists(dest_dir + '/' + jp2_file):
    os.system('wget http://archive.org/download/%(scan)s/%(file)s -O %(dir)s/%(file)s' % {
        'scan': args.scan,
        'dir': dest_dir,
        'file': jp2_file
    })
