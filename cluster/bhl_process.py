import abbyy
import compression
import contrast
import helper
from time import time


def processCollection():
    collection = helper.mongoConnect()

    processPages(collection)


def processPages(collection):
    page = getPageForProcessing(collection)
    if page is None:
        helper.log.debug('No pages for processing')
        return
    else:
        helper.log.debug('Starting Processing for scan_id: %s' % (page['scan_id']))
        if (page['abbyy_complete'] is False):
            result = abbyy.processABBYY(page)
            if (result is not False):
                page['abbyy'] = result
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
                page['contrast_complete'] = True

        page['processing_lock'] = False
        page['processing_lock_end'] = time()
        collection.save(page)

        processPages(collection)


def getPageForProcessing(collection):
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
        page['processing_lock'] = True
        page['processing_lock_start'] = time()
        collection.save(page)
        return page


if __name__ == '__main__':
    helper.log.debug("starting processing")
    processCollection()
    helper.log.debug("end processing")
