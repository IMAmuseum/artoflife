import os
import subprocess
import time
from helper import log
from helper import mongoConnect
from helper import base_path
from ftplib import FTP

server_name = 'IMA'
ftp_host = ''
ftp_username = ''
ftp_password = ''
ftp_path = '/incoming/artoflife'
mongo_host = 'localhost:27017'

if __name__ == '__main__':
    collection = mongoConnect()

    export_date = time.strftime('%Y%m%d')

    log.debug("updating records that need exported with today's date")
    collection.update(
        {'abbyy_complete':True, 'contrast_complete':True, 'processing_error':False, 'processing_lock_end':{'$gt': 0}, 'exported':{'$exists':False}},
        {'$set': {'exported': True, 'export_date': export_date}},
        multi=True
    )

    file_base_path = '%s/export' % (base_path)
    if not os.path.exists(file_base_path):
        os.mkdir(file_base_path)

    output_filename = 'export_%s_%s.json' % (server_name, export_date)
    output_file = '%s/%s' % (file_base_path, output_filename)

    log.debug("waiting 120 seconds for database to calm down")
    time.sleep(120);

    query = '{"export_date" : "' + str(export_date) + '"}';
    cstack = [
        'mongoexport',
        '-h',
        mongo_host,
        '-d',
        'artoflife',
        '-c',
        'page_data',
        '-q',
        query,
        '-o',
        output_file
    ]

    log.debug("exporting records to file")
    p = subprocess.Popen(cstack)
    p.communicate()

    log.debug("Uploading records to mobot")
    ftp = FTP(ftp_host)
    ftp.login(ftp_username, ftp_password)
    ftp.cwd(ftp_path)
    file = open(output_file,'rb')                   # file to send
    ftp.storbinary('STOR ' + output_filename, file) # send the file
    file.close()                                    # close file and FTP
    ftp.quit()

    log.debug("export complete")
