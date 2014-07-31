import os
from PIL import Image
import helper
import subprocess
import shutil
import sys
from time import time

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

def processImage(page, pageShift, pct_thresh=10):
    startTime = time()
    try:
        #ipdb.set_trace()
        # If we need to shift page number, we add one (pageShift contains 0 or 1)
        pageNum = page['ia_page_num'] + pageShift;

        helper.log.debug("contrast for scan_id: %s page_num: %s" % (page['scan_id'], pageNum))

        base_path = '%s/contrast' % (helper.base_path)

        if not os.path.exists(base_path):
            os.mkdir(base_path)
        if not os.path.exists('%s/%s' % (base_path, page['scan_id'])):
            os.mkdir('%s/%s' % (base_path, page['scan_id']))

        imgPath = '%s/%s/%s_jp2/%s_%s.jp2' % (helper.base_path, page['scan_id'], page['scan_id'], page['scan_id'], str(pageNum).zfill(4))
        working_file = '%s/%s/%s_contrast_%s.png' % (base_path, page['scan_id'], page['scan_id'], str(pageNum))

        processing_size = 500

        helper.log.debug('Converting Image')

        combinedConvert(
            imgPath,
            ['-colorspace', 'Gray', '-contrast', '-contrast', '-contrast', '-contrast', '-contrast', '-contrast', '-contrast', '-contrast', '-resize', '1x500!', '-sharpen', '0x5', '-negate', '-threshold', '0', '-negate'],
            working_file
        )

        convertTime = time() - startTime
        helper.log.debug('Contrast convert duration: %s' % (convertTime))

        processStartTime = time()

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

        processTime = time() - processStartTime
        helper.log.debug('Contrast Process duration: %s' % (processTime))

        info['max_contiguous'] = float(info['max_contiguous']) / processing_size

        if (info['max_contiguous'] > pct_thresh / 100.0):
            info['image_detected'] = True

        helper.log.debug("contrast complete for scan_id: %s page_num: %s" % (page['scan_id'], str(pageNum)))

        return info
    except Exception as e:
        helper.log.exception(e)
        helper.log.error("Unexpected error: %s", (sys.exc_info()[0]))
        helper.log.error("contrast error for scan_id: %s page_num: %s" % (page['scan_id'], str(pageNum)))
        return False
