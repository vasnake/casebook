#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

''' casebook responce message formats

'''

import simplejson

import casebook

CP = casebook.CP

class JsonResponce(object):
    """ casebook.ru JSON responce
    """

    def __init__(self, text):
        '''JsonResponce constructor
        js = casebook.messages.JsonResponce(res.text)
        '''
        self.text = text
        self.obj = simplejson.loads(text)

    @property
    def Success(self):
        '''Returns responce 'Success' field value.
        True or False
        '''
        return self.obj.get(u'Success', False)

    @property
    def Message(self):
        '''Returns responce 'Message' field value.
        Message string or 'n/a'
        '''
        res = self.obj.get(u'Message', u'')
        if res is None:
            return u''
        return res
# class JsonResponce(object):
