import tarfile, zipfile
from time import clock
from wand.image import Image as wImage
from PIL import Image as pImage 
from cStringIO import StringIO

book_id = 'mobot31753000121308'
ia_page_index = 100

t0 = clock()

tar_filename = 'scandata/%s/%s_jp2.tar' % (book_id, book_id)
tar_file = tarfile.open(tar_filename)

jp2_file = '%s_jp2/%s_%04d.jp2' % (book_id, book_id, ia_page_index)
jp2_info = tar_file.getmember(jp2_file)
jp2_data = tar_file.extractfile(jp2_file)

# Use Wand to read jp2, then pass to PIL as png
w_image = wImage(blob=jp2_data)
t1 = clock()
image = pImage.open(StringIO(w_image.make_blob('png')))

print 'Loaded image in', clock()-t0, 's', t1-t0

raw_size = w_image.width*w_image.height*w_image.depth*3/8


info = {
	'width': w_image.width,
	'height': w_image.height,
	'depth': w_image.depth,
	'file_size': jp2_info.size,
	'raw_size': raw_size,
	'size_ratio': jp2_info.size / float(raw_size)
}

print info


#image_zip.close()
#del page_img