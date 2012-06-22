from django.shortcuts import render_to_response
from django.core.files import storage
from django.http import HttpResponse, Http404

import os
import glob
import gzip
import zipfile
from xml.etree import cElementTree as ET


def scandata(request, scan_id=None):
    """
    Display a listing of scan datasets in "static/scandata"
    """
    sc = storage.get_storage_class()
    fs = sc()

    if scan_id is None:
        scandatasets = [os.path.basename(sd) for sd in glob.glob(fs.path('scandata') + '/*')]
        return render_to_response('scandata_index.html', {
            'scandatasets': scandatasets,
        })

    if not fs.exists('scandata/' + scan_id):
        raise Http404

    abbyy_file = fs.path('scandata/%s/%s_abbyy.gz' % (scan_id, scan_id))
    if not fs.exists('scandata/' + scan_id):
        raise Http404
    if not os.path.isfile(abbyy_file):
        raise Exception('Unable to find abbyy scan file: %s' % abbyy_file)

    abbyy = ET.parse(gzip.open(abbyy_file))
    pages = abbyy.findall('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page')

    return render_to_response('scandata.html', {
        'scan_id': scan_id,
        'abbyy': abbyy,
        'pages': pages,
    })

def picture_blocks(request, scan_id):
    """
    Display a list of scans that include ABBYY picture picture_blocks
    """
    sc = storage.get_storage_class()
    fs = sc()

    abbyy_file = fs.path('scandata/%s/%s_abbyy.gz' % (scan_id, scan_id))
    if not fs.exists('scandata/' + scan_id):
        raise Http404
    if not os.path.isfile(abbyy_file):
        raise Exception('Unable to find abbyy scan file: %s' % abbyy_file)

    print 'parsing abbyy'
    abbyy = ET.parse(gzip.open(abbyy_file))
    print 'finding pages'
    pages = abbyy.findall('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page')
    print 'found', len(pages), 'pages'
    picture_pages = []
    indices = []
    index = 0
    for page in pages:
        pblocks = page.findall("{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block[@blockType='Picture']")
        if len(pblocks) > 0:
            print len(pblocks)
            picture_pages.append(page)
            indices.append(index)
        index += 1
    print indices

    return render_to_response('jp2_list.html', {
        'scan_id': scan_id,
        'abbyy': abbyy,
        'jp2_indices': indices
    })    

def jp2_image(request, scan_id, index):
    """
    Return the raw contents of a scanned image
    """
    # load the zip file containing the images
    sc = storage.get_storage_class()
    fs = sc()

    zip_filename = fs.path('scandata/%s/%s_jp2.zip' % (scan_id, scan_id))
    print 'Opening', zip_filename
    image_zip = zipfile.ZipFile(zip_filename)

    file_name = '%s_jp2/%s_%04d.jp2' % (scan_id, scan_id, int(index))
    print 'Extracting', file_name
    image_data = image_zip.open(file_name)

    response = HttpResponse(image_data, content_type="image/jp2")
    return response


def flippy_image(request, scan_id, index):
    """
    Return the raw contents of a scanned image (small version)
    """
    # load the zip file containing the images
    sc = storage.get_storage_class()
    fs = sc()

    try:
        image_zip = zipfile.ZipFile(fs.path('scandata/%s/%s_flippy.zip' % (scan_id, scan_id)))
    except IOError:
        return HttpResponse('No flippy zip file')

    file_name = '%04d.jpg' % (int(index) + 1,)
    print 'Extracting', file_name
    image_data = image_zip.open(file_name)

    response = HttpResponse(image_data, content_type="image/jpg")
    return response
