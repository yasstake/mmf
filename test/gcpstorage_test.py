import unittest
import log.constant as constant
from gcp.storage import storage as gcs

from gcp.storage import LogStorage
from gcp.storage import BoardStorage


class MyTestCase(unittest.TestCase):
    def test_board_storage_list(self):
        bs = BoardStorage()

        print(bs.create_test_set())


    def test_list_dir(self):
        bs = BoardStorage()

        print(bs.list_dir(''))

    def test_storage_year(self):
        storage = LogStorage()
        years = storage.list_dir('')

        for year in years:
            print(year)

    def test_storage_list_dir(self):
        storage = LogStorage()
        years = storage.list_dir('')

        for year in years:
            print(year)

            months = storage.list_dir(year)
            for month in months:
                print(month)

    def test_storage_list_year(self):
        storage = LogStorage()
        years = storage.list_year()
        for year in years:
            print(year)

    def test_storage_list_blobs(self):
        storage = LogStorage()
        blobs = storage.list_blobs('2019/')

        for blob in blobs:
            print(blob.name)

    def test_storage_list_blobs_names(self):
        storage = LogStorage()
        blobs = storage.list_blob_names('2019/')

        for blob in blobs:
            print(blob)


    def test_storage_file_base_name(self):
        storage = LogStorage()

        base = storage.file_base_name("2019/03/16/B-2019-03-16T05-34-47.748885Z.log.gz")

        print(base)
        self.assertEqual(base, "B-2019-03-16T05-34-47.748885Z.log.gz")

    def test_download_blob(self):
        storage = LogStorage()

        storage.download_blob("2019/03/16/B-2019-03-16T05-34-47.748885Z.log.gz")

    def call_back(self, file_name):
        print(file_name)

    def test_process_blob(self):
        storage = LogStorage()

        storage.process_blob("2019/03/16/B-2019-03-16T05-34-47.748885Z.log.gz", self.call_back)

    def test_list_dir(self):
        storage = LogStorage()

        print(storage.list_blob_names("2019/03/16/"))

    def test_process_dir(self):
        storage = LogStorage()

        storage.process_blob_dir("2019/03/16/", self.call_back)

    def test_process_dir_date(self):
        storage = LogStorage()

        storage.process_blob_date_with_padding(2019, 3, 19, self.call_back)



    def test_list_dayanddayafter(self):
        storage = LogStorage()

        print(storage.list_blob_names_by_date_with_padding(2019, 3,19))

    def test_list_board_dir(self):
        pass

if __name__ == '__main__':
    unittest.main()
