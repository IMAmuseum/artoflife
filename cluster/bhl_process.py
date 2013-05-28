import abbyy
import compression
import contrast
import helper
import argparse
from time import time


def processCollection(force=False):
    collection = helper.mongoConnect()

    pages = getPagesForProcessing(collection, force)
    while (pages is not None):
        processPages(pages, collection, force)
        pages.close()

        pages = getPagesForProcessing(collection, force)


def processPages(pages, collection, force=False):
    abbyyParsed = None
    for page in pages:
        if abbyyParsed is None:
            abbyyParsed = abbyy.parseABBYY(page['scan_id'])
        processPage(page, abbyyParsed, force)
        collection.save(page)


def processPage(page, abbyyParsed, force):
    if page is None:
        helper.log.debug('No pages for processing')
        return
    else:
        helper.log.debug('Starting Processing for scan_id: %s' % (page['scan_id']))
        if (page['abbyy_complete'] is False or force):
            result = abbyy.processABBYY(page, abbyyParsed)
            if (result is not False):
                page['abbyy'] = result
                page['has_illustration']['abbyy'] = result['image_detected']
                page['abbyy_complete'] = True

        if (page['compression_complete'] is False or force):
            result = compression.processImage(page)
            if (result is not False):
                page.update(result)
                page['compression_complete'] = True

        if (page['contrast_complete'] is False or force):
            result = contrast.processImage(page)
            if (result is not False):
                page.update(result)
                page['has_illustration']['contrast'] = result['image_detected']
                page['contrast_complete'] = True

        page['processing_lock'] = False
        page['processing_lock_end'] = time()


def getPagesForProcessing(collection, force):
    if (force):
        page = collection.find_one({
            'processing_lock': False
        })
    else:
        page = collection.find_one({
            'processing_lock': False,
            'abbyy_complete': False,
            'compression_complete': False,
            'contrast_complete': False
        })

    if page is None:
        helper.log.debug("No unprocessed pages found in mongo")
        return None
    else:
        scanId = page['scan_id']
        collection.update({'scan_id': scanId}, {'$set': {'processing_lock': True, 'processing_lock_start': time()}})
        pages = collection.find({
            'scan_id': scanId
        }, timeout=False)

        # page['processing_lock'] = True
        # page['processing_lock_start'] = time()
        # collection.save(page)
        return pages


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='picture block processing')
    ap.add_argument('-f', help='force', action='store_false')

    args = ap.parse_args()

    helper.log.debug("starting processing")
    processCollection(args.f)
    helper.log.debug("end processing")
