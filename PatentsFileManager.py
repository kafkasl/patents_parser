import zipfile
import urllib
import datetime
import os


class PatentsFileManager():
    """
    It downloads patents and creates an iterator.
    Usage:
    p = PatentsFileManager()
    for patent in p.get_patent_generator():
        do_stuff with patent   <---- patent contains the file in string

    If the code is stoped for some error or lack of time, just get the last
    progress print and init the class with this date string.
    Example:
    p = PatentsFileManager("20150103")

    """

    FILE_FORMAT = "ad%s.zip"
    DOWNLOAD_URL = "http://storage.googleapis.com/patents/assignments/%s/%s"
    DOWNLOAD_OLD_URL = "http://storage.googleapis.com/patents/retro/%s/%s"

    def __init__(self, stop_point=None):
        self.old_date_format = "ad20121231-%s.zip"
        self.init_date = datetime.date(2013, 1, 1)
        self.final_date = datetime.date(2015, 3, 18)
        self.stop_point = stop_point
        if stop_point:
            self.init_date = datetime.datetime.strptime(
                stop_point, "%Y%m%d").date()

    def get_patent_generator(self):
        if not self.stop_point:
            for i in range(1, 13):
                old_date_format_str = self.old_date_format % str(i).zfill(2)
                print PatentsFileManager.DOWNLOAD_OLD_URL % (
                    2012, old_date_format_str)
                download_url = PatentsFileManager.DOWNLOAD_OLD_URL % (
                    2012, old_date_format_str)
                # Print progress
                print "progress: %s" % old_date_format_str
                # Download file
                urllib.urlretrieve(download_url, old_date_format_str)
                patents_data = self._unzip_patent(old_date_format_str)
                # os.remove(old_date_format_str)
                yield patents_data

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
            # os.remove(file_format)
            self.init_date += datetime.timedelta(days=1)
            yield patents_data

    def _unzip_patent(self, patent_zip):
        patent_xml = patent_zip.replace("zip", "xml")
        zf = zipfile.ZipFile(patent_zip)
        data = zf.read(patent_xml)
        return data
