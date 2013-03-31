import argparse, csv, os


def analyzePage(page):

    if 'alg_result' not in page:
        page['alg_result'] = {}

    if 'abbyy' in page:
        page['alg_result']['abbyy'] = classifyResult(
            page['has_illustration']['gold_standard'],
            (len(page['abbyy']['picture_blocks']) > 0)
        )

    if 'contrast' in page['has_illustration']:
        page['alg_result']['contrast'] = classifyResult(
            page['has_illustration']['gold_standard'],
            page['has_illustration']['contrast']
        )

    if 'color_result' in page:
        page['alg_result']['color'] = classifyResult(
            page['has_illustration']['gold_standard'],
            page['color_result']
        )
    else:
        page['alg_result']['color'] = 'null'


def analyzePages(pages):

    info = {
        'n_illustrations': 0,
        'pages': []
    }

    algorithms = ['abbyy', 'contrast', 'color']

    for alg in algorithms:
        info[alg] = {
            'n-true-pos': 0,
            'n-false-pos': 0,
            'n-true-neg': 0,
            'n-false-neg': 0,
            'n-null': 0,
            'precision': None,
            'recall': None,
            'accuracy': None
        }

    for page in pages:

        if page['has_illustration']['gold_standard']:
            info['n_illustrations'] += 1

        analyzePage(page)

        for alg in algorithms:
            #if alg == 'abbyy' or alg == 'color' or alg in page['has_illustration']:
            try:
                alg_result = page['alg_result'][alg]
                info[alg]['n-' + alg_result] += 1
            except KeyError:
                alg_result = '' 

        info['pages'].append(page)

    for alg in algorithms:

        if info[alg]['n-true-pos'] == 0:
            info[alg]['precision'] = 0
            info[alg]['recall'] = 0
        else:
            info[alg]['precision'] = float(info[alg]['n-true-pos']) / (info[alg]['n-true-pos'] + info[alg]['n-false-pos'])
            info[alg]['recall'] = float(info[alg]['n-true-pos']) / (info[alg]['n-true-pos'] + info[alg]['n-false-neg'])

        if pages.count() > 0:
            info[alg]['accuracy'] = float(info[alg]['n-true-pos'] + info[alg]['n-true-neg']) / pages.count()

        info[alg]['n_pos'] = info[alg]['n-true-pos'] + info[alg]['n-false-pos']

    pages.rewind()

    return info


def classifyResult(standard, result):
    if standard:
        return 'true-pos' if result else 'false-neg'
    else:
        return 'false-pos' if result else 'true-neg'


def generateHistogram(values, xlabel):

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111)

    n, bins, patches = ax.hist(values, 50, facecolor='green', alpha=0.75)
    #bincenters = 0.5*(bins[1:]+bins[:-1])

    ax.set_xlabel(xlabel)
    ax.set_ylabel('Occurrences')
    #ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
    #ax.set_xlim(0, 120)
    ax.grid(True)

    return fig


if __name__ == "__main__":

    from helpers import getMongoCollection

    coll = getMongoCollection('page_data')

    results = analyzePages(coll.find({}))

    print 'ABBYY:', results['abbyy']
    print 'Contrast:', results['contrast']
    print 'Color:', results['color']

