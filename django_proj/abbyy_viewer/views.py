from django.shortcuts import render_to_response
from django.core.files import storage
from django.http import HttpResponse, Http404

import glob, gzip, os, subprocess, zipfile

from PIL import Image, ImageDraw
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

def picture_block_index(request, scan_id):
    """
    Display a list of scans that include ABBYY picture picture_blocks
    """
    print "Picture block index"
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
            picture_pages.append(page)
            indices.append(index)
            generate_picture_blocks(scan_id, index, 'png', pblocks)
        index += 1
    print 'Pages with picture blocks:', indices

    return render_to_response('picture_blocks.html', {
        'scan_id': scan_id,
        'abbyy': abbyy,
        'indices': indices
    })


def generate_picture_blocks(scan_id, index, ext='png', pblocks=[]):
    """
    Display a scan with a picture blocks overlay
    """
    print "Picture blocks for", index
    sc = storage.get_storage_class()
    fs = sc()

    img_file = 'tmp/%s_jp2/%s_%04d.%s' % (scan_id, scan_id, int(index), ext)
    if fs.exists(img_file):
        return fs.path(img_file)

    zip_filename = fs.path('scandata/%s/%s_jp2.zip' % (scan_id, scan_id))
    print 'Opening', zip_filename
    image_zip = zipfile.ZipFile(zip_filename)

    file_name = '%s_jp2/%s_%04d.jp2' % (scan_id, scan_id, int(index))
    print 'Extracting', file_name
    image_zip.extract(file_name, fs.path('tmp'))

    print 'Converting to', img_file

    subprocess.check_call([
        "j2k_to_image",
        '-i', os.path.join(fs.path('tmp'), file_name),
        '-o', fs.path(img_file)
    ])

    img = Image.open(fs.path(img_file))

    # Do processing
    size = img.size
    print size

    scale = 0.2
    small = img.resize([int(size[0]*scale), int(size[1]*scale)])

    draw = ImageDraw.Draw(small)
    for block in pblocks:
        print block.attrib
        draw.rectangle(
            [
                (float(block.attrib['l'])*scale, float(block.attrib['t'])*scale),
                (float(block.attrib['r'])*scale, float(block.attrib['b'])*scale)
            ],
            outline=(0,255,0)
        )
    del draw

    small.save(fs.path(img_file))
    del img

    os.remove(os.path.join(fs.path('tmp'), file_name))

    return fs.path(img_file)


def picture_blocks(request, scan_id, index, ext='png'):

    img_file = generate_picture_blocks(scan_id, index, ext)

    return HttpResponse(open(img_file), content_type='image/' + ext)


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
