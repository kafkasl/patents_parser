# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
from collections import OrderedDict
import urllib2, re, sys, signal, os


patent = "<patent-assignment><assignment-record><reel-no>15946</reel-no><frame-no>343</frame-no><last-update-date><date>20130117</date></last-update-date><purge-indicator>N</purge-indicator><recorded-date><date>20050425</date></recorded-date><page-count>9</page-count><correspondent><name>GEORGE R. SCHULTZ</name><address-1>5400 LBJ FREEWAY</address-1><address-2>SUITE 1200</address-2><address-3>DALLAS, TX 75240</address-3></correspondent><conveyance-text>ASSIGNMENT OF ASSIGNORS INTEREST (SEE DOCUMENT FOR DETAILS).</conveyance-text></assignment-record><patent-assignors><patent-assignor><name>EASTWOOD, IAN M</name><execution-date><date>20050425</date></execution-date></patent-assignor><patent-assignor><name>DORLAND, ERWIN</name><execution-date><date>20050425</date></execution-date></patent-assignor><patent-assignor><name>AL-JAFARI, MOHAMMED SALEM</name><execution-date><date>20050412</date></execution-date></patent-assignor><patent-assignor><name>GOODALL, DAVID M</name><execution-date><date>20050425</date></execution-date></patent-assignor><patent-assignor><name>BERGSTROM, EDMUND T</name><execution-date><date>20050425</date></execution-date></patent-assignor></patent-assignors><patent-assignees><patent-assignee><name>AUTHENTIX, INC.</name><address-1>4355 EXCEL PARKWAY</address-1><address-2>SUITE 100</address-2><city>ADDISON</city><state>TEXAS</state><postcode>75001</postcode></patent-assignee></patent-assignees><patent-properties><patent-property><document-id><country>US</country><doc-number>10852336</doc-number><kind>X0</kind><date>20040524</date></document-id><document-id><country>US</country><doc-number>20050260764</doc-number><kind>A1</kind><date>20051124</date></document-id><document-id><country>US</country><doc-number>7919325</doc-number><kind>B2</kind><date>20110405</date></document-id><invention-title lang='en'>METHOD AND APPARATUS FOR MONITORING LIQUID FOR THE PRESENCE OF AN ADDITIVE</invention-title></patent-property></patent-properties></patent-assignment>"


class Patent(object):
    """docstring for Patent"""

    action_key_codes = ["DA”, “WK”, “BI”, “AN"]

    def __init__(self, str_patent):
        super(Patent, self).__init__()

        soup = BeautifulSoup(str_patent, "lxml")

        self.is_valid = False
        self.fields_are_valid = False
        self.errors = []

        patent = soup.contents[0].contents[0].contents[0]

        # self.dtd_version

        # # Parent element
        # self.us_patent_assignments = root_element

        #self.action_key_code = self.soup
        # self.transaction_date
        # self.patent_assignments
        # self.data_available_code


        self.assignment_record = patent.contents[0]
        self.patent_assignors = patent.contents[1]
        self.patent_assignees = patent.contents[2]
        self.patent_properties = patent.contents[3]

        self.attrs = {}

        for attr in self.assignment_record.contents:
            print "%s, %s" % (attr.name, attr.string)

        # attr = soup.children[0].children[0]
        # self.attrs[attr.name] = attr.string

        # attr = soup.children[0].children[1]
        # self.attrs[reel_no.name] = attr

        # self.last_update_date
        # self.purge_indicator
        # self.recorded_date
        # self.page_count
        # self.correspondent
        # self.name
        # self.address_1
        # self.address_2
        # self.address_3
        # self.address_4
        # self.conveyance_text
        # self.patent_assignors
        # self.patent_assignor
        # self.name
        # self.execution_date
        # self.address_1
        # self.address_2
        # self.date_acknowledged
        # self.patent_assignees
        # self.patent_assignee
        # self.name
        # self.address_1
        # self.address_2
        # self.city
        # self.state
        # self.country_name
        # self.postcode
        # self.patent_properties
        # self. patent_property
        # self.document_id
        # self.country
        # self.doc_number

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

    def set_action_key_code(self, action_key_code):
        self.action_key_code = action_key_code

    def get_action_key_code(self):
        return self.action_key_code

    def check_action_key_code(self):
        errors = []
        if self.action_key_code not in self.action_key_codes:
            errors.append(
                {"action_key_code": "Invalid action key code: [%s]" % self.action_key_code})
        return errors

    def print_csv(self):
        for key, value in Patent.__dict__.items():
            try:
                print getattr(self, "get_" + key)()
            except Exception, e:
                print e

p = Patent(patent)
p.print_csv()
