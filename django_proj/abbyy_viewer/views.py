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


def jp2_image(request, scan_id, index):
    """
    Return the raw contents of a scanned image
    """
    # load the zip file containing the images
    sc = storage.get_storage_class()
    fs = sc()

    image_zip = zipfile.ZipFile(fs.path('scandata/%s/%s_jp2.zip' % (scan_id, scan_id)))
    image_data = image_zip.open('%s_%04d.jp2' % (scan_id, index))

    response = HttpResponse(image_data, content_type="image/jp2")
    return response


def flippy_image(request, scan_id, index):
    """
    Return the raw contents of a scanned image (small version)
    """
    # load the zip file containing the images
    sc = storage.get_storage_class()
    fs = sc()

    image_zip = zipfile.ZipFile(fs.path('scandata/%s/%s_flippy.zip' % (scan_id, scan_id)))
    image_data = image_zip.open('%04d.jp2' % (index + 1,))

    response = HttpResponse(image_data, content_type="image/jp2")
    return response
