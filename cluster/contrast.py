import os
from PIL import Image
import helper
import subprocess
import shutil
import sys

def combinedConvert(working_file, commands, output_file):
    cstack = ['/usr/bin/convert', working_file]
    for c in commands:
        cstack.append(c)
    cstack.append(output_file)
    p = subprocess.Popen(cstack)
    p.communicate()

def convert(working_file, commands):
    cstack = ['/usr/bin/convert', working_file]
    for c in commands:
        cstack.append(c)
    cstack.append(working_file)
    p = subprocess.Popen(cstack)
    p.communicate()

def convertToPng(jp2Path, pngPath):
    cstack = ['/usr/bin/convert', jp2Path, pngPath]
    p = subprocess.Popen(cstack)
    p.communicate()

def processImage(page, pct_thresh=10):
    try:
        #ipdb.set_trace()
        helper.log.debug("contrast for scan_id: %s page_num: %s" % (page['scan_id'], page['ia_page_num']))

        # img = helper.getIAImage(page['scan_id'], page['ia_page_num'])

        base_path = '%s/contrast' % (helper.base_path)

        if not os.path.exists(base_path):
            os.mkdir(base_path)
        if not os.path.exists('%s/%s' % (base_path, page['scan_id'])):
            os.mkdir('%s/%s' % (base_path, page['scan_id']))

        # imgPath = '%s/%s/%s.jpeg' % (helper.base_path, page['scan_id'], page['ia_page_num'])
        imgPath = '%s/%s/%s_jp2/%s_%s.jp2' % (helper.base_path, page['scan_id'], page['scan_id'], page['scan_id'], str(page['ia_page_num']).zfill(4))
        working_file = '%s/%s/%s_contrast_%s.png' % (base_path, page['scan_id'], page['scan_id'], page['ia_page_num'])
        #shutil.copyfile(imgPath, working_file)
        helper.log.debug('converting image to png: %s => %s' % (imgPath, working_file))

        # convertToPng(imgPath, working_file)

        #img.save(working_file)
        # desaturate
        # convert(working_file, ['-colorspace', 'Gray'])

        # apply heavy contrast
        # convert(working_file, ['-contrast', '-contrast', '-contrast', '-contrast', '-contrast', '-contrast', '-contrast', '-contrast'])

        processing_size = 500

        # resize to 1px width
        # convert(working_file, ['-resize', '1x%d!' % (processing_size)])

        # sharpen
        # convert(working_file, ['-sharpen', '0x5'])

        # convert to grayscale
        # convert(working_file, ['-negate', '-threshold', '0', '-negate'])

        combinedConvert(
            imgPath,
            ['-colorspace', 'Gray', '-contrast', '-contrast', '-contrast', '-contrast', '-contrast', '-contrast', '-contrast', '-contrast', '-resize', '1x500!', '-sharpen', '0x5', '-negate', '-threshold', '0', '-negate'],
            working_file
        )

        # identify long lines
        w_compressed = Image.open(working_file)
        info = {
            'max_contiguous': 0,
            'image_detected': False,
        }

        pixel_data = list(w_compressed.getdata())
        n_contig = 0
        for p in pixel_data:
            if p == 0:
                n_contig += 1
            else:
                info['max_contiguous'] = max(info['max_contiguous'], n_contig)
                n_contig = 0

        del w_compressed
        os.remove(working_file)

        info['max_contiguous'] = float(info['max_contiguous']) / processing_size

        if (info['max_contiguous'] > pct_thresh / 100.0):
            info['image_detected'] = True

        helper.log.debug("contrast complete for scan_id: %s page_num: %s" % (page['scan_id'], page['ia_page_num']))

        return info
    except Exception as e:
        helper.log.exception(e)
        helper.log.error("Unexpected error: %s", (sys.exc_info()[0]))
        helper.log.error("contrast error for scan_id: %s page_num: %s" % (page['scan_id'], page['ia_page_num']))
        return False
