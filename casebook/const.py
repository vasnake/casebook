#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

''' casebook constants

Created on May 22, 2014

@author: vasnake@gmail.com
'''

import os

USERNAME = os.environ.get("CASEBOOK_USER", "casebook.ru account username")
PASSWORD = os.environ.get("CASEBOOK_PASSWORD", "secret")

# Filesystem directory for downloaded files
DATA_DIR = os.environ.get("CASEBOOK_DATA", "/tmp")

# Time (seconds) to next try to download an existent case/side data
FRESH_PERIOD = int(os.environ.get("CASEBOOK_FRESH_PERIOD", 12)) * 60 * 60

COMMON_HEADERS = {"Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "x-date-format": "iso",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Proxy-Connection": "keep-alive",
    "Referer": "http://casebook.ru/"}

CASES_QUERY_TEMPLATE = u'''
    {"StatusEx":[],"SideTypes":[],"ConsiderType":-1,"CourtType":-1,"CaseNumber":null,"CaseCategoryId":"",
        "MonitoredStatus":-1,"Courts":[],"Instances":[],"Judges":[],
        "Delegate":"","StateOrganizations":[],"DateFrom":null,"DateTo":null,"SessionFrom":null,"SessionTo":null,
        "FinalDocFrom":null,"FinalDocTo":null,"MinSum":0,"MaxSum":-1,
        "Sides":[],"CoSides":[],"JudgesNames":[],
        "Accuracy":2,
        "Page":1,
        "Count":30,
        "OrderBy":"incoming_date_ts desc",
        "Query":"ОАО ГАЗПРОМБАНК"}
'''
