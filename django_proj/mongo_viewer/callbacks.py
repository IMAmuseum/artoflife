import json, pymongo
from django.http import HttpResponse, Http404

def setHasIllustration(request):

    scan_id = request.GET.get('scan_id')
    index = request.GET.get('index')
    value = request.GET.get('value')

    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife

    page_data = mongo_db.page_data

    page = page_data.find_one({'scan_id': scan_id, 'ia_page_num': int(index)})

    if page is not None:

        page['has_illustration']['gold_standard'] = (value == 'true')
        #print page['has_illustration']['gold_standard']

        page_data.save(page)

        response_data = {'result': 'success'}

    else:

        response_data = {'result': 'invalid page'}

    return HttpResponse(json.dumps(response_data), mimetype="application/json")
