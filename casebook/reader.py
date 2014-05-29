#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

''' casebook reader module

'''

import os
import sys
import simplejson
import datetime
import traceback

import casebook.http
import casebook.messages
import casebook.filestor as stor
import casebook.const as const
import casebook.utils as utils

CP = casebook.CP

def main():
    session = casebook.http.HttpSession()
    session.restoreCookies(os.path.join(const.DATA_DIR, '.session'))
    session.setHeaders(const.COMMON_HEADERS)

    # check access
    url = 'http://casebook.ru/api/Message/UnreadCount?'
    res = session.get(url)
    #print (u"%s: %s" % (url, res.text)).encode(CP)
    js = casebook.messages.JsonResponce(res.text)
    if js.Success:
        print 'we good'
    else:
        print (u"Auth. need to be done. Message: %s" % js.Message).encode(CP)
        session = logon(session, const.USERNAME, const.PASSWORD)

    # read input and make queries
    inputFileName = os.path.join(const.DATA_DIR, 'input.lst')
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
    # TODO: search cases GJ

    jsCases = findCases(session, queryString)
    jsSides = findSides(session, queryString)

    forEachCase(session, jsCases)
    forEachSide(session, jsSides)


def forEachSide(session, jsSides):
    '''Collect information for each side
    '''
    numSides = len(jsSides.obj[u'Result'])
    print "forEachSide, TotalCount %s" % numSides
    if numSides <= 0:
        return

    sidesList = jsSides.obj[u'Result']
    for side in sidesList:
        try:
            collectSideData(session, side, const.DEEP)
        except casebook.RequestError:
            print u"forEachSide, error while processing current side"
            traceback.print_exc(file=sys.stderr)


def forEachCase(session, jsCases):
    '''Collect information for each case
    '''
    numCases = int(jsCases.obj[u'Result'][u'TotalCount'])
    print "forEachCase, TotalCount %s" % numCases
    if numCases <= 0:
        return

    casesList = jsCases.obj[u'Result'][u'Items']
    for case in casesList:
        try:
            collectCaseData(session, case, const.DEEP)
        except casebook.RequestError:
            print u"forEachCase, error while processing current case"
            traceback.print_exc(file=sys.stderr)


def collectSideData(session, side, deep=2):
    '''Collect all information for given side

    Sequence:
        card.accountingstat
        card.excerpt
        search.sidesdetailsex
        calendar.period
        card.bankruptcard
            case info for each case mentioned
        card.businesscard
            side info for each side mentioned
        search.cases2
            case info for each: todo?
        search.casesgj
            case info for each: todo?

    URLs:
        GET http://casebook.ru/api/Card/Excerpt
        GET http://casebook.ru/api/Search/SidesDetailsEx
        POST http://casebook.ru/api/Card/AccountingStat
        POST http://casebook.ru/api/Calendar/Period
        POST http://casebook.ru/api/Card/BankruptCard
        POST http://casebook.ru/api/Card/BusinessCard
        POST http://casebook.ru/api/Search/Cases
        POST http://casebook.ru/api/Search/CasesGj

    :param casebook.http.HttpSession session: HTTP session wrapper
    :param dict side: side data from casebook.messages.JsonResponce
    :param bool deep: recursion limit
    '''
    if deep <= 0:
        print u"collectSideData, end of recursion"
        return

    ShortName = sideShortName(side)
    sid = utils.getSidePseudoID(side)
    print "collectSideData, side short name: %s" % ShortName

    # check if we already get this side today
    if sideDataIsFresh(sid):
        print "collectSideData, side data downloaded already, nothing to do"
        return

    #~ отчетность POST http://casebook.ru/api/Card/AccountingStat
    #~ payload {"Organization":{"Address": ...
    __ = cardAccountingStat(session, side)

    #~ выписка из ЕГРЮЛ
    #~ GET http://casebook.ru/api/Card/Excerpt?Address= ...
    cardExcerpt(session, side)

    # доп.сведения
    # GET http://casebook.ru/api/Search/SidesDetailsEx?index=1&inn=1106014140&okpo=3314561
    __ = searchSidesDetailsEx(session, side)

    # расписание событий POST http://casebook.ru/api/Calendar/Period
    # payload {...,"Sides":[{"Name":"ДИРЕКЦИЯ
    __ = calendarPeriod(session, side)

    # что-то про банкротство, внутри тянет case info for each case mentioned
    # POST http://casebook.ru/api/Card/BankruptCard
    # payload {"Address":"169300, РЕСПУБЛИКА КОМИ...","Inn":"1106014140","Name":"ДИРЕКЦИЯ ...","Ogrn":"1021100895760","Okpo":"3314561","IsUnique":false,"OrganizationId":""}
    jsCardBankruptCard = cardBankruptCard(session, side)

    #~ карточка участника POST http://casebook.ru/api/Card/BusinessCard
    jsCardBusinessCard = cardBusinessCard(session, side)

    # поиск дел с участием стороны
    # POST http://casebook.ru/api/Search/Cases
    # payload {"StatusEx":[],"SideTypes":[],"ConsiderType":-1,"CourtType":-1,"CaseNumber":null,"CaseCategoryId":"","MonitoredStatus":-1,"Courts":[],"Instances":[],"Judges":[],"Delegate":"","StateOrganizations":[],"DateFrom":null,"DateTo":null,"SessionFrom":null,"SessionTo":null,"FinalDocFrom":null,"FinalDocTo":null,"MinSum":0,"MaxSum":-1,"Sides":[{"Name":"ДИРЕКЦИЯ ...","ShortName":"ТПП ...","Inn":"1106014140","Ogrn":"1021100895760","Okpo":"3314561","Address":"169300, РЕСП...","IsUnique":false,"IsOriginal":true,"IsBranch":true},{"Name":"ДИР...","ShortName":"ТПП ...","Inn":"1106014140","Ogrn":"1021100895760","Okpo":"3314561","IsUnique":false,"OrganizationId":0,"Address":"169300, РЕСП...","IsBranch":true}],"CoSides":[],"Accuracy":0,"Page":1,"Count":30,"OrderBy":"incoming_date_ts desc","JudgesNames":[]}
    __ = searchCases4Side(session, side)

    # поиск дел общей юрисдикции
    # POST http://casebook.ru/api/Search/CasesGj
    # payload {"CoSides":[],"Count":30,"DateFrom":null,"DateTo":null,"OrderBy":"incoming_date_ts desc","Page":1,"Sides":[{"Name":"ДИРЕКЦИЯ...","ShortName":"ТПП ...","Inn":"1106014140","Ogrn":"1021100895760","Okpo":"3314561","Address":"169300, РЕСП...","IsUnique":false,"IsOriginal":true,"IsBranch":true},{"Name":"ДИРЕКЦИЯ ...","ShortName":"ТПП ...","Inn":"1106014140","Ogrn":"1021100895760","Okpo":"3314561","IsUnique":false,"OrganizationId":0,"Address":"169300, РЕСП...","IsBranch":true}],"CaseTypeId":"","Courts":[]}
    __ = searchCasesGj4Side(session, side)

    bankruptCases = getCasesFromBancruptCard(jsCardBankruptCard)
    print "collectSideData, num of cases in bankruptCard: %s" % len(bankruptCases)
    for x in bankruptCases:
        case = utils.replaceNone(x)
        case[u"CaseId"] = case.get(u'Id', u'')
        print u"collectSideData, cardBankruptCard, goto case: %s" % case.get(u'Number', u'')
        # complex method, recursion
        collectCaseData(session, case, deep-1)

    businessSides = getSidesFromBusinessCard(jsCardBusinessCard)
    print "collectSideData, num of sides in businessCard: %s" % len(businessSides)
    for x in businessSides:
        bside = utils.replaceNone(x)
        print u"collectSideData, cardBusinessCard, goto side: %s" % sideShortName(bside)
        # complex method, get data recursively
        collectSideData(session, bside, deep-1)

    stor.commit('sides', sid)


def collectCaseData(session, case, deep=2):
    '''Collect all information for given case.

    Sequence:
        card.case
        Card.PdfDocumentArchiveCaseCount - just num of docs - skip it
        card.casedocuments
        File.PdfDocumentArchiveCase
        for each side
            collectSideData
        for each judge
            Card.Judge

    URLs:
        GET http://casebook.ru/api/Card/Case
        GET http://casebook.ru/api/Card/CaseDocuments
        GET http://casebook.ru/File/PdfDocumentArchiveCase
        GET http://casebook.ru/api/Card/Judge
        POST http://casebook.ru/api/Card/BusinessCard
        POST http://casebook.ru/api/Card/BankruptCard

    :param casebook.http.HttpSession session: HTTP session wrapper
    :param dict case: case data from casebook.messages.JsonResponce
    :param bool deep: recursion limit
    '''
    if deep <= 0:
        print u"collectCaseData, end of recursion"
        return

    CaseId = case[u"CaseId"]
    print "collectCaseData, CaseId: %s" % CaseId
    if not CaseId:
        print "collectCaseData, CaseId is undefined, nothing to do"
        return

    # check if we already get this case today
    if caseDataIsFresh(CaseId):
        print "collectCaseData, case data downloaded already, nothing to do"
        return

    #~ карточка дела GET http://casebook.ru/api/Card/Case?id=78d283d0-010e-4c50-b1d1-cf2395c00bf9
    jsCardCase = cardCase(session, CaseId)

    #~ инфо о документах GET http://casebook.ru/api/Card/CaseDocuments?id=78d283d0-010e-4c50-b1d1-cf2395c00bf9
    __ = cardCaseDocuments(session, CaseId)

    #~ архив документов GET http://casebook.ru/File/PdfDocumentArchiveCase/78d283d0-010e-4c50-b1d1-cf2395c00bf9/%D0%9040-27010-2012.zip
    #~ Content-Type: application/zip
    filePdfDocumentArchiveCase(session, CaseId)

    caseJudges = getJudgesFromCase(jsCardCase)
    print "collectCaseData, num of case judges: %s" % len(caseJudges)
    for x in caseJudges:
        judge = utils.replaceNone(x)
        judgeID = judge[u'Id']
        print "Judge ID: %s" % judgeID
        #~ карточка судьи GET http://casebook.ru/api/Card/Judge/96743d1a-ca39-4c2f-a5f2-94a2aa0c8b8f
        __ = cardJudge(session, judgeID)

    caseSides = getSidesFromCase(jsCardCase)
    print "collectCaseData, num of case sides: %s" % len(caseSides)
    for x in caseSides:
        side = utils.replaceNone(x)
        print "collectCaseData, case sides, goto Side: %s" % sideShortName(side)
        # complex method, get data recursively (BusinessCard, BankruptCard)
        collectSideData(session, side, deep-1)

    stor.commit('cases', CaseId)


def cardJudge(session, judgeID):
    '''Get Card/Judge data from http://casebook.ru/api/Card/Judge/
    and save results.

    Returns messages.JsonResponce with casebook message

    GET http://casebook.ru/api/Card/Judge/96743d1a-ca39-4c2f-a5f2-94a2aa0c8b8f
    '''
    print u"Card/Judge for judge ID '%s' ..." % judgeID

    url = 'http://casebook.ru/api/Card/Judge/%s' % judgeID
    res = session.get(url)

    #print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCardJudge = parseResponce(res.text)

    stor.saveCardJudge(jsCardJudge, judgeID)
    return jsCardJudge


def searchCasesGj4Side(session, side):
    '''Search cases GJ (общая юрисдикция) with given side.
    Returns casebook.ru message with list of cases.

    POST http://casebook.ru/api/Search/CasesGj
    payload example: {"CoSides":[],"Count":30,"DateFrom":null,"DateTo":null,"OrderBy":"incoming_date_ts desc",
        "Page":1,"Sides":[{"Name":"ДИРЕКЦИЯ...","ShortName":"ТПП ...","Inn":"1106014140",
        "Ogrn":"1021100895760","Okpo":"3314561","Address":"169300, РЕСП...","IsUnique":false,
        "IsOriginal":true,"IsBranch":true},{"Name":"ДИРЕКЦИЯ ...","ShortName":"ТПП ...",
        "Inn":"1106014140","Ogrn":"1021100895760","Okpo":"3314561","IsUnique":false,
        "OrganizationId":0,"Address":"169300, РЕСП...","IsBranch":true}],"CaseTypeId":"","Courts":[]}

    :param session:
    :param side:
    '''
    print u"Search/CasesGj for side '%s' ..." % sideShortName(side)

    payload = getSearchCasesGj4SidePayload(side)
    url = 'http://casebook.ru/api/Search/CasesGj'
    res = session.post(url, data=postData(payload))

    #print u"%s: %s" % (url, res.text)
    jsRes = parseResponce(res.text)
    stor.saveSearchCasesGj4Side(jsRes, side)

    return jsRes


def searchCases4Side(session, side):
    '''Search cases with given side.
    Returns casebook.ru message with list of cases.

    POST http://casebook.ru/api/Search/Cases
    payload example: {"StatusEx":[],"SideTypes":[],"ConsiderType":-1,"CourtType":-1,
        "CaseNumber":null,"CaseCategoryId":"","MonitoredStatus":-1,"Courts":[],
        "Instances":[],"Judges":[],"Delegate":"","StateOrganizations":[],"DateFrom":null,
        "DateTo":null,"SessionFrom":null,"SessionTo":null,"FinalDocFrom":null,"FinalDocTo":null,
        "MinSum":0,"MaxSum":-1,"Sides":[{"Name":"ДИРЕКЦИЯ ...","ShortName":"ТПП ...",
        "Inn":"1106014140","Ogrn":"1021100895760","Okpo":"3314561","Address":"169300, РЕСП...",
        "IsUnique":false,"IsOriginal":true,"IsBranch":true}],
        "CoSides":[],"Accuracy":0,"Page":1,"Count":30,"OrderBy":"incoming_date_ts desc","JudgesNames":[]}

    :param casebook.http.HttpSession session: HTTP session wrapper
    :param dict side: side data from casebook.messages.JsonResponce
    :rtype casebook.messages.JsonResponce
    '''
    print u"Search/Cases for side '%s' ..." % sideShortName(side)

    payload = getSearchCases4SidePayload(side)
    url = 'http://casebook.ru/api/Search/Cases'
    res = session.post(url, data=postData(payload))

    #print u"%s: %s" % (url, res.text)
    jsRes = parseResponce(res.text)
    stor.saveSearchCases4Side(jsRes, side)

    return jsRes


def calendarPeriod(session, side):
    '''Get events schedule for side, Calendar/Period.
    Returns casebook.messages.JsonResponce with casebook message.

    POST http://casebook.ru/api/Calendar/Period

    :param casebook.http.HttpSession session: HTTP session wrapper
    :param dict side: side data from casebook.messages.JsonResponce
    '''
    print u"Calendar/Period for side '%s' ..." % sideShortName(side)

    payload = getCalendarPeriodPayload(side)
    url = 'http://casebook.ru/api/Calendar/Period'
    res = session.post(url, data=postData(payload))

    #print u"%s: %s" % (url, res.text)
    jsRes = parseResponce(res.text)
    stor.saveCalendarPeriod(jsRes, side)

    return jsRes


def searchSidesDetailsEx(session, side):
    '''Get side data from casebook, Search/SidesDetailsEx.
    GET http://casebook.ru/api/Search/SidesDetailsEx?index=1&inn=1106014140&okpo=3314561

    Returns casebook.messages.JsonResponce with casebook message.

    :param casebook.http.HttpSession session: HTTP session wrapper
    '''
    print u"Search/SidesDetailsEx for side '%s' ..." % sideShortName(side)

    payload = {u'index' : 1,
               u'inn'   : side.get(u'Inn', ''),
               u'okpo'  : side.get(u'Okpo', '')}

    url = 'http://casebook.ru/api/Search/SidesDetailsEx'
    res = session.get(url, params=payload)
    #print u"%s: %s" % (url, res.text)

    jsRes = parseResponce(res.text)
    stor.saveSearchSidesDetailsEx(jsRes, side)
    return jsRes


def cardExcerpt(session, side):
    '''Get Card/Excerpt document from casebook

    выписка из ЕГРЮЛ
    GET http://casebook.ru/api/Card/Excerpt?
        Address=169300, РЕСПУБЛИКА КОМИ, Г УХТА, УЛ ОКТЯБРЬСКАЯ, Д 11
        &Inn=1106014140
        &Name=ДИРЕКЦИЯ СОЗДАЮЩЕГОСЯ ПРЕДРИЯТИЯ ...
        &Ogrn=1021100895760
        &Okpo=3314561
        &IsUnique=false
        &OrganizationId=0
        &StorageId=346280
    '''
    print u"Card/Excerpt for side '%s' ..." % sideShortName(side)

    payload = getSideCardPayload(side)
    payload[u'IsUnique'] = False
    payload[u'OrganizationId'] = ''
    payload[u'StorageId'] = ''

    url = 'http://casebook.ru/api/Card/Excerpt'
    res = session.get(url, params=payload, stream=True)

    print (u"%s: %s" % (url, res.status_code)).encode(CP)
    stor.saveCardExcerpt(res, side)


def cardAccountingStat(session, side):
    '''Get side data from casebook. отчетность.
    POST http://casebook.ru/api/Card/AccountingStat

    Side must have been set Inn, Ogrn or Okpo parameters.

    Returns messages.JsonResponce with casebook message
    '''
    print u"Card/AccountingStat for side '%s' ..." % sideShortName(side)

    payload = getSideAccountingStatPayload(side)
    url = 'http://casebook.ru/api/Card/AccountingStat'
    res = session.post(url, data=postData(payload))

    #print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCardAccountingStat = parseResponce(res.text)

    stor.saveCardAccountingStat(jsCardAccountingStat, side)
    return jsCardAccountingStat


def cardBankruptCard(session, side, sideID=''):
    '''Get side Card/BankruptCard data from casebook.ru
    and save results.

    POST http://casebook.ru/api/Card/BankruptCard
    payload {"Address":"Данные скрыты","Inn":"","Name":"Гурняк Я. Ф.","Ogrn":"","Okpo":"","IsNotPrecise":true,"OrganizationId":""}

    :rtype casebook.messages.JsonResponce: with casebook message

    :param casebook.http.HttpSession session: HTTP session wrapper
    :param dict side: side data from casebook.messages.JsonResponce
    :param str sideID: obsolete
    '''
    print u"Card/BankruptCard for side '%s' ..." % sideShortName(side)

    payload = getSideCardPayload(side)
    url = 'http://casebook.ru/api/Card/BankruptCard'
    res = session.post(url, data=postData(payload))

    #print u"%s: %s" % (url, res.text)
    jsCardBankruptCard = parseResponce(res.text)

    stor.saveCardBankruptCard(jsCardBankruptCard, side, sideID)
    return jsCardBankruptCard


def cardBusinessCard(session, side, sideID=''):
    '''Get Card/BusinessCard data from http://casebook.ru/api/Card/BusinessCard
    and save results.

    Returns messages.JsonResponce with casebook message

    side: dictionary with side data from Card/Case

    POST http://casebook.ru/api/Card/BusinessCard
    payload {"Address":"Данные скрыты","Inn":"","Name":"Гурняк Я. Ф.","Ogrn":"","Okpo":"","IsNotPrecise":true,"OrganizationId":""}
    '''
    print u"Card/BusinessCard for side '%s' ..." % sideShortName(side)

    payload = getSideCardPayload(side)
    url = 'http://casebook.ru/api/Card/BusinessCard'
    res = session.post(url, data=postData(payload))

    #print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCardBusinessCard = parseResponce(res.text)

    stor.saveCardBusinessCard(jsCardBusinessCard, side, sideID)
    return jsCardBusinessCard


def filePdfDocumentArchiveCase(session, CaseId):
    '''Get File/PdfDocumentArchiveCase data from http://casebook.ru/File/PdfDocumentArchiveCase/
    and save results (CaseId.caseDocs.zip file).
    '''
    print u"File/PdfDocumentArchiveCase by CaseId '%s' ..." % CaseId

    url = 'http://casebook.ru/File/PdfDocumentArchiveCase/%s/%s.caseDocs.zip' % (CaseId, CaseId)
    res = session.get(url, stream=True)

    print (u"%s: %s" % (url, res.status_code)).encode(CP)
    stor.saveFilePdfDocumentArchiveCase(res, CaseId)


def cardCaseDocuments(session, CaseId):
    '''Get Card/CaseDocuments data from http://casebook.ru/api/Card/CaseDocuments
    and save results.
    Returns messages.JsonResponce with casebook message
    '''
    print u"Card/CaseDocuments by CaseId '%s' ..." % CaseId

    url = 'http://casebook.ru/api/Card/CaseDocuments'
    payload = {'id': CaseId}
    res = session.get(url, params=payload)

    #print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCardCaseDocuments = parseResponce(res.text)

    stor.saveCardCaseDocuments(jsCardCaseDocuments, CaseId)
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

    #print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCardCase = parseResponce(res.text)

    stor.saveCardCase(jsCardCase, CaseId)
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

    #print (u"%s: %s" % (url, res.text)).encode(CP)
    jsSides = parseResponce(res.text)

    #~ Результат каждого запроса сохраняется в файл по шаблону:
    #~ data/query.{hash}.(cases|sides).json
    fname = stor.saveSidesSearch(jsSides, queryString)
    #~ Дополнительно, информация о запросе/ответе сохраняется в индексный файл:
    #~ index.json
    stor.updateIndexForSidesSearch(queryString, fname, jsSides)
    return jsSides


def findCases(session, queryString):
    '''Find cases via POST http://casebook.ru/api/Search/Cases
    and save results.
    Returns messages.JsonResponce with casebook message
    '''
    print (u"casesBy '%s' ..." % queryString).encode(CP)

    qt = const.CASES_QUERY_TEMPLATE
    payload = simplejson.loads(qt)
    payload[u"Query"] = queryString
    url = 'http://casebook.ru/api/Search/Cases'
    res = session.post(url, data=postData(payload))

    #print (u"%s: %s" % (url, res.text)).encode(CP)
    jsCases = parseResponce(res.text)

    #~ Результат каждого запроса сохраняется в файл по шаблону:
    #~ data/query.{hash}.(cases|sides).json
    fname = stor.saveCasesSearch(jsCases, queryString)
    #~ Дополнительно, информация о запросе/ответе сохраняется в индексный файл:
    #~ index.json
    stor.updateIndexForCasesSearch(queryString, fname, jsCases)
    return jsCases


def postData(payload):
    '''Returns JSON string for casebook POST requests payload.

    :param dict payload:
    :rtype str
    '''
    return utils.toJsonCompact(payload, False)


def sideShortName(side):
    '''Returns side ShortName or Name from dictionary

    :param dict side: side data
    :rtype str
    '''
    res = side.get(u'ShortName', u'')
    if not res:
        res = side.get(u'Name', u'')
    return res


def sideDataIsFresh(sid):
    '''Returns True if side data registered in index file and
    timestamp is no older then const.FRESH_PERIOD

    :param str sid: side pseudoID, e.g. "1106014140;1021100895760;3314561;ДИРЕКЦИЯ ..."
    :rtype bool
    '''
    return stor.ListItemIsFresh('sides', sid, const.FRESH_PERIOD)


def caseDataIsFresh(cid):
    '''Returns True if case data registered in index file and
    timestamp is no older then const.FRESH_PERIOD

    :param str cid: case ID, e.g. "4d2b538e-bd5b-4e17-806c-0ef13c367e11"
    :rtype bool
    '''
    return stor.ListItemIsFresh('cases', cid, const.FRESH_PERIOD)


def getSidesFromBusinessCard(jsCard):
    '''Returns list of sides from side business card.
    Each side is a dict.

    sides = Result.Founders + Result.AffiliatedOrganizations
        + Result.HeadOrganization + Result.Branches

    :param casebook.messages.JsonResponce jsCard: object with Card/BusinessCard data
    :rtype list
    '''
    res = []
    for x in [u'Founders', u'AffiliatedOrganizations', u'HeadOrganization', u'Branches']:
        lst = jsCard.obj.get(u'Result', {}).get(x, [])
        if isinstance(lst, list):
            res += lst
    return res


def getCasesFromBancruptCard(jsCard):
    '''Returns list of cases from side bancrupt card.
    Each case is a dict.

    :param casebook.messages.JsonResponce jsCard: object with Card/BankruptCard data
    :rtype list
    '''
    return jsCard.obj[u'Result'][u'Cases']


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


def getSearchCasesGj4SidePayload(side):
    '''Returns payload dict for POST http://casebook.ru/api/Search/CasesGj

    Search GJ cases for side.

    :param dict side: side data from casebook.messages.JsonResponce
    :rtype dict
    '''
    qt = u'''
    {
      "CoSides": [],
      "Count": 30,
      "DateFrom": null,
      "DateTo": null,
      "OrderBy": "incoming_date_ts desc",
      "Page": 1,
      "Sides": [
        {
          "Name": "ДИРЕКЦИЯ...",
          "ShortName": "ТПП ...",
          "Inn": "1106014140",
          "Ogrn": "1021100895760",
          "Okpo": "3314561",
          "Address": "169300, РЕСП...",
          "IsUnique": false,
          "IsOriginal": true,
          "IsBranch": true
        }
      ],
      "CaseTypeId": "",
      "Courts": []
    }
    '''
    payload = utils.fromJson(qt)

    sides = getCalendarPeriodPayload(side).get(u'Sides', [])
    payload[u'Sides'] = sides

    return payload


def getSearchCases4SidePayload(side):
    '''Returns payload dict for POST http://casebook.ru/api/Search/Cases

    Search cases for side.

    :param dict side: side data from casebook.messages.JsonResponce
    :rtype dict
    '''
    qt = u'''
    {
      "StatusEx": [],
      "SideTypes": [],
      "ConsiderType": -1,
      "CourtType": -1,
      "CaseNumber": null,
      "CaseCategoryId": "",
      "MonitoredStatus": -1,
      "Courts": [],
      "Instances": [],
      "Judges": [],
      "Delegate": "",
      "StateOrganizations": [],
      "DateFrom": null,
      "DateTo": null,
      "SessionFrom": null,
      "SessionTo": null,
      "FinalDocFrom": null,
      "FinalDocTo": null,
      "MinSum": 0,
      "MaxSum": -1,
      "Sides": [
        {
          "Name": "ДИРЕКЦИЯ ...",
          "ShortName": "ТПП ...",
          "Inn": "1106014140",
          "Ogrn": "1021100895760",
          "Okpo": "3314561",
          "Address": "169300, РЕСП...",
          "IsUnique": false,
          "IsOriginal": true,
          "IsBranch": true
        }
      ],
      "CoSides": [],
      "Accuracy": 0,
      "Page": 1,
      "Count": 30,
      "OrderBy": "incoming_date_ts desc",
      "JudgesNames": []
    }
    '''
    payload = utils.fromJson(qt)

    sides = getCalendarPeriodPayload(side).get(u'Sides', [])
    payload[u'Sides'] = sides

    return payload


def getCalendarPeriodPayload(side):
    '''Returns payload dict for POST http://casebook.ru/api/Calendar/Period

    :param dict side: side data from casebook
    :rtype dict
    '''
    qt = (u'''{"Courts":[],"Judges":[],"CaseTypeId":null,"CaseCategoryId":null,"Side":"","JudgesNames":[],'''
          u'''"Sides":['''
              u'''{"Name":"ДИРЕКЦИЯ ...","ShortName":"ТПП УХТАНЕФТЬ ...",'''
              u'''"Inn":"1106014140","Ogrn":"1021100895760","Okpo":"3314561","Address":"169300, РЕСПУБЛИКА КОМИ...",'''
              u'''"IsBranch":true,"IsUnique":false,"IsOriginal":true},'''
              u'''{"Name":"ДИРЕКЦИЯ ...","ShortName":"ТПП УХТАНЕФТЬ ...", '''
              u'''"Inn":"1106014140","Ogrn":"1021100895760","Okpo":"3314561","Address":"169300, РЕСПУБЛИКА КОМИ ...",'''
              u'''"IsBranch":true,"IsUnique":false,"OrganizationId":0}'''
          u'''],'''
          u'''"DateFrom":"2014-04-11","DateTo":"2014-05-10"}''')
    payload = simplejson.loads(qt)

    scp = getSideCardPayload(side) # need to add ShortName, IsUnique, IsBranch, IsOriginal, OrganizationId,
    scp[u'ShortName'] = side.get(u'ShortName', u'')
    scp[u'IsUnique'] = side.get(u'IsUnique', False)
    scp[u'IsBranch'] = side.get(u'IsBranch', False)

    today = datetime.date.today()
    payload[u'DateFrom'] = today.isoformat()
    payload[u'DateTo'] = (today + datetime.timedelta(30)).isoformat()

    payload[u'Sides'][0] = payload[u'Sides'][1] = scp
    payload[u'Sides'][0][u'IsOriginal'] = side.get(u'IsOriginal', True)
    payload[u'Sides'][1][u'OrganizationId'] = side.get(u'OrganizationId', 0)

    return payload


def getSideCardPayload(side):
    '''Returns dict payload for
    POST http://casebook.ru/api/Card/BankruptCard
    POST http://casebook.ru/api/Card/BusinessCard

    Address, Inn, Name, Ogrn, Okpo, IsUnique, IsNotPrecise, OrganizationId
    '''
    qt = u'''{"Address":"","Inn":"","Name":"","Ogrn":"","Okpo":"","IsNotPrecise":true,"IsUnique": false,"OrganizationId":""}'''
    payload = simplejson.loads(qt)

    payload[u"Address"] = side.get(u'Address', u'')
    payload[u"Inn"] = side.get(u'Inn', u'')
    payload[u"Name"] = side.get(u'Name', u'')
    payload[u"Ogrn"] = side.get(u'Ogrn', u'')
    payload[u"Okpo"] = side.get(u'Okpo', u'')

    payload[u"IsUnique"] = side.get(u'IsUnique', False)
    payload[u"IsNotPrecise"] = side.get(u'IsNotPrecise', True)
    payload[u"OrganizationId"] = side.get(u'OrganizationId', u'')

    return payload


def getSideAccountingStatPayload(side):
    '''Returns payload for http://casebook.ru/api/Card/AccountingStat
    '''
    qt = u'''{"Organization":{"Address":"","Inn":"","Name":"","Ogrn":"","Okpo":"","IsUnique":false,"OrganizationId":0,"StorageId":null},"Year":null}'''
    payload = simplejson.loads(qt)
    payload[u'Organization'] = side
    return payload


def parseResponce(text):
    '''Print results status message.
    Returns casebook.messages.JsonResponce
    '''
    js = casebook.messages.JsonResponce(text)
    if js.Success and js.Message == u'':
        print 'we good'
    else:
        print u"responce: %s" % text
        err = u"Request failed. Message: %s" % js.Message
        print err.encode(CP)
        raise casebook.RequestError({'message': err, 'responce': text})
    return js


def logon(session, username, password):
    '''Perform LogOn requests on casebook.ru
    If logon isn't successfull raise an casebook.LogOnError exception
    '''
    print "logon..."
    url = 'http://casebook.ru/api/Account/LogOn'
    payload = {"SystemName": "Sps","UserName": username,"Password": password,"RememberMe": True}
    session.deleteCookies()
    res = session.post(url, data=postData(payload))
    #print (u"%s: %s" % (url, res.text)).encode(CP)

    js = casebook.messages.JsonResponce(res.text)
    if js.Success:
        print 'we good'
    else:
        err = u"Auth failed. Message: %s" % js.Message
        print err.encode(CP)
        raise casebook.LogOnError(err)

    return session
