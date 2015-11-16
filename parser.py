# -*- coding: latin1 -*-
from bs4 import BeautifulSoup
from collections import OrderedDict
import urllib2, re, sys, signal, os



class Patent(object):
    """docstring for Patent"""

    action_key_codes = ["DA”, “WK”, “BI”, “AN"]

    def __init__(self):
        super(Patent, self).__init__()

        self.dtd_version

        # Parent element
        self.us_patent_assignments

        self.action_key_code
        self.transaction_date
        self.patent_assignments
        self.data_available_code
        self.patent_assignment
        self.assignment_record
        self.reel_no
        self.frame_no
        self.last_update_date
        self.purge_indicator
        self.recorded_date
        self.page_count
        self.correspondent
        self.name
        self.address_1
        self.address_2
        self.address_3
        self.address_4
        self.conveyance_text
        self.patent_assignors
        self.patent_assignor
        self.name
        self.execution_date
        self.address_1
        self.address_2
        self.date_acknowledged
        self.patent_assignees
        self.patent_assignee
        self.name
        self.address_1
        self.address_2
        self.city
        self.state
        self.country_name
        self.postcode
        self.patent_properties
        self. patent_property
        self.document_id
        self.country
        self.doc_number

