import os
import sys
from google.cloud import storage

def download_board(year, month, day, work_dir='/tmp'):
    #    storage_client = storage.Client('bitmmf')
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('bitboard')

    prefix = '{:04d}/{:02d}/{:02d}'.format(int(year), int(month), int(day))
    print(prefix)

    blobs = bucket.list_blobs(prefix=prefix)

    work_dir = work_dir + os.sep + prefix
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    for blob in blobs:
        target = work_dir + os.sep + os.path.basename(blob.name)

        print('[DOWNLOAD]',blob.name, target)
        blob.download_to_filename(target)


if __name__ == '__main__':
    download_board(sys.argv[1], sys.argv[2], sys.argv[3])