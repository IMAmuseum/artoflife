import argparse, csv, os


def analyzePage(page):

    if 'alg_result' not in page:
        page['alg_result'] = {}

    page['alg_result']['abbyy'] = classifyResult(
        page['has_illustration']['gold_standard'],
        (len(page['abbyy']['picture_blocks']) > 0)
    )

    if 'contrast' in page['has_illustration']:
        page['alg_result']['contrast'] = classifyResult(
            page['has_illustration']['gold_standard'],
            page['has_illustration']['contrast']
        )


def analyzePages(pages):

    info = {
        'n_illustrations': 0,
        'pages': []
    }

    algorithms = ['abbyy', 'contrast']

    for alg in algorithms:
        info[alg] = {
            'n-true-pos': 0,
            'n-false-pos': 0,
            'n-true-neg': 0,
            'n-false-neg': 0,
            'precision': None,
            'recall': None,
            'accuracy': None
        }

    for page in pages:

        if page['has_illustration']['gold_standard']:
            info['n_illustrations'] += 1

        analyzePage(page)

        for alg in algorithms:
            if alg == 'abbyy' or alg in page['has_illustration']:
                info[alg]['n-' + page['alg_result'][alg]] += 1

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

    ap = argparse.ArgumentParser(description='analysis')
    #ap.add_argument('scan', type=str, help='scan id')

    args = ap.parse_args()

    algorithms = [
        'contrast', 'pictureblocks'
    ]

    input_file = 'BHL-gold-standard.csv'

    control_file = open(input_file, 'rU')
    control_reader = csv.reader(control_file)
    control_reader.next()  # skip header

    n_control = 0
    control_data = {}
    for row in control_reader:

        if not row[0] in control_data:
            control_data[row[0]] = {'rows': [], 'n_image_pages': 0}

        control_data[row[0]]['rows'].append(row)

        if row[6] == 'Yes':
            control_data[row[0]]['n_image_pages'] += 1

    control_file.close()

    analysis_file = open('output/' + input_file.replace('.csv', '-analysis.csv'), 'w')
    analysis_writer = csv.writer(analysis_file)

    header = [
        'Internet Archive ID',
        '# pages',
        '# w/ images',
    ]

    for alg in algorithms:
        header.extend([
            alg + ' (n)',
            alg + ' (p)',
            alg + ' (r)'
        ])

    analysis_writer.writerow(header)

    for scan in control_data:

        print 'Analyzing', scan
        print len(control_data[scan]['rows']), 'pages in control data'
        print control_data[scan]['n_image_pages'], 'pages have images'

        result = [
            scan,
            len(control_data[scan]['rows']),
            control_data[scan]['n_image_pages']
        ]

        for alg in algorithms:

            output_filename = 'output/%s/%s-%s.csv' % (alg, scan, alg)
            if not os.path.exists(output_filename):
                print output_filename, 'does not exist'
                result.extend(['', '', ''])
                continue

            alg_file = open(output_filename)
            alg_reader = csv.reader(alg_file)
            alg_reader.next()  # skip header

            i = 0
            n_alg = 0
            n_correct = 0
            for row in alg_reader:
                if row[1] == 'True':
                    n_alg += 1
                    if control_data[scan]['rows'][i][6] == 'Yes':
                        n_correct += 1
                i += 1

            print alg, n_correct, 'of', n_alg
            p = None
            r = None
            if n_alg != 0:
                p = float(n_correct) / n_alg
                print alg, 'precision:', p
            if control_data[scan]['n_image_pages'] != 0:
                r = float(n_correct) / control_data[scan]['n_image_pages']
                print alg, 'recall:', r

            alg_file.close()

            result.extend([n_alg, p, r])

        analysis_writer.writerow(result)

    analysis_file.close()
