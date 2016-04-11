# -*- coding: utf8 -*-
from __future__ import print_function
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import datetime
import exceptions
from time import time
import traceback
import re
import sys



# patent = "<patent-assignment><assignment-record><reel-no>29862</reel-no><frame-no>645</frame-no><last-update-date><date>20130225</date></last-update-date><purge-indicator>N</purge-indicator><recorded-date><date>20130222</date></recorded-date><page-count>3</page-count><correspondent><name>KNOBBE, MARTENS, OLSON &amp; BEAR, LLP</name><address-1>2040 MAIN STREET, 14TH FLOOR</address-1><address-2>IRVINE, CA 92614</address-2></correspondent><conveyance-text>CORRECTIVE ASSIGNMENT TO CORRECT THE CONVEYING PARTY'S LAST NAME AND RECEIVING PARTY'S STREET NAME PREVIOUSLY RECORDED ON REEL/FRAME 028805/0592.</conveyance-text></assignment-record><patent-assignors><patent-assignor><name>D&#220;RR, MATTHIAS</name><execution-date><date>20120808</date></execution-date></patent-assignor></patent-assignors><patent-assignees><patent-assignee><name>FERAG AG</name><address-1>Z&#220;RICHSTRASSE 74</address-1><city>HINWIL</city><country-name>SWITZERLAND</country-name><postcode>8340</postcode></patent-assignee></patent-assignees><patent-properties><patent-property><document-id><country>US</country><doc-number>13514911</doc-number><kind>X0</kind><date>20120817</date></document-id><document-id><country>US</country><doc-number>20120310402</doc-number><kind>A1</kind><date>20121206</date></document-id><invention-title lang='en'>CONTROL APPARATUS AND METHOD FOR CONTROLLING A PRINTED-PRODUCT PROCESSING SYSTEM</invention-title></patent-property></patent-properties></patent-assignment>"


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
     "transaction date",  "reel-no", "frame-no", "last update date", "purge-indicator", "recorded date",
     "page-count",  "name correspondent",    "address-1 correspondent",   "address-2 correspondent",   "address-3 correspondent",
     "address-4",   "conveyance-text", "name assignor",   "date assignor",   "name assignee",
     "address assignee", "city assignee", "country-name assignee", "postcode assignee", "state assignee", "address-2 assignee",
     "X0_country", "A1_country", "A2_country", "B1_country", "B2_country", "P1_country", "P2_country", "P3_country", "P4_country", "S1_country",
     "X0 doc-number", "A1 doc-number", "A2 doc-number",
     "B1 doc-number", "B2 doc-number", "P1 doc-number", "P2 doc-number",
     "P3 doc-number", "P4 doc-number", "S1 doc-number", "X0 date", "A1 date",
     "A2 date", "B1 date", "B2 date", "P1 date", "P2 date", "P3 date",
     "P4 date", "S1 date", "invention-title", "lang"]

    CSV_FIELDS = ["dtd_version", "date_produced",   "action_key_code",
     "date",  "reel_no", "frame_no", "date2", "purge_indicator", "date3",
     "page_count",  "name",    "address_1",   "address_2", "address_3",
     "address_4",   "conveyance_text", "name_assignor",   "date_assignor", "name_assignee",
     "address_assignee", "city_assignee", "country_name_assignee", "postcode_assignee", "state_assignee", "address_2_assignee",
     "X0_country", "A1_country", "A2_country", "B1_country", "B2_country", "P1_country", "P2_country", "P3_country", "P4_country", "S1_country",
     "X0_number", "A1_number", "A2_number", "B1_number", "B2_number",
     "P1_number", "P2_number", "P3_number", "P4_number", "S1_number", "X0_date",
     "A1_date", "A2_date", "B1_date", "B2_date", "P1_date", "P2_date", "P3_date",
     "P4_date", "S1_date", "invention_title", "lang"]

    action_key_codes = ["DA", "WK", "BI", "AN"]

    dtd_version = None

    action_key_code = None
    transaction_date = None
    patent_assignments = None
    data_available_code = None

    def __init__(self, str_patent):
        super(Patent, self).__init__()

        soup = BeautifulSoup(str_patent)

        patent = soup.contents[0].contents[0].contents[0]

        patent.contents = [ p for p in patent.contents if (p != ' ' and p != '\n')]

        assignment_record = patent.contents[0]
        patent_assignors = patent.contents[1]
        patent_assignees = patent.contents[2]
        patent_properties = patent.contents[3]

        assignment_record.contents = [ p for p in assignment_record.contents if (p != ' ' and p != '\n')]
        patent_assignors.contents = [ p for p in patent_assignors.contents if (p != ' ' and p != '\n')]
        patent_assignees.contents = [ p for p in patent_assignees.contents if (p != ' ' and p != '\n')]
        patent_properties.contents = [ p for p in patent_properties.contents if (p != ' ' and p != '\n')]

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

        self.print_indices = []
        self.valid = False

        self.check_fields()

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
        # print(cls.dtd_version)
        # print(cls.date_produced)
        # print(cls.action_key_code)
        # print(cls.transaction_date)

        print(cls.dtd_version + ", " + cls.date_produced + ", " +
              cls.action_key_code + ", " + cls.transaction_date + ", " + "N", file=r_file)

    @classmethod
    def print_empty_titles(cls, r_file):
        for i in xrange(0, 4):
            print(Patent.CSV_TITLES[i] + ", ", file=r_file, end="")
        print("data-available-code", file=r_file)

    def read_attrs(self, node):
        attrs = {}
        try:
            if len(node.contents) < 1:
                raise Exception("Node %s has no attributes" % node.name)
        except Exception, e:
            print("Exception: %s" % e)

        node.contents =  [ p for p in node.contents if p != ' ' and p != '\n']

        for attr in node.contents:
            attrs[attr.name] = attr.string
        return attrs

    def is_valid(self):
        return self.valid

    def check_fields(self):
        self.remove_empty_assigs()
        lines_to_print = self.lines_to_print()
        self.init_printing_indices(lines_to_print)
        valid = True
        i = 0
        for field in Patent.CSV_FIELDS:
            try:
                i += 1
                getattr(self, "check_" + field)()
            except AttributeError:
                pass
            except Exception, e:
                tb = traceback.format_exc()
                print("exception [%s, %s]\n" % (field, tb))
                # pass
        if (not i == len(Patent.CSV_FIELDS)) or self.errors:
            # print("I, len, errors: %s, %s, %s" % (i, len(Patent.CSV_FIELDS), self.errors))
            valid = False

        self.valid = valid

    def remove_empty_assigs(self):
        for (i, assignor) in enumerate(self.patent_assignors):
            try:
                if not assignor["name"]:
                    self.patent_assignors.remove(assignor)
            except Exception, e:
                self.errors.append({"assignor ": "Trying to remove assignor but [%s]" % e})
        for (i, assignee) in enumerate(self.patent_assignees):
            try:
                if not assignee["name"]:
                    self.patent_assignees.remove(assignee)
            except Exception, e:
                self.errors.append({"assignee ": "Trying to remove assignee but [%s]" % e})

    def has_warnings(self):
        if self.warnings:
            return True
        return False

    def get_warnings(self):
        return self.warnings

    def get_errors(self):
        return self.errors

    def lines_to_print(self):
        pase = len(self.patent_assignees)
        paso = len(self.patent_assignors)
        props = len(self.patent_properties)

        return pase * paso * props

    def print_csv_titles(self):
        titles = ""
        for i, title in enumerate(Patent.CSV_TITLES):
            if i > 0:
                titles += ", "
            titles += title
        self.file.write(titles+"\n")

    def get_indices(self, pao_size, pae_size, prop_size, n):
        pao_indices = [(i/(pae_size*prop_size))%pao_size for i in xrange(0, n)]
        pae_indices = [(i/prop_size) % pae_size for i in xrange(0, n)]
        prop_indices = [i % prop_size for i in xrange(0, n)]

        return zip(pao_indices, pae_indices, prop_indices)


    def init_printing_indices(self, n):
        lpao = len(self.patent_assignors)
        lpae = len(self.patent_assignees)
        lprops = len(self.patent_properties)

        # if lpao >= lpae and lpae >= lprops:
        #     aoi, aei, propi = self.get_indices(lprops, lpae, lpao)


        self.print_indices = self.get_indices(lpao, lpae, lprops, n)


    def print_csv(self):
        lines = ""
        lines_to_print = self.lines_to_print()
        for i in xrange(0, lines_to_print):
            lines += self.print_csv_line(i)
        self.file.write(lines)
        # if len(self.patent_assignors) > 1 and len(self.patent_assignees) > 1 and len(self.patent_assignees) == len(self.patent_assignors):
        #     print(lines)

    def print_csv_line(self, i):
        line = ""
        for (x, attr) in enumerate(Patent.CSV_FIELDS):
            try:
                if x > 0:
                    line += ", "
                res = getattr(self, "get_" + attr)(i)
                if type(res) == NavigableString:
                    res = res.encode('utf-8')
                if type(res) == str:
                    res = res.replace(",", " ").replace("\"", " ").replace("\'", " ").replace(".", " ")
                    res = re.sub('\s+', ' ', res).strip()
                if not res:
                    res = " "
                line += res
            except KeyError, e:
                # print("KEYERROR: %s" % e)
                pass
            except AttributeError, e:
                # print("ATTERROR: %s" % e)
                pass
            except UnicodeEncodeError, e:
                # print("Type(e) = %s " % type(e))
                tb = traceback.format_exc()
                self.errors.append({"Exception" : tb})
                sys.exit(-1)
                # if not type(e) == exceptions.AttributeError:
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
        return self.assignment_record["conveyance-text"].encode('utf-8')

    # ASSIGNOR variable
    def get_name_assignor(self, i):

        if i < self.lines_to_print():
            index, _, _ = self.print_indices[i]

            return self.patent_assignors[index]["name"].encode('utf-8')
        return ""

    def get_date_assignor(self, i):
        if i < self.lines_to_print():
            index, _, _ = self.print_indices[i]
            return self.patent_assignors[index]["execution-date"]
        return ""

    # ASSIGNEE variables
    def get_name_assignee(self, i):
        if i < self.lines_to_print():
            _, index, _ = self.print_indices[i]
            return self.patent_assignees[index]["name"].encode('utf-8')
        return ""

    def get_address_assignee(self, i):
        if i < self.lines_to_print():
            _, index, _ = self.print_indices[i]
            return self.patent_assignees[index]["address-1"].encode('utf-8')
        return ""

    def get_city_assignee(self, i):
        if i < self.lines_to_print():
            _, index, _ = self.print_indices[i]
            return self.patent_assignees[index]["city"].encode('utf-8')
        return ""

    def get_country_name_assignee(self, i):
        if i < self.lines_to_print():
            _, index, _ = self.print_indices[i]
            try:
                return self.patent_assignees[index]["country-name"].encode('utf-8')
            except:
                pass
        return ""

    def get_postcode_assignee(self, i):
        if i < self.lines_to_print():
            _, index, _ = self.print_indices[i]
            return self.patent_assignees[index]["postcode"]
        return ""

    def get_state_assignee(self, i):
        if i < self.lines_to_print():
            _, index, _ = self.print_indices[i]

            try:
                return self.patent_assignees[index]["state"].encode('utf-8')
            except:
                pass
        return ""

    def get_address_2_assignee(self, i):
        if i < self.lines_to_print():
            _, index, _ = self.print_indices[i]
            return self.patent_assignees[index]["address-2"].encode('utf-8')
        return ""

    def get_X0_country(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "X0":
                    return doc["country"].encode('utf-8')

    def get_A1_country(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "A1":
                    return doc["country"].encode('utf-8')

    def get_A2_country(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "A2":
                    return doc["country"].encode('utf-8')

    def get_B1_country(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "B1":
                    return doc["country"].encode('utf-8')

    def get_B2_country(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "B2":
                    return doc["country"].encode('utf-8')

    def get_P1_country(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P1":
                    return doc["country"].encode('utf-8')

    def get_P2_country(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P2":
                    return doc["country"].encode('utf-8')

    def get_P3_country(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P3":
                    return doc["country"].encode('utf-8')

    def get_P4_country(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P4":
                    return doc["country"].encode('utf-8')

    def get_S1_country(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "S1":
                    return doc["country"]

    def get_X0_number(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "X0":
                    return doc["doc-number"]

    def get_A1_number(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "A1":
                    return doc["doc-number"]

    def get_A2_number(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "A2":
                    return doc["doc-number"]

    def get_B1_number(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "B1":
                    return doc["doc-number"]

    def get_B2_number(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "B2":
                    return doc["doc-number"]

    def get_P1_number(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P1":
                    return doc["doc-number"]

    def get_P2_number(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P2":
                    return doc["doc-number"]

    def get_P3_number(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P3":
                    return doc["doc-number"]

    def get_P4_number(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P4":
                    return doc["doc-number"]

    def get_S1_number(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "S1":
                    return doc["doc-number"]

    def get_X0_date(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "X0":
                    return doc["date"]

    def get_A1_date(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "A1":
                    return doc["date"]

    def get_A2_date(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "A2":
                    return doc["date"]

    def get_B1_date(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "B1":
                    return doc["date"]

    def get_B2_date(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "B2":
                    return doc["date"]

    def get_P1_date(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P1":
                    return doc["date"]

    def get_P2_date(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P2":
                    return doc["date"]

    def get_P3_date(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P3":
                    return doc["date"]

    def get_P4_date(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "P4":
                    return doc["date"]

    def get_S1_date(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            prop = self.patent_properties[index]
            for doc in prop["document-ids"]:
                if doc["kind"] == "S1":
                    return doc["date"]

    def get_invention_title(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            return self.patent_properties[index]['invention-title'].encode('utf-8')

    def get_lang(self, i):
        if i < self.lines_to_print():
            _, _, index = self.print_indices[i]
            return self.patent_properties[index]['lang'].encode('utf-8')

    def check_dtd_version(self):
        try:
            dtd = self.get_dtd_version(0)
            if not dtd:
                self.warnings.append({"dtd-version": "empty field"})
            dtd = float(dtd)
            if not is_numeric(dtd):
                self.errors.append({"dtd-version": "NaN value [%s]" % self.get_dtd_version(0)})
            if not (dtd == 0.3 or dtd == 1.0):
                self.warnings.append({"dtd-version": "version is neither 0.3 nor 1.0"})
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
            attr = self.get_date2(0)
            if attr is None:
                self.warnings.append({"date2": "empty field"})
            elif not is_valid(self.get_date2(0)):
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

    def check_name_assignor(self):
        try:
            if  len(self.patent_assignors) == 0:
                self.errors.append({"name_assignor": "ALL empty [%s]" % (i)})
        except Exception, e:
            self.warnings.append({"name_assignor": "%s" % e})

    def check_date_assignor(self):
        try:
            for assig in self.patent_assignors:
                if not assig['execution-date']:
                    self.warnings.append({"date_assignor": "empty field"})
                elif not is_valid(self.get_date_assignor(0)):
                    self.errors.append({"date_assignor": "invalid date %s" % type(self.get_date_assignor())})
        except:
            self.warnings.append({"date_assignor": "not found"})

    def check_name_assignee(self):
        try:
            if  len(self.patent_assignees) == 0:
                self.errors.append({"name_assignee": "ALL empty [%s]" % (i)})
        except Exception, e:
            self.warnings.append({"name_assignee": "%s" % e})

    def check_address_assignee(self):
        try:
            for assig in self.patent_assignees:
                address = assig['address-1'].encode('utf-8')
                if not address:
                    self.warnings.append({"address_assignee": "empty field"})
                if not is_string(self.get_address_assignee(0)):
                    self.errors.append({"address_assignee": "not a string [%s]" % type(address)})
        except:
            self.warnings.append({"address_assignee": "not found"})


    def check_city_assignee(self):
        try:
            for assig in self.patent_assignees:
                city = assig['city'].encode('utf-8')
                if not city:
                    self.warnings.append({"city": "empty field"})
                if not is_string(city):
                    self.errors.append({"city": "not a string [%s]" % type(city)})
        except:
            self.warnings.append({"city": "not found"})

    def check_country_name_assignee(self):
        try:
            for assig in self.patent_assignees:
                country = assig['country-name'].encode('utf-8')
                state = assig['state'].encode('utf-8')
                if not state and not country:
                    self.warnings.append({"country": "empty field and no state present"})
                if not is_string(country):
                    self.errors.append({"country-name": "not a string [%s]" % type(state)})
        except:
            self.warnings.append({"country-name": "not found"})

    def check_postcode_assignee(self):
        try:
            for assig in self.patent_assignees:
                postcode = assig['postcode']
                if not postcode:
                    self.warnings.append({"postcode": "empty field"})
        except:
            self.warnings.append({"postcode": "not found"})

    def check_state_assignee(self):
        try:
            for assig in self.patent_assignees:
                country = assig['country-name'].encode('utf-8')
                state = assig['state'].encode('utf-8')
                if not state and not country:
                    self.warnings.append({"state": "empty field and no state present"})
                if not is_string(state):
                    self.errors.append({"state": "not a string [%s]" % type(state)})
        except:
            self.warnings.append({"state": "not found"})

    def check_address_2_assignee(self):
        try:
            for assig in self.patent_assignees:
                if not assig['address-2'].encode('utf-8'):
                    self.warnings.append({"address-2-assignee": "empty field"})
        except:
            self.warnings.append({"address-2-assignee": "not found"})

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
            if not self.get_date_assignor(0):
                self.warnings.append({"date_assignor": "empty field"})
            elif not is_valid(self.get_date_assignor(0)):
                self.errors.append({"date_assignor": "invalid date %s" % self.get_date_assignor()})
        except Exception, e:
            self.warnings.append({"date_assignor": "not found"})

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

# trial = open("trial.csv", "w+")
# patent = open("patent.txt").read()
# p = Patent(patent)
# p.set_file(trial)

# dtd = 0.3
# dp = 20031112
# ak = "AN"
# d = 20130117

# Patent.set_zip_info(dtd, dp, ak, d)
# if p.is_valid():
#     print("valid")
#     p.print_csv_titles()
#     p.print_csv()
# else:
#     print(p.errors)
