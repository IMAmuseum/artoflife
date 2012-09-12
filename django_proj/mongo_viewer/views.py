from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from helpers import getMongoCollection
from analysis import analyzePages, classifyResult


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

    analysis = analyzePages(pages)

    return render_to_response('scan.html', {
        'scan_id': scan_id,
        'pages': analysis['pages'],
        'n_illustrations': analysis['n_illustrations'],
        'abbyy_n': analysis['abbyy']['n-true-pos'] + analysis['abbyy']['n-false-neg'],
        'abbyy_p': analysis['abbyy']['precision'],
        'abbyy_r': analysis['abbyy']['recall']
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
