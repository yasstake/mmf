from google.cloud import storage
import log.constant as constant
import os

class LogStorage:
    def __init__(self,  project = constant.LOG_PROJECT_NAME, bucket_name = constant.LOG_BUCKET_NAME):
        self.project = project
        self.bucket_name = bucket_name

    def list_dir(self, dir):
        storage_client = storage.Client(self.project)
        bucket = storage_client.get_bucket(self.bucket_name)

        blobs = bucket.list_blobs(prefix=dir, delimiter='/')

        #needs below to update blobs.prefixes value through iterator
        for blob in blobs:
            pass

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

        files = list()
        for blob in blobs:
            files.append(blob.name)

        return sorted(files)

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

