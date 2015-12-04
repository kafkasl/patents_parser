# -*- coding: utf8 -*-
from __future__ import print_function
from PatentsFileManager import PatentsFileManager
from bs4 import BeautifulSoup
from time import time
import os
import shutil


# @task()
def process_zip_line(data):
    from linear_parser import Patent
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
    d = s("transaction-date")[0].string

    results = open(os.path.join("trials_line", 'ad%s.csv' % d), "w+")
    errors = open(os.path.join("trials_line", 'errors%s.txt' % d), "w+")

    t3 = time()

    print("DTD %s, DP %s, AK %s, Dp %s" % (dtd, date_produced, ak, d))
    print("Time gathering zip info: %s" % (t3 - t2))

    # Patent.set_zip_info(dtd, date_produced, ak, d)
    # p = Patent(example)
    # p.set_file(results)
    # p.print_csv_titles()
    # p.print_csv()

    Patent.set_zip_info(dtd, date_produced, ak, d)
    first = True
    counter = 0
    t4 = time()
    for i in xrange(1, len(patents)-1):
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
            print("Printing %s" % (tv2-tv1))
            printing += (tv2-tv1)
        else:
            print(p.errors)
            print("[%s] %s %s" % (i, elem, p.errors), file=errors)
        t5 = time()
        print("Total time: %s\n\n" % (t5-t4))
        total += (t5-t4)
        t4 = t5

    if first:
        Patent.print_empty_titles(results)
        Patent.print_zip_info(results)

        print("Processing %s\nPrinting %s\nTotal %s, count: %s" % (process / counter , printing / counter, total / counter, counter))

def process_zip(data):
    from parser import Patent
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
    d = s("transaction-date")[0].string

    results = open(os.path.join("trials_chunk", 'ad%s.csv' % d), "w+")
    errors = open(os.path.join("trials_chunk", 'errors%s.txt' % d), "w+")
    warnings = open(os.path.join("trials_chunk", 'warnings%s.txt' % d), "w+")

    t3 = time()

    print("DTD %s, DP %s, AK %s, Dp %s" % (dtd, date_produced, ak, d))
    print("Time gathering zip info: %s" % (t3 - t2))

    # Patent.set_zip_info(dtd, date_produced, ak, d)
    # p = Patent(example)
    # p.set_file(results)
    # p.print_csv_titles()
    # p.print_csv()

    Patent.set_zip_info(dtd, date_produced, ak, d)
    first = True
    t4 = time()
    counter = 0
    for i in xrange(1, len(patents)-1):
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

    print("Processing %s\nPrinting %s\nTotal %s, count: %s" % (process / counter , printing / counter, total / counter, counter))


if __name__ == "__main__":

    path1 = "trials_chunk"
    path2 = "trials_line"
    for path in [path1, path2]:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
    pfm = PatentsFileManager().get_patent_generator()

    # for zip_data in pfm:
    zip_data = pfm.next()

    process_zip(zip_data)
    process_zip_line(zip_data)
