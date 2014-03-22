#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

''' casebook reader module

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
DATA_DIR = os.environ.get("CASEBOOK_DATA", "/tmp")

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


def main():
    session = casebook.http.HttpSession()
    session.restoreCookies(os.path.join(DATA_DIR, '.session'))
    session.setHeaders(COMMON_HEADERS)

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

    # read input and make queries
    inputFileName = os.path.join(DATA_DIR, 'input.lst')
    with open(inputFileName) as f:
        for x in f:
            x = x.decode(CP).strip()
            print (u"input: '%s'" % x).encode(CP)
            if x and x[0] != u'#':
                getCasesAndSides(session, x)

    # print list of cases founded by org. name
    #~ casesByOrgname(session, u'ОАО "ГАЗПРОМБАНК"')

    session.saveCookies()
    print "that's all for now"


def getCasesAndSides(session, queryString):
    '''Perform queries to casebook.ru
        POST http://casebook.ru/api/Search/Cases
        GET http://casebook.ru/api/Search/Sides

    Print results, save results

    Результат каждого запроса сохраняется в файл по шаблону:
        data/query.{hash}.(cases|sides).json
    Дополнительно, информация о запросе/ответе сохраняется в индексный файл:
        index.json
    '''
    hash = getHashString(queryString.encode(CP))

    print (u"casesBy '%s'..." % queryString).encode(CP)
    url = 'http://casebook.ru/api/Search/Cases'
    qt = CASES_QUERY_TEMPLATE
    payload = simplejson.loads(qt)
    payload[u"Query"] = queryString
    res = session.post(url, data=simplejson.dumps(payload))
    print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCases = parseResponce(res.text)

    print (u"sidesBy '%s'..." % queryString).encode(CP)
    url = 'http://casebook.ru/api/Search/Sides'
    payload = {'name': queryString}
    res = session.get(url, params=payload)
    print (u"%s: %s" % (url, res.text)).encode(CP)
    jsSides = parseResponce(res.text)

#~ Результат каждого запроса сохраняется в файл по шаблону:
    #~ data/query.{hash}.(cases|sides).json
    for x in [(jsCases, 'cases'), (jsSides, 'sides')]:
        resName = x[1]
        js = x[0]
        fname = os.path.join(DATA_DIR, "query.%s.%s.json" % (hash, resName))
        print (u"write result to file '%s'" % fname).encode(CP)
        with open(fname, 'w') as f:
            f.write(js.text.encode(CP))

#~ Дополнительно, информация о запросе/ответе сохраняется в индексный файл:
    #~ index.json
    qryResults = {
        "qryString": queryString,
        "casesRespFile": os.path.join(DATA_DIR, "query.%s.%s.json" % (hash, 'cases')),
        "sidesRespFile": os.path.join(DATA_DIR, "query.%s.%s.json" % (hash, 'sides')),
        "casesRespError": jsCases.Message, # TODO: only if jsCases.Success is False
        "casesRespWarning": jsCases.Message,
        "sidesRespError": jsSides.Message, # TODO: only if jsSides.Success is False
        "sidesRespWarning": jsSides.Message,
        "casesCount": int(jsCases.obj[u'Result'][u'TotalCount']),
        "sidesCount": len(jsSides.obj[u'Result'])
    }
    updateIndex(qryResults)


def updateIndex(qryResults):
    '''Save queries result metadata to index.json file

    dumps / loads example:
        txt = simplejson.dumps(res, ensure_ascii=False, sort_keys=True, indent=2, use_decimal=True, default=mfslib.jsonify)
            with open('layerdata.test1.json', 'wb') as fh:
                fh.write(txt.encode(CP))
        res = simplejson.loads(txt, use_decimal=True)
        with open('layerdata.test1.json') as fh:
            txt = fh.read().strip().decode(CP)
            dct = simplejson.loads(txt, use_decimal=True)
    '''
    indexObj = loadIndex()
    idxQryList = indexObj.get('queries', {})
    idxQryList[qryResults['qryString']] = qryResults
    indexObj['queries'] = idxQryList
    txt = simplejson.dumps(indexObj, sort_keys=True, indent='  ', ensure_ascii=False)
    with open(os.path.join(DATA_DIR, "index.json"), 'wb') as f:
        f.write(txt.encode(CP))


def loadIndex():
    '''Returns indexObj = simplejson.loads(indexText from index.json file)
    '''
    indexFname = os.path.join(DATA_DIR, "index.json")
    indexText = (u"{}").decode(CP)
    if os.path.isfile(indexFname):
        with open(indexFname) as f:
            indexText = f.read().strip().decode(CP)
    return simplejson.loads(indexText)


def getHashString(aStr):
    '''Returns string as hashlib.sha1(aStr).hexdigest().
    aStr must be non-unicode string
    '''
    import hashlib
    return hashlib.sha1(aStr).hexdigest()


def parseResponce(text):
    '''Print results status message.
    Returns casebook.messages.JsonResponce
    '''
    js = casebook.messages.JsonResponce(text)
    if js.Success and js.Message == u'':
        print 'we good'
    else:
        err = u"Search failed. Message: %s" % js.Message
        print err.encode(CP)
    return js


def casesByOrgname(session, orgname):
    '''Perform casebook.ru/api/Search/Cases
    and print results
    '''
    print "casesByOrgname..."
    url = 'http://casebook.ru/api/Search/Cases'
    qt = CASES_QUERY_TEMPLATE
    payload = simplejson.loads(qt)
    payload[u"Query"] = orgname
    res = session.post(url, data=simplejson.dumps(payload))
    print (u"%s: %s" % (url, res.text)).encode(CP)
    js = casebook.messages.JsonResponce(res.text)
    if js.Success:
        print 'we good'
    else:
        err = u"Search/Cases failed. Message: %s" % js.Message
        print err.encode(CP)


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
