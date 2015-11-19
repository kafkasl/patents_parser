# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
from collections import OrderedDict
import urllib2, re, sys, signal, os


patent = "<patent-assignment><assignment-record><reel-no>15946</reel-no><frame-no>343</frame-no><last-update-date><date>20130117</date></last-update-date><purge-indicator>N</purge-indicator><record


class Patent(object):
    """docstring for Patent"""

    CSV_TITLES = ["dtd-version", "date-produced",   "action-key-code",
     "date",  "reel-no", "frame-no", "date2", "purge-indicator", "date3",
     "page-count",  "name",    "address-1",   "address-2",   "address-3",
     "address-4",   "conveyance-text", "name4",   "date5",   "name6",
     "address-17", "city", "country-name", "postcode", "state", "address-28",
     "country", "doc-number 1",  "kind 1", "date9 1", "doc-number 2", "kind 2",
     "date9 2", "invention-title", "lang"]

    CSV_FIELDS = ["dtd_version", "date_produced",   "action_key_code",
     "date",  "reel_no", "frame_no", "date2", "purge_indicator", "date3",
     "page_count",  "name",    "address_1",   "address_2",   "address_3",
     "address_4",   "conveyance_text", "name4",   "date5",   "name6",
     "address_17", "city", "country_name", "postcode", "state", "address_28",
     "country", "doc_number_1",  "kind_1", "date9_1", "doc_number_2", "kind_2",
     "date9_2", "invention_title", "lang"]

    action_key_codes = ["DA”, “WK”, “BI”, “AN"]

    def __init__(self, str_patent):
        super(Patent, self).__init__()

        soup = BeautifulSoup(str_patent, "lxml")

        patent = soup.contents[0].contents[0].contents[0]

        # self.dtd_version

        # # Parent element
        # self.us_patent_assignments = root_element

        #self.action_key_code = self.soup
        # self.transaction_date
        # self.patent_assignments
        # self.data_available_code

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
            ids = []
            for doc in prop.find_all("document-id"):
                ids.append(self.read_attrs(doc))
            del p_props["document-id"]
            p_props["document-ids"] = ids
            self.patent_properties.append(p_props)

    def read_attrs(self, node):
        attrs = {}
        if len(node.contents) < 1:
            raise Exception("Node %s has no attributes" % node.name)

        for attr in node.contents:
            attrs[attr.name] = attr.string
        return attrs

    def is_valid(self):
        if self.fields_are_valid:
            return self.check_integrity()

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

    def print_csv_line(self, i):
        for (x, attr) in enumerate(Patent.CSV_FIELDS):
            if x > 0:
                print ",",
            print getattr(self, "get_" + attr)(),

    def get_dtd_version(self):
        return self.dtd_version

    def get_date_produced(self):
        return self.date_produced

    def get_action_key_code(self):
        return self.action_key_code

    def get_date(self):
        return transaction_date

    def get_reel_no(self):
        return self.assignment_record["reel-no"]

    def get_frame_no(self):
        return self.assignment_record["frame-no"]

    def get_date2(self):
        return self.assignment_record["last-update-date"]

    def get_purge_indicator(self):
        return self.assignment_record["purge-indicator"]

    def get_date3(self):
        return self.assignment_record["recorded-date"]

    def get_page_count(self):
        return self.assignment_record["page-count"]

    # def get_name(self):

    # def get_address_1(self):

    # def get_address_2(self):

    # def get_address_3(self):

    # def get_address_4(self):

    # def get_conveyance_text(self):

    # def get_name4(self):

    # def get_date5(self):

    # def get_name6(self):

    # def get_address_17(self):

    # def get_city(self):

    # def get_country_name(self):

    # def get_postcode(self):

    # def get_state(self):

    # def get_address_28(self):

    # def get_country(self):

    # def get_doc_number_1(self):

    # def get_kind_1(self):

    # def get_date9_1(self):

    # def get_doc_number_2(self):

    # def get_kind_2(self):

    # def get_date_2(self):

    # def get_invention_title(self):

    # def get_lang(self):


p = Patent(patent)
p.print_csv_line(0)
# p.print_csv()
