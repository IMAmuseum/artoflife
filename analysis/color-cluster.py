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
    print data[0]
    print coeff[1]


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


def analyzeScan(page_coll, color_coll, scan_id):

    pages = color_coll.find({'scan_id': scan_id}).sort('ia_page_num')

    with_v = []
    without_v = []

    data = []

    # Create the observation matrix
    for page in pages:
        data.append(array(page['h']['hist']))

    #tryPrincipal(array(data))
    cluster = tryScipyCluster(array(data))
    #tryDistFromCentroid(array(data))

    print cluster

    count = 0
    pages.rewind()
    for c in cluster:
        #print pages[c]['ia_page_num']
        page_data = page_coll.find_one({'scan_id': pages[c]['scan_id'], 'ia_page_num': pages[c]['ia_page_num']})
        if page_data['has_illustration']['gold_standard']:
            count += 1

    print float(count) / len(data), ' accuracy'



if __name__ == '__main__':

    import argparse

    ap = argparse.ArgumentParser(description='color analysis')
    ap.add_argument('scan', type=str, help='scan id', default=None)

    args = ap.parse_args()

    import pymongo
    mongo_conn = pymongo.Connection('localhost', 27017)
    mongo_db = mongo_conn.artoflife
    page_coll = mongo_db.page_data
    color_coll = mongo_db.color_data

    analyzeScan(page_coll, color_coll, args.scan)