
from os import SEEK_END

def processImage(image_file, image):

    image_file.seek(0, SEEK_END)
   
    mode_to_bpp = {'1':1, 'L':8, 'P':8, 'RGB':24, 'RGBA':32, 'CMYK':32, 'YCbCr':24, 'I':32, 'F':32}

    area = image.size[0] * image.size[1]

    filesize = image_file.tell()

    return {
        'file_size': filesize,
        'bytes_per_pixel': float(filesize) / area,
        'pixel_depth': mode_to_bpp[image.mode],
        'compression': float(filesize) * 8 / (area * mode_to_bpp[image.mode])
    }


