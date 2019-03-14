import os, sys, subprocess, glob, re
from google.cloud import storage
from log.timeutil import timestamp
from time import sleep


def upload(file):
    staging_file = file + '.stage'
    done_file    = file + '.done'

    os.rename(file, staging_file)

    f_org = file.split('BITLOG')[1]

    file_root = f_org.split('-')

    worker = file_root[0]
    year   = file_root[1]
    month  = file_root[2]
    day    = file_root[3].split('T')[0]

    print(worker, year, month, day)

    """Uploads a file to the bucket."""
    source_file_name = staging_file
    destination_blob_name = '/' + year + '/' + month + '/' + day + '/' + f_org

    bucket_name = 'mmflog'
    storage_client = storage.Client('bitmmf')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    os.rename(staging_file, done_file)




if __name__ == "__main__":

    log_dir = os.sep + 'tmp'

    if len(sys.argv) == 2:
        log_dir = sys.argv[1]

    file_list = glob.glob(log_dir + os.sep + '*.log')
    for file in file_list:
        subprocess.run(['/bin/gzip', '-9', file])

    file_list = glob.glob(log_dir + '/*.log.gz')
    for file in file_list:
        upload(file)

    file_list = glob.glob(log_dir + '/*.log.gz.done')
    for file in file_list:
        stat = os.stat(file)
        if stat:
            print(file, stat.st_ctime, timestamp())
            if stat.st_ctime + 24*60*60 * 2 < timestamp():  # 2 days old
                os.remove(file)
                print("delete", file)



