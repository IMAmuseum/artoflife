import abbyy
import compression
import contrast
import helper
from time import time


def processPages(pages, collection):
    abbyyParsed = None
    scanId = None

    for page in pages:
        if abbyyParsed is None:
            abbyyParsed = abbyy.parseABBYY(page['scan_id'])
        processPage(page, abbyyParsed)
        saveId = collection.save(page)
        scanId = page['scan_id']
        helper.log.debug('Save id: %s' % (saveId))

    helper.removeIAImages(scanId);


def processPage(page, abbyyParsed):
    if page is None:
        helper.log.debug('No pages for processing')
        return
    else:
        startTime = time()
        helper.log.debug('Starting Processing for scan_id: %s' % (page['scan_id']))
        if (page['abbyy_complete'] is False):
            if page['scandata_index'] <= len(abbyyParsed):
                result = abbyyParsed[page['scandata_index']]
                if (result is not False):
                    page['abbyy'] = result
                    page['has_illustration']['abbyy'] = result['image_detected']
                    page['abbyy_complete'] = True
                    page['abbyy_processing_duration'] = time() - startTime
                    helper.log.debug('ABBYY Processing duration: %s' % (page['abbyy_processing_duration']))
            else:
                page['abbyy_error'] = 'out of range %s' % (page['scandata_index'])

        #if (page['compression_complete'] is False):
            #result = compression.processImage(page)
            #if (result is not False):
                #page.update(result)
                #page['compression_complete'] = True
                #page['compression_processing_duration'] = time() - startTime
                #helper.log.debug('Compression Processing duration: %s' % (page['compression_processing_duration']))

        if (page['contrast_complete'] is False):
            result = contrast.processImage(page)
            if (result is not False):
                page.update(result)
                page['has_illustration']['contrast'] = result['image_detected']
                page['contrast_complete'] = True
                page['contrast_processing_duration'] = time() - startTime
                helper.log.debug('Contrast Processing duration: %s' % (page['contrast_processing_duration']))

        page['processing_lock'] = False
        page['processing_lock_end'] = time()

        #if (page['abbyy_complete'] is False or page['compression_complete'] is False or page['contrast_complete'] is False):
        if (page['abbyy_complete'] is False or page['contrast_complete'] is False):
            page['processing_error'] = True

        helper.log.debug('Complete: %s|%s: abbyy: %s, compression: %s, contrast: %s' %
            (page['scan_id'], page['ia_page_num'], page['abbyy_complete'], page['compression_complete'], page['contrast_complete']))
        helper.log.debug('Processing duration: %s' % (time() - startTime))


def getPagesForProcessing(collection):
    page = collection.find_one({
        'processing_lock': False,
        'abbyy_complete': False,
        #'compression_complete': False,
        'contrast_complete': False,
        'processing_error': False
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
            #'compression_complete': False,
            'contrast_complete': False,
            'processing_error': False
        }, timeout=False)
        helper.log.debug("%s: %s pages for processing" % (scanId, pages.count()))
        # page['processing_lock'] = True
        # page['processing_lock_start'] = time()
        # collection.save(page)
        return pages
