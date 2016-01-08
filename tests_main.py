# -*- coding: utf8 -*-
from __future__ import print_function
from PatentsFileManager import PatentsFileManager
from bs4 import BeautifulSoup
from time import time

import zipfile
import os
import shutil

from parser import Patent


def process_zip(data):
    data = data.replace('\n', '')
    print("Processing zip...")
    total = 0.0
    process = 0.0
    printing = 0.0

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

    s("transaction-date").contents = [p for p in s("transaction-date")[0].contents if p != " "]
    d = s("transaction-date")[0]("date")[0].string

    # print("Transaction %s" % s("transaction-date"))

    results = open(os.path.join("test_results", 'ad%s.csv' % d), "w+")
    errors = open(os.path.join("test_results", 'errors%s.txt' % d), "w+")
    warnings = open(os.path.join("test_results", 'warnings%s.txt' % d), "w+")

    t3 = time()

    print("DTD %s, DP %s, AK %s, D %s" % (dtd, date_produced, ak, d))
    print("Time gathering zip info: %s" % (t3 - t2))

    # Patent.set_zip_info(dtd, date_produced, ak, d)
    # p = Patent(example)
    # p.set_file(results)
    # p.print_csv_titles()
    # p.print_csv()

    Patent.set_zip_info(dtd, date_produced, ak, d)
    first = True
    t4 = time()
    counter = 1
    for i in xrange(1, len(patents)-1):
        if counter < 5:
            elem = patents[i]
            t_x_1 = time()
            p = Patent(elem)
            t_x_2 = time()
            # print("[%s]\nInit %s" % (i, t_x_2-t_x_1))
            process += (t_x_2 - t_x_1)
            p.set_file(results)
            if first:
                p.print_csv_titles()
                first = False
            if p.is_valid():
                tv1 = time()
                p.print_csv()
                counter += 1
                tv2 = time()
                if counter % 10000:
                    print("Printing %s" % (tv2-tv1), end="")
                    print("%s OK" % i)
                printing += (tv2-tv1)
                if p.has_warnings():
                    print(p.get_warnings(), file=warnings)
            else:
                print("\n%s Not valid %s " % (i, p.errors))
                print("[%s] %s %s\n" % (i, elem, p.errors), file=errors)
            t5 = time()
            # print("Total time: %s\n\n" % (t5-t4))
            total += (t5-t4)
            t4 = t5

    if first:
        Patent.print_empty_titles(results)
        Patent.print_zip_info(results)

    print("Path %s" % results.name)
    global zip_results
    zip_results.write(results.name)

    results.close()

    os.remove(results.name)


    print("Processing %s\nPrinting %s\nTotal %s, count: %s" % (process / counter , printing / counter, total / counter, counter))

if __name__ == "__main__":

    path1 = "test_results"
    if os.path.exists(path1):
        shutil.rmtree(path1)
    os.makedirs(path1)

    files = ["/home/kurtz/xlin/Projects/patents/test_files/ad20121231-01.xml",
             "/home/kurtz/xlin/Projects/patents/test_files/ad20130101.xml",
             "/home/kurtz/xlin/Projects/patents/test_files/ad20140101.xml",
             "/home/kurtz/xlin/Projects/patents/test_files/ad20140102.xml",
             "/home/kurtz/xlin/Projects/patents/test_files/ad20150101.xml"]

    # files = ["/home/kurtz/xlin/Projects/patents/test_files/ad20130101.xml"]


    zip_results = zipfile.ZipFile("%s/tests_results.zip" % path1, "w", zipfile.ZIP_DEFLATED)
    for patent in files:
        print("Starting zip %s" % patent)
        process_zip(open(patent, "r").read())

    zip_results.close()
