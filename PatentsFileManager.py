import zipfile
import urllib
import datetime
import os


class PatentsFileManager():

    FILE_FORMAT = "ad%s.zip"
    DOWNLOAD_URL = "http://storage.googleapis.com/patents/assignments/%s/%s"

    def __init__(self, stop_point=None):
        self.init_date = datetime.date(2013, 1, 1)
        self.final_date = datetime.date(2015, 3, 18)
        if stop_point:
            self.init_date = datetime.datetime.strptime(
                stop_point, "%Y%m%d").date()

    def get_patent_generator(self):

        while self.init_date <= self.final_date:
            init_date_str = self.init_date.strftime("%Y%m%d")
            file_format = PatentsFileManager.FILE_FORMAT % init_date_str
            download_url = PatentsFileManager.DOWNLOAD_URL % (
                self.init_date.strftime("%Y"), file_format)
            # Print progress
            print "progress: %s" % init_date_str

            # Download file
            urllib.urlretrieve(download_url, file_format)
            patents_data = self._unzip_patent(file_format)
            os.remove(file_format)
            self.init_date += datetime.timedelta(days=1)
            yield patents_data

    def _unzip_patent(self, patent_zip):
        patent_xml = patent_zip.replace("zip", "xml")
        zf = zipfile.ZipFile(patent_zip)
        data = zf.read(patent_xml)
        return data
