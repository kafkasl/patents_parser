# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from collections import OrderedDict
import urllib2, re, sys, signal, os



patent = "<patent-assignment><assignment-record><reel-no>15946</reel-no><frame-no>343</frame-no><last-update-date><date>20130117</date></last-update-date><purge-indicator>N</purge-indicator><recorded-date><date>20050425</date></recorded-date><page-count>9</page-count><correspondent><name>GEORGE R. SCHULTZ</name><address-1>5400 LBJ FREEWAY</address-1><address-2>SUITE 1200</address-2><address-3>DALLAS, TX 75240</address-3></correspondent><conveyance-text>ASSIGNMENT OF ASSIGNORS INTEREST (SEE DOCUMENT FOR DETAILS).</conveyance-text></assignment-record><patent-assignors><patent-assignor><name>EASTWOOD, IAN M</name><execution-date><date>20050425</date></execution-date></patent-assignor><patent-assignor><name>DORLAND, ERWIN</name><execution-date><date>20050425</date></execution-date></patent-assignor><patent-assignor><name>AL-JAFARI, MOHAMMED SALEM</name><execution-date><date>20050412</date></execution-date></patent-assignor><patent-assignor><name>GOODALL, DAVID M</name><execution-date><date>20050425</date></execution-date></patent-assignor><patent-assignor><name>BERGSTROM, EDMUND T</name><execution-date><date>20050425</date></execution-date></patent-assignor></patent-assignors><patent-assignees><patent-assignee><name>AUTHENTIX, INC.</name><address-1>4355 EXCEL PARKWAY</address-1><address-2>SUITE 100</address-2><city>ADDISON</city><state>TEXAS</state><postcode>75001</postcode></patent-assignee></patent-assignees><patent-properties><patent-property><document-id><country>US</country><doc-number>10852336</doc-number><kind>X0</kind><date>20040524</date></document-id><document-id><country>US</country><doc-number>20050260764</doc-number><kind>A1</kind><date>20051124</date></document-id><document-id><country>US</country><doc-number>7919325</doc-number><kind>B2</kind><date>20110405</date></document-id><invention-title lang='en'>METHOD AND APPARATUS FOR MONITORING LIQUID FOR THE PRESENCE OF AN ADDITIVE</invention-title></patent-property></patent-properties></patent-assignment>"


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

    def pprint(self):
        lines_to_print = max()
        print self.get_dtd_version() + ",",
        print self.get_date_produced() + ",",
        print self.get_date_produced() + ",",

    def print_csv_titles(self):
        for i, title in enumerate(Patent.CSV_TITLES):
            if i > 0:
                print ",",
            print title,
        print

    def print_csv_line(self, i):
        for (x, attr) in enumerate(Patent.CSV_FIELDS):
            try:
                if x > 0:
                    print ",",
                res = getattr(self, "get_" + attr)(i)
                if type(res) == NavigableString:
                    res = str(res)
                if type(res) == str:
                    res = res.replace(",", " ").replace("."," ")
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
            if i > (len(prop["document-ids"]) + seen -1):
                seen += len(prop["document-ids"])
            else:
                return prop["document-ids"][i-seen]["country"]

    def get_doc_number(self, i):
        seen = 0
        for index, prop in enumerate(self.patent_properties):
            if i > (len(prop["document-ids"]) + seen -1):
                seen += len(prop["document-ids"])
            else:
                return prop["document-ids"][i-seen]["doc-number"]

    def get_kind(self, i):
        seen = 0
        for index, prop in enumerate(self.patent_properties):
            if i > (len(prop["document-ids"]) + seen -1):
                seen += len(prop["document-ids"])
            else:
                return prop["document-ids"][i-seen]["kind"]

    def get_date9(self, i):
        seen = 0
        for index, prop in enumerate(self.patent_properties):
            if i > (len(prop["document-ids"]) + seen -1):
                seen += len(prop["document-ids"])
            else:
                return prop["document-ids"][i-seen]["date"]

    def get_invention_title(self, i):
        seen = 0
        for index, prop in enumerate(self.patent_properties):
            if i > (len(prop["document-ids"]) + seen -1):
                seen += len(prop["document-ids"])
            else:
                return prop["invention-title"]

    def get_lang(self, i):
        seen = 0
        for index, prop in enumerate(self.patent_properties):
            if i > (len(prop["document-ids"]) + seen -1):
                seen += len(prop["document-ids"])
            else:
                return prop["lang"]

p = Patent(patent)

dtd = 0.3
dp = 20031112
ak = "AN"
d = 20130117

Patent.set_zip_info(dtd, dp, ak, d)
p.print_csv_titles()
p.print_csv_line(0)
# p.print_csv()
