

def processABBYY(abbyy_page):

    result = {
        'width': int(abbyy_page.attrib['width']),
        'height': int(abbyy_page.attrib['height']),
        'picture_blocks': [],
        'total_coverage_sum': 0,
        'coverage_sum': 0
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

    return result
