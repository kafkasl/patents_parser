# -*- coding: utf8 -*-
from __future__ import print_function
#from PatentsFileManager import PatentsFileManager
from bs4 import BeautifulSoup
from time import time
import os
import sys
import shutil
import zipfile
import glob
import multiprocessing
import traceback

PATH = "."
ERROR_PATH = PATH + "/errors"
RES_PATH = PATH + "/"
WARN_PATH = PATH + "/warnings"


def process_zip(file):
    t0 = time()

    data = unzip_patent(file)
    name = os.path.basename(file).replace("zip", "csv")

    from parser import Patent
    print("Processing zip...")

    usp = "<patent-assignments"
    usp_c = "</patent-assignments>"
    # q = len(data) / 100
    index_1 = data.find(usp)
    index_2 = data.find(usp_c)
    index_2 += len(usp_c)

    head = data[0:index_1]
    tail = data[index_2:len(data)-1]

    t1 = time()

    s = BeautifulSoup(head+tail, "lxml")
    t2 = time()
    print("Soup Time: %s" % (t2-t1))

    patents = data[index_1:index_2+len(usp_c)]
    patents = patents.split("<patent-assignment>")

    patents = ["<patent-assignment>" + p for p in patents]

    dtd = s("us-patent-assignments")[0]["dtd-version"]
    date_produced = s("us-patent-assignments")[0]["date-produced"]
    ak = s("action-key-code")[0].string
    d = s("transaction-date")[0].string

    if not d:
        d = s("transaction-date")[0]("date")[0].string

    results = open(os.path.join(RES_PATH, name), "w+")
    errors = open(os.path.join(ERROR_PATH, 'errors_%s.txt' % name.replace(".csv", "")), "w+")
    warnings = open(os.path.join(WARN_PATH, 'warnings_%s.txt' % name.replace(".csv", "")), "w+")

    Patent.set_zip_info(dtd, date_produced, ak, d)
    first = True
    counter = 1
    exc = ""

    p_time = 0

    pr_time  = 	0
    p = False
    print("Patents to parse %s" % len(patents))
    for i in xrange(1, len(patents)):
        elem = patents[i]
        init = False
        retries = 0
        while not init and retries < 10:
            try:
                tx1 = time()
                p = Patent(elem)
                p_time += (time() - tx1)
                init = True
            except Exception, e:
                exc = e
                retries += 1
                tb = traceback.format_exc()
                print("Exception during init... retrying (%s)\n - %s" % (retries, tb))
                pass

        if not init:
            print("%s ERROR: could not init Patent object, [[%s]]\nString"
                  " data is shown below\n%s" % (i, exc, elem), file=errors)
        txp = time()
        p.set_file(results)
        if first:
            p.print_csv_titles()
            first = False
        if p.is_valid():
            counter += 1
            if p.has_warnings():
                print("%s WARNINGS %s" % (i, p.get_warnings()), file=warnings)
        else:
            print("%s ERROR %s " % (i, p.errors))
            print("[%s] %s %s\n" % (i, elem, p.errors), file=errors)
        p.print_csv()
        pr_time = (time() - txp)

    if first:
        Patent.print_empty_titles(results)
        Patent.print_zip_info(results)


    print("TIMES:\n\tPatent %s\n\tPrint %s" % (p_time, pr_time))


    print("Total printed: %s\nTotal patents: %s" % (counter, len(patents)))
    if counter == len(patents):
        # os.remove(file)
        pass


def unzip_patent(patent_zip):
    patent_xml = patent_zip.replace("zip", "xml")
    zf = zipfile.ZipFile(patent_zip)
    data = zf.read(os.path.basename(patent_xml))
    return data


if __name__ == "__main__":

    t_first = time()

    if len(sys.argv) > 3:
        PATH = sys.argv[1]
        ERROR_PATH = PATH + "/errors"
        RES_PATH = PATH + "/"
        WARN_PATH = PATH + "/warnings"
        DATA_PATH = sys.argv[2]
        available_threads = int(sys.argv[3])
    else:
        print("Usage: hdd_main RESULTS_PATH DATA_PATH nthreads")
        sys.exit(1)


    print(" - Starting HDD parser: \n  -- %s\n  -- %s" % (PATH, DATA_PATH))

    if not os.path.exists(PATH):
        os.makedirs(PATH)
    if not os.path.exists(ERROR_PATH):
        os.makedirs(ERROR_PATH)
    if not os.path.exists(WARN_PATH):
        os.makedirs(WARN_PATH)

    # os.makedirs(RES_PATH)
    # pfm = PatentsFileManager().get_patent_generator()

    # zip_results = zipfile.ZipFile("%s/tests_results.zip" % PATH,
    #                               "w", zipfile.ZIP_DEFLATED, allowZip64=True)
    #available_threads = multiprocessing.cpu_count()
    print("Using %s threads" % available_threads)

    p = multiprocessing.Pool(available_threads)
    try:
        files = glob.glob("%s/*.zip" % DATA_PATH)
        print("Files to parse: %s" % files)
        p.map(process_zip, files)
    except Exception, e:
        tb = traceback.format_exc()
        print("-- EXCEPTION ON POOL: %s\n. TERMINATING..."% tb)
        p.terminate()
    except:
        tb = traceback.format_exc()
        print("-- UND. EXCEPTION ON POOL.%s\n. TERMINATING..." % tb)
        p.terminate()
    finally:
        print("--  DONE")

    p.terminate()
    t_last = time()
    print("Elapsed time: %s" % (t_last-t_first))

    # for file in files:
    #     process_zip(file)


        # print("File %s" % file)
        # zip_data = unzip_patent(file)
        # if process_zip(zip_data, file.replace("zip", "csv")):
        #     # os.remove(file)
        #     print("ZIP OK")
        # zip_results.write(f, os.path.basename(f))
    # zip_data = pfm.next()
    # f = process_zip(zip_data)
    # zip_results.write(f, os.path.basename(f))
    # os.remove(f)

    # results.append(process_zip(zip_data))

    # for res in results:

    # zip_results.close()
