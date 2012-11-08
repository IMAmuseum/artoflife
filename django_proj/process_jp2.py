import tarfile, zipfile
from time import clock
from wand.image import Image as wImage
from PIL import Image as pImage 
from cStringIO import StringIO

from contrast import processImage as processContrast

mode_to_bpp = {
    '1': 1,
    'L': 8,
    'P': 8,
    'RGB': 24,
    'RGBA': 32,
    'CMYK': 32,
    'YCbCr': 24,
    'I': 32,
    'F': 32
}


def processPage(book_id, page_id):

    t0 = clock()

    tar_filename = 'scandata/%s/%s_jp2.tar' % (book_id, book_id)
    tar_file = tarfile.open(tar_filename)

    jp2_file = '%s_jp2/%s_%04d.jp2' % (book_id, book_id, ia_page_index)
    jp2_info = tar_file.getmember(jp2_file)
    jp2_data = tar_file.extractfile(jp2_file)

    scale = 0.5

    # Use Wand to read jp2, then pass to PIL as png
    w_image = wImage(blob=jp2_data)
    #w_image.resize(int(w_image.width*scale), int(w_image.height*scale)) # Improve performance?
    image = pImage.open(StringIO(w_image.make_blob('png')))

    t1 = clock()
    print 'Loaded image in', t1 - t0, 's'

    # Compression analysis
    raw_size = image.size[0] * image.size[1] * mode_to_bpp[image.mode] / 8
    compression = float(jp2_info.size) / raw_size

    # Contrast analysis
    contrast_info = processContrast(image, book_id, page_id)

    print 'Processed in', clock() - t1, 's'

    info = {
        'width': w_image.width,
        'height': w_image.height,
        'depth': w_image.depth,
        'file_size': jp2_info.size,
        'raw_size': raw_size,
        'compression_ratio': compression
    }

    print info
    print contrast_info

    del image
    del w_image


book_id = 'mobot31753000121308'
ia_page_index = 100

processPage(book_id, ia_page_index)
