#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

''' casebook file storage module

Created on May 20, 2014

@author: vasnake@gmail.com
'''

import os
import simplejson

import casebook
import casebook.const as const
import casebook.utils as utils

CP = casebook.CP

def saveSearchCases4Side(jsRes, side):
    '''Save side Search/Cases info to a file, update index

    :param casebook.messages.JsonResponce jsRes: text to save
    :param dict side: side data from casebook.messages.JsonResponce
    '''
    sid = utils.getSidePseudoID(side)
    fname = saveResults2File(jsRes, sid, 'search', 'cases4side')
    updateIndexForSearchCases4Side(sid, fname, jsRes)


def saveCalendarPeriod(jsRes, side):
    '''Save side Calendar/Period info to a file, update index

    :param casebook.messages.JsonResponce jsRes: text to save
    :param dict side: side data from casebook.messages.JsonResponce
    '''
    sid = utils.getSidePseudoID(side)
    fname = saveResults2File(jsRes, sid, 'calendar', 'period')
    updateIndexForCalendarPeriod(sid, fname, jsRes)


def saveSearchSidesDetailsEx(jsRes, side):
    '''Save side Search/SidesDetailsEx info to a file, update index
    '''
    sid = utils.getSidePseudoID(side)
    fname = saveResults2File(jsRes, sid, 'search', 'sidesdetailsex')
    updateIndexForSidesDetailsEx(sid, fname, jsRes)


def saveCardJudge(jsCardJudge, judgeID):
    '''Save judge info to a file, update index
    '''
    fname = saveResults2File(jsCardJudge, judgeID, 'card', 'judge')
    updateIndexForJudgeCard(judgeID, fname, jsCardJudge)


def saveCardExcerpt(res, side):
    '''Save side doc (выписка из ЕГРЮЛ) to file, update index

    res: requests.Responce object with binary data
    '''
    SideId = utils.getSidePseudoID(side)
    fname = saveResults2File(res, SideId, 'card', 'excerpt', 'pdf')
    updateIndexForCardExcerpt(SideId, fname, None)


def saveCardAccountingStat(jsCardAccountingStat, side):
    '''Save side accountingstat info to a file, update index
    '''
    SideId = utils.getSidePseudoID(side)
    fname = saveResults2File(jsCardAccountingStat, SideId, 'card', 'accountingstat')
    updateIndexForAccountingStatCard(SideId, fname, jsCardAccountingStat)


def saveCardBankruptCard(jsCardBankruptCard, side, sideID=''):
    '''Save side bankruptcard info to a file, update index
    '''
    pseudoID = utils.getSidePseudoID(side)
    fname = saveResults2File(jsCardBankruptCard, pseudoID, 'card', 'bankruptcard')
    updateIndexForBankruptCard(pseudoID, fname, jsCardBankruptCard, sideID)


def saveCardBusinessCard(jsCardBusinessCard, side, sideID=''):
    '''Save side businesscard info to a file, update index
    '''
    pseudoID = utils.getSidePseudoID(side)
    fname = saveResults2File(jsCardBusinessCard, pseudoID, 'card', 'businesscard')
    updateIndexForBusinessCard(pseudoID, fname, jsCardBusinessCard, sideID)


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

    respType: string, may be 'json', 'zip', 'pdf'.
        If respType is 'zip', jsResp treated as requests.Responce.
        Otherwise jsResp treated as messages.JsonResponce
    '''
    qid = utils.stringToFileName(queryString)
    fname = os.path.join(const.DATA_DIR, "%s.%s.%s.%s" % (category, qid, typeName, respType))
    print (u"write result to file '%s'" % fname).encode(CP)

    with open(fname, 'wb') as f:
        if respType == 'json':
            f.write(jsResp.text.encode(CP))
        elif respType in ['zip', 'pdf']:
            for chunk in jsResp.iter_content():
                f.write(chunk)
        else:
            raise TypeError("Unknown file type: %s" % respType)
    return fname


def updateIndexForSearchCases4Side(sid, fname, jsData):
    '''Save side id and data file name to index.json file

    :param str sid: side pseudo id
    :param str fname: data filename
    :param casebook.messages.JsonResponce jsData: side data
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'sides', sid)

    meta["SidePseudoId"] = sid
    meta["SearchCases4SideFileName"] = fname
    meta["SearchCases4SideError"] = jsData.Message if jsData.Success == False else ''
    meta["SearchCases4SideWarning"] = jsData.Message

    meta["SearchCases4SideTotalCount"] = jsData.obj.get(u'Result', {}).get(u'TotalCount', 0)

    indexObj = setListItemToIndex(indexObj, 'sides', sid, meta)
    saveIndex(indexObj)


def updateIndexForCalendarPeriod(sid, fname, jsData):
    '''Save side id and data file name to index.json file

    :param str sid: side pseudo id
    :param str fname: data filename
    :param casebook.messages.JsonResponce jsData: side data
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'sides', sid)

    meta["SidePseudoId"] = sid
    meta["CalendarPeriodFileName"] = fname
    meta["CalendarPeriodError"] = jsData.Message if jsData.Success == False else ''
    meta["CalendarPeriodWarning"] = jsData.Message

    meta["CalendarPeriodCount"] = len(jsData.obj[u'Result'])

    indexObj = setListItemToIndex(indexObj, 'sides', sid, meta)
    saveIndex(indexObj)


def updateIndexForSidesDetailsEx(sid, fname, jsData):
    '''Save side id and data file name to index.json file
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'sides', sid)

    meta["SidePseudoId"] = sid
    meta["SidesDetailsExFileName"] = fname
    meta["SidesDetailsExError"] = jsData.Message if jsData.Success == False else ''
    meta["SidesDetailsExWarning"] = jsData.Message

    indexObj = setListItemToIndex(indexObj, 'sides', sid, meta)
    saveIndex(indexObj)


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


def updateIndexForCardExcerpt(sid, fname, jsData=None):
    '''Save Card/Excerpt side id and file name to index.json file
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'sides', sid)

    meta["SidePseudoId"] = sid
    meta["CardExcerptFileName"] = fname

    indexObj = setListItemToIndex(indexObj, 'sides', sid, meta)
    saveIndex(indexObj)


def updateIndexForAccountingStatCard(sid, fname, jsData):
    '''Save side id and file name to index.json file
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'sides', sid)

    meta["SidePseudoId"] = sid
    meta["AccountingFileName"] = fname
    meta["AccountingError"] = jsData.Message if jsData.Success == False else ''
    meta["AccountingWarning"] = jsData.Message

    indexObj = setListItemToIndex(indexObj, 'sides', sid, meta)
    saveIndex(indexObj)


def updateIndexForBankruptCard(sid, fname, jsCardBankruptCard, sideID=''):
    '''Save side id and file name to index.json file
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'sides', sid)

    state = jsCardBankruptCard.obj.get(u'Result', {}).get(u'State', '')
    state = '' if state is None else state

    meta["SidePseudoId"] = sid
    meta["BankruptFileName"] = fname
    meta["BankruptState"] = state
    meta["Error"] = jsCardBankruptCard.Message if jsCardBankruptCard.Success == False else ''
    meta["Warning"] = jsCardBankruptCard.Message
    if sideID:
        meta["SideId"] = sideID

    indexObj = setListItemToIndex(indexObj, 'sides', sid, meta)
    saveIndex(indexObj)


def updateIndexForBusinessCard(sid, fname, jsCardBusinessCard, sideID=''):
    '''Save side id and file name to index.json file
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, 'sides', sid)

    meta["SidePseudoId"] = sid
    meta["FileName"] = fname
    meta["Name"] = jsCardBusinessCard.obj.get(u'Result', {}).get(u'Name', '')
    meta["Address"] = jsCardBusinessCard.obj.get(u'Result', {}).get(u'Address', '')
    meta["Error"] = jsCardBusinessCard.Message if jsCardBusinessCard.Success == False else ''
    meta["Warning"] = jsCardBusinessCard.Message
    if sideID:
        meta["SideId"] = sideID

    indexObj = setListItemToIndex(indexObj, 'sides', sid, meta)
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


def loadIndex():
    '''Returns indexObj = simplejson.loads(indexText from index.json file)
    '''
    indexFname = os.path.join(const.DATA_DIR, "index.json")
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
    with open(os.path.join(const.DATA_DIR, "index.json"), 'wb') as f:
        f.write(txt.encode(CP))


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

    :rtype dict
    '''
    idxList = indexObj.get(listName, {})
    return idxList.get(itemName, {})


def setListItemToIndex(indexObj, listName, itemName, data):
    '''Set index.{listName}.{itemName} to data.
    Returns updated indexObj
    '''
    data['Updated'] = utils.getTimeStamp()
    idxList = indexObj.get(listName, {})
    idxList[itemName] = data
    indexObj[listName] = idxList
    return indexObj


def ListItemIsFresh(listname, iid, freshPeriod):
    '''Returns True if item data registered in index file and
    timestamp is no older then freshPeriod

    :param str listname: 'cases' or 'sides' list name
    :param str iid: side or case id in index
    :param int freshPeriod: see const.FRESH_PERIOD
    :rtype bool
    '''
    idx = loadIndex()
    meta = getListItemFromIndex(idx, listname, iid)
    ts = meta .get('CommitTS', '')

    if not ts:
        return False

    se = utils.secondsElapsed(ts)
    if se > freshPeriod:
        return False
    return True


def commit(listname, iid):
    '''Update item timestamp

    :param str listname: 'cases' or 'sides' list name
    :param str iid: side or case id in index
    '''
    indexObj = loadIndex()
    meta = getListItemFromIndex(indexObj, listname, iid)

    meta['CommitTS'] = utils.getTimeStamp()

    indexObj = setListItemToIndex(indexObj, listname, iid, meta)
    saveIndex(indexObj)
