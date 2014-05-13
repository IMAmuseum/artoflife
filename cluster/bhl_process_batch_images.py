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
       #pages = None
       pages = getPagesForProcessing(collection)

def processPages(pages, collection):
    abbyyParsed = None
    imagesDownloaded = None
    scanId = None

    try:
        for page in pages:
            if abbyyParsed is None:
                abbyyParsed = abbyy.parseABBYY(page['scan_id'])

            if imagesDownloaded is None:
                imagesDownloaded = helper.fetchAllImages(page['scan_id'])

            if imagesDownloaded is false:
                raise NameError('NoImages')             

            processPage(page, abbyyParsed)
            saveId = collection.save(page)
            scanId = page['scan_id']
            helper.log.debug('Save id: %s' % (saveId))
    except:
        helper.log.debug('Error processing pages')
        page['processing_error'] = True
        saveId = collection.save(page)

    try:
        helper.removeIAImages(scanId)
    except:
        helper.log.debug('Can\'t remove images')


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
    helper.log.debug("Searching for record to process")
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
        helper.log.debug("Scan Id found: %s" % (scanId))
        helper.log.debug("Locking Records")
        collection.update({'scan_id': scanId}, {'$set': {'processing_lock': True, 'processing_lock_start': time()}}, multi=True)
        helper.log.debug("Getting all pages for %s" % (scanId))
        pages = collection.find({
            'scan_id': scanId
        }, timeout=False)
        helper.log.debug("%s: %s pages for processing" % (scanId, pages.count()))
        return pages

if __name__ == '__main__':
    helper.log.debug("starting processing")
    processCollection()
    helper.log.debug("end processing")
