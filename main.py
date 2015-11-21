# -*- coding: utf8 -*-

from PatentsFileManager import PatentsFileManager
from bs4 import BeautifulSoup


pfm = PatentsFileManager().get_patent_generator()

data = pfm.next()

print "Data downloaded"
s = BeautifulSoup(data, "lxml")

dtd = s("us-patent-assignments")["dtd-version"]
date_produced = s("us-patent-assignments")["date-produced"]

print "DTD %s, DP %s" % (dtd, date_produced)
for elem in s.find_all("patent-assignment"):
    p = Patent(elem)
p = Patent(patent)

dtd = 0.3
dp = 20031112
ak = "AN"
d = 20130117

Patent.set_zip_info(dtd, dp, ak, d)
p.print_csv_titles()
p.print_csv_line(0)
