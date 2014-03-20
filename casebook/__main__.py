#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

''' casebook main module
for using from console type commands like:
    python -m casebook

http://docs.python-requests.org/en/latest/community/faq/
http://stackoverflow.com/questions/13030095/how-to-save-requests-python-cookies-to-a-file
'''

import simplejson
import requests
import requests.utils
import pickle
import os

import casebook
import casebook.http
import casebook.messages

CP = casebook.CP

USERNAME = os.environ.get("CASEBOOK_USER", "casebook.ru account username")
PASSWORD = os.environ.get("CASEBOOK_PASSWORD", "secret")

commonHeaders = {"Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "x-date-format": "iso",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Proxy-Connection": "keep-alive",
    "Referer": "http://casebook.ru/"}

def main():
    session = casebook.http.HttpSession()
    session.restoreCookies('.session')
    session.setHeaders(commonHeaders)

    # check access
    url = 'http://casebook.ru/api/Message/UnreadCount?'
    res = session.get(url)
    print (u"%s: %s" % (url, res.text)).encode(CP)
    js = casebook.messages.JsonResponce(res.text)
    if js.Success:
        print 'we good'
    else:
        print (u"Auth. need to be done. Message: %s" % js.Message).encode(CP)
        logon(session, USERNAME, PASSWORD)

    # print list of cases founded by org. name
    casesByOrgname(session, u'ОАО "ГАЗПРОМБАНК"')

    session.saveCookies('.session')
    print "that's all for now"


def logon(session, username, password):
    '''Perform LogOn requests on casebook.ru
    If logon isn't successfull raise an casebook.LogOnError exception
    '''
    print "logon..."
    url = 'http://casebook.ru/api/Account/LogOn'
    payload = {"SystemName": "Sps","UserName": username,"Password": password,"RememberMe": True}
    res = session.post(url, data=simplejson.dumps(payload))
    print (u"%s: %s" % (url, res.text)).encode(CP)
    js = casebook.messages.JsonResponce(res.text)
    if js.Success:
        print 'we good'
    else:
        err = u"Auth failed. Message: %s" % js.Message
        print err.encode(CP)
        raise casebook.LogOnError(err)


def casesByOrgname(session, orgname):
    '''Perform casebook.ru/api/Search/Cases
    and print results
    '''
    print "casesByOrgname..."
    url = 'http://casebook.ru/api/Search/Cases'
    qt = u'''
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
    payload = simplejson.loads(qt)
    payload[u"Query"] = orgname
    res = session.post(url, data=simplejson.dumps(payload))
    print (u"%s: %s" % (url, res.text)).encode(CP)
    js = casebook.messages.JsonResponce(res.text)
    if js.Success:
        print 'we good'
    else:
        err = u"Search/Cases failed. Message: %s" % js.Message


main()

################################################################################

def oldcode():
    commonHeaders = {"Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "x-date-format": "iso",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://casebook.ru/"}

    # create session
    s = requests.Session()
    if os.path.isfile('.session'):
        with open('.session') as f:
            cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
            s.cookies = cookies

    s.headers.update(commonHeaders)


    def logon(session):
        print "logon..."
        url = 'http://casebook.ru/api/Account/LogOn'
        payload = {"SystemName": "Sps","UserName": "username","Password": "secret","RememberMe": True}
        res = session.post(url, data=simplejson.dumps(payload))
        print (u"/api/Account/LogOn: %s" % res.text).encode(CP)
        return session


    def casesByOrgname(session, orgname):
        print "casesByOrgname..."
        url = 'http://casebook.ru/api/Search/Cases'
        qt = u'''
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
        payload = simplejson.loads(qt)
        payload[u"Query"] = orgname
        res = session.post(url, data=simplejson.dumps(payload))
        print (u"/api/Search/Cases: %s" % res.text).encode(CP)
        return session


    # check access
    url = 'http://casebook.ru/api/Message/UnreadCount?'
    res = s.get(url)
    print (u"/api/Message/UnreadCount: %s" % res.text).encode(CP)
    js = simplejson.loads(res.text)
    ok = js.get(u'Success', False)
    if ok:
        print 'we good'
    else:
        print "auth. need to be done"
        print (u"Site message: %s" % js.get(u'Message', u'n/a')).encode(CP)
        s = logon(s)

    # print list of cases founded by org. name
    s = casesByOrgname(s, u'ОАО "ГАЗПРОМБАНК"')

    # save session cookies
    with open('.session', 'w') as f:
        pickle.dump(requests.utils.dict_from_cookiejar(s.cookies), f)

    print "that's all for now"
