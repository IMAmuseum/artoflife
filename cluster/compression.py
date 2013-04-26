import helper


def processImage(page):

    try:
        helper.log.debug("compression for scan_id: %s" % (page['scan_id']))

        image = helper.getIAImage(page['scan_id'], page['ia_page_num'])

        mode_to_bpp = {'1': 1, 'L': 8, 'P': 8, 'RGB': 24, 'RGBA': 32, 'CMYK': 32, 'YCbCr': 24, 'I': 32, 'F': 32}

        area = image.size[0] * image.size[1]

        filesize = image.tell()

        helper.log.debug("compression complete for scan_id: %s" % (page['scan_id']))

        return {
            'file_size': filesize,
            'bytes_per_pixel': float(filesize) / area,
            'pixel_depth': mode_to_bpp[image.mode],
            'compression': float(filesize) * 8 / (area * mode_to_bpp[image.mode])
        }
    except:
        helper.log.error("compression error scan_id: %s" % (page['scan_id']))
        return False
