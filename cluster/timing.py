import helper
from pprint import pprint


if __name__ == '__main__':
    collection = helper.mongoConnect()

    pages = collection.find({});
    abbyyTotalPages = 0
    abbyyTotalTime = 0
    contrastTotalPages = 0
    contrastTotalTime = 0
    compressionTotalPages = 0
    compressionTotalTime = 0
    for page in pages:
        accumulatedTime = 0
        if "abbyy_processing_duration" in page:
            abbyyTotalTime = abbyyTotalTime + page['abbyy_processing_duration']
            accumulatedTime = page['abbyy_processing_duration']
            abbyyTotalPages = abbyyTotalPages + 1

        if "compression_processing_duration" in page:
            accumulatedTime = page['compression_processing_duration']
            compressionTotalTime = compressionTotalTime + page['compression_processing_duration']
            compressionTotalPages = compressionTotalPages + 1

        if "contrast_processing_duration" in page:
            contrastTotalTime = contrastTotalTime + page['contrast_processing_duration'] - accumulatedTime
            contrastTotalPages = contrastTotalPages + 1

    abbyyAverage = abbyyTotalTime / abbyyTotalPages
    compressionAverage = compressionTotalTime / compressionTotalPages
    contrastAverage = contrastTotalTime / contrastTotalPages

    print "abbyy: %s/%s = %s" % (abbyyTotalTime, abbyyTotalPages, abbyyAverage)
    print "compression: %s/%s = %s" % (compressionTotalTime, compressionTotalPages, compressionAverage)
    print "contrast: %s/%s = %s" % (contrastTotalTime, contrastTotalPages, contrastAverage)
