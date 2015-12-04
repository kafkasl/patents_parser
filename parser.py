# -*- coding: utf8 -*-
from __future__ import print_function
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import datetime
from time import time



patent = "<patent-assignment><assignment-record><reel-no>29862</reel-no><frame-no>645</frame-no><last-update-date><date>20130225</date></last-update-date><purge-indicator>N</purge-indicator><recorded-date><date>20130222</date></recorded-date><page-count>3</page-count><correspondent><name>KNOBBE, MARTENS, OLSON &amp; BEAR, LLP</name><address-1>2040 MAIN STREET, 14TH FLOOR</address-1><address-2>IRVINE, CA 92614</address-2></correspondent><conveyance-text>CORRECTIVE ASSIGNMENT TO CORRECT THE CONVEYING PARTY'S LAST NAME AND RECEIVING PARTY'S STREET NAME PREVIOUSLY RECORDED ON REEL/FRAME 028805/0592.</conveyance-text></assignment-record><patent-assignors><patent-assignor><name>D&#220;RR, MATTHIAS</name><execution-date><date>20120808</date></execution-date></patent-assignor></patent-assignors><patent-assignees><patent-assignee><name>FERAG AG</name><address-1>Z&#220;RICHSTRASSE 74</address-1><city>HINWIL</city><country-name>SWITZERLAND</country-name><postcode>8340</postcode></patent-assignee></patent-assignees><patent-properties><patent-property><document-id><country>US</country><doc-number>13514911</doc-number><kind>X0</kind><date>20120817</date></document-id><document-id><country>US</country><doc-number>20120310402</doc-number><kind>A1</kind><date>20121206</date></document-id><invention-title lang='en'>CONTROL APPARATUS AND METHOD FOR CONTROLLING A PRINTED-PRODUCT PROCESSING SYSTEM</invention-title></patent-property></patent-properties></patent-assignment>"


def is_string(a):
    try:
        a = str(a)
    except:
        return False
    return type(a) == str or type(a) == NavigableString


def is_numeric(a):
    float_t = True
    int_t = True
    try:
        int(a)
    except:
        int_t = False
    try:
        float(a)
    except:
        float_t = False
    return float_t or int_t

def is_valid(date_text):
    date_text = str(date_text)
    try:
        datetime.datetime.strptime(date_text, '%Y%m%d')
    except ValueError:
        return False
    return True

class Patent(object):
    """docstring for Patent"""

    CSV_TITLES = ["dtd-version", "date-produced",   "action-key-code",
     "date",  "reel-no", "frame-no", "date2", "purge-indicator", "date3",
     "page-count",  "name",    "address-1",   "address-2",   "address-3",
     "address-4",   "conveyance-text", "name4",   "date5",   "name6",
     "address-17", "city", "country-name", "postcode", "state", "address-28",
     "country", "doc-number",  "kind", "date9", "invention-title", "lang"]

    CSV_FIELDS = ["dtd_version", "date_produced",   "action_key_code",
     "date",  "reel_no", "frame_no", "date2", "purge_indicator", "date3",
     "page_count",  "name",    "address_1",   "address_2",   "address_3",
     "address_4",   "conveyance_text", "name4",   "date5",   "name6",
     "address_17", "city", "country_name", "postcode", "state", "address_28",
     "country", "doc_number",  "kind", "date9", "invention_title", "lang"]

    action_key_codes = ["DA", "WK", "BI", "AN"]

    dtd_version = None

    action_key_code = None
    transaction_date = None
    patent_assignments = None
    data_available_code = None

    def __init__(self, str_patent):
        super(Patent, self).__init__()

        soup = BeautifulSoup(str_patent, "lxml")

        patent = soup.contents[0].contents[0].contents[0]

        assignment_record = patent.contents[0]
        patent_assignors = patent.contents[1]
        patent_assignees = patent.contents[2]
        patent_properties = patent.contents[3]

        self.assignment_record = self.read_attrs(assignment_record)
        self.assignment_record["correspondent"] = self.read_attrs(
            assignment_record.find_all("correspondent")[0])

        self.patent_assignors = []
        for assignor in patent_assignors.contents:
            self.patent_assignors.append(self.read_attrs(assignor))

        self.patent_assignees = []
        for assignee in patent_assignees.contents:
            self.patent_assignees.append(self.read_attrs(assignee))

        self.patent_properties = []
        for prop in patent_properties.contents:
            p_props = self.read_attrs(prop)
            try:
                p_props["lang"] = prop("invention-title")[0]["lang"]
            except:
                pass
            ids = []
            for doc in prop.find_all("document-id"):
                ids.append(self.read_attrs(doc))
            del p_props["document-id"]
            p_props["document-ids"] = ids
            self.patent_properties.append(p_props)

        self.errors = []
        self.warnings = []

    def set_file(self, filetowrite):
        self.file = filetowrite

    @classmethod
    def set_zip_info(cls, dtd, dp, ak, d):
        cls.dtd_version = dtd
        cls.date_produced = dp
        cls.action_key_code = ak
        cls.transaction_date = d

    @classmethod
    def print_zip_info(cls, r_file):
        print(cls.dtd_version + "," + cls.date_produced + "," +
              cls.action_key_code + "," + cls.transaction_date + "," + "N", file=r_file)

    @classmethod
    def print_empty_titles(cls, r_file):
        for i in xrange(0, 4):
            print(Patent.CSV_TITLES[i] + ",", file=r_file, end="")
        print("data-available-code", file=r_file)

    def read_attrs(self, node):
        attrs = {}
        if len(node.contents) < 1:
            raise Exception("Node %s has no attributes" % node.name)

        for attr in node.contents:
            attrs[attr.name] = attr.string
        return attrs

    def is_valid(self):
        valid = True
        i = 0
        for field in Patent.CSV_FIELDS:
            try:
                i += 1
                getattr(self, "check_" + field)()
            except Exception, e:
                print("exception [%s, %s]\n" % (field, str(e)))
                pass
        if (not i == len(Patent.CSV_FIELDS)) or self.errors:
            print("I, len, errors: %s, %s, %s" % (i, len(Patent.CSV_FIELDS), self.errors))
            valid = False

        return valid

    def has_warnings(self):
        if self.warnings:
            return True
        return False

    def get_warnings(self):
        return self.warnings

    def get_errors(self):
        return self.errors

    def lines_to_print(self):
        seen = 0

        for index, prop in enumerate(self.patent_properties):
            seen += len(prop["document-ids"])

        size = max(len(self.patent_assignees), len(self.patent_assignors), seen)
        # print "Lengths: %s, %s, %s" % (len(self.patent_assignees), len(self.patent_assignors), seen)
        return size

    def print_csv_titles(self):
        titles = ""
        for i, title in enumerate(Patent.CSV_TITLES):
            if i > 0:
                titles += ","
            titles += title
        self.file.write(titles+"\n")

    def print_csv(self):
        lines = ""
        for i in xrange(0, self.lines_to_print()):
            lines += self.print_csv_line(i)
        self.file.write(lines)

    def print_csv_line(self, i):
        line = ""
        for (x, attr) in enumerate(Patent.CSV_FIELDS):
            try:
                if x > 0:
                    line += ","
                res = getattr(self, "get_" + attr)(i)
                if type(res) == NavigableString:
                    res = str(res)
                if type(res) == str:
                    res = res.replace(",", " ")
                if not res:
                    res = " "
                line += res
            except:
                pass
        line += "\n"
        return line

    def get_dtd_version(self, i):
        return self.dtd_version

    def get_date_produced(self, i):
        return self.date_produced

    def get_action_key_code(self, i):
        return self.action_key_code

    def get_date(self, i):
        return self.transaction_date

    def get_reel_no(self, i):
        return self.assignment_record["reel-no"]

    def get_frame_no(self, i):
        return self.assignment_record["frame-no"]

    def get_date2(self, i):
        return self.assignment_record["last-update-date"]

    def get_purge_indicator(self, i):
        return self.assignment_record["purge-indicator"]

    def get_date3(self, i):
        return self.assignment_record["recorded-date"]

    def get_page_count(self, i):
        return self.assignment_record["page-count"]

    def get_name(self, i):
        return self.assignment_record["correspondent"]["name"]

    def get_address_1(self, i):
        return self.assignment_record["correspondent"]["address-1"]

    def get_address_2(self, i):
        return self.assignment_record["correspondent"]["address-2"]

    def get_address_3(self, i):
        return self.assignment_record["correspondent"]["address-3"]

    def get_address_4(self, i):
        return self.assignment_record["correspondent"]["address-4"]

    def get_conveyance_text(self, i):
        return str(self.assignment_record["conveyance-text"])

    def get_name4(self, i):
        if i < len(self.patent_assignors):
            return str(self.patent_assignors[i]["name"])

    def get_date5(self, i):
        if i < len(self.patent_assignors):
            return self.patent_assignors[i]["execution-date"]

    def get_name6(self, i):
        if i < len(self.patent_assignees):
            return str(self.patent_assignees[i]["name"])

    def get_address_17(self, i):
        if i < len(self.patent_assignees):
            return str(self.patent_assignees[i]["address-1"])

    def get_city(self, i):
        if i < len(self.patent_assignees):
            return str(self.patent_assignees[i]["city"])

    def get_country_name(self, i):
        if i < len(self.patent_assignees):
            try:
                return str(self.patent_assignees[i]["country-name"])
            except:
                return ""

    def get_postcode(self, i):
        if i < len(self.patent_assignees):
            return self.patent_assignees[i]["postcode"]

    def get_state(self, i):
        if i < len(self.patent_assignees):
            try:
                return str(self.patent_assignees[i]["state"])
            except:
                return ""

    def get_address_28(self, i):
        if i < len(self.patent_assignees):
            return self.patent_assignees[i]["address-2"]

    def get_country(self, i):
        seen = 0
        # print self.patent_properties

        for index, prop in enumerate(self.patent_properties):
            if i > (len(prop["document-ids"]) + seen - 1):
                seen += len(prop["document-ids"])
            else:
                return prop["document-ids"][i-seen]["country"]

    def get_doc_number(self, i):
        seen = 0
        for index, prop in enumerate(self.patent_properties):
            if i > (len(prop["document-ids"]) + seen - 1):
                seen += len(prop["document-ids"])
            else:
                return prop["document-ids"][i-seen]["doc-number"]

    def get_kind(self, i):
        seen = 0
        for index, prop in enumerate(self.patent_properties):
            if i > (len(prop["document-ids"]) + seen - 1):
                seen += len(prop["document-ids"])
            else:
                return prop["document-ids"][i-seen]["kind"]

    def get_date9(self, i):
        seen = 0
        for index, prop in enumerate(self.patent_properties):
            if i > (len(prop["document-ids"]) + seen - 1):
                seen += len(prop["document-ids"])
            else:
                return prop["document-ids"][i-seen]["date"]

    def get_invention_title(self, i):
        seen = 0
        for index, prop in enumerate(self.patent_properties):
            if i > (len(prop["document-ids"]) + seen - 1):
                seen += len(prop["document-ids"])
            else:
                return prop["invention-title"]

    def get_lang(self, i):
        seen = 0
        for index, prop in enumerate(self.patent_properties):
            if i > (len(prop["document-ids"]) + seen - 1):
                seen += len(prop["document-ids"])
            else:
                return prop["lang"]

    def check_dtd_version(self):
        try:
            dtd = self.get_dtd_version(0)
            if not dtd:
                self.warnings.append({"dtd-version": "empty field"})
            dtd = float(dtd)
            if not is_numeric(dtd):
                self.errors.append({"dtd-version": "NaN value [%s]" % self.get_dtd_version(0)})
            if not dtd == 0.3:
                self.errors.append({"dtd-version": "version is not 0.3"})
        except:
            self.warnings.append({"dtd-version": "not found"})

    def check_date_produced(self):
        try:
            if not self.get_date_produced(0):
                self.warnings.append({"date-produced": "empty field"})
            if not is_valid(self.get_date_produced(0)):
                self.errors.append({"date-produced": "invalid date %s" % self.get_date_produced(0)})
        except:
            self.warnings.append({"date-produced": "not found"})

    def check_action_key_code(self):
        try:
            if self.get_action_key_code(0) not in self.action_key_codes:
                self.errors.append(
                    {"action_key_code": "Invalid action key code: [%s]" % self.get_action_key_code(0)})
        except:
            self.warnings.append({"action_key_code": "not found"})

    def check_date(self):
        try:
            if not self.get_date(0):
                self.warnings.append({"date": "empty field"})
            if not is_valid(self.get_date(0)):
                self.errors.append({"date": "invalid date %s" % self.get_date()})
        except:
            self.warnings.append({"date": "not found"})

    def check_reel_no(self):
        try:
            reel_no = int(self.get_reel_no(0))
            if not reel_no:
                self.warnings.append({"reel-no": "empty field"})
            if not is_numeric(reel_no):
                self.errors.append({"reel-no": "NaN value"})
            if reel_no < 0 or reel_no > 999999:
                self.errors.append({"reel-no": "too long / short [%s]" % reel_no})
        except:
            self.warnings.append({"reel-no": "not found"})

    def check_frame_no(self):
        try:
            frame_no = int(self.get_frame_no(0))
            if not frame_no:
                self.warnings.append({"frame_no": "empty field"})
            if not is_numeric(frame_no):
                self.errors.append({"frame-no": "NaN value"})
            if frame_no < 0 or frame_no > 9999:
                self.errors.append({"frame-no": "too long / short [%s]" % frame_no})
        except:
            self.warnings.append({"frame-no": "not found"})

    def check_date2(self):
        try:
            if not self.get_date2(0):
                self.warnings.append({"date2": "empty field"})
            if not is_valid(self.get_date2(0)):
                self.errors.append({"date2": "invalid date %s" % self.get_date2(0)})
        except:
            self.warnings.append({"date2": "not found"})

    def check_purge_indicator(self):
        try:
            if not self.get_purge_indicator(0):
                self.warnings.append({"purge-indicator": "empty field"})
            pi = self.get_purge_indicator(0)
            if pi != "Y" and pi != "N":
                self.errors.append[{"purge-indicator": "incorrect value [%s]" % pi}]
        except:
            self.warnings.append({"purge-indicator": "not found"})

    def check_date3(self):
        try:
            if not self.get_date3(0):
                self.warnings.append({"date3": "empty field"})
            if not is_valid(self.get_date3(0)):
                self.errors.append({"date3": "invalid date %s" % self.get_date3()})
        except:
            self.warnings.append({"date3": "not found"})

    def check_page_count(self):
        try:
            if not self.get_page_count(0):
                self.warnings.append({"page-count": "empty field"})
            if not is_numeric(self.get_page_count(0)):
                self.errors.append({"page-count": "NaN value"})
        except:
            self.warnings.append({"page-count": "not found"})

    def check_name(self):
        try:
            if not self.get_name(0):
                self.warnings.append({"name": "empty field"})
        except:
            self.warnings.append({"name": "not found"})

    def check_address_1(self):
        try:
            if not self.get_address_1(0):
                self.warnings.append({"address1": "empty field"})
        except:
            self.warnings.append({"address1": "not found"})

    def check_address_2(self):
        return
    #     if not self.get_name():
    #    warningself.errors.append({"name": "empty field"})

    def check_address_3(self):
        return
    #     if not self.get_name():
    #    warningself.errors.append({"name": "empty field"})

    def check_address_4(self):
        return
    #     if not self.get_name():
    #    warningself.errors.append({"name": "empty field"})

    def check_conveyance_text(self):
        try:
            if not self.get_conveyance_text(0):
                self.warnings.append({"conveyance-text": "empty field"})
            if not is_string(self.get_conveyance_text(0)):
                self.errors.append({"conveyance-text": "not a string [%s]" % type(self.get_conveyance_text(0))})
        except:
            self.warnings.append({"conveyance-text": "not found"})

    def check_name4(self):
        try:
            if not self.get_name4(0):
                self.warnings.append({"name4": "empty field"})
            if not is_string(self.get_name4(0)):
                self.errors.append({"name4": "not a string [%s]" % type(self.get_name4(0))})
        except:
            self.warnings.append({"name4": "not found"})

    def check_date5(self):
        try:
            if not self.get_date5(0):
                self.warnings.append({"date5": "empty field"})
            if not is_valid(self.get_date5(0)):
                self.errors.append({"date5": "invalid date %s" % type(self.get_date5())})
        except:
            self.warnings.append({"date5": "not found"})

    def check_name6(self):
        try:
            if not self.get_name6(0):
                self.warnings.append({"name6": "empty field"})
            if not is_string(self.get_name6(0)):
                self.errors.append({"name6": "not a string [%s]" % type(self.get_name6(0))})
        except:
            self.warnings.append({"name6": "not found"})

    def check_address_17(self):
        # print("Checking address 17", end="")
        try:
            address = self.get_address_17(0)
            if not address:
                self.warnings.append({"address_17": "empty field"})
            if not is_string(self.get_address_17(0)):
                self.errors.append({"address_17": "not a string [%s]" % type(address)})
        except:
            self.warnings.append({"address_17": "not found"})
            # import os
            # warnings = open(os.path.join("trials_chunk", 'address_17.txt'), "w+")
            # print(self.patent, file=warnings)

        # print("done")

    def check_city(self):
        try:
            if not self.get_city(0):
                self.warnings.append({"city": "empty field"})
            if not is_string(self.get_city(0)):
                self.errors.append({"city": "not a string [%s]" % type(self.get_city(0))})
        except:
            self.warnings({"city": "not found"})

    def check_country_name(self):
        try:
            if not self.get_state(0) and not self.get_country_name(0):
                self.warnings.append({"country": "empty field and no state present"})
            if not is_string(self.get_country_name(0)):
                self.errors.append({"country-name": "not a string [%s]" % type(self.get_state(0))})
        except:
            self.warnings.append({"country-name": "not found"})

    def check_postcode(self):
        try:
            postcode = self.get_postcode(0)
            if not postcode:
                self.warnings.append({"postcode": "empty field"})
        except:
            self.warnings.append({"postcode": "not found"})

    def check_state(self):
        try:
            if not self.get_state(0) and not self.get_country_name(0):
                self.warnings.append({"state": "empty field and no country name present"})
            if not is_string(self.get_state(0)):
                self.errors.append({"state": "not a string [%s]" % type(self.get_state(0))})
        except:
            self.warnings.append({"state": "not found"})

    def check_address_28(self):
        try:
            if not self.get_name(0):
                self.warnings.append({"address28": "empty field"})
        except:
            self.warnings.append({"address28": "not found"})

    def check_country(self):
        try:
            if not self.get_country(0):
                self.warnings.append({"country": "empty field"})
        except:
            self.warnings.append({"country": "not found"})

    def check_doc_number(self):
        try:
            if not self.get_doc_number(0):
                self.warnings.append({"doc-number": "empty field"})
        except:
            self.warnings.append({"doc-number": "not found"})

    def check_kind(self):
        try:
            kind = self.get_kind(0)
            if not kind:
                self.warnings.append({"kind": "empty field"})
            if not (is_string(kind[0]) and is_numeric(kind[1])):
                self.errors.append({"kind": "no valid code [%s]" % kind})
        except:
            self.warnings.append({"kind": "not found"})

    def check_date9(self):
        try:
            if not self.get_date5(0):
                self.warnings.append({"date5": "empty field"})
            if not is_valid(self.get_date5(0)):
                self.errors.append({"date5": "invalid date %s" % self.get_date5()})
        except:
            self.warnings.append({"date5": "not found"})

    def check_invention_title(self):
        try:
            if not self.get_invention_title(0):
                self.warnings.append({"invention-title": "empty field"})
        except:
            self.warnings.append({"invention-title": "not found"})

    def check_lang(self):
        try:
            if not self.get_lang(0):
                self.warnings.append({"lang": "empty field"})
        except:
            self.warnings.append({"lang": "not found"})

trial = open("trial.csv", "w+")
# patent = open("patent.txt").read()
p = Patent(patent)
p.set_file(trial)

dtd = 0.3
dp = 20031112
ak = "AN"
d = 20130117

Patent.set_zip_info(dtd, dp, ak, d)
if p.is_valid():
    print("valid")
    p.print_csv_titles()
    p.print_csv()
else:
    print(p.errors)

p.print_csv()
