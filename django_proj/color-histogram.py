import tarfile, zipfile
from time import clock
from wand.image import Image as wImage
from PIL import Image as pImage 
from cStringIO import StringIO


def getJP2asPIL(book_id, ia_page_index):

    t0 = clock()

    tar_filename = 'scandata/%s/%s_jp2.tar' % (book_id, book_id)
    tar_file = tarfile.open(tar_filename)

    jp2_file = '%s_jp2/%s_%04d.jp2' % (book_id, book_id, int(ia_page_index)+1)
    jp2_info = tar_file.getmember(jp2_file)
    jp2_data = tar_file.extractfile(jp2_file)

    # Use Wand to read jp2, then pass to PIL as png
    w_image = wImage(blob=jp2_data)
    t1 = clock()
    image = pImage.open(StringIO(w_image.make_blob('png')))
    del w_image

    print 'Image load:', t1-t0, clock()-t1

    return image

def plotPILHistogram(image):

    hist = image.histogram()

    import matplotlib.pyplot as plt
    from numpy import arange
    ind = arange(len(hist))

    p1 = plt.bar(ind, hist)

    plt.show()


def plotHueHistogram(image):

    t0 = clock()

    import colorsys

    data = image.getdata()
    hues = []
    for d in data:
        hsv = colorsys.rgb_to_hsv(d[0]/255.0,d[1]/255.0,d[2]/255.0)
        hues.append(hsv[0])

    print 'HSV computed in', clock()-t0

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111)

    n, bins, patches = ax.hist(hues, 100, facecolor='green', alpha=0.75)
    #bincenters = 0.5*(bins[1:]+bins[:-1])

    ax.set_xlabel('Hue')
    ax.set_ylabel('Occurrences')
    #ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
    #ax.set_xlim(0, 120)
    ax.grid(True)

    plt.show()


if __name__ == '__main__':

    import argparse

    ap = argparse.ArgumentParser(description='picture block processing')
    ap.add_argument('scan', type=str, help='scan id', default='mobot31753002719497')
    ap.add_argument('page', type=int, help='page #', default='2')

    args = ap.parse_args()

    image = getJP2asPIL(args.scan, args.page)
    image.save('color.png')

    #plotPILHistogram(image)
    plotHueHistogram(image)


