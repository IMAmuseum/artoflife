from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404

import pymongo


def main(request):

    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife
    collection = mongo_db.page_data

    return render_to_response('main.html', {
        'scans': collection.distinct('scan_id')
    })


def scan(request, scan_id):

    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife
    collection = mongo_db.page_data

    print scan_id
    pages = collection.find({'scan_id': scan_id})
    print pages.count()

    return render_to_response('scan.html', {
        'scan_id': scan_id,
        'pages': pages
    })
