# -*- coding: utf8 -*-
from __future__ import print_function
from PatentsFileManager import PatentsFileManager
from bs4 import BeautifulSoup
from time import time
import os
import shutil
import zipfile

PATH = "../results"
ERROR_PATH = PATH + "/errors"
RES_PATH = PATH
WARN_PATH = PATH + "/warnings"


def process_zip(data):
    from parser import Patent
    print("Processing zip...")

    usp = "<patent-assignments"
    usp_c = "</patent-assignments>"
    q = len(data) / 100
    index_1 = data.find(usp, 0, q)
    index_2 = data.find(usp_c)
    index_2 += len(usp_c)

    head = data[0:index_1]
    tail = data[index_2:len(data)-1]

    t1 = time()

    s = BeautifulSoup(head+tail, "lxml")
    t2 = time()
    print("Soup is ready...Time: %s" % (t2-t1))

    patents = data[index_1:index_2+len(usp_c)]
    patents = patents.split("<patent-assignment>")

    patents = ["<patent-assignment>" + p for p in patents]

    dtd = s("us-patent-assignments")[0]["dtd-version"]
    date_produced = s("us-patent-assignments")[0]["date-produced"]
    ak = s("action-key-code")[0].string
    d = s("transaction-date")[0].string

    if not d:
        d = s("transaction-date")[0]("date")[0].string

    results = open(os.path.join(RES_PATH, 'res_%s.csv' % d), "w+")
    errors = open(os.path.join(ERROR_PATH, 'errors_%s.txt' % d), "w+")
    warnings = open(os.path.join(WARN_PATH, 'warnings_%s.txt' % d), "w+")

    Patent.set_zip_info(dtd, date_produced, ak, d)
    first = True
    counter = 0
    exc = ""
    for i in xrange(1, len(patents)):
        elem = patents[i]
        init = False
        retries = 0
        while not init and retries < 10:
            try:
                p = Patent(elem)
                init = True
            except Exception, e:
                exc = e
                retries += 1
                print("Exception during init... retrying (%s)" % retries)
                pass

        if not init:
            print("%s ERROR: could not init Patent object, [[%s]]\nString"
                  " data is shown below\n%s" % (i, exc, elem), file=errors)
        p.set_file(results)
        if first:
            p.print_csv_titles()
            first = False
        if p.is_valid():
            p.print_csv()
            counter += 1
            if p.has_warnings():
                print("%s WARNINGS %s" % (i, p.get_warnings()), file=warnings)
        else:
            print("%s ERROR %s " % (i, p.errors))
            print("[%s] %s %s\n" % (i, elem, p.errors), file=errors)

    if first:
        Patent.print_empty_titles(results)
        Patent.print_zip_info(results)

    print("Total printed: %s\nTotal patents: %s" % (counter, len(patents)-1))
    return (counter == (len(patents) - 1))

if __name__ == "__main__":

    if os.path.exists(PATH):
        shutil.rmtree(PATH)
    os.makedirs(PATH)
    os.makedirs(ERROR_PATH)
    os.makedirs(WARN_PATH)
    # os.makedirs(RES_PATH)
    pfm = PatentsFileManager().get_patent_generator()

    zip_results = zipfile.ZipFile("%s/tests_results.zip" % PATH,
                                  "w", zipfile.ZIP_DEFLATED, allowZip64=True)

    for zip_data in pfm:
        f = process_zip(zip_data)
        zip_results.write(f, os.path.basename(f))
        os.remove(f)
    # zip_data = pfm.next()
    # f = process_zip(zip_data)
    # zip_results.write(f, os.path.basename(f))
    # os.remove(f)

    # results.append(process_zip(zip_data))

    # for res in results:

    zip_results.close()
