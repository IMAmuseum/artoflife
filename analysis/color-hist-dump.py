import tarfile, zipfile
from time import clock
from wand.image import Image as wImage
from PIL import Image as pImage 
from cStringIO import StringIO
import colorsys
import matplotlib.pyplot as plt


def getJP2asPIL(book_id, ia_page_index, scale=0.5):

    tar_filename = 'scandata/%s/%s_jp2.tar' % (book_id, book_id)
    tar_file = tarfile.open(tar_filename)

    jp2_file = '%s_jp2/%s_%04d.jp2' % (book_id, book_id, int(ia_page_index)+1)
    jp2_info = tar_file.getmember(jp2_file)
    jp2_data = tar_file.extractfile(jp2_file)

    # Use Wand to read jp2, then pass to PIL as png
    w_image = wImage(blob=jp2_data)
    w_image.resize(int(w_image.width*scale), int(w_image.height*scale))

    image = pImage.open(StringIO(w_image.make_blob('png')))
    del w_image

    return image


def hueHistogram(image):

    data = image.getdata()
    hues = []
    for d in data:
        hsv = colorsys.rgb_to_hsv(d[0]/255.0,d[1]/255.0,d[2]/255.0)
        hues.append(hsv[0])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    n, bins, patches = ax.hist(hues, 100, facecolor='green', alpha=0.75)

    ax.set_xlabel('Hue')
    ax.set_ylabel('Occurrences')
    ax.grid(True)

    return plt


def satHistogram(image):

    data = image.getdata()
    hues = []
    for d in data:
        hsv = colorsys.rgb_to_hsv(d[0]/255.0,d[1]/255.0,d[2]/255.0)
        hues.append(hsv[1])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    n, bins, patches = ax.hist(hues, 100, facecolor='green', alpha=0.75)

    ax.set_xlabel('Saturation')
    ax.set_ylabel('Occurrences')
    ax.grid(True)

    return plt

scan_id = 'mobot31753002719497'

for p in range(0,20):
	image = getJP2asPIL(scan_id, p)
	h = satHistogram(image)
	plt.savefig("tmp/sat/sat-%s-%04d.jpg" % (scan_id, p))


