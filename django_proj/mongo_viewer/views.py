from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from helpers import getMongoCollection


def main(request):

    collection = getMongoCollection('page_data')

    return render_to_response('main.html', {
        'scans': collection.distinct('scan_id')
    })


def scan(request, scan_id):

    collection = getMongoCollection('page_data')

    print scan_id
    pages = collection.find({'scan_id': scan_id}).sort('scandata_index', 1)
    print pages.count()

    abbyy_n = 0
    for page in pages:
        if len(page['abbyy']['picture_blocks']) > 0:
            abbyy_n += 1

    pages.rewind()

    return render_to_response('scan.html', {
        'scan_id': scan_id,
        'pages': pages,
        'abbyy_n': abbyy_n
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
