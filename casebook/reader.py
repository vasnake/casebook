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
        session = logon(session, USERNAME, PASSWORD)

    # read input and make queries
    inputFileName = os.path.join(DATA_DIR, 'input.lst')
    with open(inputFileName) as f:
        for x in f:
            x = x.decode(CP).strip()
            print (u"input: '%s'" % x).encode(CP)
            if x and x[0] != u'#':
                getCasesAndSides(session, x)

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
    jsCases = findCases(session, queryString)
    jsSides = findSides(session, queryString)

    forEachCase(session, jsCases)
    # TODO:
    #~ forEachSide(session, jsSides)


def forEachCase(session, jsCases):
    '''Collect information for each case

    for each case
        card.case
        Card.PdfDocumentArchiveCaseCount - just num of docs - skip it
        card.casedocuments
        File.PdfDocumentArchiveCase
        for each side
            card.bankruptcard
            card.businesscard
        for each judge
            Card.Judge
    '''
    numCases = int(jsCases.obj[u'Result'][u'TotalCount'])
    print "forEachCase, TotalCount %s" % numCases
    if numCases <= 0:
        return

    casesList = jsCases.obj[u'Result'][u'Items']
    for case in casesList:
        collectCaseData(session, case)


def collectCaseData(session, case):
    '''Collect information for given case.

    Sequence:
        card.case
        Card.PdfDocumentArchiveCaseCount - just num of docs - skip it
        card.casedocuments
        File.PdfDocumentArchiveCase
        for each side
            card.businesscard
            card.bankruptcard
        for each judge
            Card.Judge

    URLs:
        GET http://casebook.ru/api/Card/Case
        GET http://casebook.ru/api/Card/CaseDocuments
        GET http://casebook.ru/File/PdfDocumentArchiveCase
        POST http://casebook.ru/api/Card/BusinessCard
        POST http://casebook.ru/api/Card/BankruptCard
        GET http://casebook.ru/api/Card/Judge
    '''
    CaseId = case[u"CaseId"]
    print "collectCaseData, CaseId %s" % CaseId

    #~ карточка дела GET http://casebook.ru/api/Card/Case?id=78d283d0-010e-4c50-b1d1-cf2395c00bf9
    jsCardCase = cardCase(session, CaseId)

    #~ инфо о документах GET http://casebook.ru/api/Card/CaseDocuments?id=78d283d0-010e-4c50-b1d1-cf2395c00bf9
    #~ jsCardCaseDocuments = cardCaseDocuments(session, CaseId)

    #~ архив документов GET http://casebook.ru/File/PdfDocumentArchiveCase/78d283d0-010e-4c50-b1d1-cf2395c00bf9/%D0%9040-27010-2012.zip
    #~ Content-Type: application/zip
    #~ filePdfDocumentArchiveCase(session, CaseId)

    caseSides = getSidesFromCase(jsCardCase)
    for x in caseSides:
        side = {} # replace None with ''
        for k,v in x.items():
            side[k] = v if v is not None else u''
        sideID = side[u'Id']
        print "Side ID: %s" % sideID

        #~ карточка участника POST http://casebook.ru/api/Card/BusinessCard
        #~ payload {"Address":"Данные скрыты","Inn":"","Name":"Гурняк Я. Ф.","Ogrn":"","Okpo":"","IsNotPrecise":true,"OrganizationId":""}
        #~ jsCardBusinessCard = cardBusinessCard(session, sideID, side)

        #~ что-то про банкротство, не знаю POST http://casebook.ru/api/Card/BankruptCard
        #~ payload {"Address":"Данные скрыты","Inn":"","Name":"Гурняк Я. Ф.","Ogrn":"","Okpo":"","IsNotPrecise":true,"OrganizationId":""}
        #~ jsCardBankruptCard = cardBankruptCard(session, sideID, side)

    caseJudges = getJudgesFromCase(jsCardCase)
    for x in caseJudges:
        judge = {} # replace None with ''
        for k,v in x.items():
            judge[k] = v if v is not None else u''
        judgeID = judge[u'Id']
        print "Judge ID: %s" % judgeID

        #~ карточка судьи GET http://casebook.ru/api/Card/Judge/96743d1a-ca39-4c2f-a5f2-94a2aa0c8b8f
        jsCardJudge = cardJudge(session, judgeID)


def cardJudge(session, judgeID):
    '''Get Card/Judge data from http://casebook.ru/api/Card/Judge/
    and save results.

    Returns messages.JsonResponce with casebook message

    GET http://casebook.ru/api/Card/Judge/96743d1a-ca39-4c2f-a5f2-94a2aa0c8b8f
    '''
    print u"Card/Judge for judge ID '%s' ..." % judgeID

    url = 'http://casebook.ru/api/Card/Judge/%s' % judgeID
    res = session.get(url)

    print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCardJudge = parseResponce(res.text)

    saveCardJudge(jsCardJudge, judgeID)
    return jsCardJudge


def cardBankruptCard(session, sideID, side):
    '''Get Card/BankruptCard data from http://casebook.ru/api/Card/BankruptCard
    and save results.

    Returns messages.JsonResponce with casebook message

    side: dictionary with side data from Card/Case

    POST http://casebook.ru/api/Card/BankruptCard
    payload {"Address":"Данные скрыты","Inn":"","Name":"Гурняк Я. Ф.","Ogrn":"","Okpo":"","IsNotPrecise":true,"OrganizationId":""}
    '''
    print u"Card/BankruptCard for side ID '%s' ..." % sideID

    payload = getSideCardPayload(side)
    url = 'http://casebook.ru/api/Card/BankruptCard'
    res = session.post(url, data=simplejson.dumps(payload))

    print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCardBankruptCard = parseResponce(res.text)

    saveCardBankruptCard(jsCardBankruptCard, sideID)
    return jsCardBankruptCard


def cardBusinessCard(session, sideID, side):
    '''Get Card/BusinessCard data from http://casebook.ru/api/Card/BusinessCard
    and save results.

    Returns messages.JsonResponce with casebook message

    side: dictionary with side data from Card/Case

    POST http://casebook.ru/api/Card/BusinessCard
    payload {"Address":"Данные скрыты","Inn":"","Name":"Гурняк Я. Ф.","Ogrn":"","Okpo":"","IsNotPrecise":true,"OrganizationId":""}
    '''
    print u"Card/BusinessCard for side ID '%s' ..." % sideID

    payload = getSideCardPayload(side)
    url = 'http://casebook.ru/api/Card/BusinessCard'
    res = session.post(url, data=simplejson.dumps(payload))

    print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCardBusinessCard = parseResponce(res.text)

    saveCardBusinessCard(jsCardBusinessCard, sideID)
    return jsCardBusinessCard


def getSideCardPayload(side):
    '''Returns payload for
    POST http://casebook.ru/api/Card/BankruptCard
    POST http://casebook.ru/api/Card/BusinessCard
    '''
    qt = u'''{"Address":"","Inn":"","Name":"","Ogrn":"","Okpo":"","IsNotPrecise":true,"OrganizationId":""}'''
    payload = simplejson.loads(qt)

    payload[u"Address"] = side.get(u'Address', u'')
    payload[u"Inn"] = side.get(u'Inn', u'')
    payload[u"Name"] = side.get(u'Name', u'')
    payload[u"Ogrn"] = side.get(u'Ogrn', u'')
    payload[u"Okpo"] = side.get(u'Okpo', u'')

    return payload


def getJudgesFromCase(jsCardCase):
    '''Returns list of judges from case card.

    jsCardCase: messages.JsonResponce object with Card/Case data
    '''
    caseJudges = []
    for x in jsCardCase.obj[u'Result'][u'Case'][u'Judges']:
        caseJudges += x[u'Judges']
    return caseJudges


def  getSidesFromCase(jsCardCase):
    '''Returns list of sides from case card.

    jsCardCase: messages.JsonResponce object with Card/Case data
    '''
    caseSides = []
    for x in [u'Plaintiffs', u'Defendants', u'Third', u'Others']:
        lst = jsCardCase.obj[u'Result'][u'Case'][u'Sides'][x]
        caseSides += lst
    return caseSides


def filePdfDocumentArchiveCase(session, CaseId):
    '''Get File/PdfDocumentArchiveCase data from http://casebook.ru/File/PdfDocumentArchiveCase/
    and save results (CaseId.caseDocs.zip file).
    '''
    print u"File/PdfDocumentArchiveCase by CaseId '%s' ..." % CaseId

    url = 'http://casebook.ru/File/PdfDocumentArchiveCase/%s/%s.caseDocs.zip' % (CaseId, CaseId)
    res = session.get(url, stream=True)

    print (u"%s: %s" % (url, res.status_code)).encode(CP)
    saveFilePdfDocumentArchiveCase(res, CaseId)


def cardCaseDocuments(session, CaseId):
    '''Get Card/CaseDocuments data from http://casebook.ru/api/Card/CaseDocuments
    and save results.
    Returns messages.JsonResponce with casebook message
    '''
    print u"Card/CaseDocuments by CaseId '%s' ..." % CaseId

    url = 'http://casebook.ru/api/Card/CaseDocuments'
    payload = {'id': CaseId}
    res = session.get(url, params=payload)

    print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCardCaseDocuments = parseResponce(res.text)

    saveCardCaseDocuments(jsCardCaseDocuments, CaseId)
    return jsCardCaseDocuments


def cardCase(session, CaseId):
    '''Get Card/Case data from http://casebook.ru/api/Card/Case
    and save results.
    Returns messages.JsonResponce with casebook message
    '''
    print u"Card/Case by CaseId '%s' ..." % CaseId

    url = 'http://casebook.ru/api/Card/Case'
    payload = {'id': CaseId}
    res = session.get(url, params=payload)

    print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCardCase = parseResponce(res.text)

    saveCardCase(jsCardCase, CaseId)
    return jsCardCase


def findSides(session, queryString):
    '''Find sides via http://casebook.ru/api/Search/Sides
    and save results.
    Returns messages.JsonResponce with casebook message
    '''
    print (u"sidesBy '%s' ..." % queryString).encode(CP)

    url = 'http://casebook.ru/api/Search/Sides'
    payload = {'name': queryString}
    res = session.get(url, params=payload)

    print (u"%s: %s" % (url, res.text)).encode(CP)
    jsSides = parseResponce(res.text)

    #~ Результат каждого запроса сохраняется в файл по шаблону:
    #~ data/query.{hash}.(cases|sides).json
    fname = saveSidesSearch(jsSides, queryString)
    #~ Дополнительно, информация о запросе/ответе сохраняется в индексный файл:
    #~ index.json
    updateIndexForSidesSearch(queryString, fname, jsSides)
    return jsSides


def findCases(session, queryString):
    '''Find cases via POST http://casebook.ru/api/Search/Cases
    and save results.
    Returns messages.JsonResponce with casebook message
    '''
    print (u"casesBy '%s' ..." % queryString).encode(CP)

    url = 'http://casebook.ru/api/Search/Cases'
    qt = CASES_QUERY_TEMPLATE
    payload = simplejson.loads(qt)
    payload[u"Query"] = queryString
    res = session.post(url, data=simplejson.dumps(payload))

    print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCases = parseResponce(res.text)

    #~ Результат каждого запроса сохраняется в файл по шаблону:
    #~ data/query.{hash}.(cases|sides).json
    fname = saveCasesSearch(jsCases, queryString)
    #~ Дополнительно, информация о запросе/ответе сохраняется в индексный файл:
    #~ index.json
    updateIndexForCasesSearch(queryString, fname, jsCases)
    return jsCases


def saveCardJudge(jsCardJudge, judgeID):
    '''Save judge info to a file, update index
    '''
    fname = saveResults2File(jsCardJudge, judgeID, 'card', 'judge')
    updateIndexForJudgeCard(judgeID, fname, jsCardJudge)


def saveCardBankruptCard(jsCardBankruptCard, sideID):
    '''Save side bankruptcard info to a file, update index
    '''
    fname = saveResults2File(jsCardBankruptCard, sideID, 'card', 'bankruptcard')
    updateIndexForBankruptCard(sideID, fname, jsCardBankruptCard)


def saveCardBusinessCard(jsCardBusinessCard, sideID):
    '''Save side businesscard info to a file, update index
    '''
    fname = saveResults2File(jsCardBusinessCard, sideID, 'card', 'businesscard')
    updateIndexForBusinessCard(sideID, fname, jsCardBusinessCard)


def saveFilePdfDocumentArchiveCase(res, CaseId):
    '''Save case documents zip archive info to file, update index

    res: requests.Responce object with binary data
    '''
    fname = saveResults2File(res, CaseId, 'file', 'casedocuments', 'zip')
    updateIndexForCaseDocumentsArchive(CaseId, fname, None)


def saveCardCaseDocuments(jsCardCaseDocuments, CaseId):
    '''Save case documents info to file, update index
    '''
    fname = saveResults2File(jsCardCaseDocuments, CaseId, 'card', 'casedocuments')
    updateIndexForCaseDocuments(CaseId, fname, jsCardCaseDocuments)


def saveCardCase(jsCardCase, CaseId):
    '''Save case data to file, update index
    '''
    fname = saveResults2File(jsCardCase, CaseId, 'card', 'case')
    updateIndexForCase(CaseId, fname, jsCardCase)


def saveCasesSearch(jsResp, queryString):
    '''Save search results to file.
    Returns file name
    '''
    return saveSearchResults2File(jsResp, queryString, 'cases')

def saveSidesSearch(jsResp, queryString):
    '''Save search results to file.
    Returns file name
    '''
    return saveSearchResults2File(jsResp, queryString, 'sides')

def saveSearchResults2File(jsResp, queryString, typeName):
    '''Save search results to file.
    Returns file name
    '''
    return saveResults2File(jsResp, queryString, 'query', typeName)


def saveResults2File(jsResp, queryString, category, typeName, respType='json'):
    '''Save search results to file.
    Returns file name

    respType: string, may be 'json', 'zip'.
        If respType is 'zip', jsResp treated as requests.Responce.
        Otherwise jsResp treated as messages.JsonResponce
    '''
    id = stringToFileName(queryString)
    fname = os.path.join(DATA_DIR, "%s.%s.%s.%s" % (category, id, typeName, respType))
    print (u"write result to file '%s'" % fname).encode(CP)

    with open(fname, 'wb') as f:
        if respType == 'json':
            f.write(jsResp.text.encode(CP))
        elif respType == 'zip':
            for chunk in jsResp.iter_content():
                f.write(chunk)
        else:
            raise TypeError("Unknown file type: %s" % respType)
    return fname


def updateIndexForJudgeCard(judgeID, fname, jsCardJudge):
    '''Save judge id and file name to index.json file
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'judges', judgeID)

    meta["JudgeId"] = judgeID
    meta["FileName"] = fname
    meta["Error"] = jsCardJudge.Message if jsCardJudge.Success == False else ''
    meta["Warning"] = jsCardJudge.Message
    meta["JudgeDisplayName"] = jsCardJudge.obj.get(u'Result', {}).get(u'JudgeDisplayName', '')
    meta["CourtFullName"] = jsCardJudge.obj.get(u'Result', {}).get(u'CourtFullName', '')

    indexObj = setListItemToIndex(indexObj, 'judges', judgeID, meta)
    saveIndex(indexObj)


def updateIndexForBankruptCard(sideID, fname, jsCardBankruptCard):
    '''Save side id and file name to index.json file
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'sides', sideID)

    state = jsCardBankruptCard.obj.get(u'Result', {}).get(u'State', '')
    state = '' if state is None else state

    meta["SideId"] = sideID
    meta["BankruptFileName"] = fname
    meta["BankruptState"] = state
    meta["Error"] = jsCardBankruptCard.Message if jsCardBankruptCard.Success == False else ''
    meta["Warning"] = jsCardBankruptCard.Message

    indexObj = setListItemToIndex(indexObj, 'sides', sideID, meta)
    saveIndex(indexObj)


def updateIndexForBusinessCard(sideID, fname, jsCardBusinessCard):
    '''Save side id and file name to index.json file
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'sides', sideID)

    meta["SideId"] = sideID
    meta["FileName"] = fname
    meta["Name"] = jsCardBusinessCard.obj.get(u'Result', {}).get(u'Name', '')
    meta["Address"] = jsCardBusinessCard.obj.get(u'Result', {}).get(u'Address', '')
    meta["Error"] = jsCardBusinessCard.Message if jsCardBusinessCard.Success == False else ''
    meta["Warning"] = jsCardBusinessCard.Message

    indexObj = setListItemToIndex(indexObj, 'sides', sideID, meta)
    saveIndex(indexObj)


def updateIndexForCaseDocumentsArchive(CaseId, fname, jsObj=None):
    '''Save case id and file name to index.json file
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'cases', CaseId)

    meta["CaseId"] = CaseId
    meta["DocsArchiveFileName"] = fname

    indexObj = setListItemToIndex(indexObj, 'cases', CaseId, meta)
    saveIndex(indexObj)


def updateIndexForCaseDocuments(CaseId, fname, jsCardCaseDocuments):
    '''Save case id and file name to index.json file
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'cases', CaseId)

    meta["CaseId"] = CaseId
    meta["DocsFileName"] = fname
    meta["DocsCount"] = len(jsCardCaseDocuments.obj[u'Result'][u'Documents'])
    meta["DocsError"] = jsCardCaseDocuments.Message if jsCardCaseDocuments.Success == False else ''
    meta["DocsWarning"] = jsCardCaseDocuments.Message

    indexObj = setListItemToIndex(indexObj, 'cases', CaseId, meta)
    saveIndex(indexObj)


def updateIndexForCase(CaseId, fname, jsCardCase):
    '''Save case id and file name to index.json file
    '''
    indexObj = loadIndex()
    caseMeta = getCaseMetaFromIndex(indexObj, CaseId)

    caseMeta["CaseId"] = CaseId
    caseMeta["Number"] = jsCardCase.obj[u'Result'][u'Case'][u'Number']
    caseMeta["FileName"] = fname
    caseMeta["Error"] = jsCardCase.Message if jsCardCase.Success == False else ''
    caseMeta["Warning"] = jsCardCase.Message

    indexObj = setCaseMetaToIndex(indexObj, CaseId, caseMeta)
    saveIndex(indexObj)


def updateIndexForSidesSearch(queryString, fname, jsSides):
    '''Save queries result metadata to index.json file
    '''
    indexObj = loadIndex()
    qryResults = getQueryResFromIndex(indexObj, queryString)

    qryResults["qryString"] = queryString
    qryResults["sidesRespFile"] = fname
    qryResults["sidesRespError"] = jsSides.Message if jsSides.Success == False else ''
    qryResults["sidesRespWarning"] = jsSides.Message
    qryResults["sidesCount"] = len(jsSides.obj[u'Result'])

    indexObj = setQueryResToIndex(indexObj, queryString, qryResults)
    saveIndex(indexObj)


def updateIndexForCasesSearch(queryString, fname, jsCases):
    '''Save queries result metadata to index.json file
    '''
    indexObj = loadIndex()
    qryResults = getQueryResFromIndex(indexObj, queryString)

    qryResults["qryString"] = queryString
    qryResults["casesRespFile"] = fname
    qryResults["casesRespError"] = jsCases.Message if jsCases.Success == False else ''
    qryResults["casesRespWarning"] = jsCases.Message
    qryResults["casesCount"] = int(jsCases.obj[u'Result'][u'TotalCount'])

    indexObj = setQueryResToIndex(indexObj, queryString, qryResults)
    saveIndex(indexObj)


def setCaseMetaToIndex(indexObj, CaseId, caseMeta):
    '''Set index.cases.{CaseId} to caseMeta.
    Returns updated indexObj
    '''
    return setListItemToIndex(indexObj, 'cases', CaseId, caseMeta)

def setQueryResToIndex(indexObj, queryString, qryResults):
    '''Set index.queries.{queryString} to qryResults.
    Returns updated indexObj
    '''
    return setListItemToIndex(indexObj, 'queries', queryString, qryResults)
    #~ idxQryList = indexObj.get('queries', {})
    #~ idxQryList[queryString] = qryResults
    #~ indexObj['queries'] = idxQryList
    #~ return indexObj

def setListItemToIndex(indexObj, listName, itemName, data):
    '''Set index.{listName}.{itemName} to data.
    Returns updated indexObj
    '''
    idxList = indexObj.get(listName, {})
    idxList[itemName] = data
    indexObj[listName] = idxList
    return indexObj


def  getCaseMetaFromIndex(indexObj, CaseId):
    '''Returns index.cases.{CaseId} dictionary from index
    '''
    return getListItemFromIndex(indexObj, 'cases', CaseId)

def getQueryResFromIndex(indexObj, queryString):
    '''Returns index.queries.{queryString} dictionary from index
    '''
    return getListItemFromIndex(indexObj, 'queries', queryString)
    #~ idxQryList = indexObj.get('queries', {})
    #~ qryResults = idxQryList.get(queryString, {})
    #~ return qryResults

def getListItemFromIndex(indexObj, listName, itemName):
    '''Returns index.{listName}.{itemName} dictionary from index
    '''
    idxList = indexObj.get(listName, {})
    return idxList.get(itemName, {})


def loadIndex():
    '''Returns indexObj = simplejson.loads(indexText from index.json file)
    '''
    indexFname = os.path.join(DATA_DIR, "index.json")
    indexText = u"{}"
    if os.path.isfile(indexFname):
        with open(indexFname) as f:
            indexText = f.read().strip().decode(CP)
    return simplejson.loads(indexText)


def saveIndex(indexObj):
    '''Save obj to index.json file
    simplejson.dumps(indexObj, sort_keys=True, indent='  ', ensure_ascii=False)
    '''
    txt = simplejson.dumps(indexObj, sort_keys=True, indent='  ', ensure_ascii=False)
    with open(os.path.join(DATA_DIR, "index.json"), 'wb') as f:
        f.write(txt.encode(CP))


def stringToFileName(aStr):
    '''Make a string good for file name
    '''
    return getHashString(aStr.encode(CP))


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
        err = u"Request failed. Message: %s" % js.Message
        print err.encode(CP)
        raise casebook.RequestError(err)
    return js


def logon(session, username, password):
    '''Perform LogOn requests on casebook.ru
    If logon isn't successfull raise an casebook.LogOnError exception
    '''
    print "logon..."
    url = 'http://casebook.ru/api/Account/LogOn'
    payload = {"SystemName": "Sps","UserName": username,"Password": password,"RememberMe": True}
    session.deleteCookies()
    res = session.post(url, data=simplejson.dumps(payload))
    print (u"%s: %s" % (url, res.text)).encode(CP)
    js = casebook.messages.JsonResponce(res.text)
    if js.Success:
        print 'we good'
    else:
        err = u"Auth failed. Message: %s" % js.Message
        print err.encode(CP)
        raise casebook.LogOnError(err)

    return session
