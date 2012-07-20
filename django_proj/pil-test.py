from PIL import Image
import os, zipfile

scan_id = "novitatesconchol11pfei"
index = 10


def openFlippy(scan_id, index):

	scan_path = os.path.join('scandata', scan_id)
	#flippy_zip = zipfile.ZipFile(os.path.join(scan_path, scan_id + '_flippy.zip'))

	#file_name = '%04d.jpg' % (int(index))
	#print 'Extracting', file_name
	#image_data = flippy_zip.open(file_name)

	#print image_data

	image_file = os.path.join(scan_path, scan_id + '_flippy/%04d.jpg' % (int(index))) 
	im = Image.open(image_file)
	im.show()


def openJp2(scan_id, index):

	scan_path = os.path.join('scandata', scan_id)
	#jp2_zip = zipfile.ZipFile(os.path.join(scan_path, scan_id + '_jp2.zip'))

	#file_name = '%s_jp2/%s_%04d.jp2' % (scan_id, scan_id, int(index))
	#print 'Extracting', file_name
	#image_data = jp2_zip.open(file_name)


	image_file = os.path.join(scan_path, scan_id + '_jp2/%s_%04d.jp2' % (scan_id, int(index)))
	im = Image.open(image_file)

openJp2(scan_id, index)
#openFlippy(scan_id, index)