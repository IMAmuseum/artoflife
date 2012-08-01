import argparse, csv


if __name__ == "__main__":

    ap = argparse.ArgumentParser(description='analysis')
    ap.add_argument('scan', type=str, help='scan id')

    args = ap.parse_args()

    algorithms = [
        'contrast', 'pictureblocks'
    ]

    control_data = []
    control_file = open('BHLIllustrations.csv', 'rU')
    control_reader = csv.reader(control_file)
    control_reader.next()  # skip header

    n_control = 0
    for row in control_reader:
        if (row[0] == args.scan):
            control_data.append(row)
            if row[6] == 'Yes':
                n_control += 1
    control_file.close()

    print len(control_data), 'pages in control data'
    print n_control, 'pages have images'

    for alg in algorithms:
        alg_file = open('output/%s/%s-%s.csv' % (alg, args.scan, alg))
        alg_reader = csv.reader(alg_file)
        alg_reader.next()  # skip header

        i = 0
        n_alg = 0
        n_correct = 0
        for row in alg_reader:
            if row[1] == 'True':
                n_alg += 1
                if control_data[i][6] == 'Yes':
                    n_correct += 1
            i += 1

        print alg, n_correct, 'of', n_alg
        print alg, 'precision:', float(n_correct) / n_alg
        print alg, 'recall:', float(n_correct) / n_control

        alg_file.close()
