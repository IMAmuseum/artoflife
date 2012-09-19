from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404
from helpers import getMongoCollection
from analysis import analyzePage, analyzePages, classifyResult


def main(request):

    collection = getMongoCollection('page_data')

    return render_to_response('main.html', {
        'scans': sorted(collection.distinct('scan_id'))
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
    })


def page(request, scan_id, page_id):

    collection = getMongoCollection('page_data')
    page = collection.find_one({'scan_id': scan_id, 'ia_page_num': int(page_id)})
    analyzePage(page)
    return render_to_response('page.html', {
        'scan_id': scan_id,
        'page': page
    })


def coverageHistogram(request):

    import StringIO
    from analysis import generateHistogram
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    collection = getMongoCollection('page_data')

    data = []
    for page in collection.find({}):
        if ('coverage_sum' in page['abbyy']) and (page['abbyy']['coverage_sum'] > 0):
            data.append(page['abbyy']['coverage_sum'])

    hist = generateHistogram(data, 'Coverage')
    canvas = FigureCanvas(hist)
    print 'got canvas'

    png_output = StringIO.StringIO()
    canvas.print_png(png_output)

    # Django's HttpResponse reads the buffer and extracts the image
    return HttpResponse(png_output.getvalue(), mimetype='image/png')


def thumbImage(request, scan_id, index):

    import os
    from urllib2 import urlopen

    cache_file = 'tmp/ia-small/%s/%s.jpeg' % (scan_id, index)

    if not os.path.exists('tmp/ia-small'):
        os.mkdir('tmp/ia-small')
    if not os.path.exists('tmp/ia-small/%s' % (scan_id)):
        os.mkdir('tmp/ia-small/%s' % (scan_id))
    if not os.path.isfile(cache_file):
        import shutil
        url = 'http://www.archive.org/download/%s/page/n%s_small' % (scan_id, index)
        req = urlopen(url)
        with open(cache_file, 'wb') as fp:
            shutil.copyfileobj(req, fp)

    return HttpResponse(open(cache_file), mimetype='image/jpeg')
