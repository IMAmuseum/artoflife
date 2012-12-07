import os
from PIL import Image

def convert(working_file, command):
    os.system('convert ' + working_file + ' ' + command + ' ' + working_file)

def processImage(img, scan_id, ia_page_index, pct_thresh=10):

    if not os.path.exists('tmp/contrast'):
        os.mkdir('tmp/contrast')
    if not os.path.exists('tmp/contrast/%s' % (scan_id)):
        os.mkdir('tmp/contrast/%s' % (scan_id))

    working_file = 'tmp/contrast/%s/%s_contrast_%s.png' % (scan_id, scan_id, ia_page_index)

    img.save(working_file)

    # desaturate
    convert(working_file, '-colorspace Gray')

    # apply heavy contrast
    convert(working_file, '-contrast -contrast -contrast -contrast -contrast -contrast -contrast -contrast')

    processing_size = 500

    # resize to 1px width
    convert(working_file, '-resize 1x%d!' % (processing_size))

    # sharpen
    convert(working_file, '-sharpen 0x5')

    # convert to grayscale
    convert(working_file, '-negate -threshold 0 -negate')

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

    return info
