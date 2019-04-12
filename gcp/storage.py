import os

from google.cloud import storage

import log.constant as constant
from log.timeutil import date_path


class BoardStorage:
    def __init__(self, project = constant.LOG_PROJECT_NAME, bucket_name = constant.BOARD_BUCKET_NAME):
        self.project = project
        self.bucket_name = bucket_name

    def list_files(self, path):
        storage_client = storage.Client(self.project)
        bucket = storage_client.get_bucket(self.bucket_name)

        print("bucket name ->", self.bucket_name)

        bucket.list_blobs(dir)


    def create_test_set(self):
        storage_client = storage.Client(self.project)
        bucket = storage_client.get_bucket(self.bucket_name)

        print(list(bucket.list_blobs(prefix='2019/', delimiter='/')))

        years = bucket.list_blobs(prefix='bitboard/', delimiter='')

        for year in years:
            print('year->', year.name)
            months = bucket.list_blobs(prefix=year.name, delimiter='/')
            for month in months:
                print(month.name)
                days = bucket.list_blobs(prefix=month.name, delimiter='/')
                for day in days:
                    print(day.name)




class LogStorage:
    def __init__(self,  project = constant.LOG_PROJECT_NAME, bucket_name = constant.LOG_BUCKET_NAME):
        self.project = project
        self.bucket_name = bucket_name

    def list_dir(self, dir):
        storage_client = storage.Client(self.project)
        bucket = storage_client.get_bucket(self.bucket_name)

        blobs = bucket.list_blobs(prefix=dir, delimiter='/')

        return blobs.prefixes

    def list_year(self):
        return self.list_dir('')

    def list_blobs(self, dir):
        storage_client = storage.Client(self.project)
        bucket = storage_client.get_bucket(self.bucket_name)

        blobs = bucket.list_blobs(prefix=dir, delimiter='')

        return blobs

    def list_blob_names(self, dir):
        blobs = self.list_blobs(dir)

        files = []
        for blob in blobs:
            files.append(blob.name)

        return sorted(files)

    def list_blob_names_by_date_with_padding(self, year, month, date):
        ''''
        Process log including 1H before and 1H after the specified date.
        '''
        #day before
        blobs = []
        blobs += self.list_blob_names(date_path(year, month, date, -1, '/') + '/A-' + date_path(year, month, date, -1, '-') + 'T23-')
        blobs += self.list_blob_names(date_path(year, month, date, -1, '/') + '/B-' + date_path(year, month, date, -1, '-') + 'T23-')
        blobs += self.list_blob_names(date_path(year, month, date, 0, '/'))
        blobs += self.list_blob_names(date_path(year, month, date, 1, '/') + '/A-' + date_path(year, month, date, 1, '-') + 'T00-')
        blobs += self.list_blob_names(date_path(year, month, date, 1, '/') + '/B-' + date_path(year, month, date, 1, '-') + 'T00-')

        return sorted(blobs)


    def file_base_name(self, full_path):
        return os.path.basename(full_path)


    def download_blob(self, blob_name, tmp='/tmp'):
        work_dir = tmp + os.sep + 'WORK'

        if not os.path.exists(work_dir):
            os.makedirs(work_dir)

        storage_client = storage.Client(self.project)
        bucket = storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(blob_name)

        file_name = work_dir + os.sep + self.file_base_name(blob_name)

        if not os.path.exists(file_name):
            print("download", file_name)
            blob.download_to_filename(file_name)

        return file_name


    def process_blob(self, path, call_back):
        try:
            work_file = self.download_blob(path)
            if call_back:
                call_back(work_file)
            else:
                print('no process for', path)

        finally:
            pass

    def process_blob_dir(self, dir, call_back):
        blob_names = self.list_blob_names(dir)

        for path in blob_names:
            self.process_blob(path, call_back)

    def process_blob_date_with_padding(self, year, month, day, call_back):
        blob_names = self.list_blob_names_by_date_with_padding(year, month, day)

        for path in blob_names:
            self.process_blob(path, call_back)


