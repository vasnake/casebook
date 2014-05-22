#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

''' casebook utils module

Created on May 20, 2014

@author: vasnake@gmail.com
'''

import time

import casebook

CP = casebook.CP

def getSidePseudoID(side):
    '''Returns unique string for side
    Inn + Ogrn + Okpo + Name + Address
    '''
    sid = []
    for x in (u'Inn', u'Ogrn', 'Okpo', u'Name', u'Address'):
        sid.append(side.get(x, u''))
    return u';'.join(sid)


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


def getTimeStamp():
    '''Returns timestamp string
    e.g. 2014-05-22 18:35:52
    '''
    return time.strftime('%Y-%m-%d %H:%M:%S')


def timeStamp2Time(ts):
    '''Convert timestamp string to time.struct_time tuple.
    Returns time.struct_time tuple.

    :param ts: string, timestamp according format '%Y-%m-%d %H:%M:%S'
    '''
    return time.strptime(ts, '%Y-%m-%d %H:%M:%S')


def secondsElapsed(ts):
    '''Returns number of seconds from now to timestamp ts.

    :param ts: string, timestamp according format '%Y-%m-%d %H:%M:%S'
    '''
    res = time.mktime(time.localtime()) - time.mktime(timeStamp2Time(ts))
    return int(res)

