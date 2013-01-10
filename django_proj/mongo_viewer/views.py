from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from helpers import getMongoCollection
from analysis import analyzePage, analyzePages, classifyResult
from time import clock


def main(request):

    collection = getMongoCollection('page_data')

    t = clock()
    total_pages = 0

    scan_info = []
    for scan in sorted(collection.distinct('scan_id')):
        pages = collection.find({'scan_id': scan})
        scan_info.append({
            'scan_id': scan,
            'n_pages': pages.count()
        })
        total_pages += pages.count()

    build_time = clock() - t
    full_build_est = build_time * 40000000 / total_pages

    return render_to_response('main.html', {
        'scans': scan_info,
        'build_time': build_time,
        'total_pages': total_pages,
        'full_build_est': full_build_est
    })


def scan(request, scan_id):

    collection = getMongoCollection('page_data')

    print scan_id
    pages = collection.find({'scan_id': scan_id}).sort('scandata_index', 1)
    print pages.count()

    analysis = analyzePages(pages)

    page_content = []
    for page in analysis['pages']:
        page_content.append(render_to_string('page.html', {
            'scan_id': scan_id,
            'page': page
        }))

    return render_to_response('scan.html', {
        'scan_id': scan_id,
        'pages': page_content,
        'n_illustrations': analysis['n_illustrations'],
        'abbyy': analysis['abbyy'],
        'contrast': analysis['contrast'],
        'color': analysis['color']
    })


def page(request, scan_id, page_id):

    collection = getMongoCollection('page_data')
    page = collection.find_one({'scan_id': scan_id, 'ia_page_num': int(page_id)})
    analyzePage(page)
    return render_to_response('page.html', {
        'scan_id': scan_id,
        'page': page
    })


def pageWithPictureBlocks(request, scan_id, page_id):

    return render_to_response('page_with_blocks.html', {
        'scan_id': scan_id,
        'page_id': page_id
    })


def pictureBlocksAsSVG(request, scan_id, page_id):
    """
    Render the picture blocks for a page as an SVG image
    """

    # Fetch the page from mongodb
    collection = getMongoCollection('page_data')
    page = collection.find_one({'scan_id': scan_id, 'ia_page_num': int(page_id)})

    # Allow stroke width as a URL parameter
    stroke_width = request.GET.get('sw')
    if stroke_width is None:
        stroke_width = '0.25%'

    # Convert block data to x,y,w,h
    rects = []
    if 'abbyy' in page:
        if 'picture_blocks' in page['abbyy']:
            for block in page['abbyy']['picture_blocks']:
                rects.append({
                    'x': block['l'],
                    'y': block['t'],
                    'w': block['r'] - block['l'],
                    'h': block['b'] - block['t']
                })

    # Render the response
    return HttpResponse(render_to_response('picture_blocks.svg', {
        'height': page['abbyy']['height'],
        'width': page['abbyy']['width'],
        'rects': rects,
        'stroke_width': stroke_width
    }), content_type='image/svg+xml')


def coverageHistogram(request):

    collection = getMongoCollection('page_data')

    data = []
    for page in collection.find({}):
        if ('coverage_sum' in page['abbyy']):
            data.append(page['abbyy']['coverage_sum'])

    return createHistogram(data, 'Sum of Picture Block Coverage')


def compressionHistogram(request):

    collection = getMongoCollection('page_data')

    data = []
    for page in collection.find({}):
        if ('compression' in page):
            data.append(page['compression'])

    return createHistogram(data, 'Compression Ratio')


def createHistogram(data, label):

    import StringIO
    from analysis import generateHistogram
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    hist = generateHistogram(data, label)
    canvas = FigureCanvas(hist)
    print 'got canvas'

    png_output = StringIO.StringIO()
    canvas.print_png(png_output)

    # Django's HttpResponse reads the buffer and extracts the image
    return HttpResponse(png_output.getvalue(), mimetype='image/png')


def thumbImage(request, scan_id, index):
    return renderIAImage(request, scan_id, index, 'small')


def renderIAImage(request, scan_id, index, size=None):

    import os
    from urllib2 import urlopen

    path = 'tmp/ia'
    if size is not None and size in ('small'):
        path = 'tmp/ia-' + size

    cache_file = '%s/%s/%s.jpeg' % (path, scan_id, index)

    if not os.path.exists(path):
        os.mkdir(path)
    if not os.path.exists('%s/%s' % (path, scan_id)):
        os.mkdir('%s/%s' % (path, scan_id))
    if not os.path.isfile(cache_file):
        import shutil
        url = 'http://www.archive.org/download/%s/page/n%s' % (scan_id, index)
        if size is not None and size in ('small'):
            url += '_' + size
        req = urlopen(url)
        with open(cache_file, 'wb') as fp:
            shutil.copyfileobj(req, fp)

    return HttpResponse(open(cache_file), mimetype='image/jpeg')


def parallelCoordinates(request):

    from collections import deque

    result = deque()

    alpha = request.GET.get('alpha')
    alpha = 0.8 if alpha is None else alpha

    illustration = request.GET.get('illustration')

    for page in getMongoCollection('page_data').find({}):

        coverage_sum = page['abbyy']['coverage_sum'] if 'coverage_sum' in page['abbyy'] else 0

        data = {
            'gold': page['has_illustration']['gold_standard'],
            'cov': round(coverage_sum, 2),
            'comp': round(100 * page['compression'], 2),
            'cont': round(100 * page['contrast']['max_contiguous'], 2)
        }

        if (page['has_illustration']['gold_standard']):
            if (illustration != 'n'):
                result.append(data)
        else:
            if (illustration != 'y'):
                result.appendleft(data)

    import json
    from django.utils.safestring import mark_safe
    return render_to_response('pcoords.html', {
        'data': mark_safe(json.dumps(list(result))),
        'alpha': alpha
    })


