import helper
import pp
import bhl_process_tasks
from time import time


def processCollection():
    collection = helper.mongoConnect()

    pages = bhl_process_tasks.getPagesForProcessing(collection)
    while (pages is not None):
        bhl_process_tasks.processPages(pages, collection)
        pages.close()

        pages = bhl_process_tasks.getPagesForProcessing(collection)


if __name__ == '__main__':
    helper.log.debug("starting processing")
    job_server = pp.Server();
    #processCollection()
    j1 = job_server.submit(processCollection, (), (), ('bhl_process_tasks','abbyy','compression','contrast','helper'))
    j2 = job_server.submit(processCollection, (), (), ('bhl_process_tasks','abbyy','compression','contrast','helper'))
    j3 = job_server.submit(processCollection, (), (), ('bhl_process_tasks','abbyy','compression','contrast','helper'))
    j4 = job_server.submit(processCollection, (), (), ('bhl_process_tasks','abbyy','compression','contrast','helper'))
    j1()
    j2()
    j3()
    j4()
    helper.log.debug("end processing")
