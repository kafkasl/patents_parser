# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from collections import OrderedDict
import urllib2, re, sys, signal, os



patent = "<patent-assignment><assignment-record><reel-no>15946</reel-no><frame-no>343</frame-no><last-update-date><date>20130117</date></last-update-date><purge-indicator>N</purge-indicator><recorded-date><date>20050425</date></recorded-date><page-count>9</page-count><correspondent><name>GEORGE R. SCHULTZ</name><address-1>5400 LBJ FREEWAY</address-1><address-2>SUITE 1200</address-2><address-3>DALLAS, TX 75240</address-3></correspondent><conveyance-text>ASSIGNMENT OF ASSIGNORS INTEREST (SEE DOCUMENT FOR DETAILS).</conveyance-text></assignment-record><patent-assignors><patent-assignor><name>EASTWOOD, IAN M</name><execution-date><date>20050425</date></execution-date></patent-assignor><patent-assignor><name>DORLAND, ERWIN</name><execution-date><date>20050425</date></execution-date></patent-assignor><patent-assignor><name>AL-JAFARI, MOHAMMED SALEM</name><execution-date><date>20050412</date></execution-date></patent-assignor><patent-assignor><name>GOODALL, DAVID M</name><execution-date><date>20050425</date></execution-date></patent-assignor><patent-assignor><name>BERGSTROM, EDMUND T</name><execution-date><date>20050425</date></execution-date></patent-assignor></patent-assignors><patent-assignees><patent-assignee><name>AUTHENTIX, INC.</name><address-1>4355 EXCEL PARKWAY</address-1><address-2>SUITE 100</address-2><city>ADDISON</city><state>TEXAS</state><postcode>75001</postcode></patent-assignee></patent-assignees><patent-properties><patent-property><document-id><country>US</country><doc-number>10852336</doc-number><kind>X0</kind><date>20040524</date></document-id><document-id><country>US</country><doc-number>20050260764</doc-number><kind>A1</kind><date>20051124</date></document-id><document-id><country>US</country><doc-number>7919325</doc-number><kind>B2</kind><date>20110405</date></document-id><invention-title lang='en'>METHOD AND APPARATUS FOR MONITORING LIQUID FOR THE PRESENCE OF AN ADDITIVE</invention-title></patent-property></patent-properties></patent-assignment>"

def is_string(a):
    return type(a) == str or type(a) == NavigableString

def is_numeric(a):
    try:
        int(a)
    except:
        return False
    return True

def is_valid(date_text):
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

    action_key_codes = ["DA”, “WK”, “BI”, “AN"]

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
            p_props["lang"] = prop("invention-title")[0]["lang"]
            ids = []
            for doc in prop.find_all("document-id"):
                ids.append(self.read_attrs(doc))
            del p_props["document-id"]
            p_props["document-ids"] = ids
            self.patent_properties.append(p_props)

    @classmethod
    def set_zip_info(cls, dtd, dp, ak, d):
        cls.dtd_version = dtd
        cls.date_produced = dp
        cls.action_key_code = ak
        cls.transaction_date = d

    def read_attrs(self, node):
        attrs = {}
        if len(node.contents) < 1:
            raise Exception("Node %s has no attributes" % node.name)

        for attr in node.contents:
            attrs[attr.name] = attr.string
        return attrs

    def check_integrity(self):
        valid = True
        for key, value in Patent.__dict__.items():
            if not key.startswith("__"):
                errors = getattr(self, "check_" + key)()
                if errors:
                    self.errors.extend(errors)

        if self.errors:
            valid = False

        return valid

    def check_assignment_record(self):
        valid = True
        return valid

    def check_patent_assignors(self):
        valid = True
        return valid

    def check_patent_assignees(self):
        valid = True
        return valid

    def check_patent_properties(self):
        valid = True
        return valid

    # def check_action_key_code(self):
    #     errors = []
    #     if self.action_key_code not in self.action_key_codes:
    #         errors.append(
    #             {"action_key_code": "Invalid action key code: [%s]" % self.action_key_code})
    #     return errors

    def lines_to_print(self):
        seen = 0

        for index, prop in enumerate(self.patent_properties):
            seen += len(prop["document-ids"])

        size = max(len(self.patent_assignees), len(self.patent_assignors), seen)
        print "Lengths: %s, %s, %s" % (len(self.patent_assignees), len(self.patent_assignors), seen)
        return size

    def print_csv_titles(self):
        for i, title in enumerate(Patent.CSV_TITLES):
            if i > 0:
                print ",",
            print title,
        print

    def print_csv(self):
        for i in xrange(0, self.lines_to_print()):
            self.print_csv_line(i)

    def print_csv_line(self, i):
        for (x, attr) in enumerate(Patent.CSV_FIELDS):
            try:
                if x > 0:
                    print ",",
                res = getattr(self, "get_" + attr)(i)
                if type(res) == NavigableString:
                    res = str(res)
                if type(res) == str:
                    res = res.replace(",", " ").replace(".", " ")
                if not res:
                    res = " "
                print res,
            except:
                pass
        print

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
        return self.assignment_record["conveyance-text"]

    def get_name4(self, i):
        if i < len(self.patent_assignors):
            return self.patent_assignors[i]["name"]

    def get_date5(self, i):
        if i < len(self.patent_assignors):
            return self.patent_assignors[i]["execution-date"]

    def get_name6(self, i):
        if i < len(self.patent_assignees):
            return self.patent_assignees[i]["name"]

    def get_address_17(self, i):
        if i < len(self.patent_assignees):
            return self.patent_assignees[i]["address-1"]

    def get_city(self, i):
        if i < len(self.patent_assignees):
            return self.patent_assignees[i]["city"]

    def get_country_name(self, i):
        if i < len(self.patent_assignees):
            try:
                return self.patent_assignees[i]["country-name"]
            except:
                return ""

    def get_postcode(self, i):
        if i < len(self.patent_assignees):
            return self.patent_assignees[i]["postcode"]

    def get_state(self, i):
        if i < len(self.patent_assignees):
            try:
                return self.patent_assignees[i]["state"]
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


    # def check_dtd_version(self):

    # def check_date_produced(self):

    # def check_action_key_code(self):

    # def check_date(self):

    def check_reel_no(self):
        reel_no = self.get_reel_no()
        if not reel_no:
            self.errors.append({"reel-no": "empty field"})
        if not is_numeric(reel_no):
            self.errors.append({"reel-no": "NaN value"})
        if reel_no < 0 or reel_no > 999999:
            self.errors.append({"reel-no": "too long / short"})

    def check_frame_no(self):
        frame_no = self.get_frame_no()
        if not frame_no():
            self.errors.append({"frame_no": "empty field"})
        if not is_numeric(frame_no):
            self.errors.append({"frame-no": "NaN value"})
        if frame_no < 0 or frame_no > 9999:
            self.errors.append({"frame-no": "too long / short"})

    def check_date2(self):
        if not self.get_date2():
            self.errors.append({"date2": "empty field"})
        if not is_valid(self.get_date2()):
            self.errors.append({"date2": "invalid date %s" % self.get_date2()})

    def check_purge_indicator(self):
        if not self.get_purge_indicator():
            self.errors.append({"purge-indicator": "empty field"})
        pi = self.get_purge_indicator()
        if pi != "Y" and pi != "N":
            self.errors.append[{"purge-indicator": "incorrect value [%s]" % pi}]

    def check_date3(self):
        if not self.get_date3():
            self.errors.append({"date3": "empty field"})
        if not is_valid(self.get_date3()):
            self.errors.append({"date3": "invalid date %s" % self.get_date3()})

    def check_page_count(self):
        if not self.get_page_count():
            self.errors.append({"page-count": "empty field"})
        if not is_numeric(self.get_page_count()):
            self.errors.append({"page-count": "NaN value"})

    def check_name(self):
        if not self.get_name():
            self.errors.append({"name": "empty field"})

    def check_address_1(self):
        if not self.get_address_1():
            self.errors.append({"address1": "empty field"})

    # def check_address_2(self):
    #     if not self.get_name():
    #         self.errors.append({"name": "empty field"})

    # def check_address_3(self):
    #     if not self.get_name():
    #         self.errors.append({"name": "empty field"})

    # def check_address_4(self):
    #     if not self.get_name():
    #         self.errors.append({"name": "empty field"})

    def check_conveyance_text(self):
        if not self.get_conveyance_text():
            self.errors.append({"conveyance-text": "empty field"})
        if not is_string(self.get_conveyance_text):
            self.errors.append({"conveyance-text": "not a string"})

    def check_name4(self):
        if not self.get_name4():
            self.errors.append({"name4": "empty field"})
        if not is_string(self.get_name4()):
            self.errors.append({"name4": "not a string"})

    def check_date5(self):
        if not self.get_date5():
            self.errors.append({"date5": "empty field"})
        if not is_valid(self.get_date5()):
            self.errors.append({"date5": "invalid date %s" % self.get_date5()})

    def check_name6(self):
        if not self.get_name6():
            self.errors.append({"name6": "empty field"})
        if not is_string(self.get_name6()):
            self.errors.append({"name6": "not a string"})

    def check_address_17(self):
        if not self.get_address_17():
            self.errors.append({"address_17": "empty field"})
        if not is_string(self.get_address_17()):
            self.errors.append({"address_17": "not a string"})

    def check_city(self):
        if not self.get_name4():
            self.errors.append({"name4": "empty field"})
        if not is_string(self.get_name4()):
            self.errors.append({"name4": "not a string"})

    def check_country_name(self):
        if not self.get_name4():
            self.errors.append({"name4": "empty field"})
        if not is_string(self.get_name4()):
            self.errors.append({"name4": "not a string"})

    def check_postcode(self):
        if not self.get_name():
            self.errors.append({"name": "empty field"})

    def check_state(self):
        if not self.get_name():
            self.errors.append({"name": "empty field"})

    def check_address_28(self):
        if not self.get_name():
            self.errors.append({"name": "empty field"})

    def check_country(self):
        if not self.get_name():
            self.errors.append({"name": "empty field"})

    def check_doc_number(self):
        if not self.get_name():
            self.errors.append({"name": "empty field"})

    def check_kind(self):
        if not self.get_name():
            self.errors.append({"name": "empty field"})

    def check_date9(self):
        if not self.get_date5():
            self.errors.append({"date5": "empty field"})
        if not is_valid(self.get_date5()):
            self.errors.append({"date5": "invalid date %s" % self.get_date5()})

    def check_invention_title(self):
        if not self.get_name():
            self.errors.append({"name": "empty field"})

    def check_lang(self):
        if not self.get_name():
            self.errors.append({"name": "empty field"})


p = Patent(patent)

dtd = 0.3
dp = 20031112
ak = "AN"
d = 20130117

Patent.set_zip_info(dtd, dp, ak, d)
p.print_csv_titles()
p.print_csv()
# p.print_csv()
