import pymongo
from numpy import mean,cov,double,cumsum,dot,linalg,array,rank
from scipy import cluster
from scipy import spatial
from mlpy import HCluster

def princomp(A):
 
  """
  # computing eigenvalues and eigenvectors of covariance matrix
  """
  M = (A-mean(A.T,axis=1)).T # subtract the mean (along columns)
  [latent,coeff] = linalg.eig(cov(M)) # attention:not always sorted
  score = dot(coeff.T,M) # projection of the data in the new space
  return coeff,score,latent


def tryPrincipal(data):
    coeff, score, latent = princomp(array(data))
    #print data[0]
    #print coeff[1]
    print score


def tryHCluster(data):
    dist = spatial.distance.pdist(array(data))
    hc = HCluster()
    linkage = hc.compute(array(data))    
    print linkage


def tryScipyCluster(data):

    linkage = cluster.hierarchy.linkage(array(data), method='complete')

    #print linkage
    #print cluster.hierarchy.fcluster(linkage, .1)

    """
    for clusternum in range(1,len(data)):

        clustdict = {i:[i] for i in xrange(len(linkage)+1)}
        for i in xrange(len(linkage)-clusternum+1):
            clust1= int(linkage[i][0])
            clust2= int(linkage[i][1])
            clustdict[max(clustdict)+1] = clustdict[clust1] + clustdict[clust2]
            del clustdict[clust1], clustdict[clust2]

        largest = 0
        for i in clustdict:
            largest = max(largest, len(clustdict[i]))

        print clusternum, 'clusters, max=', largest
    
    return
    """
    
    clusternum = 2
    clustdict = {i:[i] for i in xrange(len(linkage)+1)}
    for i in xrange(len(linkage)-clusternum+1):
        clust1= int(linkage[i][0])
        clust2= int(linkage[i][1])
        clustdict[max(clustdict)+1] = clustdict[clust1] + clustdict[clust2]
        del clustdict[clust1], clustdict[clust2]

    print clustdict

    smallest = None
    for i in clustdict:
        print i, len(clustdict[i])
        if smallest is None or len(smallest) > len(clustdict[i]):
            smallest = clustdict[i]

    return smallest


def tryDistFromCentroid(data):

    import numpy

    v_mean = numpy.mean(data, 0)
    distances = []
    for d in data:
        distances.append(numpy.linalg.norm(d - v_mean))
    d_mean = numpy.mean(distances)
    std = numpy.std(distances)
    #print std

    outliers = []
    for i in range(0, len(distances)):
        if abs(distances[i] - d_mean) > 0.25 * std:
            outliers.append(i)

    return outliers


def analyzeScan(page_coll, color_coll, scan_id):

    pages = color_coll.find({'scan_id': scan_id}).sort('ia_page_num')

    if pages.count() is 0:
        print scan_id, 'is b&w'
        return

    if pages.count() != page_coll.find({'scan_id': scan_id}).count():
        print scan_id, 'is partially b&w'
        return

    data = []

    # Create the observation matrix
    for page in pages:
        data.append(array(page['h']['hist']))

    #tryPrincipal(array(data))
    #cluster = tryScipyCluster(array(data))
    cluster = tryDistFromCentroid(array(data))

    #print 'cluster:', cluster
    #print 'length:', len(cluster)

    result = page_coll.update({'scan_id': scan_id}, {"$set": {'color_result': False}}, upsert=True, multi=True)

    correct = 0
    n = 0
    found = 0
    pages.rewind()
    for i in range(0, pages.count()):
        page_data = page_coll.find_one({'scan_id': pages[i]['scan_id'], 'ia_page_num': pages[i]['ia_page_num']})
        if (i in cluster):
            page_data['color_result'] = True
            page_coll.save(page_data)
        if page_data['has_illustration']['gold_standard']:
            n += 1
            if (i in cluster):
                found += 1
                correct += 1
        else:
            if (i not in cluster):
                correct += 1

    print scan_id, ': ', len(data), 'pages'
    print float(correct) / len(data), 'accuracy'
    print 'found', found, 'of', n, '( R =', float(found) / n, ')'
    return {
        'n': n,
        'correct': correct,
        'found': found,
        'count': pages.count()
    }

if __name__ == '__main__':

    import argparse

    ap = argparse.ArgumentParser(description='color analysis')
    ap.add_argument('--scan', type=str, help='scan id', default=None)

    args = ap.parse_args()

    import pymongo
    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife
    page_coll = mongo_db.page_data
    color_coll = mongo_db.color_data

    if args.scan == None:

        print 'all'
        info = { 'n': 0, 'correct': 0, 'found': 0, 'count': 0 }
        for scan in sorted(page_coll.distinct('scan_id')):
            result = analyzeScan(page_coll, color_coll, scan)
            if result is not None:
                info['n'] += result['n']
                info['correct'] += result['correct']
                info['found'] += result['found']
                info['count'] += result['count']

        print 'Summary:'
        print info['count'], 'pages'
        print float(info['correct']) / info['count'], ' accuracy'
        print 'found', info['found'], 'of', info['n'], '( R =', float(info['found'])/info['n'], ')'

    else:        
        analyzeScan(page_coll, color_coll, args.scan)