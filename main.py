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
        p = Patent(elem)
        p.set_file(results)
        if first:
            p.print_csv_titles()
            first = False
        if p.is_valid():
            p.print_csv()
            print "[%s] Valid line" % i
        else:
            print p.errors
            print >> errors, "[%s] %s %s" % (i, elem, p.errors)
        t5 = time()
        print "Processing time: %s" % (t5-t4)
        t4 = t5

    if first:
        Patent.print_empty_titles(results)
        Patent.print_zip_info(results)


if __name__ == "__main__":

    path = "results"
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    pfm = PatentsFileManager().get_patent_generator()

    for zip_data in pfm:
        process_zip(zip_data)
    # pool = Pool(processes=4)
    # result = []         # start 4 worker processes
    # # pool.map(process_zip, [pfm.next()])
    # for data in pfm:
    #     result.append(pool.apply_async(process_zip, [data]) )   # evaluate "f(10)"

    # for r in result:
    #     result.get()
    # p = Pool(4)
    # p.map(process_zip, pfm)
        # p = multiprocessing.Process(target=worker, args=(i,))
        # jobs.append(p)
        # p.start()


    # results = open('results.csv', "w+")
    # errors = open('errors.txt', "w+")

    # data = pfm.next()
