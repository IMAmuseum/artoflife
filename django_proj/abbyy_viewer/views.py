from django.shortcuts import render_to_response
from django.core.files import storage
from django.http import HttpResponse, Http404

import glob, gzip, os, subprocess, zipfile

from PIL import Image, ImageDraw
from xml.etree import cElementTree as ET

import pictureblocks
from helpers import scanIndexForIAIndex


def loadXml(scan_id):

    sc = storage.get_storage_class()
    fs = sc()

    # Check resources
    abbyy_file = fs.path('scandata/%s/%s_abbyy.gz' % (scan_id, scan_id))
    scandata_file = fs.path('scandata/%s/%s_scandata.xml' % (scan_id, scan_id))
    if not fs.exists('scandata/' + scan_id):
        raise Http404
    if not os.path.isfile(abbyy_file):
        raise Exception('Unable to find abbyy scan file: %s' % abbyy_file)
    if not os.path.isfile(scandata_file):
        raise Exception('Unable to find scandata file: %s' % scandata_file)

    return {
        'abbyy': ET.parse(gzip.open(abbyy_file)),
        'scandata': ET.parse(scandata_file)
    }


def scandata(request, scan_id=None):
    """
    Display a listing of scan datasets in "static/scandata"
    """

    xml_data = loadXml(scan_id)
    pages = xml_data['abbyy'].findall('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page')

    return render_to_response('scandata.html', {
        'scan_id': scan_id,
        'abbyy': xml_data['abbyy'],
        'pages': pages,
    })


def picture_block_index(request, scan_id):
    """
    Display a list of scans that include ABBYY picture picture_blocks
    """
    print "Picture block index"

    xml_data = loadXml(scan_id)

    scandata_pages = xml_data['scandata'].find('pageData').findall('page')
    print 'found', len(scandata_pages), 'in scan data'

    print 'parsing abbyy'
    abbyy_pages = xml_data['abbyy'].findall('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page')
    print 'found', len(abbyy_pages), 'pages'

    picture_pages = []
    indices = []

    scan_index = 0
    ia_index = 0
    for page in scandata_pages:

        # Skip 'delete' pages
        if page.find('pageType').text == 'Delete':
            scan_index += 1
            continue

        # Are there picture blocks on this page?
        pblocks = abbyy_pages[scan_index].findall("{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block[@blockType='Picture']")
        if len(pblocks) > 0:
            picture_pages.append(abbyy_pages[scan_index])
            indices.append(ia_index)

        ia_index += 1
        scan_index += 1

    print 'Pages with picture blocks:', indices

    return render_to_response('picture_blocks.html', {
        'scan_id': scan_id,
        'abbyy': xml_data['abbyy'],
        'indices': indices
    })


def picture_blocks(request, scan_id, index, ext='png'):
    """
    index should be the IA page index
    """

    xml_data = loadXml(scan_id)
    scandata_pages = xml_data['scandata'].find('pageData').findall('page')
    abbyy_pages = xml_data['abbyy'].findall('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page')

    print 'index', index
    scan_index = scanIndexForIAIndex(index, scandata_pages)
    blocks = abbyy_pages[scan_index].findall("{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block[@blockType='Picture']")

    img_file = pictureblocks.renderBlocks(scan_id, index, blocks)
    return HttpResponse(open(img_file), content_type='image/' + ext)


def picture_blocks_analysis(request, scan_id):
    """
    Initial implementation: Render output from a prior run
    """

    import csv

    sc = storage.get_storage_class()
    fs = sc()

    log_filepath = fs.path('output/pictureblocks/%s-pictureblocks.csv' % (scan_id))
    control_filepath = fs.path('BHLIllustrations.csv')

    #print 'Log file:', log_filepath
    #print 'Control file:', control_filepath

    if not fs.exists(log_filepath) or not fs.exists(control_filepath):
        raise Http404

    log_file = open(log_filepath, 'rU')
    control_file = open(control_filepath, 'rU')

    log_reader = csv.reader(log_file)
    control_reader = csv.reader(control_file)

    log_reader.next()
    control_reader.next()

    for control_row in control_reader:
        if control_row[0] == scan_id:
            break

    n = 0
    pages = []
    counts = {
        'tp': 0, 'fp': 0, 'tn': 0, 'fn': 0        
    }
    for log_row in log_reader:

        page = {
            'number': log_row[0],
            'detected': (log_row[1] == 'True'),
            'result' : None,
            'processing_time_ms': "{0:0.5f}".format(float(log_row[2]) * 1000),
            'n_blocks': log_row[3],
            'coverage': "{0:0.3f}".format(float(log_row[4]))
        }

        if (log_row[1] == 'True'):

            if control_row[6] == 'Yes':            
                page['result'] = 'true-positive'
                counts['tp'] += 1
            else:
                page['result'] = 'false-positive'
                counts['fp'] += 1

        else:

            if control_row[6] == 'Yes':
                page['result'] = 'false-negative'
                counts['fn'] += 1
            else:
                page['result'] = 'true-negative'
                counts['tn'] += 1
        
        n += 1

        if (page['result'] != 'true-negative'):
            pages.append(page)

        control_row = control_reader.next()            

    log_file.close()
    control_file.close()

    return render_to_response('picture_blocks_analysis.html', {
        'scan_id': scan_id,
        'n_pages': n,
        'pages': pages,
        'precision': "{0:0.3f}".format(float(counts['tp']) / (counts['tp'] + counts['fp'])),
        'recall': "{0:0.3f}".format(float(counts['tp']) / (counts['tp'] + counts['fn']))
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
