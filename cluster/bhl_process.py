import abbyy
import compression
import contrast
import helper
from time import time


def processCollection():
    collection = helper.mongoConnect()

    pages = getPagesForProcessing(collection)
    while (pages is not None):
        processPages(pages, collection)
        pages.close()

        pages = getPagesForProcessing(collection)


def processPages(pages, collection):
    abbyyParsed = None
    for page in pages:
        if abbyyParsed is None:
            abbyyParsed = abbyy.parseABBYY(page['scan_id'])
        processPage(page, abbyyParsed)
        saveId = collection.save(page)
        helper.log.debug('Save id: %s' % (saveId))


def processPage(page, abbyyParsed):
    if page is None:
        helper.log.debug('No pages for processing')
        return
    else:
        helper.log.debug('Starting Processing for scan_id: %s' % (page['scan_id']))
        if (page['abbyy_complete'] is False):
            result = abbyy.processABBYY(page, abbyyParsed)
            if (result is not False):
                page['abbyy'] = result
                page['has_illustration']['abbyy'] = result['image_detected']
                page['abbyy_complete'] = True

        if (page['compression_complete'] is False):
            result = compression.processImage(page)
            if (result is not False):
                page.update(result)
                page['compression_complete'] = True

        if (page['contrast_complete'] is False):
            result = contrast.processImage(page)
            if (result is not False):
                page.update(result)
                page['has_illustration']['contrast'] = result['image_detected']
                page['contrast_complete'] = True

        page['processing_lock'] = False
        page['processing_lock_end'] = time()

        helper.log.debug('Complete: %s|%s: abbyy: %s, compression: %s, contrast: %s' %
            (page['scan_id'], page['ia_page_num'], page['abbyy_complete'], page['compression_complete'], page['contrast_complete']))


def getPagesForProcessing(collection):
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
            'scan_id': scanId,
            'abbyy_complete': False,
            'compression_complete': False,
            'contrast_complete': False
        }, timeout=False)
        helper.log.debug("%s: %s pages for processing" % (scanId, pages.count()))
        # page['processing_lock'] = True
        # page['processing_lock_start'] = time()
        # collection.save(page)
        return pages


if __name__ == '__main__':
    helper.log.debug("starting processing")
    processCollection()
    helper.log.debug("end processing")
