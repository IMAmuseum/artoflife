import helper
from xml.etree import cElementTree as ET
import gzip


def parseABBYY(scanId):
    helper.fetch_files(scanId)
    abbyy_file = '%s/scandata/%s/%s_abbyy.gz' % (helper.base_path, scanId, scanId)
    helper.log.debug("abbyy_file: %s" % (abbyy_file))
    f = gzip.open(abbyy_file)
    parsed = ET.parse(f)
    abbyy_pages = parsed.findall('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page')
    parsed = None
    f.close()
    return abbyy_pages


def processABBYY(page, abbyy):

    try:
        scan_id = page['scan_id']
        helper.log.debug("ABBYY for scan_id: %s page_num: %s" % (scan_id, page['ia_page_num']))
        # helper.fetch_files(scan_id)
        # abbyy_file = '%s/scandata/%s/%s_abbyy' % (helper.base_path, scan_id, scan_id)

        # helper.log.debug("abbyy_file: %s" % (abbyy_file))
        # f = open(abbyy_file)
        # abbyy = ET.parse(f)
        # f.close()
        # abbyy_pages = abbyy.findall('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page')

        abbyy_page = abbyy[page['scandata_index']]

        result = {
            'width': int(abbyy_page.attrib['width']),
            'height': int(abbyy_page.attrib['height']),
            'picture_blocks': [],
            'total_coverage_sum': 0,
            'coverage_sum': 0,
            'coverage_max': 0,
            'image_detected': False
        }

        blocks = abbyy_page.findall("{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block")
        for block in blocks:

            area = (int(block.attrib['r']) - int(block.attrib['l'])) * (int(block.attrib['b']) - int(block.attrib['t']))
            result['total_coverage_sum'] += 100 * area / (result['width'] * result['height'])

            if block.attrib['blockType'] == 'Picture':
                result['picture_blocks'].append({
                    'blockType': block.attrib['blockType'],
                    'r': int(block.attrib['r']),
                    'l': int(block.attrib['l']),
                    't': int(block.attrib['t']),
                    'b': int(block.attrib['b'])
                })
                result['coverage_sum'] += area
                result['coverage_max'] = max(result['coverage_max'], area)
                result['image_detected'] = True

        helper.log.debug("ABBYY Complete for scan_id: %s page_num: %s" % (scan_id, page['ia_page_num']))
        return result
    except:
        helper.log.error("error processing ABBYY for scan_id %s page_num: %s" % (scan_id, page['ia_page_num']))
        return False
