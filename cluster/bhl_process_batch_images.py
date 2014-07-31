import abbyy
import compression
import contrast
import helper
import ipdb
import os
from time import time

def processCollection():
    collection = helper.mongoConnect()

    pages = getPagesForProcessing(collection)
    while (pages is not None):
        processPages(pages, collection)
        pages.close()
        #pages = None
        if os.path.exists("./stop.txt"):
            print("Stop file found. Exiting.\n")
            break
        pages = getPagesForProcessing(collection)


def processPages(pages, collection):
    abbyyParsed = None
    imagesDownloaded = None
    scanId = None
    pageShift = 0
    firstPass = False

    try:
        for page in pages:
            if abbyyParsed is None:
                abbyyParsed = abbyy.parseABBYY(page['scan_id'])

            if imagesDownloaded is None:
                imagesDownloaded = helper.fetchAllImages(page['scan_id'])

            if imagesDownloaded is False:
                helper.log.debug('Images Downloaded False')
                raise NameError('NoImages')

            # Determine if the page image exists. Our data starts counting at 0. Sometimes the pages start counting at 1.
            if not firstPass: # we don't want to do this every time we loop
                # Does the page 0 file exist?
                imgPath = '%s/%s/%s_jp2/%s_%s.jp2' % (helper.base_path, page['scan_id'], page['scan_id'], page['scan_id'], '0000')
                if not os.path.exists(imgPath):
                    # No, we need to shift pages when we reference files on disk
                    pageShift = 1
                    firstPass = true


            processPage(page, abbyyParsed, pageShift)
            saveId = collection.save(page)
            scanId = page['scan_id']
            helper.log.debug('Save id: %s' % (saveId))

        # Now that all pages are processed, clear the lock
        collection.update({'scan_id': page['scan_id']}, {'$set': {'processing_lock': False, 'processing_lock_end': time()}}, multi=True)

    except Exception, e:
        helper.log.debug('Error processing pages:' + str(e))
        page['processing_error'] = True
        saveId = collection.save(page)

    try:
        helper.removeIAImages(scanId)
    except Exception, e:
        helper.log.debug('Can\'t remove images' + str(e))


def processPage(page, abbyyParsed, pageShift):
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
            result = contrast.processImage(page, pageShift)
            if (result is not False):
                page.update(result)
                page['has_illustration']['contrast'] = result['image_detected']
                page['contrast_complete'] = True
                page['contrast_processing_duration'] = time() - startTime
                helper.log.debug('Contrast Processing duration: %s' % (page['contrast_processing_duration']))

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
    if os.path.exists("./stop.txt"):
        os.rename("./stop.txt","./start.txt")

    processCollection()
    helper.log.debug("end processing")
