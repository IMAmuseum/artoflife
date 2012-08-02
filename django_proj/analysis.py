import argparse, csv, os


if __name__ == "__main__":

    ap = argparse.ArgumentParser(description='analysis')
    #ap.add_argument('scan', type=str, help='scan id')

    args = ap.parse_args()

    algorithms = [
        'contrast', 'pictureblocks'
    ]

    control_file = open('BHLIllustrations.csv', 'rU')
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

    analysis_file = open('output/analysis.csv', 'w')
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
