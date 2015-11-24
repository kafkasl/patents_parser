# -*- coding: utf8 -*-

from PatentsFileManager import PatentsFileManager
from parser import Patent
from bs4 import BeautifulSoup
from time import time
import os
from pycompss.api.task import task
import shutil


# @task()
def process_zip(data):
    print "Processing zip..."
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
    print "Soup is ready...Time: %s" % (t2-t1)

    patents = data[index_1:index_2+len(usp_c)]
    patents = patents.split("<patent-assignment>")

    patents = ["<patent-assignment>" + p for p in patents]

    dtd = s("us-patent-assignments")[0]["dtd-version"]
    date_produced = s("us-patent-assignments")[0]["date-produced"]
    ak = s("action-key-code")[0].string
    d = s("transaction-date")[0].string

    results = open(os.path.join("results", 'ad%s.csv' % d), "w+")
    errors = open(os.path.join("results", 'errors%s.txt' % d), "w+")

    t3 = time()

    print "DTD %s, DP %s, AK %s, Dp %s" % (dtd, date_produced, ak, d)
    print "Time gathering zip info: %s" % (t3 - t2)

    # Patent.set_zip_info(dtd, date_produced, ak, d)
    # p = Patent(example)
    # p.set_file(results)
    # p.print_csv_titles()
    # p.print_csv()

    Patent.set_zip_info(dtd, date_produced, ak, d)
    first = True
    t4 = time()
    for i in xrange(1, len(patents)-1):
        elem = patents[i]
        t_x_1 = time()
        p = Patent(elem)
        t_x_2 = time()
        print "Init %s" % (t_x_2-t_x_1)
        process += (t_x_2 - t_x_1)
        p.set_file(results)
        if first:
            p.print_csv_titles()
            first = False
        if p.is_valid():
            tv1 = time()
            p.print_csv()
            tv2 = time()
            print "Printing %s" % (tv2-tv1)
            printing += (tv2-tv1)
        else:
            print p.errors
            print >> errors, "[%s] %s %s" % (i, elem, p.errors)
        t5 = time()
        print "Total time: %s\n\n" % (t5-t4)
        total += (t5-t4)
        t4 = t5

    if first:
        Patent.print_empty_titles(results)
        Patent.print_zip_info(results)

    print "Processing %s\nPrinting %s\nTotal %s" % (process, printing, total)


if __name__ == "__main__":

    path = "trials"
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    pfm = PatentsFileManager().get_patent_generator()

    # for zip_data in pfm:
    zip_data = pfm.next()
    process_zip(zip_data)
